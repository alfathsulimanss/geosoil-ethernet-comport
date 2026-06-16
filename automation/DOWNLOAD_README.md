# GeoLogic Download Automation

This folder contains scripts to download the latest GeoLogic application files from Google Drive to any target PC.

## Files Created

### Download Scripts
- `download-from-gdrive.ps1` - PowerShell script that downloads files using rclone
- `download-build.bat` - Batch wrapper that configures paths and calls the PowerShell script
- `download-launcher.bat` - Simple launcher for the download process

### Upload Scripts (for reference)
- `upload-to-gdrive.ps1` - PowerShell script that uploads files using rclone
- `upload-build.bat` - Batch wrapper for uploads
- `upload-launcher.bat` - Simple launcher for uploads (in project root)

## Setup for Target PC (where you want to install GeoLogic)

### 1. Install rclone
Download and install rclone from: https://rclone.org/downloads/

### 2. Configure Google Drive Access
Run this command and follow the prompts:
```bash
rclone config
```
- Choose "New remote"
- Name it `geosoilgdrive` (or update the scripts if you use a different name)
- Choose "Google Drive" as the storage type
- Leave client_id and client_secret blank (uses default)
- Choose appropriate scope (full access recommended)
- Complete the OAuth authentication

### 3. Copy Automation Scripts
Copy the `automation` folder to your target PC.

### 4. Edit Destination Paths
Edit `download-build.bat` and change these lines to match where you want files installed:
```batch
set "EXE_DEST=C:\Program Files\GeoLogic\GeoLogic.exe"
set "ALIASES_DEST=C:\Program Files\GeoLogic\GEOSOIL New Ethernet.aliases"
set "INI_DEST=C:\Program Files\GeoLogic\GeoLogic.ini"
```

## Usage

### Option 1: Run the launcher
```bash
cd automation
download-launcher.bat
```

### Option 2: Run the batch directly
```bash
cd automation
download-build.bat
```

### Option 3: Run PowerShell directly with custom paths
```powershell
powershell -ExecutionPolicy Bypass -File "download-from-gdrive.ps1" -ExeDestination "C:\MyApp\GeoLogic.exe" -AliasesDestination "C:\MyApp\GEOSOIL New Ethernet.aliases" -IniDestination "C:\MyApp\GeoLogic.ini" -RcloneRemote "geosoilgdrive"
```

## What Gets Downloaded

The script downloads these files from the `EXE` folder in Google Drive:
- `GeoLogic.exe` - The main application executable
- `GEOSOIL New Ethernet.aliases` - LabVIEW aliases configuration
- `GeoLogic.ini` - Application configuration file

## Logs

Download logs are created in the `automation/logs/` directory:
- `rclone-download-YYYYMMDD-HHMMSS-out.log` - rclone stdout
- `rclone-download-YYYYMMDD-HHMMSS-err.log` - rclone stderr

## Troubleshooting

### rclone not found
- Make sure rclone is installed and in your PATH
- Or set the RCLONE_PATH environment variable to point to rclone.exe

### Access denied / authentication errors
- Re-run `rclone config` to refresh authentication
- Make sure the remote name matches what's configured

### Files not found in Google Drive
- Verify the upload process completed successfully
- Check that files exist in the Google Drive EXE folder
- Use `rclone ls geosoilgdrive:EXE/` to list available files

## Examples

### Download to custom locations
```powershell
powershell -ExecutionPolicy Bypass -File "download-from-gdrive.ps1" `
  -ExeDestination "D:\Applications\GeoLogic\GeoLogic.exe" `
  -AliasesDestination "D:\Applications\GeoLogic\GEOSOIL New Ethernet.aliases" `
  -IniDestination "D:\Applications\GeoLogic\GeoLogic.ini" `
  -RcloneRemote "geosoilgdrive"
```

### Use different rclone remote
```powershell
powershell -ExecutionPolicy Bypass -File "download-from-gdrive.ps1" `
  -RcloneRemote "mydrive" `
  -ExeDestination "C:\Program Files\GeoLogic\GeoLogic.exe"
```