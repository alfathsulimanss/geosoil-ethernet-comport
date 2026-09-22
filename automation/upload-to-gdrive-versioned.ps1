# PowerShell Script to Upload Files to Google Drive with Versioning
# Creates sequential versions of each file and maintains a version manifest
# Automatically removes versions older than 30 days

param(
    [string]$BuildPath = "C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm",
    [string]$ProjectPath = "f:\Geosoil Drive\geosoil-ethernet-comport",
    [string]$RclonePath = "",
    [string]$RcloneRemote = "geosoilgdrive",
    [int]$RetentionDays = 30
)

Write-Host "Starting versioned upload process..."
Write-Host "Build Path: $BuildPath"
Write-Host "Project Path: $ProjectPath"
Write-Host "Retention: Last $RetentionDays days"

if ($RclonePath) {
    $trimmed = $RclonePath.Trim('"')
    if ($trimmed -ne $RclonePath) {
        Write-Host "Trimmed RclonePath to: '$trimmed'"
        $RclonePath = $trimmed
    }
}

# Local version manifest path (tracks uploaded versions)
$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
    $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
}
$versionManifestPath = Join-Path -Path $scriptRoot -ChildPath 'version-manifest.json'

# Files to upload
$FilesToUpload = @()

# Add EXE file
$exePath = "$BuildPath\GeoLogic.exe"
if (Test-Path $exePath) {
    $FilesToUpload += @{
        LocalPath = $exePath
        RemoteName = "GeoLogic.exe"
        Description = "GeoLogic Application Executable"
        FileType = "exe"
    }
}

# Add aliases file
$aliasesPath = "$BuildPath\GeoLogic.aliases"
if (Test-Path $aliasesPath) {
    $FilesToUpload += @{
        LocalPath = $aliasesPath
        RemoteName = "GeoLogic.aliases"
        Description = "LabVIEW Aliases File"
        FileType = "aliases"
    }
}

# Check for INI files
$IniFiles = "$BuildPath\GeoLogic.ini"
if (Test-Path $IniFiles) {
    $FilesToUpload += @{
        LocalPath = $IniFiles
        RemoteName = "GeoLogic.ini"
        Description = "Configuration INI File"
        FileType = "ini"
    }
}

# Function to load version manifest
function Load-VersionManifest {
    param([string]$ManifestPath)
    
    if (Test-Path $ManifestPath) {
        try {
            $manifest = Get-Content -Path $ManifestPath -Raw | ConvertFrom-Json
            return $manifest
        } catch {
            Write-Warning "Failed to load manifest, starting fresh: $($_.Exception.Message)"
            return @{}
        }
    }
    return @{}
}

# Function to save version manifest
function Save-VersionManifest {
    param(
        [object]$Manifest,
        [string]$ManifestPath
    )
    
    $Manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $ManifestPath -Force
}

# Function to get next version number for a file
function Get-NextVersionNumber {
    param(
        [object]$Manifest,
        [string]$FileType
    )
    
    if (-not $Manifest.PSObject.Properties[$FileType]) {
        return 1
    }
    
    $versions = $Manifest.$FileType.versions
    if ($versions -and $versions.Count -gt 0) {
        $maxVersion = ($versions | Measure-Object -Property number -Maximum).Maximum
        return $maxVersion + 1
    }
    
    return 1
}

# Function to upload file using rclone
function Upload-UsingRclone {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )
    
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

        $logsDir = Join-Path -Path $scriptRoot -ChildPath 'logs'
        if (-not (Test-Path $logsDir)) { New-Item -Path $logsDir -ItemType Directory | Out-Null }
        $ts = (Get-Date).ToString('yyyyMMdd-HHmmss')
        $stdout = Join-Path $logsDir ("rclone-$ts-out.log")
        $stderr = Join-Path $logsDir ("rclone-$ts-err.log")

        try { New-Item -Path $stdout -ItemType File -Force | Out-Null } catch { }
        try { New-Item -Path $stderr -ItemType File -Force | Out-Null } catch { }

        $remoteSpec = "${RcloneRemote}:$RemotePath"
        $argumentString = @('copyto', $LocalPath, $remoteSpec, '--progress')
        Write-Host "  Uploading to: $remoteSpec" -ForegroundColor Gray

        & $rcloneExe @argumentString 1> $stdout 2> $stderr
        $exit = $LASTEXITCODE
        
        if ($exit -eq 0) {
            return $true
        } else {
            Write-Host "--- rclone stderr ---" -ForegroundColor Red
            Get-Content -Path $stderr -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
            return $false
        }
    }
    catch {
        Write-Warning "rclone failed: $($_.Exception.Message)"
        return $false
    }
}

# Function to cleanup old versions
function Cleanup-OldVersions {
    param(
        [object]$Manifest,
        [int]$RetentionDays
    )
    
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $filesToDelete = @()
    
    foreach ($fileType in $Manifest.PSObject.Properties.Name) {
        $versions = $Manifest.$fileType.versions
        if ($versions) {
            $versionsToKeep = @()
            
            foreach ($version in $versions) {
                $uploadDate = [DateTime]::Parse($version.uploadDate)
                if ($uploadDate -gt $cutoffDate) {
                    $versionsToKeep += $version
                } else {
                    $filesToDelete += @{
                        FileType = $fileType
                        RemotePath = $version.remotePath
                        Version = $version.number
                    }
                }
            }
            
            $Manifest.$fileType.versions = $versionsToKeep
        }
    }
    
    # Delete old files from remote
    if ($filesToDelete.Count -gt 0) {
        Write-Host "`nCleaning up versions older than $RetentionDays days..." -ForegroundColor Yellow
        
        foreach ($file in $filesToDelete) {
            Write-Host "  Removing: $($file.FileType) v$($file.Version)" -ForegroundColor Gray
            
            $remoteSpec = "${RcloneRemote}:$($file.RemotePath)"
            & rclone delete $remoteSpec --quiet 2> $null
        }
    }
}

# Main upload logic
Write-Host "`nLoading version manifest..." -ForegroundColor Cyan
$manifest = Load-VersionManifest -ManifestPath $versionManifestPath

$uploadedCount = 0
$totalFiles = $FilesToUpload.Count

if ($totalFiles -eq 0) {
    Write-Host "No files found to upload!" -ForegroundColor Red
    exit 1
}

Write-Host "Found $totalFiles files to upload:" -ForegroundColor Cyan
foreach ($file in $FilesToUpload) {
    Write-Host "  - $($file.LocalPath)" -ForegroundColor Gray
}

Write-Host "`nStarting uploads..." -ForegroundColor Cyan

foreach ($file in $FilesToUpload) {
    Write-Host "`nUploading: $($file.RemoteName)..." -ForegroundColor Yellow
    
    # Get next version number
    $nextVersion = Get-NextVersionNumber -Manifest $manifest -FileType $file.FileType
    $versionedName = $file.RemoteName -replace '(\.[^.]+)$', "_v$('{0:D3}' -f $nextVersion)`$1"
    $remotePath = "EXE/versions/$versionedName"
    
    Write-Host "  Version: v$nextVersion ($versionedName)" -ForegroundColor Cyan
    
    $success = Upload-UsingRclone -LocalPath $file.LocalPath -RemotePath $remotePath
    
    if ($success) {
        $uploadedCount++
        
        # Initialize file type in manifest if needed
        if (-not $manifest.PSObject.Properties[$file.FileType]) {
            $manifest | Add-Member -NotePropertyName $file.FileType -NotePropertyValue @{ versions = @() }
        }
        
        # Add version record
        $versionRecord = @{
            number = $nextVersion
            uploadDate = (Get-Date).ToUniversalTime().ToString('o')
            remotePath = $remotePath
            fileName = $file.RemoteName
            fileSize = (Get-Item $file.LocalPath).Length
        }
        
        $manifest.$($file.FileType).versions += $versionRecord
        
        Write-Host "  ✓ Successfully uploaded: $($file.RemoteName)" -ForegroundColor Green
    } else {
        Write-Warning "Failed to upload: $($file.RemoteName)"
    }
}

# Cleanup old versions
Write-Host "`n" -ForegroundColor Cyan
Cleanup-OldVersions -Manifest $manifest -RetentionDays $RetentionDays

# Save manifest
Write-Host "`nSaving version manifest..." -ForegroundColor Cyan
Save-VersionManifest -Manifest $manifest -ManifestPath $versionManifestPath

# Summary
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Upload Summary:" -ForegroundColor Cyan
Write-Host "Successfully uploaded: $uploadedCount / $totalFiles files" -ForegroundColor $(if ($uploadedCount -eq $totalFiles) { "Green" } else { "Yellow" })
Write-Host "Version manifest: $versionManifestPath" -ForegroundColor Gray
Write-Host "="*60 -ForegroundColor Cyan

if ($uploadedCount -eq $totalFiles) {
    exit 0
} else {
    exit 1
}
