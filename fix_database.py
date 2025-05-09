import sqlite3
import os

def fix_database():
    conn = None
    try:
        # Check if database file exists
        if not os.path.exists('placement_tracker.db'):
            print("Database file does not exist!")
            return
            
        # Connect to the database
        conn = sqlite3.connect('placement_tracker.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if columns exist in eligibility_criteria table
        cursor.execute("PRAGMA table_info(eligibility_criteria)")
        columns = {col['name']: col for col in cursor.fetchall()}
        
        print(f"Current columns in eligibility_criteria: {list(columns.keys())}")
        
        # Check specifically for the linkedin profile column
        if 'require_linkedin_profile' not in columns:
            print("Adding missing column: require_linkedin_profile")
            try:
                cursor.execute("ALTER TABLE eligibility_criteria ADD COLUMN require_linkedin_profile INTEGER DEFAULT 0")
                conn.commit()
                print("Added require_linkedin_profile column")
            except Exception as e:
                print(f"Error adding require_linkedin_profile: {e}")
        
        # Also check for the other missing columns
        if 'require_leetcode_profile' not in columns:
            print("Adding missing column: require_leetcode_profile")
            try:
                cursor.execute("ALTER TABLE eligibility_criteria ADD COLUMN require_leetcode_profile INTEGER DEFAULT 0")
                conn.commit()
                print("Added require_leetcode_profile column")
            except Exception as e:
                print(f"Error adding require_leetcode_profile: {e}")
                
        if 'require_github_profile' not in columns:
            print("Adding missing column: require_github_profile")
            try:
                cursor.execute("ALTER TABLE eligibility_criteria ADD COLUMN require_github_profile INTEGER DEFAULT 0")
                conn.commit()
                print("Added require_github_profile column")
            except Exception as e:
                print(f"Error adding require_github_profile: {e}")
        
        # Check updated columns
        cursor.execute("PRAGMA table_info(eligibility_criteria)")
        updated_columns = {col['name'] for col in cursor.fetchall()}
        print(f"Updated columns in eligibility_criteria: {updated_columns}")
        
        # Fix the student_profiles table too
        cursor.execute("PRAGMA table_info(student_profiles)")
        sp_columns = {col['name'] for col in cursor.fetchall()}
        print(f"Current columns in student_profiles: {sp_columns}")
        
        # Add missing columns to student_profiles
        if 'project_titles' not in sp_columns:
            print("Adding project_titles to student_profiles")
            cursor.execute("ALTER TABLE student_profiles ADD COLUMN project_titles TEXT")
            conn.commit()
            
        if 'project_domains' not in sp_columns:
            print("Adding project_domains to student_profiles")
            cursor.execute("ALTER TABLE student_profiles ADD COLUMN project_domains TEXT")
            conn.commit()
            
        if 'project_github_links' not in sp_columns:
            print("Adding project_github_links to student_profiles")
            cursor.execute("ALTER TABLE student_profiles ADD COLUMN project_github_links TEXT")
            conn.commit()
            
        if 'leetcode_profile' not in sp_columns:
            print("Adding leetcode_profile to student_profiles")
            cursor.execute("ALTER TABLE student_profiles ADD COLUMN leetcode_profile TEXT")
            conn.commit()
        
        # Show updated student profiles columns
        cursor.execute("PRAGMA table_info(student_profiles)")
        sp_updated_columns = {col['name'] for col in cursor.fetchall()}
        print(f"Updated columns in student_profiles: {sp_updated_columns}")
        
        # Verify eligibility criteria data
        cursor.execute("SELECT * FROM eligibility_criteria")
        criteria = cursor.fetchall()
        print("\nEligibility Criteria Data:")
        for row in criteria:
            # Convert row to dict and print it
            row_dict = {}
            for key in columns.keys():
                row_dict[key] = row[key] if key in dict(row) else None
            print(row_dict)
        
        print("\nFix completed!")
    
    except Exception as e:
        print(f"Error fixing database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_database() 