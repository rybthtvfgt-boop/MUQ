@echo off
cd /d F:\MUQ\backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
