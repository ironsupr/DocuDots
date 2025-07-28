# Adobe India Hackathon - Challenge 1A
# PDF Structure Analysis Tool
# Python 3.11 on linux/amd64 with PyMuPDF

# Use Python 3.11 slim image as base for smaller size and better performance
FROM --platform=linux/amd64 python:3.11-slim

# Set environment variables to optimize Python runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for PyMuPDF
# - build-essential: Compilation tools for building packages
# - libffi-dev: Foreign Function Interface library development files
# - libssl-dev: SSL/TLS library development files
# - python3-dev: Python development headers
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create the input and output directories with proper permissions
# These directories will be mounted or used for file I/O operations
RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output

# Copy requirements file first to leverage Docker layer caching
# This allows pip install to be cached if requirements don't change
COPY requirements.txt /app/

# Install Python dependencies
# --no-cache-dir: Don't cache downloaded packages to reduce image size
# --upgrade: Ensure latest compatible versions are installed
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire source code to the container
# This is done after pip install to optimize build cache usage
COPY . /app/

# Set the default command to run the main application
# This will process all PDFs in /app/input and generate JSON files in /app/output
CMD ["python", "src/main.py"]

# Optional: Expose port if you plan to add a web interface later
# EXPOSE 8000

# Optional: Add health check to monitor container status
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)"
