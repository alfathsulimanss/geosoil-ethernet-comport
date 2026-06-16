# PowerShell Script to Download Files from Google Drive
# This script downloads the built EXE, aliases, and INI files from Google Drive

param(
    [string]$ExeDestination = "C:\Program Files\GeoLogic\GeoLogic.exe",
    [string]$AliasesDestination = "C:\Program Files\GeoLogic\GeoLogic.aliases", 
    [string]$IniDestination = "C:\Program Files\GeoLogic\GeoLogic.ini",
    [string]$RclonePath = "",
    [string]$RcloneRemote = "geosoilgdrive"
)

Write-Host "Starting download process..."
Write-Host "RcloneRemote: $RcloneRemote"
Write-Host "Destination paths:"
Write-Host "  EXE: $ExeDestination"
Write-Host "  Aliases: $AliasesDestination"  
Write-Host "  INI: $IniDestination"

# Handle quoted paths from batch files
if ($RclonePath) {
    $trimmed = $RclonePath.Trim('"')
    if ($trimmed -ne $RclonePath) {
        Write-Host "Trimmed RclonePath to: '$trimmed'"
        $RclonePath = $trimmed
    }
}

# Files to download
$FilesToDownload = @(
    @{
        RemotePath = "EXEAusie/GeoLogic.exe"
        LocalPath = $ExeDestination
        Description = "GeoLogic Application Executable"
    },
    @{
        RemotePath = "EXEAusie/GeoLogic.aliases"
        LocalPath = $AliasesDestination
        Description = "LabVIEW Aliases File"
    },
    @{
        RemotePath = "EXEAusie/GeoLogic.ini"
        LocalPath = $IniDestination
        Description = "Configuration INI File"
    }
)

# Function to download file using rclone
function Download-UsingRclone {
    param(
        [string]$RemotePath,
        [string]$LocalPath
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
        $rcloneExe = Resolve-Rclone -ExplicitPath $RclonePath
        if (-not $rcloneExe) {
            Write-Warning "rclone not found on PATH or in common locations. Please install rclone or set RclonePath param."
            return $false
        }

        # Create destination directory if it doesn't exist
        $destDir = Split-Path -Parent $LocalPath
        if ($destDir -and -not (Test-Path $destDir)) {
            Write-Host "Creating directory: $destDir"
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }

        # Prepare logs (robustly find script root)
        $scriptRoot = $PSScriptRoot
        if (-not $scriptRoot) {
            $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
        }
        $logsDir = Join-Path -Path $scriptRoot -ChildPath 'logs'
        if (-not (Test-Path $logsDir)) { New-Item -Path $logsDir -ItemType Directory | Out-Null }
        $ts = (Get-Date).ToString('yyyyMMdd-HHmmss')
        $stdout = Join-Path $logsDir ("rclone-download-$ts-out.log")
        $stderr = Join-Path $logsDir ("rclone-download-$ts-err.log")

        # Ensure files exist to avoid RedirectStandardOutput errors
        try { New-Item -Path $stdout -ItemType File -Force | Out-Null } catch { }
        try { New-Item -Path $stderr -ItemType File -Force | Out-Null } catch { }

        # Build remote spec safely
        $remoteSpec = "${RcloneRemote}:$RemotePath"
        # For rclone copy, destination should be directory, not full file path
        $destDir = Split-Path -Parent $LocalPath
        $argumentString = @('copy', $remoteSpec, $destDir, '--progress')
        Write-Host "Invoking rclone: $rcloneExe $($argumentString -join ' ')"

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

        # Verify the file was downloaded
        if (Test-Path $LocalPath) {
            $fileInfo = Get-Item $LocalPath
            Write-Host "Downloaded file size: $($fileInfo.Length) bytes" -ForegroundColor Green
            return $true
        } else {
            Write-Warning "Download may have failed - file not found at: $LocalPath"
            return $false
        }
    }
    catch {
        Write-Warning "rclone failed: $($_.Exception.Message)"
        return $false
    }
}

# Main download logic
$downloadedCount = 0
$totalFiles = $FilesToDownload.Count

Write-Host "`nStarting downloads..." -ForegroundColor Cyan

foreach ($file in $FilesToDownload) {
    Write-Host "`nDownloading: $($file.Description)..." -ForegroundColor Yellow
    Write-Host "  From: $($file.RemotePath)" -ForegroundColor Gray
    Write-Host "  To: $($file.LocalPath)" -ForegroundColor Gray
    
    $success = Download-UsingRclone -RemotePath $file.RemotePath -LocalPath $file.LocalPath
    
    if ($success) {
        $downloadedCount++
        Write-Host " Successfully downloaded: $($file.Description)" -ForegroundColor Green
    } else {
        Write-Warning "Failed to download: $($file.Description)"
    }
}

# Summary
Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "Download Summary:" -ForegroundColor Cyan
Write-Host "Successfully downloaded: $downloadedCount / $totalFiles files" -ForegroundColor $(if ($downloadedCount -eq $totalFiles) { "Green" } else { "Yellow" })

if ($downloadedCount -eq $totalFiles) {
    Write-Host " All files downloaded successfully!" -ForegroundColor Green
    exit 0
} elseif ($downloadedCount -gt 0) {
    Write-Host " Some files downloaded successfully, some failed." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host " No files were downloaded successfully." -ForegroundColor Red
    Write-Host "`nTo set up downloads:" -ForegroundColor Yellow
    Write-Host "1. Install rclone: https://rclone.org/downloads/" -ForegroundColor Gray
    Write-Host "2. Configure Google Drive: rclone config" -ForegroundColor Gray
    Write-Host "3. Set up a remote named 'geosoilgdrive'" -ForegroundColor Gray
    Write-Host "`nGoogle Drive folder URL: https://tinyurl.com/geologic-installer" -ForegroundColor Blue
    Write-Host "="*50 -ForegroundColor Cyan
    exit 2
}