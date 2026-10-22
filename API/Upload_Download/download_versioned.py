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
CONFIG_FILE = 'config.json'              # Path to config.json (relative or absolute)
CREDENTIALS_FILE_PATH = None             # Set to override credentials path (e.g., 'F:/path/to/credentials.json')
TOKEN_FILE_PATH = None                   # Set to override token.pickle path (e.g., 'F:/path/to/token.pickle')
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

def parse_version(version_dict):
    """
    Parse version from manifest entry.
    Handles both old format (number) and new format (version string like v1.0.1.227)
    Returns tuple of (version_string, sort_key)
    
    Sort key prioritizes new semantic versions over old sequential versions:
    - Semantic versions (v1.0.1.227): get a high base value for proper sorting
    - Sequential versions (v001): get lower values
    """
    # New format: 'version' field contains string like 'v1.0.1.227'
    if 'version' in version_dict:
        version_str = version_dict['version']
        # Remove 'v' prefix and parse as version tuple for proper sorting
        version_clean = version_str.lstrip('v')
        try:
            # Split and convert to integers, pad to 4 elements for consistency
            parts = [int(x) for x in version_clean.split('.')]
            # Pad with zeros if needed
            while len(parts) < 4:
                parts.append(0)
            # Use a high base value (10000) to sort semantic versions above sequential ones
            version_tuple = (10000,) + tuple(parts[:4])
        except ValueError:
            version_tuple = (10000, 0, 0, 0, 0)
        return version_str, version_tuple
    
    # Old format: 'number' field contains numeric version
    if 'number' in version_dict:
        num = version_dict['number']
        version_str = f"v{num:03d}"
        # Use a low base value (0) to sort sequential versions below semantic ones
        return version_str, (0, num, 0, 0, 0)
    
    return "unknown", (0, 0, 0, 0, 0)

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
        # Load files from Google Drive
        self.drive_files = {}
        self.load_files_from_drive()
    
    def load_files_from_drive(self):
        """Load actual files from Google Drive folder"""
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id,name,createdTime,size,mimeType)',
                pageSize=100
            ).execute()
            
            files = results.get('files', [])
            
            # Organize files by type
            for file in files:
                name = file.get('name', '')
                # Parse version from filename
                if 'GeoLogic_' in name:
                    # Extract version and file type
                    parts = name.split('_')
                    if len(parts) >= 2:
                        version = '_'.join(parts[1:]).rsplit('.', 1)[0]  # e.g., "v1.0.1.227"
                        
                        if name.endswith('.exe'):
                            file_type = 'exe'
                        elif name.endswith('.aliases'):
                            file_type = 'aliases'
                        elif name.endswith('.ini'):
                            file_type = 'ini'
                        else:
                            continue
                        
                        if file_type not in self.drive_files:
                            self.drive_files[file_type] = []
                        
                        self.drive_files[file_type].append({
                            'name': name,
                            'version': version,
                            'fileId': file.get('id'),
                            'fileSize': int(file.get('size', 0)),
                            'createdTime': file.get('createdTime', ''),
                            'mimeType': file.get('mimeType', '')
                        })
        except Exception as e:
            print(f"⚠️  Warning: Could not load files from Google Drive: {str(e)}")
            print("   Falling back to manifest file...")
    
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
        """Display all available exe versions from Google Drive"""
        if 'exe' not in self.drive_files or not self.drive_files['exe']:
            print("\n❌ No exe versions found on Google Drive.")
            return False
        
        print("\n" + "="*90)
        print("AVAILABLE VERSIONS (from Google Drive)")
        print("="*90)
        
        exe_files = self.drive_files['exe']
        sorted_files = sorted(exe_files, key=lambda x: x['createdTime'], reverse=True)
        
        print()
        for idx, file in enumerate(sorted_files, 1):
            size_kb = round(file['fileSize'] / 1024, 2)
            created_time = file['createdTime'].replace('T', ' ').replace('Z', '').split('.')[0]
            version_str = file['version']
            latest_marker = " ← LATEST" if idx == 1 else ""
            
            print(f"{file['name']}")
            print(f"  {version_str} | {size_kb} KB | {created_time} UTC{latest_marker}")
        
        print("\n" + "="*90)
        return True
    
    def get_version_choice(self):
        """Display interactive menu and get user choice - exe versions only"""
        if 'exe' not in self.drive_files or not self.drive_files['exe']:
            print("\n❌ No exe versions found on Google Drive.")
            return None
        
        print("\n" + "="*90)
        print("SELECT VERSION TO DOWNLOAD")
        print("="*90)
        
        # Get all exe versions sorted by creation time descending
        exe_files = self.drive_files['exe']
        sorted_files = sorted(exe_files, key=lambda x: x['createdTime'], reverse=True)
        
        print()
        menu_items = []
        
        for idx, file in enumerate(sorted_files, 1):
            size_kb = round(file['fileSize'] / 1024, 2)
            created_time = file['createdTime'].replace('T', ' ').replace('Z', '').split('.')[0]
            version_str = file['version']
            latest_marker = " ← LATEST" if idx == 1 else ""
            
            print(f"[{idx}] {file['name']}")
            print(f"    {version_str} | {size_kb} KB | {created_time} UTC{latest_marker}")
            
            menu_items.append({
                'index': idx,
                'file_info': file
            })
        
        print("\n" + "="*90)
        print("Enter the number of the version you want to download:")
        print("(0 = Download latest version)")
        
        try:
            choice = input("\nYour choice: ").strip()
            
            if choice == "0":
                return "latest"
            
            choice_num = int(choice)
            
            for item in menu_items:
                if item['index'] == choice_num:
                    return item['file_info']
            
            print("❌ Invalid choice! Please enter a valid number.")
            return self.get_version_choice()
            
        except ValueError:
            print("❌ Invalid input! Please enter a number.")
            return self.get_version_choice()
    
    def download_file(self, file_type, version_selection, destination):
        """Download a specific file version with correct filename"""
        # Handle different version_selection types
        if version_selection == "latest":
            # Get latest from drive_files
            if file_type in self.drive_files and self.drive_files[file_type]:
                sorted_files = sorted(self.drive_files[file_type], key=lambda x: x['createdTime'], reverse=True)
                file_info = sorted_files[0]
            else:
                print(f"❌ No versions found for {file_type}")
                return False
        elif isinstance(version_selection, dict):
            # Direct file info (specific file selected)
            file_info = version_selection
        else:
            print(f"❌ Invalid version selection")
            return False
        
        file_id = file_info.get('fileId')
        version_str = file_info.get('version', 'unknown')
        
        if not file_id:
            print(f"❌ File ID not found for {file_type} {version_str}")
            return False
        
        # Handle destination path
        destination = destination.strip()
        if not destination:
            print(f"❌ Destination path is empty for {file_type}")
            return False
        
        # Determine the final filename based on file_type
        final_filename = f"GeoLogic.{file_type}"
        
        # If destination is a directory, add the final filename
        if os.path.isdir(destination):
            final_path = os.path.join(destination, final_filename)
        elif not '.' in os.path.basename(destination):
            # Destination is a directory path without trailing slash
            final_path = os.path.join(destination, final_filename)
        else:
            # Destination is a full file path
            final_path = destination
        
        # Create destination directory
        dest_dir = os.path.dirname(final_path)
        if dest_dir and not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except Exception as e:
                print(f"❌ Failed to create destination directory: {dest_dir}")
                print(f"   Error: {str(e)}")
                return False
        
        try:
            print(f"   Destination: {final_path}")
            
            request = self.service.files().get_media(fileId=file_id)
            
            with open(final_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"   Progress: {int(status.progress() * 100)}%")
            
            file_size = os.path.getsize(final_path)
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
    parser.add_argument('--destination', default=None, help='Destination folder for downloaded files (overrides config.json paths)')
    
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
    
    # Determine if downloading specific version or latest of all
    if isinstance(version_to_download, dict):
        # User selected a specific file
        selected_file = version_to_download
        selected_version = selected_file.get('version')  # e.g., "v1.0.1.227"
        
        print(f"\nDownloading version: {selected_version} (all files)")
        
        # Find all files for this version
        files_to_download = {}
        for file_type, files in downloader.drive_files.items():
            for file in files:
                if file.get('version') == selected_version:
                    files_to_download[file_type] = file
                    break
        
        if not files_to_download:
            print(f"❌ No files found for version {selected_version}")
            sys.exit(1)
        
        downloaded_count = 0
        total_files = len(files_to_download)
        
        for file_type, file_info in files_to_download.items():
            # Get destination for this file type
            if args.destination:
                destination = args.destination
            else:
                destination_map = {
                    'exe': config.get('paths.exe_destination'),
                    'aliases': config.get('paths.aliases_destination'),
                    'ini': config.get('paths.ini_destination')
                }
                destination = destination_map.get(file_type)
            
            if destination:
                print(f"\n📥 Downloading: {file_info.get('name')} ({file_type})")
                print(f"   Version: {selected_version}")
                
                if downloader.download_file(file_type, file_info, destination):
                    downloaded_count += 1
        
        # Summary
        print("\n" + "="*90)
        print("Download Summary:")
        print(f"Successfully downloaded: {downloaded_count}/{total_files} files for {selected_version}")
        print("="*90)
        
        if downloaded_count == total_files:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # User selected "latest" - download all files with latest version
        print(f"\nDownloading latest versions of all files...")
        
        if args.destination:
            print(f"📁 Download destination: {args.destination}")
        
        downloaded_count = 0
        total_files = 0
        
        # Get file types from drive_files
        file_types = set(downloader.drive_files.keys())
        
        for file_type in file_types:
            if args.destination:
                destination = args.destination
            else:
                # Use paths from config.json
                destination_map = {
                    'exe': config.get('paths.exe_destination'),
                    'aliases': config.get('paths.aliases_destination'),
                    'ini': config.get('paths.ini_destination')
                }
                destination = destination_map.get(file_type)
            
            if destination:
                total_files += 1
                if downloader.download_file(file_type, "latest", destination):
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
