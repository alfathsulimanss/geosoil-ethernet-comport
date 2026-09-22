@echo off
REM Batch script to download files from Google Drive
REM This script should be run on the target PC where you want to install the files

setlocal EnableDelayedExpansion

echo ========================================
echo   GeoLogic Download Automation  
echo ========================================
echo.

REM Default destination paths - EDIT THESE for your target PC
REM Note: To install to Program Files, run this script as Administrator
set "EXE_DEST=%USERPROFILE%\Documents\GeoLogic\GeoLogic.exe"
set "ALIASES_DEST=%USERPROFILE%\Documents\GeoLogic\GeoLogic.aliases"
set "INI_DEST=%USERPROFILE%\Documents\GeoLogic\GeoLogic.ini"

REM Set script path
set "SCRIPT_PATH=%~dp0download-from-gdrive.ps1"

echo Download destinations:
echo   EXE: %EXE_DEST%
echo   Aliases: %ALIASES_DEST%
echo   INI: %INI_DEST%
echo.

REM Check if PowerShell script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: PowerShell download script not found!
    echo Expected location: %SCRIPT_PATH%
    pause
    exit /b 1
)

echo ✓ Found PowerShell download script
echo.

REM Auto-detect rclone if RCLONE_PATH is not explicitly set
set "RCLONE_ARG="
if not defined RCLONE_PATH (
    REM Try to find rclone on PATH
    for /f "usebackq tokens=*" %%I in (`where rclone 2^>nul`) do set "RCLONE_PATH=%%~I"
)
if not defined RCLONE_PATH (
    REM Common install locations - try a few likely candidates
    if exist "F:\rclone-v1.71.1-windows-amd64\rclone.exe" set "RCLONE_PATH=F:\rclone-v1.71.1-windows-amd64\rclone.exe"
)
if not defined RCLONE_PATH (
    if exist "%ProgramFiles%\rclone\rclone.exe" set "RCLONE_PATH=%ProgramFiles%\rclone\rclone.exe"
)
if not defined RCLONE_PATH (
    if exist "%ProgramFiles(x86)%\rclone\rclone.exe" set "RCLONE_PATH=%ProgramFiles(x86)%\rclone\rclone.exe"
)
if not defined RCLONE_PATH (
    if exist "%USERPROFILE%\scoop\apps\rclone\current\rclone.exe" set "RCLONE_PATH=%USERPROFILE%\scoop\apps\rclone\current\rclone.exe"
)

if defined RCLONE_PATH (
    set "RCLONE_ARG=-RclonePath \"%RCLONE_PATH%\""
    echo Using rclone: %RCLONE_PATH%
)

echo.
echo Starting download process...
echo.

REM Execute PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_PATH%" -ExeDestination "%EXE_DEST%" -AliasesDestination "%ALIASES_DEST%" -IniDestination "%INI_DEST%" %RCLONE_ARG% -RcloneRemote "geosoilgdrive"

if %ERRORLEVEL%==0 (
    echo.
    echo ✓ Download completed successfully!
) else (
    echo.
    echo ✗ Download failed with error code: %ERRORLEVEL%
)

echo.