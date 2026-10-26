# Start MUQ Project
Write-Host "Starting MUQ Project..." -ForegroundColor Green

# Start Django Backend
Write-Host "Starting Django Backend on port 8000..." -ForegroundColor Yellow
$backendJob = Start-Process -FilePath "python" -ArgumentList "manage.py","runserver" -WorkingDirectory "F:\MUQ\backend" -NoNewWindow -PassThru

# Start Frontend
Write-Host "Starting Frontend on port 58272..." -ForegroundColor Yellow
$frontendJob = Start-Process -FilePath "python" -ArgumentList "-m","http.server","58272" -WorkingDirectory "F:\MUQ\frontend" -NoNewWindow -PassThru

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Django Backend: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://127.0.0.1:58272" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Wait for jobs
Wait-Process -Id $backendJob.Id
Wait-Process -Id $frontendJob.Id
