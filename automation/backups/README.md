# Backup Files - August 4, 2026

This folder contains backups of the original (non-versioned) upload and download scripts.

## Backed Up Files

- **upload-to-gdrive.ps1.backup** - Original PowerShell upload script (replaces files, no versioning)
- **download-from-gdrive.ps1.backup** - Original PowerShell download script (fixed paths, no version selection)
- **upload-build.bat.backup** - Original batch launcher for upload
- **download-launcher.bat.backup** - Original batch launcher for download
- **upload-to-gdrive.py.backup** - Original Python Google Drive API implementation

## Why These Backups Exist

The versioning system was implemented on August 4, 2026, to:
- Create sequential versions of uploaded files (v001, v002, etc.)
- Allow downloading specific versions from history
- Automatically cleanup versions older than 30 days
- Track all uploaded versions in a local manifest

The original scripts replaced files instead of creating versions.

## When to Use

Use these backup files if you need to:
1. **Revert to the original behavior** - Copy a `.backup` file and remove the `.backup` extension
2. **Compare with the new system** - See what changed between old and new implementations
3. **Understand the migration** - Reference the original code for learning purposes

## Migration Path

If you want to go back to the old system:

```powershell
# Copy backup to restore original
Copy-Item "backups\upload-to-gdrive.ps1.backup" -Destination "upload-to-gdrive.ps1" -Force
Copy-Item "backups\download-from-gdrive.ps1.backup" -Destination "download-from-gdrive.ps1" -Force
```

Then use the original batch files:
- `upload-build.bat`
- `download-launcher.bat`

## Versioned System Files

The new versioning scripts are:
- **upload-to-gdrive-versioned.ps1** - Upload with sequential versioning
- **download-from-gdrive-versioned.ps1** - Download with version selection
- **upload-build-versioned.bat** - Launcher for versioned uploads
- **download-launcher-versioned.bat** - Launcher for versioned downloads
- **list-versions.bat** - Show all available versions
- **version-manifest.json** - Auto-created manifest tracking all versions

---

**Created**: 2026-08-04
**Backup Date**: Before versioning system implementation
