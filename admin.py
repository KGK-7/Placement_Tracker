from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify, send_file
import database as db
import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def dashboard():
    """Admin dashboard page"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    all_students = db.get_all_students()
    eligible_students = db.get_eligible_students()
    criteria = db.get_eligibility_criteria()
    
    return render_template('dashboard.html', 
                          user=user, 
                          all_students=all_students,
                          eligible_students=eligible_students,
                          criteria=criteria,
                          role='admin')

@admin_bp.route('/admin/students_by_department/<department>')
def students_by_department(department):
    """Get students by department"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    students = db.get_all_students_by_department(department)
    return jsonify({'students': students})

@admin_bp.route('/admin/eligibility_criteria', methods=['GET', 'POST'])
def eligibility_criteria():
    """View and update eligibility criteria"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    criteria = db.get_eligibility_criteria()
    
    if request.method == 'POST':
        try:
            # Print received form data for debugging
            form_data = request.form
            print("Received form data:", form_data)
            
            # Update criteria
            new_criteria = {
                'min_attendance': float(form_data.get('min_attendance', 85.0)),
                'min_assessment_score': float(form_data.get('min_assessment_score', 80.0)),
                'min_cgpa': float(form_data.get('min_cgpa', 8.5)),
                'min_leetcode_problems': int(form_data.get('min_leetcode_problems', 100)),
                'min_projects': int(form_data.get('min_projects', 3)),
                'require_portfolio': 1 if form_data.get('require_portfolio') else 0,
                'require_leetcode_profile': 1 if form_data.get('require_leetcode_profile') else 0,
                'require_github_profile': 1 if form_data.get('require_github_profile') else 0,
                'require_linkedin_profile': 1 if form_data.get('require_linkedin_profile') else 0
            }
            
            # Print criteria for debugging
            print("New criteria values:", new_criteria)
            
            success = db.update_eligibility_criteria(new_criteria)
            
            if success:
                flash('Eligibility criteria updated successfully', 'success')
            else:
                flash('Failed to update eligibility criteria. Check server logs for details.', 'error')
            
            # Redirect back to the same page
            return redirect(url_for('admin.eligibility_criteria'))
        except Exception as e:
            flash(f'Error updating criteria: {str(e)}', 'error')
            print(f"Error updating criteria: {str(e)}")
            return redirect(url_for('admin.eligibility_criteria'))
    
    # Get updated criteria
    criteria = db.get_eligibility_criteria()
    print("Retrieved criteria for display:", criteria)
    
    return render_template('dashboard.html', user=user, criteria=criteria, tab='criteria', role='admin')

@admin_bp.route('/admin/approve_student/<int:student_id>', methods=['POST'])
def approve_student(student_id):
    """Approve or reject a student for placement"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        approved_str = request.form.get('approved', 'false')
        print(f"Received approval request: student_id={student_id}, approved={approved_str}")
        
        # Convert string to boolean
        approved = approved_str.lower() == 'true'
        
        success = db.approve_student(student_id, approved)
        
        if not success:
            return jsonify({'success': False, 'message': 'Failed to update approval status'}), 500
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error approving student: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@admin_bp.route('/admin/student_details/<int:student_id>')
def student_details(student_id):
    """Get detailed information about a student"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    admin_user = db.get_user_by_id(user_id)
    student_detail = db.get_user_by_id(student_id)
    student_profile = db.get_student_profile(student_id)
    
    if not student_detail or not student_profile:
        flash('Student not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('dashboard.html', 
                          user=admin_user,
                          student_detail=student_detail, 
                          student_profile=student_profile,
                          tab='student_detail',
                          role='admin')

@admin_bp.route('/admin/export_excel')
def export_excel():
    """Export eligible students to Excel file"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    try:
        # Get eligible students count for debugging
        conn = db.get_db_connection()
        if conn:
            count = conn.execute("SELECT COUNT(*) FROM student_profiles WHERE is_eligible = 1").fetchone()[0]
            conn.close()
            print(f"Eligible student count before export: {count}")
        
        # Generate the Excel file
        excel_data = db.export_eligible_students_to_excel()
        
        if not excel_data:
            flash('No eligible students to export or error generating Excel file. Check server logs.', 'error')
            return redirect(url_for('admin.dashboard'))
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'eligible_students_{timestamp}.xlsx'
        
        print(f"Sending Excel file {filename} to client")
        
        return send_file(
            excel_data,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"Error in export_excel route: {str(e)}")
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    """Admin settings page"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    
    if request.method == 'POST':
        new_admin_key = request.form.get('admin_key')
        if new_admin_key:
            db.update_admin_key(new_admin_key)
            flash('Admin key updated successfully', 'success')
        else:
            flash('Admin key cannot be empty', 'error')
    
    admin_key = db.get_admin_key()
    
    return render_template('dashboard.html',
                          user=user,
                          admin_key=admin_key,
                          tab='admin_settings',
                          role='admin') 