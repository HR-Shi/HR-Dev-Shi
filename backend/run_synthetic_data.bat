@echo off
echo 🎯 HR Dashboard - Synthetic Data Generator
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Install required packages
echo 📦 Installing required packages...
pip install -r requirements_synthetic.txt

echo.
echo 🚀 Starting synthetic data generation...
echo.

REM Run the synthetic data generator
python generate_synthetic_data.py

echo.
echo ✅ Data generation completed!
echo You can now access your HR Dashboard with realistic data
pause 