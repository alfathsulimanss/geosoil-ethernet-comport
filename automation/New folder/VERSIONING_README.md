# Google Drive Versioning System - Documentation

## Overview

The versioning system allows you to maintain multiple versions of your uploaded files with automatic cleanup of old versions. Each time you upload, a new sequential version is created (v001, v002, etc.) instead of replacing the previous file.

## Features

- **Sequential Versioning**: Files are versioned as v001, v002, v003, etc.
- **Version Tracking**: A `version-manifest.json` file locally tracks all uploaded versions
- **Automatic Cleanup**: Versions older than 30 days are automatically deleted
- **Flexible Downloads**: Choose specific versions or always download the latest
- **Version Metadata**: Track upload dates, file sizes, and remote paths

## New Scripts

### 1. Upload with Versioning

**File**: `upload-to-gdrive-versioned.ps1`

Creates new sequential versions of your files on Google Drive.

**Usage**:
```powershell
.\upload-to-gdrive-versioned.ps1
```

**Or use the batch file**:
```
upload-build-versioned.bat
```

**Parameters**:
- `-BuildPath`: Path to compiled EXE (default: C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm)
- `-ProjectPath`: Path to project directory (default: f:\Geosoil Drive\geosoil-ethernet-comport)
- `-RclonePath`: Path to rclone.exe (auto-detected if not specified)
- `-RcloneRemote`: rclone remote name (default: geosoilgdrive)
- `-RetentionDays`: Keep versions from last N days (default: 30)

**What happens**:
1. Checks for GeoLogic.exe, GeoLogic.aliases, and GeoLogic.ini
2. Uploads each to `EXE/versions/` with sequential naming:
   - `GeoLogic_v001.exe`, `GeoLogic_v002.exe`, etc.
   - `GeoLogic_v001.aliases`, `GeoLogic_v002.aliases`, etc.
   - `GeoLogic_v001.ini`, `GeoLogic_v002.ini`, etc.
3. Updates local `version-manifest.json` with version info
4. Removes versions older than 30 days from Google Drive

### 2. Download with Version Selection

**File**: `download-from-gdrive-versioned.ps1`

Lists available versions and downloads your choice.

**Usage - Download Latest**:
```powershell
.\download-from-gdrive-versioned.ps1 -VersionToDownload "latest"
```

**Or use the batch file** (downloads latest by default):
```
download-launcher-versioned.bat
```

**Usage - Download Specific Version**:
```powershell
.\download-from-gdrive-versioned.ps1 -VersionToDownload "v002"
# or just the number
.\download-from-gdrive-versioned.ps1 -VersionToDownload "002"
```

**Parameters**:
- `-ExeDestination`: Where to save GeoLogic.exe (default: C:\Program Files\GeoLogic\GeoLogic.exe)
- `-AliasesDestination`: Where to save aliases file (default: C:\Program Files\GeoLogic\GeoLogic.aliases)
- `-IniDestination`: Where to save INI file (default: C:\Program Files\GeoLogic\GeoLogic.ini)
- `-VersionToDownload`: Version to download - "latest" or "v001", "v002", etc. (default: latest)
- `-RclonePath`: Path to rclone.exe (auto-detected if not specified)
- `-RcloneRemote`: rclone remote name (default: geosoilgdrive)
- `-ListVersionsOnly`: Only show available versions, don't download

**What happens**:
1. Reads `version-manifest.json` to get available versions
2. Displays all versions with dates and file sizes
3. Downloads the requested version (or latest if not specified)
4. Places files in specified destinations

### 3. List All Versions

**File**: `list-versions.bat`

Shows all available versions without downloading.

**Usage**:
```
list-versions.bat
```

**Or PowerShell**:
```powershell
.\download-from-gdrive-versioned.ps1 -ListVersionsOnly
```

## Version Manifest File

**Location**: `version-manifest.json` (in the same folder as the scripts)

**Format**:
```json
{
  "exe": {
    "versions": [
      {
        "number": 1,
        "uploadDate": "2026-08-04T14:30:00Z",
        "remotePath": "EXE/versions/GeoLogic_v001.exe",
        "fileName": "GeoLogic.exe",
        "fileSize": 5242880
      }
    ]
  },
  "aliases": {
    "versions": [...]
  },
  "ini": {
    "versions": [...]
  }
}
```

This file is:
- **Auto-created** on first upload
- **Auto-updated** after each upload
- **Used for** version history and cleanup tracking
- **Keep backed up** - it's your version history!

## Workflow Example

### Step 1: Upload New Build
```
upload-build-versioned.bat
```
Output:
```
Starting versioned upload process...
Found 3 files to upload:
  - C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm\GeoLogic.exe
  - C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm\GeoLogic.aliases
  - C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm\GeoLogic.ini

Starting uploads...

Uploading: GeoLogic.exe...
  Version: v001 (GeoLogic_v001.exe)
  Uploading to: geosoilgdrive:EXE/versions/GeoLogic_v001.exe
  ✓ Successfully uploaded: GeoLogic.exe

Uploading: GeoLogic.aliases...
  Version: v001 (GeoLogic_v001.aliases)
  Uploading to: geosoilgdrive:EXE/versions/GeoLogic_v001.aliases
  ✓ Successfully uploaded: GeoLogic.aliases

Uploading: GeoLogic.ini...
  Version: v001 (GeoLogic_v001.ini)
  Uploading to: geosoilgdrive:EXE/versions/GeoLogic_v001.ini
  ✓ Successfully uploaded: GeoLogic.ini

Upload Summary:
Successfully uploaded: 3 / 3 files
Version manifest: ...\version-manifest.json
```

### Step 2: View Available Versions
```
list-versions.bat
```
Output:
```
Available Versions:
================================================================================

GeoLogic.exe:
  [v001]  Uploaded: 2026-08-04 14:30:00 UTC  Size: 5120.50 KB
  [v002]  Uploaded: 2026-08-04 15:45:30 UTC  Size: 5150.75 KB
  [v003]  Uploaded: 2026-08-04 16:20:15 UTC  Size: 5200.25 KB

GeoLogic.aliases:
  [v001]  Uploaded: 2026-08-04 14:30:05 UTC  Size: 45.30 KB

GeoLogic.ini:
  [v001]  Uploaded: 2026-08-04 14:30:10 UTC  Size: 12.50 KB

================================================================================
```

### Step 3: Download Specific Version
```powershell
# Download the specific build from 2 versions ago
.\download-from-gdrive-versioned.ps1 -VersionToDownload "v002"
```

Or edit `download-launcher-versioned.bat`:
```batch
set VERSION_TO_DOWNLOAD=v002
```

## Automatic Cleanup

Every time you upload:
1. Old versions are checked against the retention period (30 days)
2. Any version older than 30 days is automatically deleted from Google Drive
3. The version manifest is updated to reflect deletions

**Example**:
- Upload date: 2026-08-04
- Version uploaded: 2026-07-01 (older than 30 days)
- Action: Automatically removed from Google Drive

## Google Drive Structure

Your Google Drive will now have:

```
Google Drive Root
└── EXE/
    └── versions/
        ├── GeoLogic_v001.exe
        ├── GeoLogic_v002.exe
        ├── GeoLogic_v003.exe
        ├── GeoLogic_v001.aliases
        ├── GeoLogic_v002.aliases
        ├── GeoLogic_v001.ini
        ├── GeoLogic_v002.ini
        └── ...
```

## Customization

### Change Retention Period

**PowerShell**:
```powershell
.\upload-to-gdrive-versioned.ps1 -RetentionDays 60
```

**Batch file** - edit `upload-build-versioned.bat`:
```batch
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "!SCRIPT_DIR!upload-to-gdrive-versioned.ps1" -RetentionDays 60
```

### Change Default Download Version

**Batch file** - edit `download-launcher-versioned.bat`:
```batch
REM Download v002 by default instead of latest
set VERSION_TO_DOWNLOAD=v002
```

### Change Destination Paths

**PowerShell**:
```powershell
.\download-from-gdrive-versioned.ps1 `
  -ExeDestination "D:\MyApp\GeoLogic.exe" `
  -VersionToDownload "latest"
```

## Troubleshooting

### Version manifest file not found
**Solution**: Run upload script once to create it. The manifest is created after the first successful upload.

### rclone not found
**Solution**: 
1. Install rclone from https://rclone.org/downloads/
2. Or specify path: `.\upload-to-gdrive-versioned.ps1 -RclonePath "C:\path\to\rclone.exe"`

### Old versions not being deleted
**Reason**: Cleanup only deletes versions older than the retention period (30 days). Recent versions are always kept.

**Solution**: Increase `-RetentionDays` or manually delete old files from Google Drive.

### Script execution disabled
**Error**: "cannot be loaded because running scripts is disabled"

**Solution 1**: Run PowerShell as admin and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solution 2**: Use batch file (it bypasses execution policy automatically)

## Migration from Old System

If you have existing files in `EXE/` folder:

1. **Option A - Start Fresh**: 
   - Files stay where they are
   - New versioned uploads go to `EXE/versions/`
   - You can manually download/reorganize as needed

2. **Option B - Manual Migration**:
   - Rename existing files with version tags:
     - `GeoLogic.exe` → `GeoLogic_v001.exe`
     - Move to `EXE/versions/`
   - Update manifest manually (advanced)

3. **Option C - Simple Override**:
   - Delete old files from Google Drive
   - Run new upload script fresh
   - Creates v001, v002, etc. going forward

## Support

For issues or questions, check:
1. `logs/` folder for detailed error messages
2. `version-manifest.json` for version history
3. Ensure rclone is properly configured and authenticated

---

**Version**: 1.0
**Last Updated**: 2026-08-04
