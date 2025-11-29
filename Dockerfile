# Dockerfile for Racing Club Django App with PostgreSQL
# Based on Ubuntu 22.04

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Update package list and install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql-client \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python command
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements file first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt && cat requirements.txt

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/logs /app/media /app/data

# Set proper permissions
RUN chmod +x /app/docker-entrypoint.sh

# Expose port 8000
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
