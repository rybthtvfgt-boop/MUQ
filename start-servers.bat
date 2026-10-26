@echo off
echo Starting MUQ Project Servers...
echo.

echo Starting Django Backend...
start "Django Backend" /D F:\MUQ\backend python manage.py runserver

echo Starting Frontend...
start "Frontend" /D F:\MUQ\frontend python -m http.server 58272

echo.
echo Servers started!
echo Django: http://localhost:8000
echo Frontend: http://127.0.0.1:58272
echo.
pause
