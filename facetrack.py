import cv2
import face_recognition
import numpy as np
import csv
from datetime import datetime
import os
import matplotlib.pyplot as plt


# Define number of students and load images for training
num_students = 3
folder_path = 'assets'
known_images = []
known_names = []

for filename in os.listdir(folder_path):
    if filename.endswith('.jpg'):
        image = face_recognition.load_image_file(os.path.join(folder_path, filename))
        encoding = face_recognition.face_encodings(image)[0]
        known_images.append(encoding)
        known_names.append(os.path.splitext(filename)[0])

# Capture a picture
camera = cv2.VideoCapture(0)
ret, frame = camera.read()
if ret:
    # Pause for face detection
    cv2.waitKey(6000)

    # Process the captured picture
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    names = []
    for face_encoding in face_encodings:
        # Compare each face in the captured picture with the face encoding of each student in the database
        matches = face_recognition.compare_faces(known_images, face_encoding)
        name = "Unknown"
        if True in matches:
            # If a match is found, mark them as present in the attendance record
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

    # Save the attendance record
    now = datetime.now()
    timestamp = now.strftime("%H-%M-%S_%b-%d-%Y")
    attendance_filename = f"attendance_{timestamp}.csv"
    with open(attendance_filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Timestamp'])
        for name in set(names): # remove duplicates
            if name != "Unknown":
                writer.writerow([name, timestamp])
            else:
                writer.writerow([name, timestamp])                
#                writer.writerow([name, timestamp + " - Unidentified"])

    # Save the captured picture with rectangles
    image_filename = f"attendance_{timestamp}.jpg"
    cv2.imwrite(image_filename, frame)

    # Display the captured picture with rectangles
    cv2.imshow('Attendance Record', frame)
    cv2.waitKey(0)

    # Read in the attendance data from the CSV file
    with open(attendance_filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        data = list(reader)

    # Convert the timestamp strings to datetime objects
    timestamps = [datetime.strptime(row[1], '%H-%M-%S_%b-%d-%Y') for row in data]

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
    plt.xticks(rotation=45, ha='right')
    plt.show()    

camera.release()
cv2.destroyAllWindows()


