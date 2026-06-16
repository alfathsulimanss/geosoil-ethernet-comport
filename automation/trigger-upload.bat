@echo off
REM Simple upload trigger for LabVIEW integration
REM This can be called from LabVIEW using System Exec.vi

echo Starting upload process...
cd /d "%~dp0"

REM Check if main upload script exists
if exist "upload-build.bat" (
    call upload-build.bat
) else (
    echo ERROR: upload-build.bat not found!
    exit /b 1
)

REM Return success/failure code for LabVIEW
exit /b %ERRORLEVEL%