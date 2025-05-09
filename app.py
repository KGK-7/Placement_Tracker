from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import database as db
from student import student_bp
from admin import admin_bp

app = Flask(__name__)
# Use a fixed secret key or environment variable to ensure sessions remain valid
app.secret_key = os.environ.get('SECRET_KEY', 'placement_tracker_secret_key')

# Register blueprints
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)

# Initialize database
db.init_db()

@app.route('/')
def index():
    """Main landing page with login form"""
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Login route"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = db.authenticate_user(username, password)
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        role = request.form.get('role', 'student')
        department = request.form.get('department') if role == 'student' else None
        specialization = request.form.get('specialization') if role == 'student' else None
        admin_key = request.form.get('admin_key') if role == 'admin' else None
        
        if not username or not password or not email:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
            
        if role == 'admin' and not admin_key:
            flash('Admin key is required for admin registration', 'error')
            return redirect(url_for('register'))
        
        success = db.register_user(username, password, email, role, department, specialization, admin_key)
        
        if success:
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('index'))
        else:
            if role == 'admin':
                flash('Registration failed. Invalid admin key or username/email already exists', 'error')
            else:
                flash('Username or email already exists', 'error')
            return redirect(url_for('register'))
    
    return render_template('index.html', register=True)

if __name__ == '__main__':
    app.run(debug=True, port=5050) 