@echo off
REM Installation and Setup Helper for LabVIEW Test Data Display
REM Run this batch file to set up the environment

setlocal enabledelayedexpansion

echo.
echo ========================================
echo LabVIEW Test Data Display Setup Helper
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo.

REM Install dependencies
echo Installing Python packages...
echo This may take a few minutes...
echo.

pip install -r "%SCRIPT_DIR%requirements.txt" >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install packages
    echo Run this manually:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Done installing packages.
echo.

REM Run test
echo Running installation test...
echo.

python "%SCRIPT_DIR%test_install.py"

if errorlevel 1 (
    echo.
    echo Installation test found issues.
    echo Please fix them before proceeding.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now call from LabVIEW using:
echo   %SCRIPT_DIR%display.bat ^<fileid^> "^<stagename^>"
echo.
echo Example:
echo   %SCRIPT_DIR%display.bat 1 "Stage 1"
echo.
echo See README.md and LABVIEW_GUIDE.md for more information.
echo.
pause
