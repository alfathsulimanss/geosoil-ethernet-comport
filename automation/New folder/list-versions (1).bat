@echo off
REM List all available versions of uploaded files
REM Shows version numbers, upload dates, and file sizes

setlocal enabledelayedexpansion

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Optional: Set rclone path if not in PATH
set RCLONE_PATH=

REM Call the PowerShell script with list-only flag
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "!SCRIPT_DIR!download-from-gdrive-versioned.ps1" -ListVersionsOnly

pause
