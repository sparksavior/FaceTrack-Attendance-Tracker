# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
# COPY . /app

# Create and activate a virtual environment
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate"

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the HTML page into the container
COPY templates/index.html /app/templates/index.html

# Copy the Swagger YAML file into the container
COPY swagger.yaml /app/swagger.yaml

# Copy Event config json file into the container
COPY event_config.json /app/event_config.json

# Copy facetrack file into the container
COPY facetrack.py /app/facetrack.py

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Set environment variable for the base URL
ENV BASE_URL=http://localhost:3000

# Set environment variable for the assets folder
ENV ABSOLUTE_PATH_TO_ASSETS="D:\\c-downloads\\facetrack\\v3\\assets"

# Set environment variable for the data folder
ENV ABSOLUTE_PATH_TO_DATA="D:\\c-downloads\\facetrack\\v3\\data"

# Run facetrack.py and the Flask web server when the container launches
CMD ["python", "./facetrack.py"]
