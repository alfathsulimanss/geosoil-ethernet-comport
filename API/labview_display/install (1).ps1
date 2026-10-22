# PowerShell script to install dependencies
# Run as Administrator for best results
# Usage: .\install.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "LabVIEW Test Data Display Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.7+ first." -ForegroundColor Red
    exit 1
}

# Check current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$requirementsFile = Join-Path $scriptPath "requirements.txt"

if (-not (Test-Path $requirementsFile)) {
    Write-Host "✗ requirements.txt not found in $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow

# Install requirements
pip install -r $requirementsFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✓ Installation completed!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run test: python test_install.py" -ForegroundColor White
    Write-Host "2. Check database connection is working" -ForegroundColor White
    Write-Host "3. Call from LabVIEW: display.bat <fileid> <stage_name>" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Installation failed" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Red
    exit 1
}
