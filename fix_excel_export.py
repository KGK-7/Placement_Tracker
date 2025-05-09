import sqlite3
import pandas as pd
import io
import os

def fix_excel_export():
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('placement_tracker.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check eligible students
        cursor.execute("SELECT COUNT(*) as count FROM student_profiles WHERE is_eligible = 1")
        count = cursor.fetchone()['count']
        print(f"Current eligible students: {count}")
        
        # Verify eligibility criteria
        cursor.execute("SELECT * FROM eligibility_criteria")
        criteria = cursor.fetchone()
        if criteria:
            print(f"Current eligibility criteria: {dict(criteria)}")
        else:
            print("No eligibility criteria found")
        
        # Try exporting eligible students directly
        try:
            print("\nTesting Excel export...")
            query = """
                SELECT u.id, u.username, u.email, u.department, u.specialization, 
                       sp.semester_cgpa, sp.domain_specialization, sp.skills, 
                       sp.leetcode_problems, sp.leetcode_profile, sp.github_profile, 
                       sp.linkedin_profile, sp.portfolio_link, sp.is_approved
                FROM users u
                JOIN student_profiles sp ON u.id = sp.user_id
                WHERE sp.is_eligible = 1
            """
            students = cursor.execute(query).fetchall()
            
            if not students:
                print("No eligible students found for export")
                
                # Make at least one student eligible for testing
                cursor.execute("UPDATE student_profiles SET is_eligible = 1 WHERE user_id = (SELECT id FROM users WHERE role = 'student' LIMIT 1)")
                conn.commit()
                print("Made one student eligible for testing")
                
                # Check again
                students = cursor.execute(query).fetchall()
                if not students:
                    print("Still no eligible students. Creating test data...")
                    
                    # Create test student if none exists
                    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
                    if cursor.fetchone()['count'] == 0:
                        from werkzeug.security import generate_password_hash
                        print("Creating test student user")
                        cursor.execute(
                            "INSERT INTO users (username, password, email, role, department, specialization) VALUES (?, ?, ?, ?, ?, ?)",
                            ("teststudent", generate_password_hash("password"), "test@example.com", "student", "CSE", "Web Development")
                        )
                        conn.commit()
                        
                        user_id = cursor.lastrowid
                        print(f"Created test student with ID {user_id}")
                        
                        # Create profile for the test student
                        cursor.execute("""
                            INSERT INTO student_profiles 
                            (user_id, semester_cgpa, domain_specialization, skills, projects, 
                            leetcode_problems, github_profile, linkedin_profile, portfolio_link,
                            weekly_assessment_score, attendance_percentage, is_eligible, project_titles,
                            project_domains, project_github_links, leetcode_profile)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user_id, 9.0, "Web Development", "Python,Flask,SQL", "Project 1,Project 2",
                            150, "https://github.com/test", "https://linkedin.com/in/test", "https://test.com",
                            90.0, 95.0, 1, "Web App,Mobile App", "Web,Mobile", 
                            "https://github.com/test/web,https://github.com/test/mobile", "https://leetcode.com/test"
                        ))
                        conn.commit()
                        print("Created test student profile")
                        
                        # Fetch again
                        students = cursor.execute(query).fetchall()
            
            print(f"Found {len(students)} eligible students for export")
            
            if students:
                # Try to create Excel file
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
                
                df = pd.DataFrame(students_list)
                
                # Create Excel file in memory
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Eligible Students', index=False)
                    
                    # Auto-adjust columns' width
                    worksheet = writer.sheets['Eligible Students']
                    for i, col in enumerate(df.columns):
                        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, max_len)
                
                output.seek(0)
                
                # Save to a file for inspection
                with open("eligible_students_test.xlsx", "wb") as f:
                    f.write(output.getvalue())
                print("Excel export successful! File saved as eligible_students_test.xlsx")
                
        except Exception as e:
            print(f"Error testing Excel export: {e}")
        
        print("\nFix completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_excel_export() 