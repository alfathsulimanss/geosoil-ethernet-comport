@echo off
REM LabVIEW Test Data Display Launcher
REM Usage: display.bat <fileid> <stage_name>
REM Example: display.bat 1 "Stage 1"

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Error: fileid parameter is missing
    echo Usage: display.bat fileid stage_name
    echo Example: display.bat 1 "Stage 1"
    pause
    exit /b 1
)

if "%2"=="" (
    echo Error: stage_name parameter is missing
    echo Usage: display.bat fileid stage_name
    echo Example: display.bat 1 "Stage 1"
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Run the Python script with the provided arguments
python "%SCRIPT_DIR%main.py" %1 %2

REM Exit with the same exit code as Python
exit /b %errorlevel%
