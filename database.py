
"""
SQLite Database Handler - Intelligent Resume Screening and Ranking System
Author: Forget Hangwani Ramukumba (202353346)
"""

import sqlite3
import hashlib

DB_PATH = 'database.db'


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    """SHA-256 hash for password storage."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Jobs
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        department TEXT,
        location TEXT,
        type TEXT,
        description TEXT,
        skills TEXT,
        posted TEXT,
        applications_count INTEGER DEFAULT 0
    )''')

    # Applications
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        job_title TEXT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        filename TEXT,
        filepath TEXT,
        cover_letter TEXT,
        resume_text TEXT,
        status TEXT DEFAULT 'pending',
        applied TEXT,
        score REAL,
        similarity_score REAL,
        skill_score REAL,
        skills_found TEXT,
        education TEXT,
        experience_years INTEGER,
        matched_skills TEXT,
        missing_skills TEXT,
        gap_analysis TEXT,
        cv_valid INTEGER DEFAULT 1,
        cv_warning TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
    )''')

    # Employees
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        position TEXT,
        score REAL,
        hired TEXT
    )''')

    # HR Members (login)
    c.execute('''CREATE TABLE IF NOT EXISTS hr_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_number TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        created TEXT DEFAULT (datetime('now'))
    )''')

    # Default HR member
    c.execute("SELECT COUNT(*) FROM hr_members")
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO hr_members (employee_number, password_hash, full_name)
                     VALUES (?, ?, ?)''',
                  ('202353346', hash_password('RAM1701@200'),
                   'Forget Hangwani Ramukumba'))
        print("[OK] HR Member created")
        print("     Employee Number: 202353346")
        print("     Password:        RAM1701@200")

    conn.commit()
    conn.close()
    print("[OK] Database initialized")


# ============================================================
# HR MEMBER AUTH
# ============================================================
def verify_hr_member(employee_number, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM hr_members WHERE employee_number = ?", (employee_number,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    if row['password_hash'] == hash_password(password):
        return dict(row)
    return None


def get_hr_member_by_id(member_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM hr_members WHERE id = ?", (member_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def add_hr_member(employee_number, password, full_name=''):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO hr_members (employee_number, password_hash, full_name)
                     VALUES (?, ?, ?)''',
                  (employee_number, hash_password(password), full_name))
        member_id = c.lastrowid
        conn.commit()
        conn.close()
        return member_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


# ============================================================
# JOBS
# ============================================================
def add_job(title, department, location, type_, description, skills):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO jobs (title, department, location, type, description, skills, posted)
                 VALUES (?, ?, ?, ?, ?, ?, datetime('now'))''',
              (title, department, location, type_, description, skills))
    job_id = c.lastrowid
    conn.commit()
    conn.close()
    return job_id


def get_all_jobs():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs ORDER BY id DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_job(job_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_job(job_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM applications WHERE job_id = ?', (job_id,))
    c.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()


def delete_all_jobs():
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM applications')
    c.execute('DELETE FROM jobs')
    conn.commit()
    conn.close()


# ============================================================
# APPLICATIONS
# ============================================================
def add_application(job_id, job_title, name, email, phone, filename, filepath,
                    cover_letter, resume_text, cv_valid=1, cv_warning=''):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO applications
        (job_id, job_title, name, email, phone, filename, filepath, cover_letter,
         resume_text, applied, cv_valid, cv_warning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?)''',
        (job_id, job_title, name, email, phone, filename, filepath, cover_letter,
         resume_text, cv_valid, cv_warning))
    app_id = c.lastrowid
    c.execute('UPDATE jobs SET applications_count = applications_count + 1 WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
    return app_id


def get_all_applications():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM applications ORDER BY id DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_application(app_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM applications WHERE id = ?', (app_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_applications_for_job(job_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM applications WHERE job_id = ? ORDER BY id DESC', (job_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def update_application_score(app_id, final_score, similarity_score, skill_score,
                             skills_found, education, experience_years,
                             matched_skills, missing_skills, gap_analysis):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''UPDATE applications
                 SET score = ?, similarity_score = ?, skill_score = ?,
                     skills_found = ?, education = ?, experience_years = ?,
                     matched_skills = ?, missing_skills = ?, gap_analysis = ?
                 WHERE id = ?''',
              (final_score, similarity_score, skill_score,
               ','.join(skills_found), ','.join(education),
               experience_years, ','.join(matched_skills),
               ','.join(missing_skills), gap_analysis, app_id))
    conn.commit()
    conn.close()


def update_application_status(app_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE applications SET status = ? WHERE id = ?', (status, app_id))
    conn.commit()
    conn.close()


def delete_application(app_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM applications WHERE id = ?', (app_id,))
    conn.commit()
    conn.close()


# ============================================================
# EMPLOYEES
# ============================================================
def add_employee(name, email, position, score):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO employees (name, email, position, score, hired)
                 VALUES (?, ?, ?, ?, datetime('now'))''',
              (name, email, position, score))
    conn.commit()
    conn.close()


def get_all_employees():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM employees ORDER BY id DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows