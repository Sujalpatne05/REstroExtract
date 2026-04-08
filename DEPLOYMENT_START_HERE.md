# 🚀 DEPLOYMENT START HERE

## Your FSSAI Restaurant Scraper is Ready to Deploy!

This guide will help you deploy to GitHub + Google Drive in **30 minutes** with **NO CODING**.

---

## What You'll Get

✅ **Automated Scraping** - Runs daily at 9 AM UTC
✅ **Excel Files** - Restaurant data in Excel format
✅ **Google Drive** - Files automatically uploaded to Google Drive
✅ **Share Link** - Your sir can view/download anytime
✅ **FREE** - No cost, no servers, no credit card needed

---

## Prerequisites

You need:
1. **GitHub Account** (free) - https://github.com/signup
2. **Google Account** (free) - https://accounts.google.com/signup
3. **Git installed** - https://git-scm.com/download/win (Windows)
4. **Command Prompt/Terminal** - Built into your computer

---

## QUICK START (30 minutes)

### Phase 1: GitHub Setup (5 min)

**Step 1: Create GitHub Account**
```
1. Go to https://github.com/signup
2. Create account
3. Verify email
4. Save your username
```

**Step 2: Create Repository**
```
1. Go to https://github.com/new
2. Name: fssai-restaurant-scraper
3. Click "Create repository"
4. Copy the repository URL
```

**Step 3: Upload Your Project**
```
1. Open Command Prompt
2. Navigate to your project folder:
   cd Desktop\REstroExtract

3. Run these commands:
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/fssai-restaurant-scraper.git
   git push -u origin main

4. Enter your GitHub username and password
5. Wait for upload to complete
```

**Step 4: Verify on GitHub**
```
1. Go to your repository URL
2. Verify all files are there
3. You should see: src/, tests/, main.py, etc.
```

---

### Phase 2: Google Cloud Setup (10 min)

**Step 5: Create Google Cloud Project**
```
1. Go to https://console.cloud.google.com/
2. Click "Select a Project" (top left)
3. Click "NEW PROJECT"
4. Name: FSSAI Restaurant Scraper
5. Click "CREATE"
6. Wait for project to be created
```

**Step 6: Enable Google Drive API**
```
1. Go to https://console.cloud.google.com/apis/library/drive.googleapis.com
2. Click "ENABLE"
3. Wait for it to enable
```

**Step 7: Create Service Account**
```
1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "CREATE SERVICE ACCOUNT"
3. Service account name: fssai-scraper
4. Click "CREATE AND CONTINUE"
5. Click "CONTINUE" (skip optional steps)
6. Click "DONE"
```

**Step 8: Create and Download Key**
```
1. Click the service account you created
2. Go to "KEYS" tab
3. Click "ADD KEY" → "Create new key"
4. Choose "JSON"
5. Click "CREATE"
6. JSON file downloads automatically
7. SAVE THIS FILE SAFELY - you'll need it later
8. Copy the service account email (looks like: fssai-scraper@project-id.iam.gserviceaccount.com)
```

---

### Phase 3: Google Drive Setup (5 min)

**Step 9: Create Google Drive Folder**
```
1. Go to https://drive.google.com
2. Click "New" → "Folder"
3. Name: FSSAI Restaurant Data
4. Click "Create"
```

**Step 10: Share Folder with Service Account**
```
1. Right-click the folder
2. Click "Share"
3. Paste the service account email (from Step 8)
4. Give "Editor" permission
5. Click "Share"
```

**Step 11: Get Folder ID**
```
1. Open the folder
2. Look at the URL in your browser
3. Copy the part after /folders/
   Example: https://drive.google.com/drive/folders/1ABC2DEF3GHI4JKL5MNO6PQR7STU8VWX
   Copy: 1ABC2DEF3GHI4JKL5MNO6PQR7STU8VWX
4. Save this ID - you'll need it later
```

---

### Phase 4: GitHub Secrets Setup (5 min)

**Step 12: Add Google Service Account Key**
```
1. Go to your GitHub repository
2. Click "Settings" tab
3. Click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Name: GOOGLE_SERVICE_ACCOUNT_KEY
6. Value: Copy the ENTIRE contents of the JSON file from Step 8
7. Click "Add secret"
```

**Step 13: Add Google Drive Folder ID**
```
1. Click "New repository secret"
2. Name: GOOGLE_DRIVE_FOLDER_ID
3. Value: Paste the folder ID from Step 11
4. Click "Add secret"
```

---

### Phase 5: Workflow Setup (2 min)

**Step 14: Verify Workflow File**
```
1. Go to your GitHub repository
2. Click "Actions" tab
3. You should see "FSSAI Restaurant Scraper" workflow
4. If not, the workflow file wasn't uploaded - check Step 3
```

---

### Phase 6: Testing (5 min)

**Step 15: Manual Test**
```
1. Go to your GitHub repository
2. Click "Actions" tab
3. Click "FSSAI Restaurant Scraper"
4. Click "Run workflow"
5. Click "Run workflow" again
6. Wait for it to complete (2-3 minutes)
```

**Step 16: Verify Results**
```
1. Check GitHub Actions logs for errors
2. Go to your Google Drive folder
3. You should see the Excel file there
4. Download and open to verify data
```

---

### Phase 7: Share with Your Sir (2 min)

**Step 17: Get Google Drive Link**
```
1. Go to your Google Drive folder
2. Right-click the folder
3. Click "Share"
4. Change to "Anyone with the link"
5. Copy the link
```

**Step 18: Send to Your Sir**
```
1. Send the link via:
   - Email
   - WhatsApp
   - Telegram
   - Any messaging app

2. Tell him:
   "Click this link to see the restaurant data"
   "You can download the Excel file anytime"
```

---

## Automatic Daily Runs

After setup, your scraper will:

**Every day at 9 AM UTC:**
1. Run automatically
2. Generate Excel file
3. Upload to Google Drive
4. Your sir can download anytime

**No manual work needed!**

---

## Troubleshooting

### "fatal: No configured push destination"
```
This means git remote isn't set up.
Run this command:
git remote add origin https://github.com/YOUR-USERNAME/fssai-restaurant-scraper.git
Then run: git push -u origin main
```

### Workflow Not Running?
```
1. Go to "Actions" tab
2. Is the workflow enabled? (Should show green checkmark)
3. If not, click "Enable workflow"
```

### Excel File Not in Google Drive?
```
1. Go to "Actions" tab
2. Click the failed workflow run
3. Expand "Upload to Google Drive" step
4. Read the error message
5. Common issues:
   - Wrong folder ID
   - Service account doesn't have permission
   - Invalid JSON key
```

### Your Sir Can't Access Link?
```
1. Verify link is shared "Anyone with the link"
2. Try opening in incognito mode
3. Check that link is correct
```

---

## Important Information to Save

Save these somewhere safe:

```
GitHub Username: _________________
Repository URL: _________________
Google Project ID: _________________
Service Account Email: _________________
Google Drive Folder ID: _________________
Google Drive Link: _________________
```

---

## Files You'll Need

These files are already in your project:

- `.github/workflows/scraper.yml` - GitHub Actions workflow
- `scripts/upload_to_drive.py` - Google Drive upload script
- `main.py` - Scraper entry point
- `requirements.txt` - Python dependencies
- `DEPLOYMENT_CHECKLIST.md` - Detailed checklist
- `GOOGLE_DRIVE_INTEGRATION.md` - Detailed Google Drive guide

---

## Summary

✅ **Setup Time**: 30 minutes
✅ **Cost**: FREE
✅ **Coding**: None needed
✅ **Result**: Automated daily scraping with Google Drive uploads

---

## Next Steps

1. Follow the QUICK START above
2. Complete all 18 steps
3. Test the workflow manually
4. Share Google Drive link with your sir
5. Wait for automatic daily runs

**That's it! Your deployment is complete!**

---

## Need Help?

Check these files:
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `GOOGLE_DRIVE_INTEGRATION.md` - Detailed Google Drive guide
- `GITHUB_ACTIONS_SETUP.md` - Detailed GitHub Actions guide
- `README.md` - Full documentation

---

## Questions?

If you get stuck:
1. Read the error message carefully
2. Check the troubleshooting section above
3. Check the detailed guides
4. Try again

**You've got this!** 🚀

</content>
