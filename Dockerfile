# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Accept APP_PORT as a build argument
ARG APP_PORT
ENV APP_PORT=${APP_PORT}

# Expose the application port
EXPOSE ${APP_PORT}

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
