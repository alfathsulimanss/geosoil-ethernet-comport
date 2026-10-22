@echo off
REM Upload GeoLogic build files to Google Drive with versioning (Python)
REM Works with both Laragon Python and system Python
REM Creates sequential versions (v001, v002, etc.) of each file

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   GeoLogic Upload Versioned (Python)
echo ========================================
echo.

REM Detect Python installation (Laragon only)
set PYTHON_EXE=F:\laragon\bin\python\python-3.13\python.exe
set PIP_EXE=F:\laragon\bin\python\python-3.13\Scripts\pip.exe

REM Check if Laragon Python exists
if not exist "!PYTHON_EXE!" (
    echo ERROR: Laragon Python not found at !PYTHON_EXE!
    echo Please install Laragon: https://laragon.org/
    pause
    exit /b 1
)

echo ✓ Using Laragon Python: !PYTHON_EXE!

echo Checking for required Python packages...
"!PYTHON_EXE!" -c "import googleapiclient, google_auth_oauthlib" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Required Python packages not found.
    echo Installing dependencies...
    "!PIP_EXE!" install google-api-python-client google-auth-httplib2 google-auth-oauthlib
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Checking for config.json...
if not exist "config.json" (
    echo ERROR: config.json not found!
    echo Please create config.json with your Google Drive settings.
    echo See QUICK_START.md for instructions.
    pause
    exit /b 1
)

echo ✓ Configuration file found
echo.
echo Checking for credentials.json...
if not exist "credentials.json" (
    echo WARNING: credentials.json not found!
    echo You will need to authenticate on first run.
    echo See QUICK_START.md for setup instructions.
    echo.
)

echo Starting upload...
echo.

"!PYTHON_EXE!" upload_versioned.py --config config.json

if %ERRORLEVEL%==0 (
    echo.
    echo ✓ Upload completed successfully!
) else (
    echo.
    echo ✗ Upload failed with error code: %ERRORLEVEL%
)

echo.
pause
