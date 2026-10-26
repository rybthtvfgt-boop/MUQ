@echo off
cd backend
echo Initializing MUQ Database...
echo.
python init_db.py
echo.
echo Database setup completed!
echo Username: admin
echo Password: admin123
echo.
pause
