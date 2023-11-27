# syntax=docker/dockerfile:1
FROM python

WORKDIR /app

# Install Git

# Copy requirements.txt to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code to the container
COPY . .

# Set the working directory

EXPOSE 3100

# Define the command to run the application
CMD ["gunicorn", "main:app"]