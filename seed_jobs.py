"""
Bulk-post the 5 test jobs.
Run once: python seed_jobs.py
"""
import database as db

JOBS = [
    {
        "title": "Senior Python Developer",
        "department": "Engineering",
        "location": "Remote",
        "type": "Full-time",
        "description": "We are seeking an experienced Senior Python Developer to join our growing engineering team. The successful candidate will design, build, and maintain scalable backend services and REST APIs. You will work closely with data scientists to integrate machine learning models into production systems. Applicants should have strong experience with Flask or Django, database design, and modern software engineering practices. Minimum 5 years of professional Python development experience is required.",
        "skills": "Python, Flask, Django, REST API, SQL, PostgreSQL, Docker, AWS, Git, Machine Learning"
    },
    {
        "title": "Data Scientist (Machine Learning)",
        "department": "Data & Analytics",
        "location": "Johannesburg, South Africa",
        "type": "Full-time",
        "description": "We are looking for a Data Scientist with a strong foundation in machine learning and natural language processing. You will be responsible for building predictive models, analysing large datasets, and delivering actionable insights to business stakeholders. The ideal candidate has hands-on experience with scikit-learn, TensorFlow or PyTorch, and is comfortable working with both structured and unstructured data. A minimum of 3 years of experience in a data science role and a degree in Computer Science, Statistics or a related field is required.",
        "skills": "Python, Machine Learning, Deep Learning, NLP, scikit-learn, TensorFlow, Pandas, NumPy, SQL, Data Analysis"
    },
    {
        "title": "Frontend React Developer",
        "department": "Engineering",
        "location": "Cape Town, South Africa",
        "type": "Full-time",
        "description": "We are hiring a Frontend React Developer to build beautiful, responsive, and performant user interfaces for our web applications. You will collaborate closely with designers and backend engineers to deliver seamless user experiences. Strong knowledge of JavaScript, React, HTML, CSS, and modern build tools is essential. Experience with TypeScript and REST APIs is a strong advantage. Minimum 3 years of frontend development experience required.",
        "skills": "JavaScript, TypeScript, React, HTML, CSS, REST API, Git, Figma, UI, UX"
    },
    {
        "title": "DevOps Engineer",
        "department": "Infrastructure",
        "location": "Remote",
        "type": "Full-time",
        "description": "We are seeking a skilled DevOps Engineer to manage and improve our cloud infrastructure and deployment pipelines. The successful candidate will be responsible for setting up CI/CD pipelines, automating deployments, monitoring system health, and ensuring high availability. Hands-on experience with AWS or Azure, Docker, Kubernetes, and Infrastructure-as-Code tools such as Terraform is required. Minimum 4 years of experience in a DevOps or SRE role is essential.",
        "skills": "AWS, Azure, Docker, Kubernetes, Terraform, Jenkins, CI/CD, Linux, Bash, Python, Ansible, Git"
    },
    {
        "title": "HR Recruitment Officer",
        "department": "Human Resources",
        "location": "Pretoria, South Africa",
        "type": "Full-time",
        "description": "We are looking for a motivated HR Recruitment Officer to manage end-to-end recruitment processes, from sourcing and screening to interviewing and onboarding. The ideal candidate will have strong communication and organisational skills, experience with applicant tracking systems, and a good understanding of labour legislation. A diploma or degree in Human Resources Management or a related field is required, along with at least 2 years of recruitment experience.",
        "skills": "Recruitment, HR, Communication, Interviewing, Project Management, Excel, Leadership"
    }
]


def seed():
    existing = db.get_all_jobs()
    if existing:
        print(f"[!] You already have {len(existing)} job(s). Skipping to avoid duplicates.")
        print("    To re-seed, delete database.db first.")
        return

    for j in JOBS:
        job_id = db.add_job(j["title"], j["department"], j["location"],
                            j["type"], j["description"], j["skills"])
        print(f"[+] Posted job #{job_id}: {j['title']}")

    print(f"\n[OK] Posted {len(JOBS)} jobs successfully!")
    print("-> Open http://localhost:5000 to see them")


if __name__ == '__main__':
    seed()
