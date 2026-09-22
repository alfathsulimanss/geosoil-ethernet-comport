@echo off
REM Download latest versions without prompting
REM Use this if you always want the latest version

setlocal enabledelayedexpansion

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Optional: Set rclone path if not in PATH
set RCLONE_PATH=

REM Call the PowerShell script with explicit "latest" version
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "!SCRIPT_DIR!download-from-gdrive-versioned.ps1" -VersionToDownload "latest"

pause
