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
        conn = mysql.connector.connect(host='localhost',  # replace 'localhost' with your host
                                       database='webdev',  # replace 'webdev' with your database name
                                       user='root',  # replace 'root' with your username
                                       password='gruhit@2004')  # replace 'gruhit@2004' with your password
        return conn
    except Error as e:
        print(e)

# Function to retrieve student data including image paths from the database
def get_students(conn):
    students = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Student_name, Student_image FROM student")
        students = cursor.fetchall()
    except Error as e:
        print(e)
    return students

# Function to recognize faces and display student information
def recognize_faces(frame, known_face_encodings, known_face_names):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        # Compare the face encoding with known face encodings
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Display the recognized name
        cv2.putText(frame, f"Name: {name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return frame

# Create a connection to the database
conn = create_connection()
if conn is None:
    print("Error! Cannot create a database connection.")
else:
    # Retrieve student data including image paths from the database
    students = get_students(conn)

    # Initialize lists to store face encodings and names
    known_face_encodings = []
    known_face_names = []

    # Iterate over each student and load their image and corresponding name
    for student in students:
        student_name, student_image_path = student
        # Load the image file using the retrieved path
        student_image = face_recognition.load_image_file(student_image_path)
        # Perform face encoding
        student_face_encoding = face_recognition.face_encodings(student_image)[0]
        # Append face encoding and corresponding name to the lists
        known_face_encodings.append(student_face_encoding)
        known_face_names.append(student_name)

    # Release the database connection
    conn.close()

    # Initialize the video capture object
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Recognize faces and display student information
        frame = recognize_faces(frame, known_face_encodings, known_face_names)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object
    video_capture.release()
    cv2.destroyAllWindows()
