@echo off
echo ========================================
echo MUQ Project - Railway Deployment Setup
echo ========================================
echo.

echo Step 1: Checking Git status...
git status
echo.

echo Step 2: Adding all files...
git add .
echo.

echo Step 3: Committing changes...
git commit -m "Prepare for Railway deployment - add deployment configs and scripts"
echo.

echo Step 4: Checking remote...
git remote -v
echo.

echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. If no remote is set, run:
echo    git remote add origin https://github.com/YOUR_USERNAME/muq-system.git
echo.
echo 2. Push to GitHub:
echo    git push -u origin main
echo.
echo 3. Go to https://railway.app/new
echo 4. Click "Deploy from GitHub repo"
echo 5. Select your muq-system repository
echo 6. Railway will auto-detect railway.yaml
echo.
echo 7. Add environment variables in Railway:
echo    - DEBUG = False
echo    - SECRET_KEY = (generate a strong key)
echo    - ALLOWED_HOSTS = .railway-app,.vercel.app
echo    - CORS_ALLOWED_ORIGINS = https://*.railway.app,https://*.vercel.app
echo    - ADMIN_PASSWORD = (strong password)
echo.
echo 8. Run migrations in Railway:
echo    python manage.py migrate --noinput
echo.
echo 9. Create admin user:
echo    python manage.py shell < create_admin_production.py
echo.
echo For detailed guide, see: RAILWAY_DEPLOYMENT_GUIDE.md
echo ========================================
pause
