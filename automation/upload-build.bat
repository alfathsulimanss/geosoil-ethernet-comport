@echo off
REM Batch script to automate upload after LabVIEW build
REM This script should be run after building the EXE in LabVIEW

setlocal EnableDelayedExpansion

echo ========================================
echo   GeoLogic Build Upload Automation
echo ========================================
echo.

REM Set paths
set "BUILD_PATH=C:\Users\ralfsuliman\Desktop\EXE\GEOSOIL Ausie"
set "PROJECT_PATH=%~dp0.."
set "SCRIPT_PATH=%~dp0upload-to-gdrive.ps1"

echo Build Path: %BUILD_PATH%
echo Project Path: %PROJECT_PATH%
echo Script Path: %SCRIPT_PATH%
echo.

REM Check if build output exists
if not exist "%BUILD_PATH%\GeoLogic.exe" (
    echo ERROR: GeoLogic.exe not found in build directory!
    echo Please build the application first using LabVIEW.
    echo Expected location: %BUILD_PATH%\GeoLogic.exe
    pause
    exit /b 1
)

echo ✓ Found GeoLogic.exe in build directory
echo.

REM Check if PowerShell script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: PowerShell upload script not found!
    echo Expected location: %SCRIPT_PATH%
    pause
    exit /b 1
)

echo ✓ Found PowerShell upload script
echo.

REM Check for aliases file
REM Ensure we join paths correctly (PROJECT_PATH does not include trailing backslash)
if not exist "%PROJECT_PATH%\GEOSOIL New Ethernet.aliases" (
    echo WARNING: Aliases file not found in project directory
) else (
    echo ✓ Found aliases file
)

REM Check for INI files in build directory
set "INI_COUNT=0"
for %%f in ("%BUILD_PATH%\*.ini") do (
    if exist "%%f" (
        set /a INI_COUNT+=1
        echo ✓ Found INI file: %%~nxf
    )
)

if %INI_COUNT%==0 (
    echo WARNING: No INI files found in build directory
)

echo.
echo Starting upload process...
echo.

REM Execute PowerShell script
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

powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_PATH%" -BuildPath "%BUILD_PATH%" -ProjectPath "%PROJECT_PATH%" %RCLONE_ARG% -RcloneRemote "geosoilgdrive"

if %ERRORLEVEL%==0 (
    echo.
    echo ✓ Upload completed successfully!
) else (
    echo.
    echo ✗ Upload failed with error code: %ERRORLEVEL%
)

echo.
echo Press any key to continue...
pause >nul