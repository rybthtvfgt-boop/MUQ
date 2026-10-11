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

# Run the Flask app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "ml_backend:ml_backend"]
