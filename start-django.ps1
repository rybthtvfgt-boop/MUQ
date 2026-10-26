# Start Django Backend
Write-Host "Starting Django Backend..." -ForegroundColor Green

cd backend

# Check if admin exists
Write-Host "Checking admin user..." -ForegroundColor Yellow
python check_admin.py

# Start server
Write-Host "Starting Django server on http://localhost:8000" -ForegroundColor Green
Write-Host "Login with: admin / admin123" -ForegroundColor Cyan
python manage.py runserver 0.0.0.0:8000
