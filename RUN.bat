@echo off
REM Darwin Log Compare - Auto Setup & Run
REM Double-click this file to automatically install dependencies and run the pipeline

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo.
echo ============================================================
echo   Darwin Log Compare - Auto Setup ^& Run
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo After installation, restart your computer and try again.
    echo.
    pause
    exit /b 1
)

REM Get the full path to Python
for /f "delims=" %%i in ('where python') do set PYTHON_PATH="%%i"
echo Python found at: %PYTHON_PATH%

REM Get current directory
cd /d "%~dp0"
echo Working directory: %cd%

REM Run the setup and execution script
echo.
echo Launching Darwin Log Compare...
echo.

%PYTHON_PATH% setup_and_run.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Pipeline execution failed!
    echo.
    echo Please check:
    echo 1. All input log files exist (SystemLog.csv, hl7Log.txt, sbxLog.xml, DoComLog.txt)
    echo 2. Python 3.8+ is installed
    echo 3. At least 500MB free disk space
    echo.
    pause
    exit /b 1
)

echo.
echo SUCCESS! Press any key to close this window...
pause
exit /b 0
