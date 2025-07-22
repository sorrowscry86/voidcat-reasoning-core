@echo off
setlocal

:: ========================================================
::   VoidCat Reasoning Core - Enhanced MCP Launcher
:: ========================================================

:: Set the project directory to where the batch file is located
set "PROJECT_DIR=%~dp0"
cd /D "%PROJECT_DIR%"

:: Set the path to your Python executable
set "PYTHON_EXE=python"

:: Set the name of the virtual environment directory
set "VENV_DIR=.venv"

echo ======================================================== 1>&2
echo   VoidCat Reasoning Core - Enhanced MCP Launcher 1>&2
echo ======================================================== 1>&2

:: Check if the virtual environment exists. If not, create it.
if not exist "%VENV_DIR%\Scripts\activate" (
    echo Creating Python virtual environment... 1>&2
    "%PYTHON_EXE%" -m venv "%VENV_DIR%" 1>&2
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment. 1>&2
        pause
        exit /b 1
    )
)

:: Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

echo Checking and installing dependencies... 1>&2
:: Install dependencies from requirements.txt
:: IMPORTANT: Redirect pip's output to STDERR to avoid polluting STDOUT
pip install -r requirements.txt 1>&2

echo Launching VoidCat MCP Server... 1>&2
echo Press Ctrl+C to stop the server 1>&2
echo ======================================================== 1>&2

:: Run the server. It will now find its local modules and have all dependencies.
python mcp_server.py

if %errorlevel% neq 0 (
    echo. 1>&2
    echo ERROR: MCP server exited with code %errorlevel%. 1>&2
)

endlocal