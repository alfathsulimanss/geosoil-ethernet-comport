@echo off
REM Quick launcher for upload automation
REM Run this from the project root directory

echo.
echo ========================================
echo   GeoLogic Upload Automation Launcher
echo ========================================
echo.

REM Change to automation directory
cd /d "%~dp0automation"

if not exist "upload-build.bat" (
    echo ERROR: Automation scripts not found!
    echo Please ensure the automation folder exists with the required scripts.
    pause
    exit /b 1
)

echo Launching upload automation from automation folder...
echo.

REM Call the main upload script
call upload-build.bat

echo.
echo Returning to project root directory...
cd /d "%~dp0"

echo.
echo Upload automation completed.
pause