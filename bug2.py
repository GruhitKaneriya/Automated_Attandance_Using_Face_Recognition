import mysql.connector
from mysql.connector import Error
import face_recognition
import cv2
import numpy as np
from datetime import datetime

# Function to create a connection to the MySQL database
def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost', # replace 'localhost' with your host
                                       database='webdev', # replace 'database_name' with your database name
                                       user='root', # replace 'user_name' with your username
                                       password='gruhit@2004') # replace 'password' with your password
        return conn
    except Error as e:
        print(e)

# Function to create a table
def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), roll_no INT, date_time DATETIME)")
    except Error as e:
        print(e)

# Function to fetch student data from the MySQL table
def fetch_students(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Student_name, Registration_no, Student_image FROM student")
        return cursor.fetchall()
    except Error as e:
        print(e)

# Function to insert values into the table
def insert_values(conn, entities):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, roll_no, date_time) VALUES (%s, %s, %s)", entities)
        conn.commit()
    except Error as e:
        print(e)

# Create a connection and a table
conn = create_connection()
if conn is not None:
    create_table(conn)
else:
    print("Error! Cannot create a database connection.")

# Fetch student data from the MySQL table
students_data = fetch_students(conn)
if students_data:
    known_faces_names = [student[0] for student in students_data]
    known_faces_roll_nos = [int(student[1][10:]) for student in students_data]  # Extract roll numbers from Registration_no
    known_faces_image_paths = [student[2] for student in students_data]
else:
    print("Error! No student data retrieved from the database.")

# Load face encodings from images
known_face_encodings = []
for image_path in known_faces_image_paths:
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)

# Create an empty list to store the names of recognized students
recognized_students = []

video_capture = cv2.VideoCapture(0)

while True:
    _, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = ""
        roll_no = 0
        face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distance)

        if matches[best_match_index]:
            name = known_faces_names[best_match_index]
            roll_no = known_faces_roll_nos[best_match_index]

            # Check if the student has already been recognized
            if name not in recognized_students:
                date_time = datetime.now()
                entities = (name, roll_no, date_time)
                insert_values(conn, entities)

                # Add the recognized student's name to the list
                recognized_students.append(name)

            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Display registration number
            cv2.putText(frame, f"Reg. No: {roll_no}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("attendance system", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
