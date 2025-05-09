import sqlite3
import os

def rebuild_eligibility_table():
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('placement_tracker.db')
        conn.row_factory = sqlite3.Row
        
        # First, backup the existing data
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eligibility_criteria LIMIT 1")
        existing_data = cursor.fetchone()
        
        if existing_data:
            print("Backing up existing eligibility criteria data")
            existing = dict(existing_data)
            print(f"Existing data: {existing}")
        else:
            print("No existing eligibility criteria data found")
            existing = {
                'min_attendance': 85.0,
                'min_assessment_score': 80.0,
                'min_cgpa': 8.5,
                'min_leetcode_problems': 100,
                'min_projects': 3,
                'require_portfolio': 1
            }
        
        # Drop the existing table
        print("Dropping existing eligibility_criteria table")
        cursor.execute("DROP TABLE IF EXISTS eligibility_criteria")
        conn.commit()
        
        # Create a new table with all required columns
        print("Creating new eligibility_criteria table")
        cursor.execute('''
        CREATE TABLE eligibility_criteria (
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
        conn.commit()
        
        # Insert the data back
        print("Restoring eligibility criteria data")
        cursor.execute('''
        INSERT INTO eligibility_criteria 
        (id, min_attendance, min_assessment_score, min_cgpa, min_leetcode_problems, min_projects, 
        require_portfolio, require_leetcode_profile, require_github_profile, require_linkedin_profile)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            existing.get('id', 1),
            existing.get('min_attendance', 85.0),
            existing.get('min_assessment_score', 80.0),
            existing.get('min_cgpa', 8.5),
            existing.get('min_leetcode_problems', 100),
            existing.get('min_projects', 3),
            existing.get('require_portfolio', 1),
            existing.get('require_leetcode_profile', 0),
            existing.get('require_github_profile', 0),
            existing.get('require_linkedin_profile', 0)
        ))
        conn.commit()
        
        # Verify the new table
        print("\nVerifying rebuilt table")
        cursor.execute("PRAGMA table_info(eligibility_criteria)")
        columns = [col['name'] for col in cursor.fetchall()]
        print(f"Columns in rebuilt table: {columns}")
        
        cursor.execute("SELECT * FROM eligibility_criteria")
        new_data = cursor.fetchone()
        if new_data:
            print(f"New data: {dict(new_data)}")
        else:
            print("No data in rebuilt table!")
            
        # Fix student_profiles table if needed
        print("\nChecking student_profiles table")
        cursor.execute("PRAGMA table_info(student_profiles)")
        sp_columns = {col['name'] for col in cursor.fetchall()}
        
        # Add missing columns to student_profiles
        missing_columns = []
        if 'project_titles' not in sp_columns:
            missing_columns.append(("project_titles", "TEXT"))
        if 'project_domains' not in sp_columns:
            missing_columns.append(("project_domains", "TEXT"))
        if 'project_github_links' not in sp_columns:
            missing_columns.append(("project_github_links", "TEXT"))
        if 'leetcode_profile' not in sp_columns:
            missing_columns.append(("leetcode_profile", "TEXT"))
        
        for col_name, col_type in missing_columns:
            print(f"Adding column {col_name} to student_profiles")
            cursor.execute(f"ALTER TABLE student_profiles ADD COLUMN {col_name} {col_type}")
            conn.commit()
        
        print("\nRebuild completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    rebuild_eligibility_table() 