from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
import database as db

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/dashboard')
def dashboard():
    """Student dashboard page"""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    profile = db.get_student_profile(user_id)
    criteria = db.get_eligibility_criteria()
    
    return render_template('dashboard.html', user=user, profile=profile, criteria=criteria, role='student')

@student_bp.route('/student/update_profile', methods=['POST'])
def update_profile():
    """Update student profile"""
    if 'user_id' not in session or session.get('role') != 'student':
        flash('You must be logged in as a student to update your profile', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    
    try:
        # Get data from form
        data = {
            'semester_cgpa': float(request.form.get('semester_cgpa', 0)),
            'domain_specialization': request.form.get('domain_specialization', ''),
            'skills': request.form.get('skills', ''),
            'projects': request.form.get('projects', ''),
            'project_titles': request.form.get('project_titles', ''),
            'project_domains': request.form.get('project_domains', ''),
            'project_github_links': request.form.get('project_github_links', ''),
            'leetcode_problems': int(request.form.get('leetcode_problems', 0)),
            'leetcode_profile': request.form.get('leetcode_profile', ''),
            'github_profile': request.form.get('github_profile', ''),
            'linkedin_profile': request.form.get('linkedin_profile', ''),
            'portfolio_link': request.form.get('portfolio_link', ''),
            'weekly_assessment_score': float(request.form.get('weekly_assessment_score', 0)),
            'attendance_percentage': float(request.form.get('attendance_percentage', 0))
        }
        
        success = db.update_student_profile(user_id, data)
        
        if success:
            flash('Profile updated successfully', 'success')
        else:
            flash('Failed to update profile. Please try again.', 'error')
            
        return redirect(url_for('student.profile'))
    
    except (ValueError, TypeError) as e:
        flash(f'Invalid data format: {str(e)}', 'error')
        return redirect(url_for('student.profile'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('student.profile'))

@student_bp.route('/student/profile')
def profile():
    """Student profile page"""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    profile = db.get_student_profile(user_id)
    criteria = db.get_eligibility_criteria()
    
    # Calculate eligibility status
    is_eligible = False
    if profile:
        project_count = len(profile['projects'].split(',')) if profile['projects'] else 0
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
    
    return render_template('dashboard.html', 
                          user=user, 
                          profile=profile, 
                          criteria=criteria, 
                          is_eligible=is_eligible,
                          tab='profile',
                          role='student') 