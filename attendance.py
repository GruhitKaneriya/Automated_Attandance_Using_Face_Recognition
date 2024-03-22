import mysql.connector
from mysql.connector import Error
import face_recognition
import cv2
import numpy as np

def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='webdev',
                                       user='root',
                                       password='gruhit@2004')
        return conn
    except Error as e:
        print(e)

def create_table(conn, table_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), roll_no INT, total_classes INT DEFAULT 0, total_present INT DEFAULT 0)")
    except Error as e:
        print(e)

def fetch_students(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Student_name, Registration_no, Student_image FROM student")
        return cursor.fetchall()
    except Error as e:
        print(e)

def insert_values(conn, table_name, entities):
    try:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table_name} (Registration_no, Student_name) VALUES (%s, %s)", (entities[0], entities[1]))
        conn.commit()
    except Error as e:
        print(e)

def mark_attendance(conn, table_name, known_faces_names, known_faces_roll_nos, known_faces_image_paths, known_face_encodings, recognized_students):
    print("Starting attendance...")  # Display starting attendance message

    # Set initial value of attendance status
    attendance_status = "Starting attendance..."

    # Update the attendance status displayed on the website
    update_attendance_status(attendance_status)

    video_capture = cv2.VideoCapture(0)

    # Increment total classes only once when attendance marking starts
    increment_total_classes(conn, table_name)

    while True:
        _, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = ""
            registration_no = ""  # Initialize registration number variable
            face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distance)

            if matches[best_match_index]:
                name = known_faces_names[best_match_index]
                registration_no = f"{known_faces_roll_nos[best_match_index]:04d}"  # Create registration number

                if registration_no not in recognized_students:
                    recognized_students.append(registration_no)  # Add to recognized list
                    update_attendance(conn, table_name, registration_no)

                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"Reg. No: {registration_no}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("attendance system", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            attendance_status = "Attendance recorded."  # Update attendance status
            update_attendance_status(attendance_status)  # Update the attendance status displayed on the website
            print("Attendance recorded.")  # Display attendance recorded message
            break

    video_capture.release()
    cv2.destroyAllWindows()

def increment_total_classes(conn, table_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name} SET total_classes = total_classes + 1")
        conn.commit()
        print("Total classes incremented successfully")
    except Error as e:
        print("Error incrementing total classes:", e)

def update_attendance(conn, table_name, registration_no):
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name} SET total_present = total_present + 1 WHERE Registration_no = %s", (int(registration_no),))
        conn.commit()
        print("Attendance updated successfully for:", registration_no)
    except Error as e:
        print("Error updating attendance:", e)

def update_attendance_status(status):
    with open("attendance_status.txt", "w") as file:
        file.write(status)

def main(subject_id, section):
    table_name = f"{section}{subject_id}"

    conn = create_connection()
    if conn is not None:
        create_table(conn, table_name)
    else:
        print("Error! Cannot create a database connection.")

    students_data = fetch_students(conn)
    if students_data:
        known_faces_names = [student[0] for student in students_data]
        known_faces_roll_nos = [int(student[1][10:]) for student in students_data]
        known_faces_image_paths = [student[2] for student in students_data]

        known_face_encodings = []  # Define known_face_encodings here

        for image_path in known_faces_image_paths:
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)

        recognized_students = []

        mark_attendance(conn, table_name, known_faces_names, known_faces_roll_nos, known_faces_image_paths, known_face_encodings, recognized_students)
    else:
        print("Error! No student data retrieved from the database.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2])
