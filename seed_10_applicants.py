"""
Bulk-seed 10 test applications for the 'Senior Python Developer' job.
Run once: python seed_10_applicants.py
"""
import database as db
import nlp_engine as nlp

APPLICANTS = [
    {
        "name": "Forget Ramukumba",
        "email": "hangwanirforgie@gmail.com",
        "phone": "084 270 6260",
        "filename": "Forget_Ramukumba_Python_Developer.pdf",
        "resume_text": """
        FORGET HANGWANI RAMUKUMBA - Senior Python Developer
        Email: hangwanirforgie@gmail.com | Phone: 084 270 6260
        Limpopo, South Africa (willing to relocate)

        PROFESSIONAL SUMMARY
        Experienced Python developer with 5 years building scalable backend systems,
        REST APIs with Flask and Django, and deploying machine learning models to AWS.
        Strong knowledge of SQL, PostgreSQL, Docker, and Git.

        TECHNICAL SKILLS
        Python, Flask, Django, REST API, SQL, PostgreSQL, Docker, AWS, Git, Machine Learning

        WORK EXPERIENCE
        Freelance Python Developer (2023 - Present)
        - Built 5+ Flask web apps
        - Deployed ML models to AWS EC2 and S3
        - Worked with Docker containers and PostgreSQL databases

        EDUCATION
        BSc in Computer Science, Sol Plaatje University, 2021-2024
        """
    },
    {
        "name": "Tricia Naidoo",
        "email": "tricia.naidoo@email.com",
        "phone": "083 555 4422",
        "filename": "Tricia_Naidoo_Senior_Dev.pdf",
        "resume_text": """
        TRICIA NAIDOO - Senior Full-Stack Developer
        Email: tricia.naidoo@email.com | Phone: 083 555 4422
        Cape Town, South Africa

        PROFESSIONAL SUMMARY
        Senior full-stack developer with 6+ years of experience in Python, Flask,
        Django, React, AWS, Docker, Kubernetes, PostgreSQL. Delivered 5M+ API requests/day.
        Led a team of 4 developers. Mentored junior engineers.

        TECHNICAL SKILLS
        Python, Flask, Django, REST API, SQL, PostgreSQL, Docker, AWS, Git, Machine Learning,
        TensorFlow, Kubernetes, React

        WORK EXPERIENCE
        Senior Full-Stack Developer | FinanceHub (2022 - Present)
        - Built REST APIs in Flask serving 5M+ requests/day
        - Deployed ML models for fraud detection
        - Migrated monolith to Docker + Kubernetes
        - Reduced AWS costs by 35%

        EDUCATION
        BSc Honours in Computer Science, University of Cape Town, 2015-2018
        """
    },
    {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "082 123 4567",
        "filename": "John_Doe_Python.pdf",
        "resume_text": """
        JOHN DOE - Python Developer
        Email: john.doe@email.com | Phone: 082 123 4567
        Remote

        PROFESSIONAL SUMMARY
        Python developer with 3 years of experience. Strong in Flask, SQL, Git.
        Some exposure to AWS and Docker. Eager to grow into ML.

        TECHNICAL SKILLS
        Python, Flask, SQL, Git, basic AWS, basic Docker

        WORK EXPERIENCE
        Junior Python Developer | TechCorp (2021 - Present)
        - Built small Flask apps
        - Wrote SQL queries
        - Used Git for version control

        EDUCATION
        Diploma in IT, Tshwane University of Technology, 2018-2021
        """
    },
    {
        "name": "Sarah Chen",
        "email": "sarah.chen@email.com",
        "phone": "083 987 6543",
        "filename": "Sarah_Chen_Synonyms.pdf",
        "resume_text": """
        SARAH CHEN - Full-Stack Engineer
        Email: sarah.chen@email.com | Phone: 083 987 6543

        PROFILE
        Full-stack engineer with strong foundation in py and JS. Extensive experience
        in ML pipelines and cloud infrastructure. Comfortable with both backend services
        and data engineering.

        EXPERTISE
        Languages: py, js, SQL, bash
        Frameworks: flask, django, node.js
        Cloud: amazon web services, k8s, docker
        ML/AI: sklearn, tensorflow, pandas
        Databases: postgres, mongo

        EXPERIENCE
        Software Engineer | DataFlow Inc (2020 - Present)
        - Built microservices with flask and deployed on k8s clusters
        - Developed ML models using sklearn
        - Worked with postgres handling TB-scale data
        - Set up CI CD pipelines on amazon web services

        EDUCATION
        BSc Computer Science, University of Cape Town, 2014-2018
        """
    },
    {
        "name": "Michael Ndlovu",
        "email": "michael.ndlovu@email.com",
        "phone": "082 555 7788",
        "filename": "Michael_Ndlovu_Junior.pdf",
        "resume_text": """
        MICHAEL NDLOVU - Backend Developer
        Email: michael.ndlovu@email.com | Phone: 082 555 7788

        SUMMARY
        Backend developer with 2 years Python experience. Currently learning ML and cloud.

        SKILLS
        Python (intermediate), SQL, Flask (basic), Git, Linux
        Currently learning: AWS, Machine Learning, Docker

        EXPERIENCE
        Backend Developer | SmallTech (2022 - Present)
        - Developed REST APIs using Python and Flask
        - Wrote SQL queries
        - Used Git for version control

        EDUCATION
        Diploma in Information Technology, TUT, 2019-2021
        """
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@email.com",
        "phone": "071 234 5678",
        "filename": "Priya_Patel_DataSci.pdf",
        "resume_text": """
        PRIYA PATEL - Data Scientist
        Email: priya.patel@email.com | Phone: 071 234 5678

        SUMMARY
        Data Scientist with 4 years experience in Python, Machine Learning, NLP,
        Deep Learning. Deployed models to production using Flask and AWS.

        SKILLS
        Python, Machine Learning, Deep Learning, NLP, scikit-learn, TensorFlow,
        Pandas, NumPy, SQL, Flask, AWS, Docker, Git

        EXPERIENCE
        Data Scientist | AI Labs (2020 - Present)
        - Built NLP pipelines for text classification
        - Deployed ML models via Flask REST APIs on AWS
        - Worked with SQL databases and Docker containers

        EDUCATION
        MSc in Data Science, University of Pretoria, 2018-2020
        """
    },
    {
        "name": "David Mokoena",
        "email": "david.mokoena@email.com",
        "phone": "082 999 1122",
        "filename": "David_Mokoena_Fullstack.pdf",
        "resume_text": """
        DAVID MOKOENA - Full-Stack Developer
        Email: david.mokoena@email.com | Phone: 082 999 1122

        SUMMARY
        Full-stack developer with 4 years experience. Strong in Python, Flask,
        REST API, SQL, PostgreSQL, Docker, AWS.

        SKILLS
        Python, Flask, REST API, SQL, PostgreSQL, Docker, AWS, Git, JavaScript, React

        EXPERIENCE
        Full-Stack Developer | MediTech (2021 - Present)
        - Built Flask REST APIs for healthcare platform
        - Deployed to AWS using Docker
        - Worked with PostgreSQL databases

        EDUCATION
        BSc in Computer Science, Wits University, 2017-2020
        """
    },
    {
        "name": "Lerato Khumalo",
        "email": "lerato.khumalo@email.com",
        "phone": "073 555 9988",
        "filename": "Lerato_Khumalo_Python.pdf",
        "resume_text": """
        LERATO KHUMALO - Python Developer
        Email: lerato.khumalo@email.com | Phone: 073 555 9988

        SUMMARY
        Python developer with 3 years of experience in Flask and SQL. Basic ML.

        SKILLS
        Python, Flask, SQL, Git, basic Machine Learning, basic AWS

        EXPERIENCE
        Python Developer | FinStart (2021 - Present)
        - Developed Flask REST APIs
        - Worked with MySQL databases
        - Used AWS S3 for file storage

        EDUCATION
        BSc in Information Technology, UJ, 2018-2021
        """
    },
    {
        "name": "Thabo Mthembu",
        "email": "thabo.mthembu@email.com",
        "phone": "084 777 6655",
        "filename": "Thabo_Mthembu_Senior.pdf",
        "resume_text": """
        THABO MTHEMBU - Senior Backend Engineer
        Email: thabo.mthembu@email.com | Phone: 084 777 6655

        SUMMARY
        Senior backend engineer with 7 years experience in Python, Django, Flask,
        AWS, Docker, PostgreSQL. Expert in designing scalable REST APIs.

        SKILLS
        Python, Django, Flask, REST API, SQL, PostgreSQL, Docker, AWS, Git,
        Machine Learning, Kubernetes, Redis, Celery

        EXPERIENCE
        Senior Backend Engineer | CloudScale (2018 - Present)
        - Designed microservices using Flask and Django
        - Deployed to AWS with Docker and Kubernetes
        - Mentored 5 junior developers
        - Built ML-based recommendation engine

        EDUCATION
        BSc Honours in Computer Science, UCT, 2013-2016
        """
    },
    {
        "name": "Jane Smith",
        "email": "jane.smith@email.com",
        "phone": "084 555 1234",
        "filename": "Jane_Smith_Marketing.pdf",
        "resume_text": """
        JANE SMITH - Marketing Professional
        Email: jane.smith@email.com | Phone: 084 555 1234

        SUMMARY
        Marketing professional with 4 years experience in digital marketing,
        social media, SEO, copywriting. No programming experience.

        SKILLS
        Social Media Marketing, Content Writing, SEO, Copywriting, Google Analytics,
        Canva, Adobe Photoshop, Email Marketing

        EXPERIENCE
        Marketing Specialist | BrightAds (2021 - Present)
        - Managed social media accounts for 12 clients
        - Wrote blog posts
        - Ran Google Ads campaigns

        EDUCATION
        BA in Communications, UCT, 2016-2020
        """
    }
]


def seed():
    # Get first job (Python Developer)
    jobs = db.get_all_jobs()
    if not jobs:
        print("[!] No jobs found. Run seed_jobs.py first.")
        return

    # Find Python Developer job
    target = None
    for j in jobs:
        if 'python' in j['title'].lower() and 'developer' in j['title'].lower():
            target = j
            break
    if not target:
        target = jobs[-1]  # oldest job (created first)

    print(f"[*] Posting applications for: {target['title']} (job_id={target['id']})")

    for i, a in enumerate(APPLICANTS, 1):
        # Validate CV
        validation = nlp.validate_cv(a['resume_text'])
        app_id = db.add_application(
            target['id'], target['title'],
            a['name'], a['email'], a['phone'],
            a['filename'], f"uploads/{a['filename']}", '',
            a['resume_text'],
            cv_valid=1 if validation['is_valid'] else 0,
            cv_warning=validation['reason']
        )
        print(f"  [{i:02d}] {a['name']:<25} -> app_id={app_id}")

    print(f"\n[OK] Posted {len(APPLICANTS)} applications for '{target['title']}'")
    print("-> Open http://localhost:5000/admin -> Ranking -> Generate Rankings")


if __name__ == '__main__':
    seed()