# Python Versioned Upload/Download - Setup & Usage

## Overview

The Python implementation uses the Google Drive API directly instead of rclone. It provides:
- Sequential file versioning (v001, v002, etc.)
- Interactive version selection menu
- Configuration via `config.json`
- Automatic cleanup of old versions

## Prerequisites

### 1. Install Python
Download and install Python 3.8+ from https://www.python.org/downloads/

**Important**: Check "Add Python to PATH" during installation!

Verify installation:
```cmd
python --version
```

### 2. Install Dependencies
The batch files will auto-install these, but you can manually install:

```cmd
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. Get Google Drive Credentials

**Step 1: Create Google Cloud Project**
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Search for "Google Drive API" and enable it
4. Click "Create Credentials" → "OAuth 2.0 Desktop App"
5. Download as JSON file

**Step 2: Save Credentials**
1. Download the credentials file
2. Rename it to `credentials.json`
3. Place it in the automation folder (same directory as the batch files)

**Step 3: Get Your Google Drive Folder ID**
1. Open the folder in Google Drive where you want to store versions
2. The URL looks like: `https://drive.google.com/drive/folders/XXXXXXX`
3. Copy the `XXXXXXX` part (the folder ID)

## Configuration

### Setup config.json

Edit `config.json` with your settings:

```json
{
  "google_drive": {
    "folder_id": "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE",
    "credentials_file": "credentials.json",
    "token_file": "token.pickle"
  },
  "paths": {
    "build_path": "C:\\Users\\ralfsuliman\\Desktop\\EXE\\Geosoil New Controller Multi Comm",
    "project_path": "f:\\Geosoil Drive\\geosoil-ethernet-comport",
    "exe_destination": "C:\\Program Files\\GeoLogic\\GeoLogic.exe",
    "aliases_destination": "C:\\Program Files\\GeoLogic\\GeoLogic.aliases",
    "ini_destination": "C:\\Program Files\\GeoLogic\\GeoLogic.ini"
  },
  "versioning": {
    "retention_days": 30,
    "enable_versioning": true
  },
  "files_to_upload": {
    "exe": {
      "local_name": "GeoLogic.exe",
      "remote_name": "GeoLogic.exe",
      "description": "GeoLogic Application Executable"
    },
    "aliases": {
      "local_name": "GeoLogic.aliases",
      "remote_name": "GeoLogic.aliases",
      "description": "LabVIEW Aliases File"
    },
    "ini": {
      "local_name": "GeoLogic.ini",
      "remote_name": "GeoLogic.ini",
      "description": "Configuration INI File"
    }
  }
}
```

**Key Settings:**
- `folder_id`: Your Google Drive folder ID (required)
- `credentials_file`: Path to credentials.json
- `build_path`: Where your compiled files are
- `retention_days`: Keep versions from last N days
- `exe_destination`, `aliases_destination`, `ini_destination`: Where to download files

## Usage

### Upload Files with Versioning

**Using Batch File:**
```cmd
upload-py-versioned.bat
```

**Or from Command Line:**
```cmd
python upload_versioned.py
```

**What happens:**
1. Reads config.json settings
2. Finds build files (exe, aliases, ini)
3. Uploads each as new version (v001, v002, etc.)
4. Creates/updates `version-manifest.json` 
5. Removes versions older than 30 days
6. Shows upload progress

**Example Output:**
```
======================================================================
  GeoLogic Google Drive Versioned Upload (Python)
======================================================================

✓ Configuration loaded from: config.json
✓ Successfully authenticated with Google Drive

📁 Found 3 files to upload:
   - GeoLogic.exe
   - GeoLogic.aliases
   - GeoLogic.ini

📤 Uploading: GeoLogic.exe
   Version: v001 (GeoLogic_v001.exe)
   Progress: 50%
   Progress: 100%
✅ Successfully uploaded: GeoLogic.exe

...

🗑️  Cleaning up old versions from exe...
   Removed: v001 (2026-07-01T14:30:00Z)

======================================================================
Upload Summary:
Successfully uploaded: 3/3 files
Manifest saved to: version-manifest.json
======================================================================
```

### Download Files Interactively

**Using Batch File:**
```cmd
download-py-versioned.bat
```

**Or from Command Line:**
```cmd
python download_versioned.py
```

**What happens:**
1. Reads version-manifest.json
2. Displays all available versions with dates and sizes
3. Shows interactive menu with numbered choices
4. User types number to select version
5. Downloads selected versions

**Example Interactive Menu:**
```
==============================================================================================
AVAILABLE VERSIONS
==============================================================================================

📄 GeoLogic.exe:
   v003  |  2026-08-04 16:20:15 UTC  |  5200.25 KB ← LATEST
   v002  |  2026-08-04 15:45:30 UTC  |  5150.75 KB
   v001  |  2026-08-04 14:30:00 UTC  |  5120.50 KB

📄 GeoLogic.aliases:
   v001  |  2026-08-04 14:30:05 UTC  |  45.30 KB ← LATEST

📄 GeoLogic.ini:
   v001  |  2026-08-04 14:30:10 UTC  |  12.50 KB ← LATEST

==============================================================================================
SELECT VERSION TO DOWNLOAD
==============================================================================================

📄 GeoLogic.exe:
  [1] v003  |  2026-08-04 16:20:15 UTC  |  5200.25 KB ← LATEST
  [2] v002  |  2026-08-04 15:45:30 UTC  |  5150.75 KB
  [3] v001  |  2026-08-04 14:30:00 UTC  |  5120.50 KB

📄 GeoLogic.aliases:
  [4] v001  |  2026-08-04 14:30:05 UTC  |  45.30 KB ← LATEST

📄 GeoLogic.ini:
  [5] v001  |  2026-08-04 14:30:10 UTC  |  12.50 KB ← LATEST

==============================================================================================
Enter the number of the version you want to download:
(0 = Download latest versions of all files)

Your choice: 2
```

### List Versions Only

**Using Batch File:**
```cmd
list-versions-py.bat
```

**Or from Command Line:**
```cmd
python download_versioned.py --list-only
```

Shows all available versions without downloading.

## Command Line Options

### Upload Script
```powershell
python upload_versioned.py [--config CONFIG_FILE]
```

**Options:**
- `--config CONFIG_FILE` - Path to config.json (default: config.json)

### Download Script
```powershell
python download_versioned.py [--config CONFIG_FILE] [--version VERSION_NUMBER] [--list-only]
```

**Options:**
- `--config CONFIG_FILE` - Path to config.json (default: config.json)
- `--version VERSION_NUMBER` - Download specific version (0 for latest, 1-999 for version number)
- `--list-only` - List versions without downloading

**Examples:**
```cmd
# Interactive menu
python download_versioned.py

# Download v002 without prompting
python download_versioned.py --version 2

# Download latest without prompting
python download_versioned.py --version 0

# List only
python download_versioned.py --list-only
```

## Version Manifest File

**Location:** `version-manifest.json` (auto-created in automation folder)

**Format:**
```json
{
  "exe": {
    "fileName": "GeoLogic.exe",
    "versions": [
      {
        "number": 1,
        "uploadDate": "2026-08-04T14:30:00Z",
        "remotePath": "versions/GeoLogic_v001.exe",
        "fileName": "GeoLogic.exe",
        "fileSize": 5242880,
        "googleFileId": "XXXXXXXXXXXX"
      },
      {
        "number": 2,
        "uploadDate": "2026-08-04T15:45:30Z",
        "remotePath": "versions/GeoLogic_v002.exe",
        "fileName": "GeoLogic.exe",
        "fileSize": 5282880,
        "googleFileId": "YYYYYYYYYYYY"
      }
    ]
  }
}
```

This file is:
- **Auto-created** by the upload script
- **Auto-updated** after each upload
- **Used by** download script to find available versions
- **Should be backed up** for version history

## Troubleshooting

### "Python is not installed or not in PATH"
**Solution:**
1. Install Python from https://www.python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Restart your computer
4. Run the batch file again

### "credentials.json not found"
**Solution:**
1. Go to https://console.cloud.google.com/
2. Create/select a project
3. Enable Google Drive API
4. Create OAuth 2.0 Desktop credentials
5. Download as JSON
6. Rename to `credentials.json`
7. Place in automation folder

### "folder_id is not configured"
**Solution:**
1. Open config.json
2. Go to your Google Drive folder
3. Copy the folder ID from the URL
4. Replace `YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE` with actual ID
5. Save config.json

### "version-manifest.json not found"
**Solution:**
1. Run the upload script first
2. It will create version-manifest.json
3. Then you can use the download script

### "Authentication failed"
**Solution:**
1. Delete `token.pickle` file
2. Run upload or download script again
3. You'll be prompted to authenticate in browser
4. This creates a new token.pickle

### "Failed to upload/download: Permission denied"
**Solution:**
1. Check Google Drive folder permissions
2. Make sure credentials have access to the folder
3. Try re-authenticating (delete token.pickle)

## Comparison: Python vs PowerShell

| Feature | Python | PowerShell |
|---------|--------|-----------|
| Dependencies | Python + Google API library | Windows + rclone |
| Setup Complexity | Medium (credentials needed) | Medium (rclone setup) |
| Speed | Good | Good |
| Features | Full versioning + manifest | Full versioning + manifest |
| Cross-platform | Yes (Python works on Mac/Linux) | Windows only |
| Interactive Menu | Yes, native Python | Yes, PowerShell prompt |
| Auto Install Deps | Yes, pip | No |

## Tips

1. **Test First**: Run upload script to verify config works
2. **Check Manifest**: Always check version-manifest.json is being created
3. **Keep Credentials Safe**: Don't share credentials.json
4. **Backup Manifest**: Keep version-manifest.json in version control
5. **Monitor Space**: Check Google Drive space with older retention periods

## Support

For issues:
1. Check config.json is valid JSON
2. Verify credentials.json in automation folder
3. Check Google Drive folder permissions
4. See batch file console output for error messages
5. Try command line version for more verbose output

---

**Version**: 1.0
**Last Updated**: 2026-08-04
