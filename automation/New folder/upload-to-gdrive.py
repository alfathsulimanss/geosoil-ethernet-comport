#!/usr/bin/env python3
"""
Google Drive Upload Automation for GeoLogic Build
Alternative Python implementation using Google Drive API
"""

import os
import sys
import json
import argparse
from pathlib import Path
import mimetypes

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
except ImportError:
    print("Required Google API libraries not installed.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# Google Drive API configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'credentials.json'  # Download from Google Cloud Console
TOKEN_FILE = 'token.pickle'

class GoogleDriveUploader:
    def __init__(self, folder_id):
        self.folder_id = folder_id
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    print(f"ERROR: {CREDENTIALS_FILE} not found!")
                    print("Please download credentials from Google Cloud Console")
                    print("and save as 'credentials.json' in the project directory.")
                    sys.exit(1)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
        print("✓ Successfully authenticated with Google Drive")
    
    def upload_file(self, file_path, remote_name=None, description=""):
        """Upload a file to Google Drive"""
        if not os.path.exists(file_path):
            print(f"✗ File not found: {file_path}")
            return False
        
        if not remote_name:
            remote_name = os.path.basename(file_path)
        
        print(f"Uploading: {remote_name}...")
        
        try:
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # File metadata
            file_metadata = {
                'name': remote_name,
                'parents': [self.folder_id],
                'description': description
            }
            
            # Upload file
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"  Progress: {int(status.progress() * 100)}%")
            
            print(f"✓ Successfully uploaded: {remote_name}")
            print(f"  File ID: {response.get('id')}")
            print(f"  View URL: {response.get('webViewLink')}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to upload {remote_name}: {str(e)}")
            return False
    
    def list_folder_contents(self):
        """List contents of the target folder"""
        try:
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                fields="files(id, name, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                print(f"\nCurrent files in Google Drive folder:")
                for file in files:
                    print(f"  - {file['name']} (Modified: {file['modifiedTime']})")
            else:
                print("No files found in the target folder.")
                
        except Exception as e:
            print(f"Error listing folder contents: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Upload GeoLogic build files to Google Drive')
    parser.add_argument('--build-path', 
                       default=r'C:\Users\ralfsuliman\Desktop\EXE\Geosoil New Controller Multi Comm',
                       help='Path to the build output directory')
    parser.add_argument('--project-path', 
                       default=r'f:\Geosoil Drive\geosoil-ethernet-comport',
                       help='Path to the project directory')
    parser.add_argument('--folder-id', 
                       required=True,
                       help='Google Drive folder ID (get from URL)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("  GeoLogic Google Drive Upload Tool")
    print("="*60)
    print(f"Build Path: {args.build_path}")
    print(f"Project Path: {args.project_path}")
    print(f"Folder ID: {args.folder_id}")
    print()
    
    # Initialize uploader
    uploader = GoogleDriveUploader(args.folder_id)
    
    # Files to upload
    files_to_upload = []
    
    # EXE file
    exe_path = os.path.join(args.build_path, 'GeoLogic.exe')
    if os.path.exists(exe_path):
        files_to_upload.append({
            'path': exe_path,
            'name': 'GeoLogic.exe',
            'description': 'GeoLogic Application Executable'
        })
    else:
        print(f"WARNING: EXE file not found: {exe_path}")
    
    # Aliases file
    aliases_path = os.path.join(args.project_path, 'GEOSOIL New Ethernet.aliases')
    if os.path.exists(aliases_path):
        files_to_upload.append({
            'path': aliases_path,
            'name': 'GEOSOIL New Ethernet.aliases',
            'description': 'LabVIEW Aliases Configuration File'
        })
    else:
        print(f"WARNING: Aliases file not found: {aliases_path}")
    
    # INI files
    build_path = Path(args.build_path)
    for ini_file in build_path.glob('*.ini'):
        files_to_upload.append({
            'path': str(ini_file),
            'name': ini_file.name,
            'description': 'Configuration INI File'
        })
    
    if not files_to_upload:
        print("ERROR: No files found to upload!")
        sys.exit(1)
    
    print(f"Found {len(files_to_upload)} files to upload:")
    for file_info in files_to_upload:
        print(f"  - {file_info['name']}")
    print()
    
    # Upload files
    successful_uploads = 0
    total_files = len(files_to_upload)
    
    for file_info in files_to_upload:
        success = uploader.upload_file(
            file_info['path'],
            file_info['name'],
            file_info['description']
        )
        if success:
            successful_uploads += 1
        print()
    
    # Summary
    print("="*60)
    print("Upload Summary:")
    print(f"Successfully uploaded: {successful_uploads}/{total_files} files")
    
    if successful_uploads == total_files:
        print("✓ All files uploaded successfully!")
    else:
        print("⚠ Some files failed to upload.")
    
    # List current folder contents
    uploader.list_folder_contents()
    
    print("\nGoogle Drive folder URL:")
    print(f"https://drive.google.com/drive/folders/{args.folder_id}")
    print("="*60)

if __name__ == '__main__':
    main()