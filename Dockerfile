FROM python:3.11-slim

WORKDIR /app

# Copy mysql directory
COPY mysql ./mysql

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080
EXPOSE 8080

# Run the Flask app
CMD cd mysql && python database.py
