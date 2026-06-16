# PowerShell Script to Upload Files to Google Drive
# This script uploads the built EXE, aliases, and INI files to Google Drive

param(
    [string]$BuildPath = "C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm",
    [string]$ProjectPath = "f:\Geosoil Drive\geosoil-ethernet-comport",
    [string]$RclonePath = "",
    [string]$RcloneRemote = "geosoilgdrive"
)

Write-Host "Starting upload process..."
Write-Host "Build Path: $BuildPath"
Write-Host "Project Path: $ProjectPath"
if ($RclonePath) {
    $trimmed = $RclonePath.Trim('"')
    if ($trimmed -ne $RclonePath) {
        Write-Host "Trimmed RclonePath to: '$trimmed'"
        $RclonePath = $trimmed
    }
}

# Files to upload
$FilesToUpload = @()

# Add EXE file
$exePath = "$BuildPath\GeoLogic.exe"
if (Test-Path $exePath) {
    $FilesToUpload += @{
        LocalPath = $exePath
        RemoteName = "GeoLogic.exe"
        Description = "GeoLogic Application Executable"
    }
}

# Add aliases file
$aliasesPath = "$BuildPath\GeoLogic.aliases"
if (Test-Path $aliasesPath) {
    $FilesToUpload += @{
        LocalPath = $aliasesPath
        RemoteName = "GeoLogic.aliases"
        Description = "LabVIEW Aliases File"
    }
}

# Check for INI files
$IniFiles = "$BuildPath\GeoLogic.ini"
if (Test-Path $IniFiles) {
    $FilesToUpload += @{
        LocalPath = $IniFiles
        RemoteName = "GeoLogic.ini"
        Description = "Configuration INI File"
    }
}

# Function to upload file using rclone
function Upload-UsingRclone {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )
    
    # Resolve rclone executable
    function Resolve-Rclone {
        param([string]$ExplicitPath)
        if ($ExplicitPath -and (Test-Path $ExplicitPath)) { return $ExplicitPath }
        $cmd = Get-Command rclone -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
        $candidates = @(
            "$env:ProgramFiles\rclone\rclone.exe",
            "$env:ProgramFiles(x86)\rclone\rclone.exe",
            "$env:USERPROFILE\scoop\apps\rclone\current\rclone.exe",
            "$env:USERPROFILE\bin\rclone.exe"
        )
        foreach ($p in $candidates) {
            if ($p -and (Test-Path $p)) { return $p }
        }
        return $null
    }

    try {
        if (-not (Test-Path $LocalPath)) {
            Write-Warning "File not found: $LocalPath"
            return $false
        }

        $rcloneExe = Resolve-Rclone -ExplicitPath $RclonePath
        if (-not $rcloneExe) {
            Write-Warning "rclone not found on PATH or in common locations. Please install rclone or set RclonePath param."
            return $false
        }

    # Prepare logs (robustly find script root)
    $scriptRoot = $PSScriptRoot
    if (-not $scriptRoot) {
        $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
    }
    $logsDir = Join-Path -Path $scriptRoot -ChildPath 'logs'
    if (-not (Test-Path $logsDir)) { New-Item -Path $logsDir -ItemType Directory | Out-Null }
    $ts = (Get-Date).ToString('yyyyMMdd-HHmmss')
    $stdout = Join-Path $logsDir ("rclone-$ts-out.log")
    $stderr = Join-Path $logsDir ("rclone-$ts-err.log")

    # Ensure files exist to avoid RedirectStandardOutput errors
    try { New-Item -Path $stdout -ItemType File -Force | Out-Null } catch { }
    try { New-Item -Path $stderr -ItemType File -Force | Out-Null } catch { }

    # Build remote spec safely to avoid variable parsing issues (e.g. ${RcloneRemote}:path)
    $remoteSpec = "${RcloneRemote}:$RemotePath"
    # Use copyto to write the exact file path on the remote (prevents rclone creating a folder with the file's name)
    $argumentString = @('copyto', $LocalPath, $remoteSpec, '--progress')
    Write-Host "Invoking rclone (copyto): $rcloneExe $($argumentString -join ' ')"

    try {
        # Direct invocation (handles spaces) with redirection
        & $rcloneExe @argumentString 1> $stdout 2> $stderr
        $exit = $LASTEXITCODE
        Write-Host "rclone exit code: $exit"
    }
    catch {
        Write-Warning "Direct invocation failed: $($_.Exception.Message)"
        return $false
    }

    # Output logs to console for diagnostics
    Write-Host "--- rclone stdout ($stdout) ---" -ForegroundColor Cyan
    Get-Content -Path $stdout -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
    Write-Host "--- rclone stderr ($stderr) ---" -ForegroundColor Cyan
    Get-Content -Path $stderr -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }

    return $exit -eq 0
    }
    catch {
        Write-Warning "rclone failed: $($_.Exception.Message)"
        return $false
    }
}

# Main upload logic
$uploadedCount = 0
$totalFiles = $FilesToUpload.Count

if ($totalFiles -eq 0) {
    Write-Host "No files found to upload!" -ForegroundColor Red
    Write-Host "Please check that:" -ForegroundColor Yellow
    Write-Host "  - LabVIEW build completed successfully" -ForegroundColor Yellow
    Write-Host "  - GeoLogic.exe exists in: $BuildPath" -ForegroundColor Yellow
    Write-Host "  - Aliases file exists in: $ProjectPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nFound $totalFiles files to upload:" -ForegroundColor Cyan
foreach ($file in $FilesToUpload) {
    Write-Host "  - $($file.LocalPath)" -ForegroundColor Gray
}

Write-Host "`nStarting uploads..." -ForegroundColor Cyan

foreach ($file in $FilesToUpload) {
    Write-Host "`nUploading: $($file.RemoteName)..." -ForegroundColor Yellow
    
    $success = $false
    
    # Try rclone (Resolve-Rclone will check RclonePath param and common locations)
    Write-Host "Trying rclone..." -ForegroundColor Gray
    $success = Upload-UsingRclone -LocalPath $file.LocalPath -RemotePath "EXE/$($file.RemoteName)"
    
    if ($success) {
        $uploadedCount++
        Write-Host " Successfully uploaded: $($file.RemoteName)" -ForegroundColor Green
    } else {
        Write-Warning "Failed to upload: $($file.RemoteName)"
    }
}

# Summary
Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "Upload Summary:" -ForegroundColor Cyan
Write-Host "Successfully uploaded: $uploadedCount / $totalFiles files" -ForegroundColor $(if ($uploadedCount -eq $totalFiles) { "Green" } else { "Yellow" })

if ($uploadedCount -eq $totalFiles) {
    Write-Host " All files uploaded successfully!" -ForegroundColor Green
    exit 0
} elseif ($uploadedCount -gt 0) {
    Write-Host " Some files uploaded successfully, some failed." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host " No files were uploaded successfully." -ForegroundColor Red
    Write-Host "`nTo set up uploads:" -ForegroundColor Yellow
    Write-Host "1. Install rclone: https://rclone.org/downloads/" -ForegroundColor Gray
    Write-Host "2. Configure Google Drive: rclone config" -ForegroundColor Gray
    Write-Host "3. Set up a remote named 'gdrive'" -ForegroundColor Gray
    Write-Host "`nGoogle Drive folder URL: https://tinyurl.com/geologic-installer" -ForegroundColor Blue
    Write-Host "="*50 -ForegroundColor Cyan
    exit 2
}
