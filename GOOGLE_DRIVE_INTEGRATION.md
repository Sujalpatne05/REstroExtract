# Google Drive Integration Guide

## Overview

This guide shows how to automatically upload your Excel files to Google Drive so your sir can view them online without downloading.

---

## What You'll Get

✅ Excel files automatically uploaded to Google Drive daily
✅ Your sir can view/download anytime from Google Drive link
✅ No manual uploads needed
✅ Completely free

---

## STEP 1: Create Google Service Account

### 1.1 Go to Google Cloud Console

Open: https://console.cloud.google.com/

### 1.2 Create New Project

1. Click "Select a Project" (top left)
2. Click "NEW PROJECT"
3. Name: `FSSAI Restaurant Scraper`
4. Click "CREATE"
5. Wait for project to be created

### 1.3 Enable Google Drive API

1. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com
2. Click "ENABLE"
3. Wait for it to enable

### 1.4 Create Service Account

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "CREATE SERVICE ACCOUNT"
3. Fill in:
   - **Service account name**: `fssai-scraper`
   - **Service account ID**: (auto-filled)
4. Click "CREATE AND CONTINUE"
5. Click "CONTINUE" (skip optional steps)
6. Click "DONE"

### 1.5 Create Key

1. Click the service account you just created
2. Go to "KEYS" tab
3. Click "ADD KEY" → "Create new key"
4. Choose "JSON"
5. Click "CREATE"
6. A JSON file will download - **SAVE THIS FILE SAFELY**

---

## STEP 2: Create Google Drive Folder

### 2.1 Go to Google Drive

Open: https://drive.google.com

### 2.2 Create Folder

1. Click "New" (left side)
2. Click "Folder"
3. Name: `FSSAI Restaurant Data`
4. Click "Create"

### 2.3 Share with Service Account

1. Right-click the folder
2. Click "Share"
3. Copy the email from your JSON file (looks like: `fssai-scraper@project-id.iam.gserviceaccount.com`)
4. Paste it in the share dialog
5. Give "Editor" permission
6. Click "Share"

### 2.4 Get Folder ID

1. Open the folder
2. Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
3. Copy the `FOLDER_ID_HERE` part
4. Save it somewhere

---

## STEP 3: Add Secret to GitHub

### 3.1 Go to Your Repository

Open: https://github.com/YOUR-USERNAME/fssai-restaurant-scraper

### 3.2 Go to Settings

1. Click "Settings" tab
2. Click "Secrets and variables" (left menu)
3. Click "Actions"

### 3.3 Add Google Service Account Key

1. Click "New repository secret"
2. Name: `GOOGLE_SERVICE_ACCOUNT_KEY`
3. Value: Copy the entire contents of your JSON file
4. Click "Add secret"

### 3.4 Add Google Drive Folder ID

1. Click "New repository secret"
2. Name: `GOOGLE_DRIVE_FOLDER_ID`
3. Value: Paste your folder ID from Step 2.4
4. Click "Add secret"

---

## STEP 4: Update GitHub Actions Workflow

### 4.1 Edit Workflow File

1. Go to your repository
2. Click `.github/workflows/scraper.yml`
3. Click the edit button (pencil icon)
4. Replace the entire content with this:

```yaml
name: FSSAI Restaurant Scraper

on:
  schedule:
    - cron: '0 9 * * *'  # Run daily at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        python -m playwright install chromium
        pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
    
    - name: Run scraper with mock data
      run: python main.py --state Maharashtra --append-mode --mock
    
    - name: Upload to Google Drive
      env:
        GOOGLE_SERVICE_ACCOUNT_KEY: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_KEY }}
        GOOGLE_DRIVE_FOLDER_ID: ${{ secrets.GOOGLE_DRIVE_FOLDER_ID }}
      run: |
        python scripts/upload_to_drive.py
    
    - name: Upload results as artifact
      uses: actions/upload-artifact@v3
      with:
        name: excel-files
        path: output/
        retention-days: 30
    
    - name: Commit and push results
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add output/
        git commit -m "Update restaurant data - $(date)" || true
        git push
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

5. Click "Commit changes"

---

## STEP 5: Create Upload Script

### 5.1 Create Script File

1. In your repository, create a new file: `scripts/upload_to_drive.py`
2. Copy this code:

```python
"""Upload Excel files to Google Drive."""

import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive():
    """Upload Excel files from output/ to Google Drive."""
    
    # Get credentials from environment
    key_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not key_json or not folder_id:
        print("ERROR: Missing Google Drive credentials")
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
            print("No output directory found")
            return False
        
        excel_files = list(output_dir.glob('*.xlsx'))
        if not excel_files:
            print("No Excel files found")
            return False
        
        for excel_file in excel_files:
            print(f"Uploading {excel_file.name}...")
            
            # Check if file already exists in Drive
            query = f"name='{excel_file.name}' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
            files = results.get('files', [])
            
            if files:
                # Update existing file
                file_id = files[0]['id']
                media = MediaFileUpload(str(excel_file), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                service.files().update(fileId=file_id, media_body=media).execute()
                print(f"  ✓ Updated {excel_file.name}")
            else:
                # Create new file
                file_metadata = {
                    'name': excel_file.name,
                    'parents': [folder_id]
                }
                media = MediaFileUpload(str(excel_file), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f"  ✓ Uploaded {excel_file.name}")
        
        print("All files uploaded successfully!")
        return True
    
    except Exception as e:
        print(f"ERROR uploading to Google Drive: {str(e)}")
        return False

if __name__ == '__main__':
    success = upload_to_drive()
    exit(0 if success else 1)
```

---

## STEP 6: Test the Setup

### 6.1 Manual Test

1. Go to your repository
2. Click "Actions" tab
3. Click "FSSAI Restaurant Scraper"
4. Click "Run workflow"
5. Click "Run workflow" again
6. Wait for it to complete (2-3 minutes)

### 6.2 Check Results

1. Go to your Google Drive folder
2. You should see the Excel file there
3. Download and verify it has data

---

## STEP 7: Share with Your Sir

### 7.1 Get Google Drive Link

1. Go to your Google Drive folder
2. Right-click the folder
3. Click "Share"
4. Change to "Anyone with the link"
5. Copy the link

### 7.2 Send to Your Sir

Send him the link via:
- Email
- WhatsApp
- Telegram
- Any messaging app

### 7.3 What Your Sir Does

1. Click the link
2. See the Excel file
3. Download or view online
4. Done!

---

## Automatic Daily Updates

Your scraper will now:

**Every day at 9 AM UTC:**
1. Run the scraper
2. Generate Excel file
3. Upload to Google Drive
4. Your sir can download anytime

---

## Troubleshooting

### Excel file not appearing in Google Drive?

**Check:**
1. Go to "Actions" tab
2. Click latest workflow run
3. Look for "Upload to Google Drive" step
4. Check if there are any errors

**Fix:**
1. Verify Google Drive folder ID is correct
2. Verify service account has access to folder
3. Check that JSON key is valid

### Workflow fails?

**Check the logs:**
1. Go to "Actions" tab
2. Click the failed run
3. Expand "Upload to Google Drive" step
4. Read the error message

**Common issues:**
- Missing `scripts/upload_to_drive.py` file
- Invalid Google Drive folder ID
- Service account doesn't have permission

---

## Summary

✅ **What's Happening:**
- Scraper runs daily at 9 AM UTC
- Excel file is generated
- File is uploaded to Google Drive
- Your sir can access it anytime

✅ **No Cost:**
- GitHub Actions is free
- Google Drive is free (15GB)
- No server needed

✅ **Automatic:**
- No manual uploads
- No manual intervention
- Completely hands-off

---

## Next Steps

1. ✅ Create Google Cloud project
2. ✅ Create service account
3. ✅ Create Google Drive folder
4. ✅ Add secrets to GitHub
5. ✅ Update workflow file
6. ✅ Create upload script
7. ✅ Test manually
8. ✅ Share link with sir

**Your deployment is complete!**

---

## Useful Links

- Google Cloud Console: https://console.cloud.google.com/
- Google Drive: https://drive.google.com/
- GitHub Actions: https://github.com/YOUR-USERNAME/fssai-restaurant-scraper/actions
- Google Drive API Docs: https://developers.google.com/drive/api

</content>
