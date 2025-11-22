# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .


# Copy SSL certificates
COPY cert.pem cert.pem
COPY key.pem key.pem
# Copy Baltimore CyberTrust Root CA for Azure IoT Hub
COPY baltimore_cybertrust_root.pem baltimore_cybertrust_root.pem

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "run.py"]
