# LabVIEW Test Data Display Launcher (PowerShell)
# Alternative to display.bat
# Usage: .\display.ps1 -FileID 1 -StageName "Stage 1"

param(
    [Parameter(Mandatory=$true)]
    [string]$FileID,
    
    [Parameter(Mandatory=$true)]
    [string]$StageName
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Build the full path to main.py
$PythonScript = Join-Path $ScriptDir "main.py"

# Run the Python application
try {
    # Run in a new window (non-blocking)
    Start-Process python -ArgumentList "`"$PythonScript`" `"$FileID`" `"$StageName`"" -WorkingDirectory $ScriptDir
    
    # Exit with success code
    exit 0
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
