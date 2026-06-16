@echo off
REM Quick launcher for download automation
REM This script is already in the automation directory

echo.
echo ========================================
echo   GeoLogic Download Automation Launcher
echo ========================================
echo.

if not exist "download-build.bat" (
    echo ERROR: Download scripts not found!
    echo Please ensure the automation folder exists with the required scripts.
    pause
    exit /b 1
)

echo Launching download automation...
echo.

REM Call the main download script
call download-build.bat

echo.
echo Download automation completed.
pause