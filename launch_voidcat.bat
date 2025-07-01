@echo off
REM VoidCat Reasoning Core - Windows Launcher
REM Strategic deployment automation for Lord Wykeve
REM Author: Albedo, Overseer of the Digital Scriptorium

echo.
echo ================================================
echo   🛡️ VOIDCAT REASONING CORE LAUNCHER
echo ================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH
    echo Please install Python 3.13+ and try again
    pause
    exit /b 1
)

REM Launch VoidCat system
echo 🚀 Launching VoidCat Reasoning Core...
echo.

python voidcat_launcher.py

echo.
echo 🛡️ VoidCat deployment session complete
pause
