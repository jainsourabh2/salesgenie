# Use an official lightweight Python image as a base image.
# python:3.11-slim-buster is a good choice for smaller image size.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Create and set the working directory
WORKDIR $APP_HOME

# Copy the requirements file into the container at $APP_HOME
COPY requirements.txt .
COPY config.json .

# Install Python dependencies, including Flask and Gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY main.py .

# Expose the port that Cloud Run expects.
# The application uses the PORT environment variable set by Cloud Run.
EXPOSE 8080

# Run the web service using Gunicorn.
# The format is: gunicorn [OPTIONS] [APP_MODULE]:[APP_INSTANCE]
# - 'main:app' references the 'app' variable in 'main.py'
# - '--bind 0.0.0.0:$PORT' makes it listen on the port provided by Cloud Run
# - '--workers 2' is a good starting point for concurrency
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 main:app
