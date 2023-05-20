# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app source code to the working directory
COPY . .

# Expose the port that the Flask app listens on (replace 5000 with your app's port if necessary)
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=main.py

# Run the Flask app when the container launches
CMD ["flask", "run", "--host", "0.0.0.0"]