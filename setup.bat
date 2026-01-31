@echo off
REM Bike Equipment Tracker Setup Script for Windows

echo ==========================================
echo Bike Equipment Tracker - Setup Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    
    echo [OK] .env file created
    echo.
    echo WARNING: You need to add your Strava API credentials to the .env file
    echo.
    echo Please follow these steps:
    echo 1. Go to https://www.strava.com/settings/api
    echo 2. Create a new application
    echo 3. Copy your Client ID and Client Secret
    echo 4. Edit the .env file and replace:
    echo    - STRAVA_CLIENT_ID=your-strava-client-id
    echo    - STRAVA_CLIENT_SECRET=your-strava-client-secret
    echo.
    echo Also, generate a secure secret key and replace FLASK_SECRET_KEY
    echo.
) else (
    echo [OK] .env file already exists
    echo.
)

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo 1. Make sure your Strava credentials are in the .env file
echo 2. Activate the virtual environment: venv\Scripts\activate.bat
echo 3. Run the application: python app.py
echo 4. Open your browser to: http://localhost:5000
echo.
pause

