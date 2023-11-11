FROM python:slim

# Install Git
RUN apt-get update && apt-get install -y git

# Copy requirements.txt to the container
COPY requirements.txt /

# Install Python dependencies
RUN pip install -r /requirements.txt

# Copy the application code to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Define the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]