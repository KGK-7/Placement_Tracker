import sqlite3
import os
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import time
import pandas as pd
import io

def init_db():
    """Initialize the database and create necessary tables if they don't exist"""
    conn = None
    try:
        conn = sqlite3.connect('placement_tracker.db')
        cur = conn.cursor()
        
        # Create users table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            department TEXT,
            specialization TEXT
        )
        ''')
        
        # Create student_profiles table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            semester_cgpa REAL,
            domain_specialization TEXT,
            skills TEXT,
            projects TEXT,
            project_titles TEXT,
            project_domains TEXT,
            project_github_links TEXT,
            leetcode_problems INTEGER DEFAULT 0,
            leetcode_profile TEXT,
            github_profile TEXT,
            linkedin_profile TEXT,
            portfolio_link TEXT,
            weekly_assessment_score REAL,
            attendance_percentage REAL,
            is_eligible INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create eligibility_criteria table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS eligibility_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            min_attendance REAL DEFAULT 85.0,
            min_assessment_score REAL DEFAULT 80.0,
            min_cgpa REAL DEFAULT 8.5,
            min_leetcode_problems INTEGER DEFAULT 100,
            min_projects INTEGER DEFAULT 3,
            require_portfolio INTEGER DEFAULT 1,
            require_leetcode_profile INTEGER DEFAULT 0,
            require_github_profile INTEGER DEFAULT 0,
            require_linkedin_profile INTEGER DEFAULT 0
        )
        ''')
        
        # Create admin_settings table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY,
            admin_key TEXT NOT NULL DEFAULT 'admin123'
        )
        ''')
        
        # Insert default admin settings if not exists
        cur.execute("SELECT COUNT(*) FROM admin_settings")
        if cur.fetchone()[0] == 0:
            cur.execute('''
            INSERT INTO admin_settings (id, admin_key)
            VALUES (1, 'admin123')
            ''')
        
        # Insert default eligibility criteria if not exists
        cur.execute("SELECT COUNT(*) FROM eligibility_criteria")
        if cur.fetchone()[0] == 0:
            cur.execute('''
            INSERT INTO eligibility_criteria 
            (min_attendance, min_assessment_score, min_cgpa, min_leetcode_problems, min_projects, 
            require_portfolio, require_leetcode_profile, require_github_profile, require_linkedin_profile)
            VALUES (85.0, 80.0, 8.5, 100, 3, 1, 0, 0, 0)
            ''')
        
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get database connection"""
    for attempt in range(3):  # Try up to 3 times
        try:
            conn = sqlite3.connect('placement_tracker.db', timeout=20)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < 2:
                time.sleep(1)  # Wait a bit before retrying
            else:
                raise
    return None

def register_user(username, password, email, role, department=None, specialization=None, admin_key=None):
    """Register a new user"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        # Check admin key if registering as admin
        if role == 'admin':
            if not admin_key:
                return False
            
            # Verify admin key
            admin_settings = conn.execute('SELECT admin_key FROM admin_settings WHERE id = 1').fetchone()
            if not admin_settings or admin_settings['admin_key'] != admin_key:
                return False
            
        hashed_password = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, password, email, role, department, specialization) VALUES (?, ?, ?, ?, ?, ?)',
            (username, hashed_password, email, role, department, specialization)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        return False
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            return dict(user)
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return dict(user) if user else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_student_profile(user_id, data):
    """Update or create student profile"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        profile = conn.execute('SELECT * FROM student_profiles WHERE user_id = ?', (user_id,)).fetchone()
        
        if profile:
            conn.execute('''
                UPDATE student_profiles SET 
                semester_cgpa = ?, domain_specialization = ?, skills = ?,
                projects = ?, project_titles = ?, project_domains = ?, project_github_links = ?,
                leetcode_problems = ?, leetcode_profile = ?, github_profile = ?,
                linkedin_profile = ?, portfolio_link = ?, weekly_assessment_score = ?,
                attendance_percentage = ?
                WHERE user_id = ?
            ''', (
                data['semester_cgpa'], data['domain_specialization'], data['skills'],
                data['projects'], data['project_titles'], data['project_domains'], data['project_github_links'],
                data['leetcode_problems'], data['leetcode_profile'], data['github_profile'],
                data['linkedin_profile'], data['portfolio_link'], data['weekly_assessment_score'],
                data['attendance_percentage'], user_id
            ))
        else:
            conn.execute('''
                INSERT INTO student_profiles 
                (user_id, semester_cgpa, domain_specialization, skills, projects, project_titles, project_domains, project_github_links, 
                leetcode_problems, leetcode_profile, github_profile, linkedin_profile, portfolio_link, 
                weekly_assessment_score, attendance_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, data['semester_cgpa'], data['domain_specialization'], data['skills'],
                data['projects'], data['project_titles'], data['project_domains'], data['project_github_links'],
                data['leetcode_problems'], data['leetcode_profile'], data['github_profile'],
                data['linkedin_profile'], data['portfolio_link'], data['weekly_assessment_score'],
                data['attendance_percentage']
            ))
        
        conn.commit()
        
        # Check eligibility based on criteria
        check_eligibility(user_id)
        
        return True
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error during profile update: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_student_profile(user_id):
    """Get student profile by user ID"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        profile = conn.execute('SELECT * FROM student_profiles WHERE user_id = ?', (user_id,)).fetchone()
        return dict(profile) if profile else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_students_by_department(department):
    """Get all students by department with their profiles"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        students = conn.execute('''
            SELECT u.id, u.username, u.email, u.department, sp.*
            FROM users u
            LEFT JOIN student_profiles sp ON u.id = sp.user_id
            WHERE u.role = 'student' AND u.department = ?
        ''', (department,)).fetchall()
        return [dict(student) for student in students]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_students():
    """Get all students with their profiles"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        students = conn.execute('''
            SELECT u.id, u.username, u.email, u.department, sp.*
            FROM users u
            LEFT JOIN student_profiles sp ON u.id = sp.user_id
            WHERE u.role = 'student'
        ''').fetchall()
        return [dict(student) for student in students]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_eligible_students():
    """Get all eligible students"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        students = conn.execute('''
            SELECT u.id, u.username, u.email, u.department, sp.*
            FROM users u
            JOIN student_profiles sp ON u.id = sp.user_id
            WHERE u.role = 'student' AND sp.is_eligible = 1
        ''').fetchall()
        return [dict(student) for student in students]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_eligibility_criteria():
    """Get current eligibility criteria"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        criteria = conn.execute('SELECT * FROM eligibility_criteria LIMIT 1').fetchone()
        return dict(criteria) if criteria else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_eligibility_criteria(criteria):
    """Update eligibility criteria"""
    conn = None
    try:
        print("Starting criteria update with values:", criteria)
        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection")
            return False
        
        # Ensure all required fields are present
        required_fields = [
            'min_attendance', 'min_assessment_score', 'min_cgpa',
            'min_leetcode_problems', 'min_projects', 'require_portfolio',
            'require_leetcode_profile', 'require_github_profile', 'require_linkedin_profile'
        ]
        
        for field in required_fields:
            if field not in criteria:
                print(f"Missing required field: {field}")
                return False
        
        # Check if the table has all the necessary columns
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(eligibility_criteria)")
        columns = {col['name'] for col in cursor.fetchall()}
        
        # Check if we need to add any missing columns
        missing_columns = []
        if 'require_leetcode_profile' not in columns:
            missing_columns.append(("require_leetcode_profile", "INTEGER DEFAULT 0"))
        if 'require_github_profile' not in columns:
            missing_columns.append(("require_github_profile", "INTEGER DEFAULT 0"))
        if 'require_linkedin_profile' not in columns:
            missing_columns.append(("require_linkedin_profile", "INTEGER DEFAULT 0"))
        
        # Add any missing columns
        for col_name, col_type in missing_columns:
            try:
                print(f"Adding missing column: {col_name}")
                cursor.execute(f"ALTER TABLE eligibility_criteria ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except Exception as e:
                print(f"Error adding column {col_name}: {e}")
        
        # Now perform the update
        cursor.execute('''
            UPDATE eligibility_criteria SET
            min_attendance = ?,
            min_assessment_score = ?,
            min_cgpa = ?,
            min_leetcode_problems = ?,
            min_projects = ?,
            require_portfolio = ?,
            require_leetcode_profile = ?,
            require_github_profile = ?,
            require_linkedin_profile = ?
            WHERE id = 1
        ''', (
            criteria['min_attendance'],
            criteria['min_assessment_score'],
            criteria['min_cgpa'],
            criteria['min_leetcode_problems'],
            criteria['min_projects'],
            criteria['require_portfolio'],
            criteria['require_leetcode_profile'],
            criteria['require_github_profile'],
            criteria['require_linkedin_profile']
        ))
        
        # If no rows were affected, insert a new record
        if cursor.rowcount == 0:
            print("No rows updated, inserting new criteria")
            cursor.execute('''
                INSERT OR IGNORE INTO eligibility_criteria 
                (id, min_attendance, min_assessment_score, min_cgpa, min_leetcode_problems, min_projects, 
                require_portfolio, require_leetcode_profile, require_github_profile, require_linkedin_profile)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                criteria['min_attendance'],
                criteria['min_assessment_score'],
                criteria['min_cgpa'],
                criteria['min_leetcode_problems'],
                criteria['min_projects'],
                criteria['require_portfolio'],
                criteria['require_leetcode_profile'],
                criteria['require_github_profile'],
                criteria['require_linkedin_profile']
            ))
        
        conn.commit()
        print("Criteria updated successfully")
        
        # Recalculate eligibility for all students
        update_all_eligibility()
        
        return True
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error during criteria update: {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Unexpected error during criteria update: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_all_eligibility():
    """Update eligibility for all students based on current criteria"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return
            
        students = conn.execute('SELECT user_id FROM student_profiles').fetchall()
        
        for student in students:
            check_eligibility(student['user_id'])
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def check_eligibility(user_id):
    """Check if a student meets eligibility criteria"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        criteria = conn.execute('SELECT * FROM eligibility_criteria LIMIT 1').fetchone()
        profile = conn.execute('SELECT * FROM student_profiles WHERE user_id = ?', (user_id,)).fetchone()
        
        if not profile or not criteria:
            return False
        
        # Count projects
        project_count = len(profile['projects'].split(',')) if profile['projects'] else 0
        
        # Check all criteria
        is_eligible = (
            profile['attendance_percentage'] >= criteria['min_attendance'] and
            profile['weekly_assessment_score'] >= criteria['min_assessment_score'] and
            profile['semester_cgpa'] >= criteria['min_cgpa'] and
            profile['leetcode_problems'] >= criteria['min_leetcode_problems'] and
            project_count >= criteria['min_projects'] and
            (not criteria['require_portfolio'] or profile['portfolio_link']) and
            (not criteria['require_leetcode_profile'] or profile['leetcode_profile']) and
            (not criteria['require_github_profile'] or profile['github_profile']) and
            (not criteria['require_linkedin_profile'] or profile['linkedin_profile'])
        )
        
        # Update eligibility status
        conn.execute('UPDATE student_profiles SET is_eligible = ? WHERE user_id = ?', 
                     (1 if is_eligible else 0, user_id))
        conn.commit()
        return is_eligible
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def approve_student(user_id, approved):
    """Approve or disapprove a student for placement"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        conn.execute('UPDATE student_profiles SET is_approved = ? WHERE user_id = ?', 
                     (1 if approved else 0, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_admin_key():
    """Get the admin key for registration"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
            
        admin_key = conn.execute('SELECT admin_key FROM admin_settings WHERE id = 1').fetchone()
        return admin_key['admin_key'] if admin_key else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_admin_key(new_key):
    """Update the admin key"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        conn.execute('UPDATE admin_settings SET admin_key = ? WHERE id = 1', (new_key,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def export_eligible_students_to_excel():
    """Export eligible students' data to Excel file"""
    conn = None
    try:
        print("Starting export to Excel process")
        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection")
            return None
        
        # Get eligible students with all required fields - using a safer query
        query = """
            SELECT 
                u.id, 
                u.username, 
                u.email, 
                u.department, 
                u.specialization, 
                sp.semester_cgpa, 
                sp.domain_specialization, 
                sp.skills, 
                sp.leetcode_problems, 
                sp.leetcode_profile, 
                sp.github_profile, 
                sp.linkedin_profile, 
                sp.portfolio_link, 
                sp.is_approved
            FROM users u
            JOIN student_profiles sp ON u.id = sp.user_id
            WHERE sp.is_eligible = 1 AND u.role = 'student'
        """
        
        students = conn.execute(query).fetchall()
        print(f"Retrieved {len(students)} eligible students from the database")
        
        if not students or len(students) == 0:
            print("No eligible students data retrieved")
            return None
        
        # Create Excel file
        students_list = []
        for student in students:
            student_dict = dict(student)
            students_list.append({
                'ID': student_dict.get('id'),
                'Username': student_dict.get('username'),
                'Email': student_dict.get('email'),
                'Department': student_dict.get('department', ''),
                'Specialization': student_dict.get('specialization', ''),
                'CGPA': student_dict.get('semester_cgpa', 0),
                'Domain Specialization': student_dict.get('domain_specialization', ''),
                'Skills': student_dict.get('skills', ''),
                'LeetCode Problems': student_dict.get('leetcode_problems', 0),
                'LeetCode Profile': student_dict.get('leetcode_profile', ''),
                'GitHub Profile': student_dict.get('github_profile', ''),
                'LinkedIn Profile': student_dict.get('linkedin_profile', ''),
                'Portfolio Link': student_dict.get('portfolio_link', ''),
                'Approved': 'Yes' if student_dict.get('is_approved') else 'No'
            })
        
        # Import pandas inside the function to avoid loading it unnecessarily
        import pandas as pd
        import io
        
        df = pd.DataFrame(students_list)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Eligible Students', index=False)
            
            # Auto-adjust columns' width
            worksheet = writer.sheets['Eligible Students']
            for i, col in enumerate(df.columns):
                # Get the maximum length in the column
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)
        
        output.seek(0)
        print("Excel file generated successfully")
        return output
    
    except sqlite3.Error as e:
        print(f"Database error during Excel export: {e}")
        return None
    except Exception as e:
        print(f"Error in Excel export: {e}")
        print(f"Error details: {str(e)}")
        return None
    finally:
        if conn:
            conn.close() 