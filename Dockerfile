FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt from root
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose port
EXPOSE 5000

# Run the Flask app directly from mysql/database.py
CMD ["python", "mysql/database.py"]
