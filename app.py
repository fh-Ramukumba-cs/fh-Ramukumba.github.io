
"""
Flask Backend - Intelligent Resume Screening and Ranking System
Author: Forget Hangwani Ramukumba (202353346)
"""

import os
import json
from functools import wraps
from flask import (Flask, request, jsonify, send_from_directory,
                   session, redirect)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

import database as db
import nlp_engine as nlp

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__,
            template_folder='Frontend',
            static_folder='Frontend',
            static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['SECRET_KEY'] = 'intelligent-resume-screening-secret-2026'

CORS(app, supports_credentials=True)
db.init_db()


def login_required(f):
    """Protect HR-only routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('hr_id'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized. Please log in.'}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF error: {e}")
        return ""


def extract_text_from_image(filepath):
    return f"Image CV: {os.path.basename(filepath)}"


def safe_filename(filename):
    filename = secure_filename(filename)
    base, ext = os.path.splitext(filename)
    counter = 1
    final = filename
    while os.path.exists(os.path.join(UPLOAD_FOLDER, final)):
        final = f"{base}_{counter}{ext}"
        counter += 1
    return final


# ==================== AUTH ROUTES ====================
@app.route('/login')
def login_page():
    if session.get('hr_id'):
        return redirect('/admin')
    return send_from_directory('Frontend', 'login.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    emp_num = data.get('employee_number', '').strip()
    password = data.get('password', '').strip()

    if not emp_num or not password:
        return jsonify({'error': 'Employee number and password required'}), 400

    member = db.verify_hr_member(emp_num, password)
    if not member:
        return jsonify({'error': 'Invalid employee number or password'}), 401

    session['hr_id'] = member['id']
    session['hr_number'] = member['employee_number']
    session['hr_name'] = member.get('full_name') or member['employee_number']
    return jsonify({
        'status': 'success',
        'message': f"Welcome, {session['hr_name']}",
        'member': {
            'id': member['id'],
            'employee_number': member['employee_number'],
            'name': session['hr_name']
        }
    })


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success'})


@app.route('/api/me', methods=['GET'])
def api_me():
    if not session.get('hr_id'):
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({
        'id': session['hr_id'],
        'employee_number': session.get('hr_number'),
        'name': session.get('hr_name')
    })


# ==================== PAGES ====================
@app.route('/')
def public_board():
    return send_from_directory('Frontend', 'index.html')


@app.route('/apply')
def apply_page():
    return send_from_directory('Frontend', 'apply.html')


@app.route('/admin')
@login_required
def hr_page():
    return send_from_directory('Frontend', 'admin.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('Frontend', filename)


# ==================== JOBS API ====================
@app.route('/api/jobs', methods=['GET'])
def api_get_jobs():
    return jsonify(db.get_all_jobs())


@app.route('/api/jobs', methods=['POST'])
@login_required
def api_add_job():
    data = request.json or {}
    for f in ['title', 'department', 'location', 'type', 'description']:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    job_id = db.add_job(
        data['title'].strip(),
        data['department'].strip(),
        data['location'].strip(),
        data['type'].strip(),
        data['description'].strip(),
        data.get('skills', '').strip()
    )
    return jsonify({'status': 'success', 'job_id': job_id}), 201


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def api_get_job(job_id):
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def api_delete_job(job_id):
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    db.delete_job(job_id)
    return jsonify({'status': 'success', 'message': f"Job '{job['title']}' deleted"})


@app.route('/api/jobs/all', methods=['DELETE'])
@login_required
def api_delete_all_jobs():
    db.delete_all_jobs()
    return jsonify({'status': 'success'})


# ==================== APPLICATIONS API ====================
@app.route('/api/applications', methods=['GET'])
@login_required
def api_get_applications():
    return jsonify(db.get_all_applications())


@app.route('/api/applications/<int:app_id>', methods=['GET'])
@login_required
def api_get_application(app_id):
    app_ = db.get_application(app_id)
    if not app_:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(app_)


@app.route('/api/apply', methods=['POST'])
def api_apply():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    cover = request.form.get('cover_letter', '').strip()
    job_id = request.form.get('job_id', '').strip()

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400
    if not job_id:
        return jsonify({'error': 'Job ID is required'}), 400

    job = db.get_job(int(job_id))
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if 'cv' not in request.files:
        return jsonify({'error': 'CV required'}), 400

    file = request.files['cv']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF, PNG, JPG, JPEG allowed'}), 400

    filename = safe_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        resume_text = extract_text_from_pdf(filepath)
    else:
        resume_text = extract_text_from_image(filepath)

    validation = nlp.validate_cv(resume_text)

    app_id = db.add_application(
        int(job_id), job['title'], name, email, phone,
        filename, filepath, cover, resume_text,
        cv_valid=1 if validation['is_valid'] else 0,
        cv_warning=validation['reason']
    )

    return jsonify({
        'status': 'success',
        'message': f'Application submitted for {job["title"]}',
        'application_id': app_id,
        'cv_valid': validation['is_valid'],
        'cv_message': validation['reason']
    }), 201


@app.route('/api/applications/<int:app_id>', methods=['DELETE'])
@login_required
def api_delete_application(app_id):
    db.delete_application(app_id)
    return jsonify({'status': 'success'})


@app.route('/api/applications/bulk-delete', methods=['POST'])
@login_required
def api_bulk_delete():
    data = request.json or {}
    for i in data.get('ids', []):
        db.delete_application(i)
    return jsonify({'status': 'success'})


# ==================== NLP RANKING ====================
@app.route('/api/rank/<int:job_id>', methods=['POST'])
@login_required
def api_rank(job_id):
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    data = request.json or {}
    selected = data.get('application_ids')

    apps = db.get_applications_for_job(job_id)
    if not apps:
        return jsonify({'error': 'No applications'}), 404

    if selected:
        apps = [a for a in apps if a['id'] in selected]

    job_text = job['description'] + " " + (job['skills'] or '')
    job_skills = nlp.extract_skills(job_text)
    job_years = nlp.extract_experience_years(job_text)
    job_edu = nlp.extract_education(job_text)

    results = []
    for a in apps:
        analysis = nlp.compute_final_score(job_text, a.get('resume_text') or '', job_skills)

        gap = nlp.analyze_gaps(
            job_skills,
            analysis['skills_found'],
            job_years,
            analysis['experience_years'],
            job_edu,
            analysis['education']
        )

        db.update_application_score(
            a['id'],
            analysis['final_score'],
            analysis['similarity_score'],
            analysis['skill_score'],
            analysis['skills_found'],
            analysis['education'],
            analysis['experience_years'],
            analysis['matched_skills'],
            analysis['missing_skills'],
            json.dumps(gap)
        )

        results.append({
            'id': a['id'],
            'name': a['name'],
            'email': a['email'],
            'filename': a['filename'],
            'status': a['status'],
            'score': analysis['final_score'],
            'bert_score': analysis.get('bert_score'),
            'similarity_score': analysis['similarity_score'],
            'skill_score': analysis['skill_score'],
            'skills_found': analysis['skills_found'],
            'matched_skills': analysis['matched_skills'],
            'missing_skills': analysis['missing_skills'],
            'education': analysis['education'],
            'experience_years': analysis['experience_years'],
            'gap_analysis': gap,
            'cv_valid': a.get('cv_valid', 1),
            'cv_warning': a.get('cv_warning', '')
        })

    results.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({
        'job_title': job['title'],
        'job_skills': job_skills,
        'job_years': job_years,
        'job_education': job_edu,
        'total_candidates': len(results),
        'rankings': results
    })


# ==================== HIRE / RESPOND ====================
@app.route('/api/hire/<int:app_id>', methods=['POST'])
@login_required
def api_hire(app_id):
    a = db.get_application(app_id)
    if not a:
        return jsonify({'error': 'Not found'}), 404
    db.update_application_status(app_id, 'hired')
    db.add_employee(a['name'], a['email'], a['job_title'], a['score'] or 0)
    return jsonify({'status': 'success', 'message': f"{a['name']} hired!"})


@app.route('/api/respond/<int:app_id>', methods=['POST'])
@login_required
def api_respond(app_id):
    data = request.json or {}
    status = data.get('status', 'reviewed')
    db.update_application_status(app_id, status)
    if status == 'hired':
        a = db.get_application(app_id)
        db.add_employee(a['name'], a['email'], a['job_title'], a['score'] or 0)
    return jsonify({'status': 'success'})


@app.route('/api/employees', methods=['GET'])
@login_required
def api_employees():
    return jsonify(db.get_all_employees())


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  INTELLIGENT RESUME SCREENING AND RANKING SYSTEM")
    print("  NLP + ML Candidate Ranking + BERT Semantic Matching")
    print("=" * 60)
    print("  Public board:  http://localhost:5000")
    print("  HR login page: http://localhost:5000/login")
    print("  HR dashboard:  http://localhost:5000/admin")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)