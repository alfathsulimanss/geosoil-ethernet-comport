# PowerShell Script to Download Files from Google Drive with Version Selection
# Allows choosing which version of a file to download

param(
    [string]$ExeDestination = "C:\Program Files\GeoLogic\GeoLogic.exe",
    [string]$AliasesDestination = "C:\Program Files\GeoLogic\GeoLogic.aliases", 
    [string]$IniDestination = "C:\Program Files\GeoLogic\GeoLogic.ini",
    [string]$RclonePath = "",
    [string]$RcloneRemote = "geosoilgdrive",
    [string]$VersionToDownload = "latest",  # "latest" or specific version like "v001"
    [switch]$ListVersionsOnly = $false
)

Write-Host "Starting versioned download process..."
Write-Host "RcloneRemote: $RcloneRemote"
Write-Host "Download Mode: $VersionToDownload"

if ($RclonePath) {
    $trimmed = $RclonePath.Trim('"')
    if ($trimmed -ne $RclonePath) {
        Write-Host "Trimmed RclonePath to: '$trimmed'"
        $RclonePath = $trimmed
    }
}

# Local version manifest path
$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
    $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
}
$versionManifestPath = Join-Path -Path $scriptRoot -ChildPath 'version-manifest.json'

# Function to load version manifest from local file
function Load-VersionManifest {
    param([string]$ManifestPath)
    
    if (Test-Path $ManifestPath) {
        try {
            $manifest = Get-Content -Path $ManifestPath -Raw | ConvertFrom-Json
            return $manifest
        } catch {
            Write-Warning "Failed to load manifest: $($_.Exception.Message)"
            return $null
        }
    } else {
        Write-Warning "Version manifest not found. Run upload script first."
        return $null
    }
}

# Function to list available versions
function List-AvailableVersions {
    param([object]$Manifest)
    
    if (-not $Manifest) {
        return
    }
    
    Write-Host "`nAvailable Versions:" -ForegroundColor Cyan
    Write-Host "="*80
    
    foreach ($fileType in $Manifest.PSObject.Properties.Name) {
        $fileInfo = $Manifest.$fileType
        Write-Host "`n$($fileInfo.fileName):" -ForegroundColor Yellow
        
        $versions = $fileInfo.versions
        if ($versions) {
            # Sort by version number descending (newest first)
            $sortedVersions = $versions | Sort-Object -Property number -Descending
            
            foreach ($version in $sortedVersions) {
                $uploadDate = [DateTime]::Parse($version.uploadDate)
                $sizeKB = [math]::Round($version.fileSize / 1KB, 2)
                $versionStr = "v$($("{0:D3}" -f $version.number))"
                
                Write-Host "  [$versionStr]  Uploaded: $($uploadDate.ToString('yyyy-MM-dd HH:mm:ss')) UTC  Size: $($sizeKB) KB" -ForegroundColor Gray
            }
        } else {
            Write-Host "  No versions available" -ForegroundColor Gray
        }
    }
    
    Write-Host "`n" + "="*80
}

# Function to get version to download
function Get-VersionToDownload {
    param(
        [object]$Manifest,
        [string]$FileType,
        [string]$VersionRequest
    )
    
    $versions = $Manifest.$FileType.versions
    if (-not $versions) {
        return $null
    }
    
    if ($VersionRequest -eq "latest") {
        return $versions | Sort-Object -Property number -Descending | Select-Object -First 1
    } else {
        # Parse version string (e.g., "v001" or just "001")
        $versionNum = $VersionRequest -replace '^v', ''
        $versionNum = [int]$versionNum
        
        return $versions | Where-Object { $_.number -eq $versionNum } | Select-Object -First 1
    }
}

# Function to download file using rclone
function Download-UsingRclone {
    param(
        [string]$RemotePath,
        [string]$LocalPath
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
        $rcloneExe = Resolve-Rclone -ExplicitPath $RclonePath
        if (-not $rcloneExe) {
            Write-Warning "rclone not found on PATH or in common locations."
            return $false
        }

        # Create destination directory if it doesn't exist
        $destDir = Split-Path -Parent $LocalPath
        if ($destDir -and -not (Test-Path $destDir)) {
            Write-Host "Creating directory: $destDir" -ForegroundColor Gray
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }

        $logsDir = Join-Path -Path $scriptRoot -ChildPath 'logs'
        if (-not (Test-Path $logsDir)) { New-Item -Path $logsDir -ItemType Directory | Out-Null }
        $ts = (Get-Date).ToString('yyyyMMdd-HHmmss')
        $stdout = Join-Path $logsDir ("rclone-download-$ts-out.log")
        $stderr = Join-Path $logsDir ("rclone-download-$ts-err.log")

        try { New-Item -Path $stdout -ItemType File -Force | Out-Null } catch { }
        try { New-Item -Path $stderr -ItemType File -Force | Out-Null } catch { }

        $remoteSpec = "${RcloneRemote}:$RemotePath"
        $destDir = Split-Path -Parent $LocalPath
        $argumentString = @('copy', $remoteSpec, $destDir, '--progress')

        Write-Host "  Downloading from: $remoteSpec" -ForegroundColor Gray

        & $rcloneExe @argumentString 1> $stdout 2> $stderr
        $exit = $LASTEXITCODE
        
        if ($exit -ne 0) {
            Write-Host "--- rclone stderr ---" -ForegroundColor Red
            Get-Content -Path $stderr -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
            return $false
        }

        # Verify the file was downloaded
        if (Test-Path $LocalPath) {
            $fileInfo = Get-Item $LocalPath
            Write-Host "  Downloaded successfully. Size: $($fileInfo.Length) bytes" -ForegroundColor Green
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

# Main logic
Write-Host "`nLoading version manifest..." -ForegroundColor Cyan
$manifest = Load-VersionManifest -ManifestPath $versionManifestPath

if (-not $manifest) {
    exit 1
}

# Function to display interactive menu and get user choice
function Get-VersionChoice {
    param(
        [object]$Manifest
    )
    
    Write-Host "`n" + "="*80
    Write-Host "SELECT VERSION TO DOWNLOAD" -ForegroundColor Yellow
    Write-Host "="*80
    
    $fileTypeIndex = 0
    $fileVersionMap = @{}
    $menuIndex = 1
    
    foreach ($fileType in $Manifest.PSObject.Properties.Name) {
        $fileInfo = $Manifest.$fileType
        Write-Host "`n$($fileInfo.fileName):" -ForegroundColor Cyan
        
        $versions = $fileInfo.versions
        if ($versions) {
            # Sort by version number descending (newest first)
            $sortedVersions = $versions | Sort-Object -Property number -Descending
            
            foreach ($version in $sortedVersions) {
                $uploadDate = [DateTime]::Parse($version.uploadDate)
                $sizeKB = [math]::Round($version.fileSize / 1KB, 2)
                $versionStr = "v$($("{0:D3}" -f $version.number))"
                $marker = if ($version.number -eq ($sortedVersions[0].number)) { " ← LATEST" } else { "" }
                
                Write-Host "  [$menuIndex] $versionStr  |  $($uploadDate.ToString('yyyy-MM-dd HH:mm:ss')) UTC  |  $sizeKB KB$marker" -ForegroundColor Gray
                $fileVersionMap[$menuIndex] = @{
                    FileType = $fileType
                    VersionNumber = $version.number
                }
                $menuIndex++
            }
        }
    }
    
    Write-Host "`n" + "="*80
    Write-Host "Enter the number of the version you want to download:" -ForegroundColor Yellow
    Write-Host "(0 = Download latest versions of all files)" -ForegroundColor Gray
    
    $choice = Read-Host "Your choice"
    
    if ($choice -eq "0") {
        return "latest"
    }
    
    $choiceNum = $null
    if ([int]::TryParse($choice, [ref]$choiceNum)) {
        if ($fileVersionMap.ContainsKey($choiceNum)) {
            return $fileVersionMap[$choiceNum].VersionNumber
        } else {
            Write-Host "Invalid choice! Please enter a valid number." -ForegroundColor Red
            return Get-VersionChoice -Manifest $Manifest
        }
    } else {
        Write-Host "Invalid input! Please enter a number." -ForegroundColor Red
        return Get-VersionChoice -Manifest $Manifest
    }
}

# Display available versions
List-AvailableVersions -Manifest $manifest

if ($ListVersionsOnly) {
    exit 0
}

# If no version specified, ask user interactively
if ($VersionToDownload -eq "latest") {
    $userChoice = Get-VersionChoice -Manifest $manifest
    $VersionToDownload = $userChoice
    Write-Host "`nDownloading version: $VersionToDownload" -ForegroundColor Cyan
}

# Download files
$filesMap = @{
    "exe" = @{
        destination = $ExeDestination
        description = "GeoLogic Application Executable"
    }
    "aliases" = @{
        destination = $AliasesDestination
        description = "LabVIEW Aliases File"
    }
    "ini" = @{
        destination = $IniDestination
        description = "Configuration INI File"
    }
}

$downloadedCount = 0
$totalFiles = 0

Write-Host "`nStarting downloads (Version: $VersionToDownload)..." -ForegroundColor Cyan

foreach ($fileType in $filesMap.Keys) {
    if (-not $manifest.PSObject.Properties[$fileType]) {
        continue
    }
    
    $totalFiles++
    $fileInfo = $filesMap[$fileType]
    $version = Get-VersionToDownload -Manifest $manifest -FileType $fileType -VersionRequest $VersionToDownload
    
    if (-not $version) {
        Write-Warning "Version not found for $fileType (requested: $VersionToDownload)"
        continue
    }
    
    Write-Host "`nDownloading: $($fileInfo.description)..." -ForegroundColor Yellow
    Write-Host "  Version: v$($("{0:D3}" -f $version.number))" -ForegroundColor Cyan
    Write-Host "  Uploaded: $($version.uploadDate)" -ForegroundColor Gray
    
    $success = Download-UsingRclone -RemotePath $version.remotePath -LocalPath $fileInfo.destination
    
    if ($success) {
        $downloadedCount++
        Write-Host "  ✓ Successfully downloaded" -ForegroundColor Green
    } else {
        Write-Warning "Failed to download"
    }
}

# Summary
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Download Summary:" -ForegroundColor Cyan
if ($totalFiles -gt 0) {
    Write-Host "Successfully downloaded: $downloadedCount / $totalFiles files" -ForegroundColor $(if ($downloadedCount -eq $totalFiles) { "Green" } else { "Yellow" })
} else {
    Write-Host "No files to download" -ForegroundColor Yellow
}
Write-Host "="*60 -ForegroundColor Cyan

if ($downloadedCount -eq $totalFiles -and $totalFiles -gt 0) {
    exit 0
} else {
    exit 1
}
