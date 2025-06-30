@echo off
echo ==========================================
echo HR System - Admin Setup Script
echo ==========================================
echo.
echo This will create admin users and fix authentication issues.
echo.
pause

cd backend
python create_admin_simple.py

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
pause 