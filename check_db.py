import sqlite3
import os

def check_db():
    try:
        # Check if database file exists
        if not os.path.exists('placement_tracker.db'):
            print("Database file does not exist!")
            return
            
        # Connect to the database
        conn = sqlite3.connect('placement_tracker.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        print("Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table['name']}")
        
        # Check eligibility_criteria table
        print("\nEligibility Criteria Table:")
        try:
            cursor.execute("SELECT * FROM eligibility_criteria")
            criteria = cursor.fetchall()
            if criteria:
                for row in criteria:
                    print(dict(row))
            else:
                print("No eligibility criteria found!")
                
                # Insert default criteria
                print("Inserting default criteria...")
                cursor.execute('''
                INSERT INTO eligibility_criteria 
                (id, min_attendance, min_assessment_score, min_cgpa, min_leetcode_problems, min_projects, 
                require_portfolio, require_leetcode_profile, require_github_profile, require_linkedin_profile)
                VALUES (1, 85.0, 80.0, 8.5, 100, 3, 1, 0, 0, 0)
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error checking eligibility criteria: {e}")
        
        # Check student_profiles table
        print("\nStudent Profiles:")
        try:
            cursor.execute("SELECT COUNT(*) as count FROM student_profiles")
            count = cursor.fetchone()['count']
            print(f"Total student profiles: {count}")
            
            cursor.execute("SELECT COUNT(*) as count FROM student_profiles WHERE is_eligible = 1")
            eligible_count = cursor.fetchone()['count']
            print(f"Eligible students: {eligible_count}")
            
            if eligible_count > 0:
                print("\nEligible Students Details:")
                cursor.execute('''
                SELECT u.id, u.username, u.email, sp.is_eligible 
                FROM users u
                JOIN student_profiles sp ON u.id = sp.user_id
                WHERE sp.is_eligible = 1
                ''')
                eligible_students = cursor.fetchall()
                for student in eligible_students:
                    print(dict(student))
        except sqlite3.Error as e:
            print(f"Error checking student profiles: {e}")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_db() 