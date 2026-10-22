@echo off
REM Upload build files to Google Drive with versioning
REM Creates sequential versions (v001, v002, etc.) of each file
REM Automatically removes versions older than 30 days

setlocal enabledelayedexpansion

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Optional: Set rclone path if not in PATH
set RCLONE_PATH=

REM Call the PowerShell script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "!SCRIPT_DIR!upload-to-gdrive-versioned.ps1"

pause
