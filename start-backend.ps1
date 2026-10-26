# Start Django Backend
Write-Host "Starting Django Backend..." -ForegroundColor Green

cd backend

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Run migrations
Write-Host "Running migrations..." -ForegroundColor Yellow
python manage.py migrate

# Create admin if not exists
Write-Host "Creating admin user..." -ForegroundColor Yellow
python create_admin.py

# Start server
Write-Host "Starting Django server on http://localhost:8000" -ForegroundColor Green
python manage.py runserver
