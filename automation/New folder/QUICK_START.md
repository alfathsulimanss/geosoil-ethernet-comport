# Quick Start Guide - File Versioning System

## TL;DR - Get Started in 30 Seconds

### Upload a New Version
Simply run:
```
upload-build-versioned.bat
```
Done! Your files are now versioned as v001, v002, v003, etc.

### Download Latest Version
```
download-launcher-versioned.bat
```
Downloads the most recent versions of all files.

### View All Available Versions
```
list-versions.bat
```
Shows version history with dates and file sizes.

---

## Common Tasks

### Task 1: Upload a New Build
**Scenario**: You just compiled a new build and want to upload it.

**Steps**:
1. Double-click `upload-build-versioned.bat`
2. Wait for it to complete
3. Your new version is now on Google Drive (v001, v002, etc.)

**Result**: 
- Old versions are kept
- Automatic cleanup removes versions older than 30 days
- Version manifest tracks everything

---

### Task 2: Download the Latest Build
**Scenario**: You want to download the newest version.

**Steps**:
1. Double-click `download-launcher-versioned.bat`
2. Files are downloaded to the configured paths

**Or from PowerShell**:
```powershell
.\download-from-gdrive-versioned.ps1 -VersionToDownload "latest"
```

---

### Task 3: Download a Specific Old Version
**Scenario**: The latest version has a bug, you want to go back to v002.

**Steps - Option A (Simple)**:
1. Open `download-launcher-versioned.bat` in a text editor
2. Change `set VERSION_TO_DOWNLOAD=latest` to `set VERSION_TO_DOWNLOAD=v002`
3. Save and run the batch file

**Steps - Option B (PowerShell)**:
```powershell
.\download-from-gdrive-versioned.ps1 -VersionToDownload "v002"
```

---

### Task 4: See Version History
**Scenario**: You want to know what versions exist and when they were uploaded.

**Steps**:
1. Double-click `list-versions.bat`
2. Read the output with all version info

**Example Output**:
```
GeoLogic.exe:
  [v001]  Uploaded: 2026-08-04 14:30:00 UTC  Size: 5120.50 KB
  [v002]  Uploaded: 2026-08-04 15:45:30 UTC  Size: 5150.75 KB
  [v003]  Uploaded: 2026-08-04 16:20:15 UTC  Size: 5200.25 KB
```

---

## File Organization

### Local Files
```
automation/
├── upload-to-gdrive-versioned.ps1      ← Main upload script
├── download-from-gdrive-versioned.ps1  ← Main download script
├── upload-build-versioned.bat          ← Click to upload
├── download-launcher-versioned.bat     ← Click to download latest
├── list-versions.bat                   ← Click to view versions
├── version-manifest.json               ← Auto-created, tracks versions
├── logs/                               ← Debug info
├── VERSIONING_README.md                ← Detailed documentation
└── QUICK_START.md                      ← This file
```

### Google Drive Files
```
Google Drive
└── EXE/
    └── versions/
        ├── GeoLogic_v001.exe
        ├── GeoLogic_v002.exe
        ├── GeoLogic_v001.aliases
        ├── GeoLogic_v002.aliases
        ├── GeoLogic_v001.ini
        └── ...
```

---

## Settings You Might Want to Change

### 1. How Many Days to Keep Versions?
**File**: `upload-to-gdrive-versioned.ps1`

**Default**: 30 days (versions older than 30 days are deleted)

**To change to 60 days**:
```powershell
.\upload-to-gdrive-versioned.ps1 -RetentionDays 60
```

### 2. Where Should Downloaded Files Go?
**File**: `download-from-gdrive-versioned.ps1`

**Default Locations**:
- EXE: `C:\Program Files\GeoLogic\GeoLogic.exe`
- Aliases: `C:\Program Files\GeoLogic\GeoLogic.aliases`
- INI: `C:\Program Files\GeoLogic\GeoLogic.ini`

**To change**:
```powershell
.\download-from-gdrive-versioned.ps1 `
  -ExeDestination "C:\MyFolder\GeoLogic.exe" `
  -AliasesDestination "C:\MyFolder\GeoLogic.aliases" `
  -IniDestination "C:\MyFolder\GeoLogic.ini"
```

### 3. Where Are Builds Located?
**File**: `upload-to-gdrive-versioned.ps1`

**Default**: `C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm`

**To change**:
```powershell
.\upload-to-gdrive-versioned.ps1 -BuildPath "D:\MyBuilds"
```

---

## Troubleshooting

### Problem: Batch file doesn't do anything
**Solution**: 
1. Check Windows Defender isn't blocking it
2. Try running as Administrator
3. Open PowerShell manually and run the script directly

### Problem: "rclone not found"
**Solution**: 
1. Install rclone: https://rclone.org/downloads/
2. Restart your computer
3. Run the script again

### Problem: Authentication fails
**Solution**:
1. Run: `rclone config` in PowerShell
2. Reconfigure your Google Drive connection
3. Make sure remote is named `geosoilgdrive`

### Problem: Old versions not deleted
**Reason**: Versions are only deleted after 30 days (or your configured retention period)

**Solution**: To delete immediately, use `list-versions.bat` to find the remote path, then delete manually from Google Drive

---

## How It Works (Simple Explanation)

1. **Upload**: 
   - Take your files
   - Add version number (v001, v002, etc.)
   - Upload to Google Drive `EXE/versions/` folder
   - Save version info to local `version-manifest.json`
   - Delete files older than 30 days

2. **Download**:
   - Read `version-manifest.json` for available versions
   - Show list of versions to you
   - Download whichever version you request
   - Save to your specified location

3. **List**:
   - Read `version-manifest.json`
   - Display all versions with dates and sizes

---

## PowerShell Command Reference

### Upload with custom settings
```powershell
.\upload-to-gdrive-versioned.ps1 `
  -BuildPath "C:\path\to\builds" `
  -RetentionDays 60 `
  -RcloneRemote "myremote"
```

### Download latest
```powershell
.\download-from-gdrive-versioned.ps1 -VersionToDownload "latest"
```

### Download specific version
```powershell
.\download-from-gdrive-versioned.ps1 -VersionToDownload "v005"
```

### List versions only (don't download)
```powershell
.\download-from-gdrive-versioned.ps1 -ListVersionsOnly
```

### Download to custom location
```powershell
.\download-from-gdrive-versioned.ps1 `
  -ExeDestination "D:\Apps\GeoLogic.exe" `
  -VersionToDownload "latest"
```

---

## For Automation

If you want to integrate this into automated builds, you can:

**Upload after build completes**:
```powershell
& "C:\path\to\upload-to-gdrive-versioned.ps1" -RetentionDays 30
```

**Download before running tests**:
```powershell
& "C:\path\to\download-from-gdrive-versioned.ps1" -VersionToDownload "latest"
```

**In batch file**:
```batch
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\path\to\upload-to-gdrive-versioned.ps1"
```

---

## Summary

| Task | Command |
|------|---------|
| Upload new version | `upload-build-versioned.bat` |
| Download latest | `download-launcher-versioned.bat` |
| View versions | `list-versions.bat` |
| Download specific v | `.\download-from-gdrive-versioned.ps1 -VersionToDownload "v002"` |
| Keep versions for 60 days | `.\upload-to-gdrive-versioned.ps1 -RetentionDays 60` |

That's it! For more details, see [VERSIONING_README.md](VERSIONING_README.md)
