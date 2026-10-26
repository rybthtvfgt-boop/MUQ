@echo off
echo ===================================================
echo MUQ Professional Training System - Installation
echo ===================================================
echo.
echo This will install the professional AI training system.
echo CPU Only - High Accuracy Image Classification
echo.
pause

cd professional_training
call install.bat

echo.
echo ===================================================
echo Installation Completed!
echo ===================================================
echo.
echo To start training:
echo   cd professional_training
echo   python train.py
echo.
echo For more information, see professional_training/README.md
echo.
pause
