# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install Git
# RUN apt-get update && apt-get install -y git

# Install build tools and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements.txt to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code to the container
COPY . .

# Set the working directory

EXPOSE 8000

EXPOSE 3100


# Define the command to run the application
CMD ["gunicorn", "main:app"]