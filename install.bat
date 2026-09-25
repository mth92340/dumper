@echo off
title NO1 / No1 FXAP - Setup
color 0B
cls

echo ========================================
echo        NO1   /   NO1 FXAP
echo        Setup & Install Requirements
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Python not found. Please install Python 3.x and add it to PATH.
    pause
    exit /b
)

echo [*] Upgrading pip...
python -m pip install --upgrade pip

echo [*] Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ========================================
echo   Setup completed successfully! 🎉
echo   You can now run: a.bat
echo ========================================
echo.

pause
