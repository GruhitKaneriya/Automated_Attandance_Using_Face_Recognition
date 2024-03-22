import subprocess

import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="gruhit@2004",
    database="webdev"
)

app = Flask(__name__)
app.secret_key = b'N\xe61[Ub\xe8I\xfd\x8b\xcc\xf0\x08<#G\xae\x81\xcf\xa9\xecq\xbb\x82'
@app.route('/')
def home():
    return render_template('home.html')

# Function to authenticate teacher login
def authenticate_teacher(id, password):
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM teachers WHERE teacher_id = %s AND password = %s"
        cursor.execute(query, (id, password))
        teacher = cursor.fetchone()
        cursor.close()
        if teacher:
            return True
        else:
            return False
    except mysql.connector.Error as error:
        print("Error:", error)
        return False

# Route for teacher login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        teacher_id = request.form['id']
        teacher_password = request.form['password']

        if authenticate_teacher(teacher_id, teacher_password):
            # Store the teacher_id in the session
            session['teacher_id'] = teacher_id
            # Redirect to teacher dashboard if authentication is successful
            return redirect(url_for('teacher_dashboard'))

        else:
            # Display error message for invalid credentials
            return render_template('teacher-login.html', error=True)

    return render_template('teacher-login.html', error=False)

# Function to authenticate student login
def authenticate_student(id, password):
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM students WHERE student_id = %s AND password = %s"
        cursor.execute(query, (id, password))
        student = cursor.fetchone()
        cursor.close()
        if student:
            return True
        else:
            return False
    except mysql.connector.Error as error:
        print("Error:", error)
        return False


def get_teacher_name(teacher_id):
    try:
        cursor = conn.cursor()
        query = "SELECT teacher_name FROM teachers WHERE teacher_id = %s"
        cursor.execute(query, (teacher_id,))
        teacher_name = cursor.fetchone()[0]  # Fetch the first column of the first row
        cursor.close()
        return teacher_name
    except mysql.connector.Error as error:
        print("Error:", error)
        return None

# Route for teacher dashboard
def get_teacher_sections(teacher_id):
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT subject_id, subject_name, section1, section2, section3, section4, section5 FROM teacher_subjects WHERE teacher_id = %s"
        cursor.execute(query, (teacher_id,))
        teacher_sections = cursor.fetchall()
        cursor.close()
        return teacher_sections
    except mysql.connector.Error as error:
        print("Error:", error)
        return []

# Route for teacher dashboard
@app.route('/teacher-dashboard')
def teacher_dashboard():
    # Check if the teacher is logged in
    if 'teacher_id' in session:
        teacher_id = session['teacher_id']
        teacher_name = get_teacher_name(teacher_id)
        if teacher_name:
            teacher_sections = get_teacher_sections(teacher_id)
            return render_template('teacher-dashboard.html', teacher_id=teacher_id, teacher_name=teacher_name, teacher_sections=teacher_sections)
        else:
            return "Error: Teacher details not found."
    else:
        # If not logged in, redirect to the login page
        return redirect(url_for('login'))

@app.route('/start-attendance', methods=['POST'])
def start_attendance():
    # Get selected sections and subject ID from the request
    data = request.get_json()
    selected_subject_id = data.get('subject_id')
    selected_sections = data.get('sections', [])

    # Here you can execute attendance.py for the selected sections
    subprocess.Popen(['python', 'attendance.py', selected_subject_id, ','.join(selected_sections)])

    return jsonify({"message": f"Attendance process started for subject ID: {selected_subject_id} and sections: " + ','.join(selected_sections)})


@app.route('/process_selection', methods=['POST'])
def process_selection():
    subject_id = request.form['subject']
    # Process the selected subject ID here
    return "Selected Subject ID: " + subject_id


def authenticate_student(id):
    try:
        cursor = conn.cursor()
        query = "SELECT Student_name FROM student WHERE Registration_no = %s"
        cursor.execute(query, (id,))
        student = cursor.fetchone()
        cursor.close()
        if student:
            return student[0]  # Return the student's name
        else:
            return None
    except mysql.connector.Error as error:
        print("Error:", error)
        return None
# Route for student login
@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['id']
        student_name = authenticate_student(student_id)  # Fetch student name directly from authentication function
        if student_name:
            # Store the student_id in the session
            session['student_id'] = student_id
            # Redirect to student dashboard if authentication is successful
            return redirect(url_for('student_dashboard'))
        else:
            # Display error message for invalid credentials
            return render_template('student-login.html', error=True)

    return render_template('student-login.html', error=False)

# Route for student dashboard
# Route for student dashboard
@app.route('/student-dashboard')
def student_dashboard():
    # Check if the student is logged in
    if 'student_id' in session:
        student_id = session['student_id']
        # Fetch student details
        student_details = get_student_details(student_id)
        if student_details:
            # Fetch enrolled subjects for the student
            student_subjects = get_student_subjects(student_id)
            # Fetch course details for the enrolled subjects
            courses = get_courses(student_subjects)
            return render_template('student-dashboard.html', student_details=student_details, courses=courses)
        else:
            return "Error: Student details not found."
    else:
        # If not logged in, redirect to the login page
        return redirect(url_for('student_login'))



def get_student_details(student_id):
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT Registration_no, Student_name, mail_id, batch, semester, section, Student_image FROM student WHERE Registration_no = %s"
        cursor.execute(query, (student_id,))
        student_details = cursor.fetchone()
        cursor.close()
        return student_details
    except mysql.connector.Error as error:
        print("Error:", error)
        return None


def get_student_subjects(student_id):
    try:
        cursor = conn.cursor()
        query = "SELECT subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10 FROM student_subjects WHERE Roll_No = %s"
        cursor.execute(query, (student_id,))
        subjects = cursor.fetchone()
        cursor.close()
        return subjects
    except mysql.connector.Error as error:
        print("Error:", error)
        return None

def get_courses(subjects):
    try:
        cursor = conn.cursor(dictionary=True)
        courses = []
        for subject in subjects:
            if subject:
                query = "SELECT Course_name, Course_credit FROM courses WHERE Course_id = %s"
                cursor.execute(query, (subject,))
                course = cursor.fetchone()
                if course:
                    courses.append({'Subject_id': subject, 'Course_name': course['Course_name'], 'Course_credit': course['Course_credit']})
        cursor.close()
        return courses
    except mysql.connector.Error as error:
        print("Error:", error)
        return []
def get_attendance_data(table_name):
    try:
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT total_present, total_classes FROM {table_name}"
        cursor.execute(query)
        attendance_data = cursor.fetchall()
        cursor.close()
        return attendance_data
    except mysql.connector.Error as error:
        print("Error:", error)
        return None
@app.route('/view-attendance', methods=['POST'])
def view_attendance():
    if 'student_id' in session:
        student_id = session['student_id']
        student_details = get_student_details(student_id)
        if student_details:
            data = request.json  # Get JSON data sent from the client
            subject_id = data.get('subject_id')
            section = student_details['section']
            table_name = f"{section}{subject_id}"  # Construct the table name
            attendance_data = get_attendance_data(table_name)
            if attendance_data:
                total_present = 0
                total_classes = 0
                for row in attendance_data:
                    total_present += row.get('total_present', 0)
                    total_classes += row.get('total_classes', 0)
                return jsonify({'total_present': total_present, 'total_classes': total_classes})
            else:
                return jsonify({'error': 'Attendance data not found.'}), 404
        else:
            return jsonify({'error': 'Student details not found.'}), 404
    else:
        return redirect(url_for('student_login'))

if __name__ == '__main__':
    app.run(debug=True)