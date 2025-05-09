# Student Placement Tracker System

A web application for tracking student eligibility for placement opportunities. The system allows students to enter their academic and technical details, while administrators can set eligibility criteria and approve eligible students for placement drives.

## Features

### Student Features
- Profile management with academic details
- Self-assessment of eligibility based on admin-defined criteria
- Tracking of skills, projects, and technical achievements
- Status tracking for placement eligibility and approval

### Admin Features
- View and manage all registered students
- Set and update placement eligibility criteria
- Filter students by department
- Approve eligible students for placement opportunities
- Detailed view of student profiles and achievements

## Tech Stack

### Frontend
- HTML, CSS, JavaScript
- Responsive design for all device sizes

### Backend
- Python with Flask
- SQLite database for data storage
- Session-based authentication

## Project Structure
```
.
├── app.py              # Main Flask application
├── admin.py            # Admin dashboard backend logic
├── student.py          # Student dashboard backend logic
├── database.py         # Database operations
├── templates/          # HTML templates
│   ├── index.html      # Login and registration page
│   └── dashboard.html  # Dashboard for students and admin
├── static/             # Static files
│   ├── styles.css      # CSS styling
│   └── script.js       # JavaScript functionality
└── placement_tracker.db # SQLite database file
```

## Setup and Installation

1. Make sure you have Python 3.6+ installed.

2. Clone the repository:
```bash
git clone <repository-url>
cd student-placement-tracker
```

3. Install the required dependencies:
```bash
pip install flask werkzeug
```

4. Run the application:
```bash
python app.py
```

5. Access the application at http://127.0.0.1:5050/

## First Time Setup

When you first run the application, you'll need to:

1. Register an admin account (select 'Admin' as the role)
2. Register student accounts (select 'Student' as the role)
3. Login with the admin account to set eligibility criteria
4. Students can then login to complete their profiles

## Default Eligibility Criteria

- Minimum attendance: 85%
- Minimum weekly assessment score: 80%
- Minimum CGPA: 8.5
- Minimum LeetCode problems solved: 100
- Minimum completed projects: 3
- Personal portfolio required: Yes

These criteria can be adjusted by the admin as needed. 