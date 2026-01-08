@echo off
REM Change to project root (parent of scripts/)
cd /d "%~dp0\.."

echo ====================================
echo Multi-Agent Code Generator - Web UI
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with your configuration.
    echo See .env.example for reference.
    echo.
    pause
)

REM Install Python dependencies if needed
echo Checking Python dependencies...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    pip install -r backend\requirements.txt
)

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo ====================================
echo Starting servers...
echo ====================================
echo.
echo Backend API will run on: http://localhost:5000
echo Frontend UI will run on: http://localhost:3000
echo.
echo Press Ctrl+C in each window to stop the servers
echo.

REM Start backend in a new window
start "Backend API" cmd /k "python -m backend.api_server"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "Frontend UI" cmd /k "cd frontend && npm start"

echo.
echo Servers are starting...
echo The UI will open automatically in your browser.
echo.
pause
