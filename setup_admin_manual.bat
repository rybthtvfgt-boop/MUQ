@echo off
cd F:\MUQ\backend
echo ========================================
echo تنظيف مستخدم Admin
echo ========================================
echo.
echo جاري حذف قاعدة البيانات القديمة...
del db.sqlite3
echo.
echo جاري تشغيل migrations...
python manage.py migrate
echo.
echo جاري إنشاء مستخدم admin...
python users\management\commands\create_admin.py
echo.
echo تم! 
echo Username: admin
echo Password: admin123
echo.
pause