# GitHub + Google Drive Deployment Checklist

Complete these steps to deploy your FSSAI Restaurant Scraper.

---

## PHASE 1: GitHub Setup (5 minutes)

### Step 1: Create GitHub Account
- [ ] Go to https://github.com/signup
- [ ] Create account with your email
- [ ] Verify email
- [ ] Save your username: `_________________`

### Step 2: Create GitHub Repository
- [ ] Go to https://github.com/new
- [ ] Repository name: `fssai-restaurant-scraper`
- [ ] Choose Public or Private
- [ ] Click "Create repository"
- [ ] Save repository URL: `_________________`

### Step 3: Upload Project to GitHub
- [ ] Open Command Prompt/Terminal
- [ ] Navigate to your project folder
- [ ] Run these commands:
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  git branch -M main
  git remote add origin https://github.com/YOUR-USERNAME/fssai-restaurant-scraper.git
  git push -u origin main
  ```
- [ ] Enter GitHub credentials when prompted
- [ ] Verify files appear on GitHub

### Step 4: Create GitHub Actions Workflow
- [ ] Go to your GitHub repository
- [ ] Click "Actions" tab
- [ ] Click "set up a workflow yourself"
- [ ] Copy the workflow from `.github/workflows/scraper.yml`
- [ ] Click "Commit changes"
- [ ] Verify workflow appears in Actions tab

---

## PHASE 2: Google Cloud Setup (10 minutes)

### Step 5: Create Google Cloud Project
- [ ] Go to https://console.cloud.google.com/
- [ ] Click "Select a Project" (top left)
- [ ] Click "NEW PROJECT"
- [ ] Name: `FSSAI Restaurant Scraper`
- [ ] Click "CREATE"
- [ ] Wait for project to be created
- [ ] Save Project ID: `_________________`

### Step 6: Enable Google Drive API
- [ ] Go to https://console.cloud.google.com/apis/library/drive.googleapis.com
- [ ] Click "ENABLE"
- [ ] Wait for it to enable

### Step 7: Create Service Account
- [ ] Go to https://console.cloud.google.com/iam-admin/serviceaccounts
- [ ] Click "CREATE SERVICE ACCOUNT"
- [ ] Service account name: `fssai-scraper`
- [ ] Click "CREATE AND CONTINUE"
- [ ] Click "CONTINUE" (skip optional steps)
- [ ] Click "DONE"

### Step 8: Create and Download Key
- [ ] Click the service account you created
- [ ] Go to "KEYS" tab
- [ ] Click "ADD KEY" → "Create new key"
- [ ] Choose "JSON"
- [ ] Click "CREATE"
- [ ] JSON file downloads automatically
- [ ] Save the file safely: `_________________`
- [ ] Copy the service account email: `_________________`

---

## PHASE 3: Google Drive Setup (5 minutes)

### Step 9: Create Google Drive Folder
- [ ] Go to https://drive.google.com
- [ ] Click "New" → "Folder"
- [ ] Name: `FSSAI Restaurant Data`
- [ ] Click "Create"

### Step 10: Share Folder with Service Account
- [ ] Right-click the folder
- [ ] Click "Share"
- [ ] Paste the service account email (from Step 8)
- [ ] Give "Editor" permission
- [ ] Click "Share"

### Step 11: Get Folder ID
- [ ] Open the folder
- [ ] Look at URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
- [ ] Copy the FOLDER_ID_HERE part
- [ ] Save it: `_________________`

---

## PHASE 4: GitHub Secrets Setup (5 minutes)

### Step 12: Add Google Service Account Key
- [ ] Go to your GitHub repository
- [ ] Click "Settings" tab
- [ ] Click "Secrets and variables" → "Actions"
- [ ] Click "New repository secret"
- [ ] Name: `GOOGLE_SERVICE_ACCOUNT_KEY`
- [ ] Value: Copy entire contents of JSON file from Step 8
- [ ] Click "Add secret"

### Step 13: Add Google Drive Folder ID
- [ ] Click "New repository secret"
- [ ] Name: `GOOGLE_DRIVE_FOLDER_ID`
- [ ] Value: Paste folder ID from Step 11
- [ ] Click "Add secret"

---

## PHASE 5: Workflow Update (2 minutes)

### Step 14: Update Workflow File
- [ ] Go to your repository
- [ ] Click `.github/workflows/scraper.yml`
- [ ] Click edit button (pencil icon)
- [ ] Replace content with updated workflow (includes Google Drive upload)
- [ ] Click "Commit changes"

### Step 15: Create Upload Script
- [ ] Create folder: `scripts/`
- [ ] Create file: `scripts/upload_to_drive.py`
- [ ] Copy content from `scripts/upload_to_drive.py` in this repository
- [ ] Commit and push

---

## PHASE 6: Testing (5 minutes)

### Step 16: Manual Test
- [ ] Go to your repository
- [ ] Click "Actions" tab
- [ ] Click "FSSAI Restaurant Scraper"
- [ ] Click "Run workflow"
- [ ] Click "Run workflow" again
- [ ] Wait for completion (2-3 minutes)

### Step 17: Verify Results
- [ ] Check GitHub Actions logs for errors
- [ ] Go to your Google Drive folder
- [ ] Verify Excel file is there
- [ ] Download and open to verify data

---

## PHASE 7: Share with Your Sir (2 minutes)

### Step 18: Get Google Drive Link
- [ ] Go to your Google Drive folder
- [ ] Right-click the folder
- [ ] Click "Share"
- [ ] Change to "Anyone with the link"
- [ ] Copy the link
- [ ] Save it: `_________________`

### Step 19: Send to Your Sir
- [ ] Send the link via:
  - [ ] Email
  - [ ] WhatsApp
  - [ ] Telegram
  - [ ] Other: `_________________`

### Step 20: Verify Your Sir Can Access
- [ ] Ask your sir to click the link
- [ ] Verify he can see the Excel file
- [ ] Verify he can download it

---

## PHASE 8: Automatic Daily Runs (0 minutes)

### Step 21: Verify Automatic Schedule
- [ ] Scraper will run daily at 9 AM UTC
- [ ] Excel file will be updated automatically
- [ ] Your sir can download anytime
- [ ] No manual intervention needed

---

## Troubleshooting

### Workflow Not Running?
- [ ] Check "Actions" tab - is workflow enabled?
- [ ] Check schedule time (9 AM UTC)
- [ ] Click "Enable workflow" if disabled

### Excel File Not in Google Drive?
- [ ] Check GitHub Actions logs
- [ ] Verify Google Drive folder ID is correct
- [ ] Verify service account has access to folder
- [ ] Check that JSON key is valid

### Your Sir Can't Access Link?
- [ ] Verify link is shared "Anyone with the link"
- [ ] Try opening in incognito mode
- [ ] Check that link is correct

---

## Summary

✅ **Total Time**: ~30 minutes
✅ **Cost**: FREE
✅ **Coding**: None needed
✅ **Result**: Automated daily scraping with Google Drive uploads

---

## Important Information to Save

| Item | Value |
|------|-------|
| GitHub Username | `_________________` |
| Repository URL | `_________________` |
| Google Project ID | `_________________` |
| Service Account Email | `_________________` |
| Google Drive Folder ID | `_________________` |
| Google Drive Link | `_________________` |

---

## Next Steps

1. ✅ Complete all 21 steps above
2. ✅ Test the workflow manually
3. ✅ Share Google Drive link with your sir
4. ✅ Wait for automatic daily runs
5. ✅ Monitor GitHub Actions for any issues

**Your deployment is complete!**

</content>
