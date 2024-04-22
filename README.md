# FaceTrack - Face Recognition Program

## Overview

The FaceTrack system utilizes facial recognition to identify students and track attendance in a class. This README provides an overview of the functionalities available to users.
<img width="712" alt="Screenshot 2024-04-21 at 8 27 25 PM" src="https://github.com/sparksavior/FaceTrack/assets/127971233/2f11a355-25e4-43e2-9e29-02f9b0aa8dd3">

## Features

- Simplifies attendance tracking for various sectors.
- Reduces workload for administrative staff.
- Applicable in educational institutions, companies, and border security.
- Generates quick and real-time attendance reports.

## Requirements

- Python 3.6 or higher
- OpenCV library
- face-recognition library
- numpy library

## Installation

1. Clone the repository to your local machine.
2. Install required libraries using the command: `pip install -r requirements.txt`.
3. Add student or employee photos to the `assets` folder. Each photo should be named with the person's name (e.g., John.jpg).
4. Run the program using the command: `python facetrack.py`.

## Configuration

- The `event_config.json` file is used to configure settings for different events. Adjust the configurations as needed.

## Environment Variables

- Set the following environment variables for the Flask app:
  - `ABSOLUTE_PATH_TO_ASSETS`: Absolute path to the 'assets' folder.
  - `ABSOLUTE_PATH_TO_DATA`: Absolute path to the 'data' folder.

## Usage

The system provides the following functionalities:

### 1. Event Information

- Event details are dynamically loaded from the `event_config.json` file.
- Information includes the event name, description, and additional details.

### 2. User Registration

- Users can register for the event by providing their full name and email.
- Click the "User Registration" button to submit registration details.

### 3. Verification

- The "Verification" button initiates the face recognition process.
- Detected faces are marked with a red rectangle on the camera feed.

### 4. Attendance

- Clicking the "Attendance" button triggers the retrieval of attendance data.
- The data is available as a downloadable CSV file named `attendance.csv`.

### 5. Report

- The "Report" button fetches the attendance report.
- The report is available as a downloadable PNG file named `attendance_report.png`.

## API Documentation

Explore the Swagger API documentation for the FaceTrack program: [Swagger API Link](http://localhost/apidocs).

## Python Virtual Environment

It is recommended to use a Python virtual environment. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
