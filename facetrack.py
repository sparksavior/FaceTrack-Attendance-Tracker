import cv2
import face_recognition
import numpy as np
import csv
from datetime import datetime
import os
import re
import matplotlib.pyplot as plt
from flask import Flask,render_template,  jsonify, request, send_file, make_response
from flasgger import Swagger
from io import BytesIO


app = Flask(__name__)
swagger = Swagger(app)

# Get the absolute path to the 'assets' folder
ABSOLUTE_PATH_TO_ASSETS = os.getenv('ABSOLUTE_PATH_TO_ASSETS', "D:\\c-downloads\\facetrack\\v3\\assets")
# Get the absolute path to the 'data' folder
ABSOLUTE_PATH_TO_DATA = os.getenv('ABSOLUTE_PATH_TO_DATA', "D:\\c-downloads\\facetrack\\v3\\data")

folder_path = 'assets'
known_images = []
known_names = []

for filename in os.listdir(folder_path):
    if filename.endswith('.jpg'):
        image = face_recognition.load_image_file(os.path.join(folder_path, filename))
        encoding = face_recognition.face_encodings(image)[0]
        known_images.append(encoding)
        known_names.append(os.path.splitext(filename)[0])

@app.route('/registration', methods=['POST'])
def user_registration():
    """
    User Registration endpoint
    ---
    tags:
      - Registration
    parameters:
      - name: userName
        in: formData
        type: string
        required: true
        description: User's name
      - name: userEmail
        in: formData
        type: string
        required: true
        description: User's email address
    responses:
      200:
        description: User registered successfully.
      400:
        description: Bad request or validation error.
      500:
        description: Internal server error.
    """
    try:
        # Extract data from the request
        user_name = request.form.get('userName')
        user_email = request.form.get('userEmail')

        # Create a filename for the user's picture
        filename = re.sub(r'[^a-zA-Z0-9.]+', '_', f"{user_name}#{user_email}.jpg")

        # Capture photo for registration
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()

        # Save the user's picture with an absolute path in the assets folder
        user_picture_path = os.path.join(ABSOLUTE_PATH_TO_ASSETS, filename)

        # Check if the file already exists
        if os.path.exists(user_picture_path):
            return jsonify({'error': 'User already exists.'}), 400        

        # Save the user's picture in the 'assets' folder
        try:
            cv2.imwrite(user_picture_path, frame)
        except Exception as e:
            return jsonify({'error': f'Failed to write file: {str(e)}'}), 500

        # Save the user registration information to the CSV file
        user_data_filename = os.path.join(ABSOLUTE_PATH_TO_ASSETS, 'user_data.csv')
        with open(user_data_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            if os.stat(user_data_filename).st_size == 0:  # Check if the file is empty
                writer.writerow(['Name', 'Email', 'Picture Path'])  # Write header only if file is empty
            writer.writerow([user_name, user_email, filename])

        camera.release()
        cv2.destroyAllWindows()

        return jsonify({'message': 'User registered successfully.'}), 200

    except Exception as e:
        print(f"Error in user registration: {str(e)}")
        return jsonify({'error': 'Internal server error.'}), 500


@app.route('/capture', methods=['GET'])
def capture():
    """
    Capture endpoint
    ---
    tags:
      - Capture
    responses:
      200:
        description: Successfully called capture endpoint
    """
    try:
        # Create the 'data' folder if it does not exist
        if not os.path.exists(ABSOLUTE_PATH_TO_DATA):
            os.makedirs(ABSOLUTE_PATH_TO_DATA)

        # Capture photo for verification
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()

        # Process the captured picture
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        names = []

        for face_encoding in face_encodings:
            # Compare each face in the captured picture with the face encoding of each student in the database
            matches = face_recognition.compare_faces(known_images, face_encoding)
            name = "Unknown"

            if True in matches:
                # If a match is found, use the detected name
                index = matches.index(True)
                name = known_names[index]
            names.append(name)

            # Draw a rectangle around the detected face
            top, right, bottom, left = face_locations[0]
            if name == "Unknown":
                color = (0, 0, 255)  # Red for unknown
            else:
                color = (0, 255, 0)  # Green for known
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Save the verification picture with an absolute path in the data folder
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y")

        for i, name in enumerate(set(names), start=1):
            if name != "Unknown":
                verification_filename = f"{timestamp}_{name}.jpg"
            else:
                counter = 1
                while True:
                    verification_filename = f"{timestamp}_unknown_{counter}.jpg"
                    verification_path = os.path.join(ABSOLUTE_PATH_TO_DATA, verification_filename)
                    
                    if not os.path.exists(verification_path):
                        break  # Break the loop when a unique filename is found
                    counter += 1

            verification_path = os.path.join(ABSOLUTE_PATH_TO_DATA, verification_filename)
            cv2.imwrite(verification_path, frame)

        # Save the attendance record
        attendance_filename = f"{timestamp}_attendance.csv"
        attendance_path = os.path.join(ABSOLUTE_PATH_TO_DATA, attendance_filename)

        # Check if the file already exists
        file_exists = os.path.exists(attendance_path)

        with open(attendance_path, 'a', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:  # Check if the file is empty
                writer.writerow(['Name', 'Timestamp'])  # Write header only if the file is empty

            for name in set(names):  # remove duplicates
                writer.writerow([name, timestamp])

        camera.release()
        cv2.destroyAllWindows()

        return jsonify({'message': 'Verification successful.', 'verification_filename': verification_filename}), 200

    except Exception as e:
        print(f"Error in verification: {str(e)}")
        return jsonify({'error': 'Internal server error during verification.'}), 500


@app.route('/attendance', methods=['GET'])
def get_attendance():
    """
    Attendance endpoint
    ---
    tags:
      - Attendance
    responses:
      200:
        description: Successfully called attendance endpoint
    """
    try:
        # Retrieve the <eventname>__attendance_dd_mm_yyyy.csv file for the day
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y")
        attendance_filename = f"{timestamp}_attendance.csv"
        attendance_path = os.path.join(ABSOLUTE_PATH_TO_DATA, attendance_filename)

        # Check if the file exists
        if not os.path.exists(attendance_path):
            return jsonify({'error': 'Attendance data not available for today.'}), 404

        # Create a response with the CSV data
        response = make_response(send_file(attendance_path, as_attachment=True))
        response.headers['Content-Disposition'] = f'attachment; filename={attendance_filename}'

        return response, 200

    except Exception as e:
        print(f"Error in attendance: {str(e)}")
        return jsonify({'error': 'Internal server error during attendance data retrieval.'}), 500


@app.route('/report', methods=['GET'])
def get_report():
    """
    Report endpoint
    ---
    tags:
      - Report
    responses:
      200:
        description: Successfully called report endpoint
    """
    try:
        # Retrieve the <eventname>__attendance_dd_mm_yyyy.csv file for the day
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y")
        attendance_filename = f"{timestamp}_attendance.csv"
        attendance_path = os.path.join(ABSOLUTE_PATH_TO_DATA, attendance_filename)

        # Check if the file exists
        if not os.path.exists(attendance_path):
            return jsonify({'error': 'Attendance data not available for today.'}), 404

        # Read in the attendance data from the CSV file
        with open(attendance_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # skip header row
            data = list(reader)

        # Count the number of occurrences of each student in the attendance data
        present_counts = {}
        unknown_count = 0

        for row in data:
            name = row[0]
            if name == 'Unknown':
                unknown_count += 1
            else:
                present_counts[name] = present_counts.get(name, 0) + 1

        # Extract the counts for each student and for unknowns
        students = sorted(present_counts.keys())
        present_values = [present_counts[name] for name in students]
        unknown_value = unknown_count

        # Create a histogram with Matplotlib
        fig, ax = plt.subplots()
        ax.bar(students + ['Unknown'], present_values + [unknown_value], color='green')
        ax.set_xlabel('Students')
        ax.set_ylabel('Number of times present')
        ax.set_title('Attendance Histogram')

        # Save the histogram image to a BytesIO buffer
        image_buffer = BytesIO()
        plt.savefig(image_buffer, format='png')
        image_buffer.seek(0)

        # Create a response with the histogram image
        response = make_response(send_file(image_buffer, mimetype='image/png'))
        response.headers['Content-Disposition'] = 'inline; filename=attendance_histogram.png'

        return response, 200

    except Exception as e:
        print(f"Error in report: {str(e)}")
        return jsonify({'error': 'Internal server error during report generation.'}), 500


@app.route('/get_event_config', methods=['GET'])
def get_event_config():
    try:
        config_path = 'event_config.json'  # Adjust the path based on your project structure
        if os.path.exists(config_path):
            return send_file(config_path, mimetype='application/json', as_attachment=True)
        else:
            return jsonify({'error': 'Config file not found.'}), 404

    except Exception as e:
        print(f"Error in get_event_config: {str(e)}")
        return jsonify({'error': 'Internal server error during config retrieval.'}), 500


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
