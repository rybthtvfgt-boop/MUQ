FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for OpenCV and ML libraries
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt from root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose port 8080
EXPOSE 8080

# Run the Flask app using Gunicorn on port 8080 (Railway can override with PORT)
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 app:app
