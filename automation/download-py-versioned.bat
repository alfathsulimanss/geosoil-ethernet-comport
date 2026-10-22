@echo off
REM Download GeoLogic files from Google Drive with version selection (Python)
REM Lists available versions and prompts you to choose which version to download

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   GeoLogic Download Versioned (Python)
echo ========================================
echo.

REM Detect Python installation (Laragon only)
set PYTHON_EXE=C:\laragon\bin\python\python.exe
set PIP_EXE=C:\laragon\bin\python\Scripts\pip.exe

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

echo Checking for version manifest...
if not exist "version-manifest.json" (
    echo ERROR: version-manifest.json not found!
    echo Please run the upload script first to create the version manifest.
    pause
    exit /b 1
)

echo ✓ Version manifest found
echo.
echo Starting download...
echo.

"!PYTHON_EXE!" download_versioned.py --config config.json

if %ERRORLEVEL%==0 (
    echo.
    echo ✓ Download completed successfully!
) else (
    echo.
    echo ✗ Download failed with error code: %ERRORLEVEL%
)

echo.
pause
