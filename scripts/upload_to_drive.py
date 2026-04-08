"""Upload Excel files to Google Drive.

This script uploads the generated Excel files to Google Drive automatically.
Used by GitHub Actions workflow.
"""

import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_drive():
    """Upload Excel files from output/ to Google Drive.
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Get credentials from environment
    key_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not key_json or not folder_id:
        print("ERROR: Missing Google Drive credentials")
        print("  - GOOGLE_SERVICE_ACCOUNT_KEY not set")
        print("  - GOOGLE_DRIVE_FOLDER_ID not set")
        return False
    
    try:
        # Parse service account key
        key_dict = json.loads(key_json)
        
        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            key_dict,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build Drive service
        service = build('drive', 'v3', credentials=credentials)
        
        # Find and upload Excel files
        output_dir = Path('output')
        if not output_dir.exists():
            print("ERROR: No output directory found")
            return False
        
        excel_files = list(output_dir.glob('*.xlsx'))
        if not excel_files:
            print("ERROR: No Excel files found in output/")
            return False
        
        print(f"Found {len(excel_files)} Excel file(s) to upload")
        
        for excel_file in excel_files:
            print(f"\nUploading {excel_file.name}...")
            
            try:
                # Check if file already exists in Drive
                query = f"name='{excel_file.name}' and '{folder_id}' in parents and trashed=false"
                results = service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id)',
                    pageSize=1
                ).execute()
                files = results.get('files', [])
                
                if files:
                    # Update existing file
                    file_id = files[0]['id']
                    media = MediaFileUpload(
                        str(excel_file),
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    service.files().update(fileId=file_id, media_body=media).execute()
                    print(f"  ✓ Updated {excel_file.name}")
                else:
                    # Create new file
                    file_metadata = {
                        'name': excel_file.name,
                        'parents': [folder_id]
                    }
                    media = MediaFileUpload(
                        str(excel_file),
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    print(f"  ✓ Uploaded {excel_file.name}")
            
            except Exception as e:
                print(f"  ✗ Error uploading {excel_file.name}: {str(e)}")
                return False
        
        print("\n✓ All files uploaded successfully!")
        return True
    
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON in GOOGLE_SERVICE_ACCOUNT_KEY")
        return False
    
    except Exception as e:
        print(f"ERROR uploading to Google Drive: {str(e)}")
        return False


if __name__ == '__main__':
    success = upload_to_drive()
    exit(0 if success else 1)
