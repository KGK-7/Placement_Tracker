import sqlite3
import pandas as pd
import io
import datetime

def export_eligible_students_to_excel():
    """Export eligible students' data to Excel file"""
    conn = None
    try:
        print("Starting export to Excel process")
        conn = sqlite3.connect('placement_tracker.db')
        conn.row_factory = sqlite3.Row
        
        # Get eligible students with all required fields
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
            WHERE sp.is_eligible = 1
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
        
        df = pd.DataFrame(students_list)
        
        # Create Excel file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'eligible_students_{timestamp}.xlsx'
        
        # Create Excel with auto-sized columns
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Eligible Students', index=False)
            
        # Auto-adjust columns' width
        worksheet = writer.sheets['Eligible Students']
        for i, col in enumerate(df.columns):
            # Get the maximum length in the column
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
        
        writer.close()
        print(f"Excel file generated successfully as {filename}")
        return True
    
    except Exception as e:
        print(f"Error in Excel export: {e}")
        return None
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    export_eligible_students_to_excel() 