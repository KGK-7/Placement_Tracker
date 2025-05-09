// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Get all forms with class 'profile-form'
    const profileForms = document.querySelectorAll('.profile-form');
    
    // Add validation to each form
    profileForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const cgpaInput = form.querySelector('#semester_cgpa');
            const leetcodeInput = form.querySelector('#leetcode_problems');
            const weeklyScoreInput = form.querySelector('#weekly_assessment_score');
            const attendanceInput = form.querySelector('#attendance_percentage');
            
            // Validate CGPA (0-10)
            if (cgpaInput && (cgpaInput.value < 0 || cgpaInput.value > 10)) {
                event.preventDefault();
                alert('CGPA must be between 0 and 10');
                return;
            }
            
            // Validate LeetCode problems (non-negative)
            if (leetcodeInput && leetcodeInput.value < 0) {
                event.preventDefault();
                alert('Number of LeetCode problems cannot be negative');
                return;
            }
            
            // Validate Weekly Assessment Score (0-100)
            if (weeklyScoreInput && (weeklyScoreInput.value < 0 || weeklyScoreInput.value > 100)) {
                event.preventDefault();
                alert('Weekly Assessment Score must be between 0 and 100');
                return;
            }
            
            // Validate Attendance Percentage (0-100)
            if (attendanceInput && (attendanceInput.value < 0 || attendanceInput.value > 100)) {
                event.preventDefault();
                alert('Attendance Percentage must be between 0 and 100');
                return;
            }
        });
    });
    
    // Get all forms with class 'criteria-form'
    const criteriaForms = document.querySelectorAll('.criteria-form');
    
    // Add validation to each form
    criteriaForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const minCgpaInput = form.querySelector('#min_cgpa');
            const minLeetcodeInput = form.querySelector('#min_leetcode_problems');
            const minScoreInput = form.querySelector('#min_assessment_score');
            const minAttendanceInput = form.querySelector('#min_attendance');
            
            // Validate Min CGPA (0-10)
            if (minCgpaInput && (minCgpaInput.value < 0 || minCgpaInput.value > 10)) {
                event.preventDefault();
                alert('Minimum CGPA must be between 0 and 10');
                return;
            }
            
            // Validate Min LeetCode problems (non-negative)
            if (minLeetcodeInput && minLeetcodeInput.value < 0) {
                event.preventDefault();
                alert('Minimum LeetCode problems cannot be negative');
                return;
            }
            
            // Validate Min Assessment Score (0-100)
            if (minScoreInput && (minScoreInput.value < 0 || minScoreInput.value > 100)) {
                event.preventDefault();
                alert('Minimum Assessment Score must be between 0 and 100');
                return;
            }
            
            // Validate Min Attendance (0-100)
            if (minAttendanceInput && (minAttendanceInput.value < 0 || minAttendanceInput.value > 100)) {
                event.preventDefault();
                alert('Minimum Attendance must be between 0 and 100');
                return;
            }
        });
    });
    
    // Registration form role toggle
    const roleSelect = document.getElementById('role');
    if (roleSelect) {
        toggleDepartment();
        roleSelect.addEventListener('change', toggleDepartment);
    }
});

// Function to toggle department field visibility
function toggleDepartment() {
    const roleSelect = document.getElementById('role');
    const departmentGroup = document.getElementById('department-group');
    
    if (!roleSelect || !departmentGroup) return;
    
    if (roleSelect.value === 'admin') {
        departmentGroup.style.display = 'none';
    } else {
        departmentGroup.style.display = 'block';
    }
}

// Function to show student tab
function showStudentTab(tabName) {
    document.querySelectorAll('.student-tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    document.querySelectorAll('.student-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById('tab-' + tabName).style.display = 'block';
    document.querySelector('.student-tabs .tab-btn[onclick="showStudentTab(\'' + tabName + '\')"]').classList.add('active');
}

// Function to filter students by department
function filterByDepartment() {
    const department = document.getElementById('department-filter').value;
    
    // Filter all students table
    const allStudentRows = document.querySelectorAll('#all-students-table tr');
    if (allStudentRows) {
        allStudentRows.forEach(row => {
            if (department === 'all' || row.getAttribute('data-department') === department) {
                row.style.display = 'table-row';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Filter eligible students table
    const eligibleStudentRows = document.querySelectorAll('#eligible-students-table tr');
    if (eligibleStudentRows) {
        eligibleStudentRows.forEach(row => {
            if (department === 'all' || row.getAttribute('data-department') === department) {
                row.style.display = 'table-row';
            } else {
                row.style.display = 'none';
            }
        });
    }
}

// Function to approve/reject student
function approveStudent(studentId, approved) {
    fetch(`/admin/approve_student/${studentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `approved=${approved}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Failed to update approval status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating approval status');
    });
} 