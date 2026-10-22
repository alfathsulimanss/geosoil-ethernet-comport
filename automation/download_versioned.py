#!/usr/bin/env python3
"""
Google Drive Download with Version Selection
Downloads GeoLogic build files from Google Drive with interactive version selection.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    from io import FileIO
except ImportError:
    print("❌ Required Google API libraries not installed.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# ============================================================================
# USER CONFIGURATION - Edit these paths if config.json and credentials.json 
# are in a different location
# ============================================================================
CONFIG_FILE = 'config.json'              # Path to config.json
CREDENTIALS_FILE_PATH = None             # Set to override credentials path (e.g., 'C:/path/to/credentials.json')
TOKEN_FILE_PATH = None                   # Set to override token.pickle path (e.g., 'C:/path/to/token.pickle')
# ============================================================================

# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
MANIFEST_FILE = 'version-manifest.json'

class Config:
    """Load and manage configuration"""
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        # Try the provided path first
        if os.path.exists(self.config_file):
            config_path = self.config_file
        else:
            # Try in script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, os.path.basename(self.config_file))
            
            if not os.path.exists(config_path):
                print(f"❌ Configuration file not found: {self.config_file}")
                print(f"   Checked: {self.config_file}")
                print(f"   Also checked: {config_path}")
                print("Please create config.json with your Google Drive settings.")
                sys.exit(1)
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

class GoogleDriveVersionedDownloader:
    def __init__(self, config):
        self.config = config
        self.folder_id = config.get('google_drive.folder_id')
        # Use override paths if set, otherwise use paths from config.json
        self.credentials_file = CREDENTIALS_FILE_PATH or config.get('google_drive.credentials_file')
        self.token_file = TOKEN_FILE_PATH or config.get('google_drive.token_file')
        self.manifest = self.load_manifest()
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        # Find credentials file (try provided path first, then script directory)
        cred_file = self.credentials_file
        if not os.path.exists(cred_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cred_file = os.path.join(script_dir, os.path.basename(self.credentials_file))
        
        if not os.path.exists(cred_file):
            print(f"❌ Credentials file not found: {self.credentials_file}")
            print("Download from Google Cloud Console and save as 'credentials.json'")
            sys.exit(1)
        
        # Find token file (try provided path first, then script directory)
        token_file = self.token_file
        if not os.path.exists(token_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            token_file = os.path.join(script_dir, os.path.basename(self.token_file))
        
        creds = None
        
        # Load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Successfully authenticated with Google Drive")
    
    def load_manifest(self):
        """Load version manifest from file"""
        if os.path.exists(MANIFEST_FILE):
            try:
                with open(MANIFEST_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def display_versions(self):
        """Display all available versions"""
        if not self.manifest:
            print("\n❌ No version manifest found. Run upload first.")
            return False
        
        print("\n" + "="*90)
        print("AVAILABLE VERSIONS")
        print("="*90)
        
        for file_type, file_info in self.manifest.items():
            print(f"\n📄 {file_info.get('fileName', file_type)}:")
            
            versions = file_info.get('versions', [])
            if not versions:
                print("   No versions available")
                continue
            
            # Sort by version number descending
            sorted_versions = sorted(versions, key=lambda x: x['number'], reverse=True)
            
            for version in sorted_versions:
                upload_date = datetime.fromisoformat(version['uploadDate'].replace('Z', '+00:00'))
                size_kb = round(version['fileSize'] / 1024, 2)
                version_str = f"v{version['number']:03d}"
                is_latest = version['number'] == sorted_versions[0]['number']
                latest_marker = " ← LATEST" if is_latest else ""
                
                print(f"   {version_str}  |  {upload_date.strftime('%Y-%m-%d %H:%M:%S')} UTC  |  {size_kb} KB{latest_marker}")
        
        print("\n" + "="*90)
        return True
    
    def get_version_choice(self):
        """Display interactive menu and get user choice"""
        if not self.manifest:
            print("\n❌ No version manifest found. Run upload first.")
            return None
        
        print("\n" + "="*90)
        print("SELECT VERSION TO DOWNLOAD")
        print("="*90)
        
        menu_items = []
        menu_index = 1
        
        for file_type, file_info in self.manifest.items():
            print(f"\n📄 {file_info.get('fileName', file_type)}:")
            
            versions = file_info.get('versions', [])
            sorted_versions = sorted(versions, key=lambda x: x['number'], reverse=True)
            
            for version in sorted_versions:
                upload_date = datetime.fromisoformat(version['uploadDate'].replace('Z', '+00:00'))
                size_kb = round(version['fileSize'] / 1024, 2)
                version_str = f"v{version['number']:03d}"
                is_latest = version['number'] == sorted_versions[0]['number']
                latest_marker = " ← LATEST" if is_latest else ""
                
                print(f"  [{menu_index}] {version_str}  |  {upload_date.strftime('%Y-%m-%d %H:%M:%S')} UTC  |  {size_kb} KB{latest_marker}")
                
                menu_items.append({
                    'index': menu_index,
                    'file_type': file_type,
                    'version_number': version['number']
                })
                menu_index += 1
        
        print("\n" + "="*90)
        print("Enter the number of the version you want to download:")
        print("(0 = Download latest versions of all files)")
        
        try:
            choice = input("\nYour choice: ").strip()
            
            if choice == "0":
                return "latest"
            
            choice_num = int(choice)
            
            for item in menu_items:
                if item['index'] == choice_num:
                    return item['version_number']
            
            print("❌ Invalid choice! Please enter a valid number.")
            return self.get_version_choice()
            
        except ValueError:
            print("❌ Invalid input! Please enter a number.")
            return self.get_version_choice()
    
    def download_file(self, file_type, version_number, destination):
        """Download a specific file version"""
        if file_type not in self.manifest:
            print(f"❌ File type not found: {file_type}")
            return False
        
        versions = self.manifest[file_type].get('versions', [])
        
        # Find the specific version
        target_version = None
        if version_number == "latest":
            # Get latest version
            if versions:
                target_version = max(versions, key=lambda x: x['number'])
        else:
            # Find specific version number
            for version in versions:
                if version['number'] == version_number:
                    target_version = version
                    break
        
        if not target_version:
            print(f"❌ Version not found for {file_type}")
            return False
        
        file_id = target_version.get('googleFileId')
        if not file_id:
            print(f"❌ File ID not found in manifest for {file_type} v{target_version['number']:03d}")
            return False
        
        # Handle destination path - can be directory or full file path
        destination = destination.strip()
        if not destination:
            print(f"❌ Destination path is empty for {file_type}")
            return False
        
        # If destination is a directory (doesn't end with common file extension), add filename
        if os.path.isdir(destination) or (not destination.endswith(('.exe', '.aliases', '.ini', '.py', '.bat')) and not '.' in os.path.basename(destination)):
            # It's a directory
            filename = self.manifest[file_type]['fileName']
            destination = os.path.join(destination, filename)
        
        # Create destination directory
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except Exception as e:
                print(f"❌ Failed to create destination directory: {dest_dir}")
                print(f"   Error: {str(e)}")
                return False
        
        try:
            print(f"\n📥 Downloading: {self.manifest[file_type]['fileName']}")
            print(f"   Version: v{target_version['number']:03d}")
            print(f"   Destination: {destination}")
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            
            with open(destination, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"   Progress: {int(status.progress() * 100)}%")
            
            file_size = os.path.getsize(destination)
            size_kb = round(file_size / 1024, 2)
            print(f"✅ Downloaded successfully ({size_kb} KB)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Download GeoLogic files from Google Drive with version selection')
    parser.add_argument('--config', default=CONFIG_FILE, help='Path to config.json')
    parser.add_argument('--version', type=int, default=None, help='Specific version number to download (0 for latest)')
    parser.add_argument('--list-only', action='store_true', help='Only list versions, do not download')
    
    args = parser.parse_args()
    
    print("="*90)
    print("  GeoLogic Google Drive Versioned Download (Python)")
    print("="*90)
    
    # Load configuration
    config = Config(args.config)
    
    print(f"\n📋 Configuration loaded from: {args.config}")
    
    # Initialize downloader
    downloader = GoogleDriveVersionedDownloader(config)
    
    # Display versions
    if not downloader.display_versions():
        sys.exit(1)
    
    # If list-only, exit here
    if args.list_only:
        sys.exit(0)
    
    # Get version choice
    if args.version is not None:
        if args.version == 0:
            version_to_download = "latest"
        else:
            version_to_download = args.version
    else:
        version_to_download = downloader.get_version_choice()
    
    if version_to_download is None:
        print("\n❌ Invalid version choice")
        sys.exit(1)
    
    print(f"\nDownloading version: {version_to_download if version_to_download != 'latest' else 'LATEST'}")
    
    # Download files
    destinations = {
        'exe': config.get('paths.exe_destination'),
        'aliases': config.get('paths.aliases_destination'),
        'ini': config.get('paths.ini_destination')
    }
    
    downloaded_count = 0
    total_files = 0
    
    for file_type, destination in destinations.items():
        if file_type in downloader.manifest:
            total_files += 1
            
            if downloader.download_file(file_type, version_to_download, destination):
                downloaded_count += 1
    
    # Summary
    print("\n" + "="*90)
    print("Download Summary:")
    print(f"Successfully downloaded: {downloaded_count}/{total_files} files")
    print("="*90)
    
    if downloaded_count == total_files:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
