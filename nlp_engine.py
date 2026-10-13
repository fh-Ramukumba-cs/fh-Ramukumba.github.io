
"""
NLP Engine - Resume Screening & Candidate Ranking
Implements:
  - Text pre-processing (tokenization, stopwords, lemmatization)
  - Synonym normalization (JS -> JavaScript, ML -> Machine Learning, etc.)
  - Skill extraction
  - TF-IDF + Cosine Similarity (BASELINE - keyword-based)
  - Sentence-BERT semantic similarity (ADVANCED - meaning-based)
  - Gap analysis and CV validation

Author: Forget Hangwani Ramukumba (202353346)
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------- Lazy-load BERT (only loads on first use) --------
_bert_model = None


def get_bert_model():
    """Load Sentence-BERT model on demand (caches after first call)."""
    global _bert_model
    if _bert_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("[BERT] Loading model 'all-MiniLM-L6-v2' (first time only)...")
            _bert_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[BERT] Model loaded successfully.")
        except Exception as e:
            print(f"[BERT] Failed to load: {e}")
            _bert_model = False
    return _bert_model if _bert_model is not False else None


# -------- NLTK setup --------
for pkg in ['tokenizers/punkt', 'corpora/stopwords', 'corpora/wordnet']:
    try:
        nltk.data.find(pkg)
    except LookupError:
        try:
            nltk.download(pkg.split('/')[-1], quiet=True)
        except Exception:
            pass

lemmatizer = WordNetLemmatizer()
try:
    stop_words = set(stopwords.words('english'))
except Exception:
    stop_words = set()


# ============================================================
# SYNONYM MAP
# ============================================================
SYNONYM_MAP = {
    'js': 'javascript',
    'ts': 'typescript',
    'py': 'python',
    'golang': 'go',
    'c sharp': 'c#',
    'csharp': 'c#',
    'c plus plus': 'c++',
    'react.js': 'react',
    'reactjs': 'react',
    'node.js': 'node',
    'nodejs': 'node',
    'vue.js': 'vue',
    'vuejs': 'vue',
    'next.js': 'nextjs',
    'nuxt.js': 'nuxt',
    'postgres': 'postgresql',
    'mongo': 'mongodb',
    'ms sql': 'sql server',
    'mssql': 'sql server',
    'amazon web services': 'aws',
    'google cloud': 'gcp',
    'google cloud platform': 'gcp',
    'k8s': 'kubernetes',
    'ci cd': 'ci/cd',
    'continuous integration': 'ci/cd',
    'ml': 'machine learning',
    'dl': 'deep learning',
    'ai': 'artificial intelligence',
    'nlp': 'natural language processing',
    'sklearn': 'scikit-learn',
    'pm': 'project management',
    'hr': 'human resources',
}


def normalize_synonyms(text):
    if not text:
        return ""
    result = text.lower()
    for synonym, canonical in sorted(SYNONYM_MAP.items(), key=lambda x: -len(x[0])):
        pattern = r'\b' + re.escape(synonym) + r'\b'
        result = re.sub(pattern, canonical, result)
    return result


# ============================================================
# PREPROCESSING
# ============================================================
def preprocess_text(text):
    if not text:
        return ""
    text = text.lower()
    text = normalize_synonyms(text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()
    cleaned = [lemmatizer.lemmatize(t) for t in tokens
               if t not in stop_words and len(t) > 2]
    return ' '.join(cleaned)


# ============================================================
# SKILL DATABASE
# ============================================================
SKILL_DATABASE = [
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby',
    'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'dart',
    'react', 'angular', 'vue', 'node', 'nodejs', 'express', 'django', 'flask',
    'spring', 'laravel', 'rails', 'asp.net', 'nextjs', 'nuxt', 'svelte',
    'sql', 'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'redis',
    'machine learning', 'deep learning', 'nlp', 'natural language processing',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
    'data analysis', 'data science', 'data mining', 'big data', 'hadoop', 'spark',
    'tableau', 'power bi', 'excel',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
    'gitlab', 'ci/cd', 'terraform', 'ansible', 'linux', 'unix', 'bash',
    'project management', 'agile', 'scrum', 'kanban', 'jira', 'communication',
    'leadership', 'teamwork', 'problem solving', 'critical thinking',
    'time management', 'adaptability', 'creativity',
    'figma', 'photoshop', 'illustrator', 'ui', 'ux', 'ui/ux', 'sketch',
    'api', 'rest', 'graphql', 'microservices', 'html', 'css', 'sass',
    'seo', 'marketing', 'sales', 'accounting', 'finance', 'hr', 'recruitment',
    'human resources', 'artificial intelligence', 'sql server'
]


def extract_skills(text):
    if not text:
        return []
    text_lower = normalize_synonyms(text)
    found = []
    for skill in SKILL_DATABASE:
        if len(skill) <= 3:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found.append(skill)
        else:
            if skill in text_lower:
                found.append(skill)
    return sorted(set(found))


def extract_education(text):
    if not text:
        return []
    t = text.lower()
    degrees = {
        'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
        'master': ['master', 'msc', 'm.sc', 'mba', 'meng', 'm.eng'],
        'bachelor': ['bachelor', 'bsc', 'b.sc', 'beng', 'b.eng', 'honours'],
        'diploma': ['diploma', 'certificate', 'certification', 'certified']
    }
    found = []
    for level, keywords in degrees.items():
        for kw in keywords:
            if kw in t:
                found.append(level)
                break
    return found


def extract_experience_years(text):
    if not text:
        return 0
    t = text.lower()
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
        r'experience\s+(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)\s+in\s+',
    ]
    max_years = 0
    for pattern in patterns:
        for match in re.findall(pattern, t):
            try:
                y = int(match)
                if 0 < y < 50:
                    max_years = max(max_years, y)
            except Exception:
                pass
    return max_years


# ============================================================
# CV VALIDATION
# ============================================================
CV_INDICATOR_KEYWORDS = [
    'experience', 'education', 'skill', 'work', 'employment', 'project',
    'university', 'college', 'degree', 'certificate', 'reference',
    'responsibility', 'achievement', 'qualification', 'position',
    'company', 'role', 'job', 'career', 'professional', 'resume', 'curriculum',
    'summary', 'profile', 'objective', 'training', 'award', 'language',
    'email', 'phone', 'contact', 'address', 'linkedin'
]


def validate_cv(resume_text):
    if not resume_text or len(resume_text.strip()) < 30:
        return {'is_valid': False,
                'reason': 'Document is empty or has almost no readable text. May be a scanned image, corrupted file, or not a CV.',
                'confidence': 'high'}

    text_lower = resume_text.lower()
    word_count = len(text_lower.split())
    matches = sum(1 for kw in CV_INDICATOR_KEYWORDS if kw in text_lower)
    core_sections = ['experience', 'education', 'skill', 'work', 'project']
    core_hits = sum(1 for kw in core_sections if kw in text_lower)

    if word_count < 100:
        return {'is_valid': False,
                'reason': f'Document is too short ({word_count} words). A typical CV has 200+ words. May not be a real CV.',
                'confidence': 'high'}
    if core_hits < 2:
        return {'is_valid': False,
                'reason': f'Document is missing key CV sections. Expected at least 2 of: Experience, Education, Skills, Work, Projects. Found {core_hits}.',
                'confidence': 'high'}
    if matches < 4:
        return {'is_valid': False,
                'reason': f'Document does not resemble a typical CV. Only {matches} CV-related keywords detected.',
                'confidence': 'medium'}

    return {'is_valid': True,
            'reason': f'Document appears to be a valid CV ({word_count} words, {matches} CV indicators found).',
            'confidence': 'high'}


# ============================================================
# BASELINE: TF-IDF + COSINE
# ============================================================
def compute_tfidf_similarity(job_desc, resume_text):
    if not job_desc or not resume_text:
        return 0.0
    clean_job = preprocess_text(job_desc)
    clean_resume = preprocess_text(resume_text)
    if not clean_job.strip() or not clean_resume.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000,
                                     min_df=1, sublinear_tf=True)
        matrix = vectorizer.fit_transform([clean_job, clean_resume])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(sim) * 100, 2)
    except Exception as e:
        print(f"TF-IDF error: {e}")
        return 0.0


# ============================================================
# ADVANCED: SENTENCE-BERT SEMANTIC SIMILARITY
# ============================================================
def compute_bert_similarity(job_desc, resume_text):
    if not job_desc or not resume_text:
        return 0.0
    model = get_bert_model()
    if model is None:
        return None
    try:
        embeddings = model.encode([job_desc, resume_text],
                                  convert_to_tensor=False,
                                  show_progress_bar=False)
        sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        rescaled = max(0.0, (float(sim) - 0.15) / 0.7)
        score = min(100.0, rescaled * 100)
        return round(score, 2)
    except Exception as e:
        print(f"BERT error: {e}")
        return None


# ============================================================
# SKILL MATCH
# ============================================================
def compute_skill_match(job_skills, resume_skills):
    if not job_skills:
        return 0.0, [], []
    job_set = set(job_skills)
    resume_set = set(resume_skills)
    if not job_set:
        return 0.0, [], []
    matched = sorted(job_set & resume_set)
    missing = sorted(job_set - resume_set)
    score = round((len(matched) / len(job_set)) * 100, 2)
    return score, matched, missing


# ============================================================
# GAP ANALYSIS
# ============================================================
def analyze_gaps(job_skills, resume_skills, job_years, resume_years,
                 job_edu, resume_edu):
    gap = {
        'matched_skills': [], 'missing_skills': [], 'extra_skills': [],
        'experience_required': job_years, 'experience_found': resume_years,
        'experience_gap': 0, 'education_required': job_edu,
        'education_found': resume_edu, 'education_match': True,
        'red_flags': [], 'strengths': [], 'reasoning': ''
    }

    if job_skills:
        js = set(job_skills)
        rs = set(resume_skills)
        gap['matched_skills'] = sorted(js & rs)
        gap['missing_skills'] = sorted(js - rs)
        gap['extra_skills'] = sorted(rs - js)

    if job_years and resume_years < job_years:
        gap['experience_gap'] = job_years - resume_years

    if job_edu and resume_edu:
        edu_rank = {'diploma': 1, 'bachelor': 2, 'master': 3, 'phd': 4}
        job_level = max([edu_rank.get(e, 0) for e in job_edu] or [0])
        resume_level = max([edu_rank.get(e, 0) for e in resume_edu] or [0])
        if resume_level < job_level:
            gap['education_match'] = False

    if len(gap['missing_skills']) >= 3:
        gap['red_flags'].append(
            f"Missing {len(gap['missing_skills'])} required skills: {', '.join(gap['missing_skills'][:5])}")
    if gap['experience_gap'] >= 2:
        gap['red_flags'].append(f"{gap['experience_gap']} year(s) short of experience requirement")
    if not gap['education_match']:
        gap['red_flags'].append("Education level below job requirement")

    if gap['matched_skills']:
        gap['strengths'].append(
            f"Matches {len(gap['matched_skills'])} required skill(s): {', '.join(gap['matched_skills'][:5])}")
    if resume_years >= job_years and job_years > 0:
        gap['strengths'].append(f"Meets experience requirement ({resume_years} yrs)")
    if resume_years > job_years and job_years > 0:
        gap['strengths'].append(f"Exceeds experience requirement by {resume_years - job_years} yr(s)")
    if gap['education_match'] and resume_edu:
        gap['strengths'].append(f"Education requirement met ({', '.join(resume_edu)})")

    total_skills = len(job_skills) if job_skills else 0
    matched_count = len(gap['matched_skills'])

    if total_skills == 0:
        verdict = "⚠️ JOB HAS NO SKILLS — ranking uses text similarity"
    else:
        coverage = (matched_count / total_skills) * 100
        if coverage >= 80 and gap['experience_gap'] == 0:
            verdict = "🟢 STRONG FIT"
        elif coverage >= 50:
            verdict = "🟡 MODERATE FIT"
        else:
            verdict = "🔴 WEAK FIT"

    parts = [verdict + '.']
    if gap['strengths']:
        parts.append("Strengths: " + " | ".join(gap['strengths']) + ".")
    if gap['red_flags']:
        parts.append("⚠️ Concerns: " + " | ".join(gap['red_flags']) + ".")
    if not gap['strengths'] and not gap['red_flags']:
        parts.append("No significant strengths or concerns identified.")

    gap['reasoning'] = ' '.join(parts)
    return gap


# ============================================================
# MASTER FUNCTION
# ============================================================
def compute_final_score(job_desc, resume_text, job_skills=None):
    tfidf_score = compute_tfidf_similarity(job_desc, resume_text)
    bert_score = compute_bert_similarity(job_desc, resume_text)

    resume_skills = extract_skills(resume_text)

    if job_skills:
        skill_score, matched, missing = compute_skill_match(job_skills, resume_skills)
    else:
        skill_score, matched, missing = 0.0, [], []

    if bert_score is not None:
        final = (0.5 * bert_score) + (0.2 * tfidf_score) + (0.3 * skill_score)
    else:
        bert_score = 0.0
        final = (0.6 * tfidf_score) + (0.4 * skill_score)

    return {
        'final_score': round(final, 2),
        'bert_score': round(bert_score, 2) if bert_score is not None else None,
        'tfidf_score': tfidf_score,
        'similarity_score': tfidf_score,
        'skill_score': skill_score,
        'skills_found': resume_skills,
        'matched_skills': matched,
        'missing_skills': missing,
        'education': extract_education(resume_text),
        'experience_years': extract_experience_years(resume_text)
    }


# ============================================================
# SELF-TEST
# ============================================================
if __name__ == '__main__':
    job = "We need a Machine Learning engineer with experience in Python, AWS, and SQL."
    cv_exact = "I am a Python developer with experience in SQL and AWS. I have built Machine Learning models."
    cv_synonym = "I've been working with ML models and cloud infrastructure. Skilled in py and databases."

    print("\n--- Test 1: Exact words ---")
    r1 = compute_final_score(job, cv_exact, extract_skills(job))
    print(f"  TF-IDF: {r1['tfidf_score']}%")
    print(f"  BERT:   {r1['bert_score']}%")
    print(f"  Final:  {r1['final_score']}%")

    print("\n--- Test 2: SYNONYMS (ML, py, cloud) ---")
    r2 = compute_final_score(job, cv_synonym, extract_skills(job))
    print(f"  TF-IDF: {r2['tfidf_score']}%  <- keyword matching fails")
    print(f"  BERT:   {r2['bert_score']}%  <- semantic matching succeeds")
    print(f"  Final:  {r2['final_score']}%")
    print(f"  Skills found: {r2['skills_found']}")