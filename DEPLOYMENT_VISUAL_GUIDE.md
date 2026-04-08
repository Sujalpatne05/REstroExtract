# Visual Deployment Guide

## How It Works - Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER (Now)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FSSAI Restaurant Scraper Project                        │  │
│  │  ├── src/                                                │  │
│  │  ├── tests/                                              │  │
│  │  ├── main.py                                             │  │
│  │  ├── requirements.txt                                    │  │
│  │  └── .github/workflows/scraper.yml                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│                    git push to GitHub                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      GITHUB (Cloud)                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Your Repository                                         │  │
│  │  Sujalpatne05/fssai-restaurant-scraper                   │  │
│  │                                                          │  │
│  │  ├── .github/workflows/scraper.yml                       │  │
│  │  │   └── Runs daily at 9 AM UTC                          │  │
│  │  │       ├── Installs dependencies                       │  │
│  │  │       ├── Runs scraper                                │  │
│  │  │       ├── Generates Excel file                        │  │
│  │  │       └── Uploads to Google Drive                     │  │
│  │  │                                                       │  │
│  │  └── output/                                             │  │
│  │      └── FSSAI_Restaurants_Maharashtra.xlsx              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│                  Upload to Google Drive                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   GOOGLE DRIVE (Cloud)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FSSAI Restaurant Data (Folder)                          │  │
│  │                                                          │  │
│  │  ├── FSSAI_Restaurants_Maharashtra.xlsx                  │  │
│  │  │   ├── Sheet 1: Restaurant Data                        │  │
│  │  │   │   ├── Business Name                               │  │
│  │  │   │   ├── License Number                              │  │
│  │  │   │   ├── License Type                                │  │
│  │  │   │   └── ... (14 fields total)                       │  │
│  │  │   │                                                   │  │
│  │  │   └── Sheet 2: Metadata                               │  │
│  │  │       ├── Total Records                               │  │
│  │  │       ├── Validation Status                           │  │
│  │  │       └── Generation Date                             │  │
│  │  │                                                       │  │
│  │  └── (Updated daily)                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│                    Share Link with Sir                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR SIR'S COMPUTER                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Google Drive Link                                       │  │
│  │  https://drive.google.com/drive/folders/...              │  │
│  │                                                          │  │
│  │  ├── Click link                                          │  │
│  │  ├── See Excel file                                      │  │
│  │  ├── Download or view online                             │  │
│  │  └── Done!                                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Daily Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVERY DAY AT 9 AM UTC                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  GitHub Actions Wakes Up              │
        │  (Automatically)                      │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  1. Install Dependencies              │
        │     - requests                        │
        │     - beautifulsoup4                  │
        │     - openpyxl                        │
        │     - playwright                      │
        │     - google-api-python-client        │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  2. Run Scraper                       │
        │     python main.py                    │
        │     --state Maharashtra               │
        │     --append-mode                     │
        │     --mock                            │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  3. Generate Excel File               │
        │     - Fetch data                      │
        │     - Validate records                │
        │     - Remove duplicates               │
        │     - Create Excel file               │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  4. Upload to Google Drive            │
        │     - Connect to Google Drive         │
        │     - Upload Excel file               │
        │     - Update existing file            │
        └───────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │  5. Done!                             │
        │     Your sir can download anytime     │
        └───────────────────────────────────────┘
```

---

## Setup Steps - Visual

```
STEP 1: GitHub Account
┌─────────────────────────────────────────┐
│ https://github.com/signup               │
│ Create account → Verify email           │
└─────────────────────────────────────────┘
                    ↓
STEP 2: GitHub Repository
┌─────────────────────────────────────────┐
│ https://github.com/new                  │
│ Create repository                       │
│ Name: fssai-restaurant-scraper          │
└─────────────────────────────────────────┘
                    ↓
STEP 3: Upload Project
┌─────────────────────────────────────────┐
│ git init                                │
│ git add .                               │
│ git commit -m "Initial commit"          │
│ git remote add origin ...               │
│ git push -u origin main                 │
└─────────────────────────────────────────┘
                    ↓
STEP 4: Google Cloud Project
┌─────────────────────────────────────────┐
│ https://console.cloud.google.com/       │
│ Create project                          │
│ Name: FSSAI Restaurant Scraper          │
└─────────────────────────────────────────┘
                    ↓
STEP 5: Enable Google Drive API
┌─────────────────────────────────────────┐
│ https://console.cloud.google.com/       │
│ apis/library/drive.googleapis.com       │
│ Click ENABLE                            │
└─────────────────────────────────────────┘
                    ↓
STEP 6: Create Service Account
┌─────────────────────────────────────────┐
│ https://console.cloud.google.com/       │
│ iam-admin/serviceaccounts               │
│ Create service account                  │
│ Name: fssai-scraper                     │
└─────────────────────────────────────────┘
                    ↓
STEP 7: Download JSON Key
┌─────────────────────────────────────────┐
│ Go to service account                   │
│ KEYS tab                                │
│ Create new key (JSON)                   │
│ Download and save safely                │
└─────────────────────────────────────────┘
                    ↓
STEP 8: Create Google Drive Folder
┌─────────────────────────────────────────┐
│ https://drive.google.com                │
│ New → Folder                            │
│ Name: FSSAI Restaurant Data             │
└─────────────────────────────────────────┘
                    ↓
STEP 9: Share Folder with Service Account
┌─────────────────────────────────────────┐
│ Right-click folder                      │
│ Share                                   │
│ Paste service account email             │
│ Give Editor permission                  │
└─────────────────────────────────────────┘
                    ↓
STEP 10: Get Folder ID
┌─────────────────────────────────────────┐
│ Open folder                             │
│ Copy ID from URL                        │
│ https://drive.google.com/drive/         │
│ folders/FOLDER_ID_HERE                  │
└─────────────────────────────────────────┘
                    ↓
STEP 11: Add GitHub Secrets
┌─────────────────────────────────────────┐
│ GitHub Repository Settings              │
│ Secrets and variables → Actions         │
│ Add GOOGLE_SERVICE_ACCOUNT_KEY          │
│ Add GOOGLE_DRIVE_FOLDER_ID              │
└─────────────────────────────────────────┘
                    ↓
STEP 12: Test Workflow
┌─────────────────────────────────────────┐
│ GitHub Actions tab                      │
│ Run workflow manually                   │
│ Wait for completion                     │
│ Verify Excel file in Google Drive       │
└─────────────────────────────────────────┘
                    ↓
STEP 13: Share with Sir
┌─────────────────────────────────────────┐
│ Get Google Drive folder link            │
│ Send to sir via:                        │
│ - Email                                 │
│ - WhatsApp                              │
│ - Telegram                              │
│ - Any messaging app                     │
└─────────────────────────────────────────┘
                    ↓
✅ DEPLOYMENT COMPLETE!
```

---

## What Your Sir Sees

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Google Drive Link                                          │
│  https://drive.google.com/drive/folders/...                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  FSSAI Restaurant Data                              │   │
│  │                                                     │   │
│  │  📄 FSSAI_Restaurants_Maharashtra.xlsx              │   │
│  │     Size: 2.5 MB                                    │   │
│  │     Modified: Today at 9:15 AM                      │   │
│  │                                                     │   │
│  │  [Download] [Preview] [Share]                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Your sir can:                                              │
│  ✓ Click to download                                        │
│  ✓ Click to preview online                                  │
│  ✓ Share with others                                        │
│  ✓ View anytime                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Excel File Structure

```
FSSAI_Restaurants_Maharashtra.xlsx
│
├── Sheet 1: Data
│   ├── Headers:
│   │   ├── Business Name
│   │   ├── License Number
│   │   ├── License Type
│   │   ├── Business Type
│   │   ├── District
│   │   ├── City/Town
│   │   ├── Pin Code
│   │   ├── Issue Date
│   │   ├── Valid Till
│   │   ├── Owner/Contact
│   │   ├── Mobile
│   │   ├── Email
│   │   ├── Address
│   │   └── State
│   │
│   └── Rows: Restaurant records (45 per day)
│       ├── Row 1: Restaurant 1
│       ├── Row 2: Restaurant 2
│       ├── Row 3: Restaurant 3
│       └── ... (continues)
│
└── Sheet 2: Metadata
    ├── Generation Date: 2024-04-09 09:15:00
    ├── Total Records: 45
    ├── Validation Status: All Valid
    ├── Duplicates Removed: 5
    └── Extraction Status: Success
```

---

## Timeline

```
Day 1:
  9:00 AM UTC → Scraper runs
  9:05 AM UTC → Excel file created (45 records)
  9:10 AM UTC → Uploaded to Google Drive
  9:15 AM UTC → Your sir can download

Day 2:
  9:00 AM UTC → Scraper runs
  9:05 AM UTC → Excel file updated (90 records total)
  9:10 AM UTC → Uploaded to Google Drive
  9:15 AM UTC → Your sir can download

Day 3:
  9:00 AM UTC → Scraper runs
  9:05 AM UTC → Excel file updated (135 records total)
  9:10 AM UTC → Uploaded to Google Drive
  9:15 AM UTC → Your sir can download

... and so on, every day!
```

---

## Cost Breakdown

```
GitHub Account:        FREE
GitHub Repository:     FREE
GitHub Actions:        FREE (2000 min/month)
Google Account:        FREE
Google Drive (15GB):   FREE
Google Cloud Project:  FREE (with free tier)
Scraper:               FREE (open source)
─────────────────────────────
TOTAL:                 FREE ✓
```

---

## Support

If you get stuck:

1. **Read the error message** - It usually tells you what's wrong
2. **Check DEPLOYMENT_CHECKLIST.md** - Step-by-step guide
3. **Check GOOGLE_DRIVE_INTEGRATION.md** - Detailed Google Drive guide
4. **Check GITHUB_ACTIONS_SETUP.md** - Detailed GitHub Actions guide
5. **Check README.md** - Full documentation

---

## Summary

✅ **Setup Time**: 30 minutes
✅ **Cost**: FREE
✅ **Coding**: None needed
✅ **Result**: Automated daily scraping with Google Drive uploads
✅ **Your Sir**: Just clicks link to view data

**You've got this!** 🚀

</content>
