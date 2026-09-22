#!/usr/bin/env python3
"""
Google Drive Upload with Versioning
Uploads GeoLogic build files to Google Drive with sequential versioning (v001, v002, etc.)
Automatically removes versions older than the retention period.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import mimetypes

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
except ImportError:
    print("❌ Required Google API libraries not installed.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CONFIG_FILE = 'config.json'
MANIFEST_FILE = 'version-manifest.json'

class Config:
    """Load and manage configuration"""
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        if not os.path.exists(self.config_file):
            print(f"❌ Configuration file not found: {self.config_file}")
            print("Please create config.json with your Google Drive settings.")
            sys.exit(1)
        
        try:
            with open(self.config_file, 'r') as f:
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

class GoogleDriveVersionedUploader:
    def __init__(self, config):
        self.config = config
        self.folder_id = config.get('google_drive.folder_id')
        self.credentials_file = config.get('google_drive.credentials_file')
        self.token_file = config.get('google_drive.token_file')
        self.retention_days = config.get('versioning.retention_days', 30)
        self.manifest = self.load_manifest()
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        if not os.path.exists(self.credentials_file):
            print(f"❌ Credentials file not found: {self.credentials_file}")
            print("Download from Google Cloud Console and save as 'credentials.json'")
            sys.exit(1)
        
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
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
    
    def save_manifest(self):
        """Save version manifest to file"""
        with open(MANIFEST_FILE, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def get_next_version(self, file_type):
        """Get the next version number for a file type"""
        if file_type not in self.manifest or 'versions' not in self.manifest[file_type]:
            return 1
        
        versions = self.manifest[file_type]['versions']
        if not versions:
            return 1
        
        max_version = max(v['number'] for v in versions)
        return max_version + 1
    
    def upload_file(self, local_path, file_type, remote_name, description):
        """Upload a file to Google Drive"""
        if not os.path.exists(local_path):
            print(f"❌ File not found: {local_path}")
            return False
        
        # Get next version number
        next_version = self.get_next_version(file_type)
        version_str = f"v{next_version:03d}"
        name_parts = remote_name.rsplit('.', 1)
        if len(name_parts) == 2:
            versioned_name = f"{name_parts[0]}_{version_str}.{name_parts[1]}"
        else:
            versioned_name = f"{remote_name}_{version_str}"
        
        print(f"\n📤 Uploading: {remote_name}")
        print(f"   Version: {version_str} ({versioned_name})")
        
        try:
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(local_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # File metadata
            file_metadata = {
                'name': versioned_name,
                'parents': [self.folder_id],
                'description': f"{description} - {version_str}"
            }
            
            # Upload file
            media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
            
            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,size'
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"   Progress: {int(status.progress() * 100)}%")
            
            print(f"✅ Successfully uploaded: {remote_name}")
            
            # Record version in manifest
            if file_type not in self.manifest:
                self.manifest[file_type] = {
                    'fileName': remote_name,
                    'versions': []
                }
            
            version_record = {
                'number': next_version,
                'uploadDate': datetime.utcnow().isoformat() + 'Z',
                'remotePath': f"versions/{versioned_name}",
                'fileName': remote_name,
                'fileSize': int(response.get('size', os.path.getsize(local_path))),
                'googleFileId': response.get('id')
            }
            
            self.manifest[file_type]['versions'].append(version_record)
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload {remote_name}: {str(e)}")
            return False
    
    def cleanup_old_versions(self):
        """Remove versions older than retention period"""
        cutoff_date = (datetime.utcnow() - timedelta(days=self.retention_days)).isoformat()
        
        for file_type in list(self.manifest.keys()):
            versions = self.manifest[file_type].get('versions', [])
            versions_to_keep = []
            files_to_delete = []
            
            for version in versions:
                upload_date = version.get('uploadDate', '')
                if upload_date > cutoff_date:
                    versions_to_keep.append(version)
                else:
                    files_to_delete.append(version)
            
            self.manifest[file_type]['versions'] = versions_to_keep
            
            # Delete old files from Google Drive
            if files_to_delete:
                print(f"\n🗑️  Cleaning up old versions from {file_type}...")
                for file_to_delete in files_to_delete:
                    try:
                        file_id = file_to_delete.get('googleFileId')
                        if file_id:
                            self.service.files().delete(fileId=file_id).execute()
                            print(f"   Removed: v{file_to_delete['number']:03d} ({file_to_delete.get('uploadDate', 'N/A')})")
                    except Exception as e:
                        print(f"   Failed to delete: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Upload GeoLogic build files to Google Drive with versioning')
    parser.add_argument('--config', default=CONFIG_FILE, help='Path to config.json')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  GeoLogic Google Drive Versioned Upload (Python)")
    print("="*70)
    
    # Load configuration
    config = Config(args.config)
    
    print(f"\n📋 Configuration loaded from: {args.config}")
    print(f"   Folder ID: {config.get('google_drive.folder_id')}")
    print(f"   Retention: {config.get('versioning.retention_days')} days")
    
    # Initialize uploader
    uploader = GoogleDriveVersionedUploader(config)
    
    # Prepare files to upload
    build_path = config.get('paths.build_path')
    files_config = config.get('files_to_upload', {})
    files_to_upload = []
    
    for file_type, file_info in files_config.items():
        local_name = file_info.get('local_name')
        file_path = os.path.join(build_path, local_name)
        
        if os.path.exists(file_path):
            files_to_upload.append({
                'type': file_type,
                'path': file_path,
                'remote_name': file_info.get('remote_name', local_name),
                'description': file_info.get('description', '')
            })
        else:
            print(f"⚠️  File not found: {file_path}")
    
    if not files_to_upload:
        print("\n❌ No files found to upload!")
        sys.exit(1)
    
    print(f"\n📁 Found {len(files_to_upload)} files to upload:")
    for f in files_to_upload:
        print(f"   - {f['remote_name']}")
    
    # Upload files
    uploaded_count = 0
    for file_info in files_to_upload:
        if uploader.upload_file(
            file_info['path'],
            file_info['type'],
            file_info['remote_name'],
            file_info['description']
        ):
            uploaded_count += 1
    
    # Cleanup old versions
    print()
    uploader.cleanup_old_versions()
    
    # Save manifest
    uploader.save_manifest()
    
    # Summary
    print("\n" + "="*70)
    print("Upload Summary:")
    print(f"Successfully uploaded: {uploaded_count}/{len(files_to_upload)} files")
    print(f"Manifest saved to: {MANIFEST_FILE}")
    print("="*70)
    
    if uploaded_count == len(files_to_upload):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
