import sqlite3
import os

def final_fix():
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('placement_tracker.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = {col['name'] for col in cursor.fetchall()}
        print(f"Current columns in users table: {columns}")
        
        # Add specialization column if missing
        if 'specialization' not in columns:
            print("Adding specialization column to users table")
            cursor.execute("ALTER TABLE users ADD COLUMN specialization TEXT")
            conn.commit()
            print("Column added successfully")
            
            # Update existing users with a default specialization
            cursor.execute("UPDATE users SET specialization = 'General' WHERE role = 'student' AND specialization IS NULL")
            conn.commit()
            print("Updated existing student users with default specialization")
        
        # Now fix the export query
        print("\nFixing export query to use safe column access")
        export_query = """
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
            sp.is_approved,
            sp.is_eligible
        FROM users u
        JOIN student_profiles sp ON u.id = sp.user_id
        WHERE sp.is_eligible = 1
        """
        
        students = cursor.execute(export_query).fetchall()
        print(f"Found {len(students)} eligible students")
        
        if students:
            print("\nEligible students details:")
            for student in students:
                print(dict(student))
        
        # Make sure we have pandas and xlsxwriter for Excel export
        try:
            import pandas as pd
            import xlsxwriter
            print("\nRequired Excel libraries are available")
        except ImportError:
            print("\nWARNING: pandas and/or xlsxwriter libraries are missing.")
            print("Please install them with: pip install pandas xlsxwriter")
        
        print("\nAll issues should now be fixed. Try running the application again.")
    
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    final_fix() 