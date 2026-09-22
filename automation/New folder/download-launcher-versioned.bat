@echo off
REM Download files from Google Drive with version selection
REM Lists available versions and prompts you to choose which version to download

setlocal enabledelayedexpansion

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Optional: Set rclone path if not in PATH
set RCLONE_PATH=

REM Call the PowerShell script (interactive mode - user will be prompted to choose version)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "!SCRIPT_DIR!download-from-gdrive-versioned.ps1"

pause
