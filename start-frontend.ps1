# Start MUQ Frontend
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "MUQ System - Starting Frontend" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

cd F:\MUQ\frontend

# Start server
Write-Host "Starting frontend server on http://localhost:8010" -ForegroundColor Green
python -m http.server 8010
