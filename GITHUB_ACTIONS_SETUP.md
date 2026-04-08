# GitHub Actions Deployment - Step by Step

## What is GitHub Actions?

GitHub Actions automatically runs your scraper in the cloud every day - **completely free!**

No server needed. No cost. Just push your code to GitHub.

---

## Step 1: Create GitHub Account

1. Go to https://github.com/signup
2. Create a free account
3. Verify your email

---

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `fssai-restaurant-scraper`
   - **Description**: `FSSAI Restaurant Data Scraper`
   - **Public** or **Private** (your choice)
3. Click "Create repository"

---

## Step 3: Install Git (If Not Already Installed)

### Windows
1. Download from: https://git-scm.com/download/win
2. Run installer
3. Accept all defaults

### Mac
```bash
brew install git
```

### Linux
```bash
sudo apt install git
```

---

## Step 4: Upload Your Project to GitHub

### Option A: Using Command Line (Recommended)

1. **Open Command Prompt/Terminal**

2. **Navigate to your project**
   ```bash
   cd Desktop\REstroExtract
   ```

3. **Initialize Git**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. **Add GitHub remote**
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/fssai-restaurant-scraper.git
   ```
   
   Replace `YOUR-USERNAME` with your GitHub username

5. **Push to GitHub**
   ```bash
   git push -u origin main
   ```

6. **Enter GitHub credentials** when prompted

### Option B: Using GitHub Desktop (Easier)

1. Download from: https://desktop.github.com/
2. Sign in with your GitHub account
3. Click "Add" → "Add Existing Repository"
4. Select your project folder
5. Click "Publish repository"

---

## Step 5: Create GitHub Actions Workflow

1. **Go to your GitHub repository** (https://github.com/YOUR-USERNAME/fssai-restaurant-scraper)

2. **Click "Actions" tab**

3. **Click "set up a workflow yourself"**

4. **Copy and paste this code:**

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
    
    - name: Run scraper
      run: python main.py --state Maharashtra --append-mode
    
    - name: Upload results
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
        git commit -m "Update restaurant data" || true
        git push
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

5. **Click "Commit changes"**

6. **Name the file**: `.github/workflows/scraper.yml`

7. **Click "Commit new file"**

---

## Step 6: Verify Setup

1. **Go to "Actions" tab** in your repository

2. **You should see** "FSSAI Restaurant Scraper" workflow

3. **Click on it** to see the workflow details

4. **Click "Run workflow"** to test it manually

5. **Wait for it to complete** (usually 2-3 minutes)

6. **Check the results:**
   - Click the workflow run
   - Scroll down to "Artifacts"
   - Download the Excel file to verify

---

## Step 7: Automatic Daily Runs

The scraper will now run automatically:

- **Time**: 9 AM UTC every day
- **What it does**: 
  - Fetches restaurant data
  - Validates records
  - Appends to Excel file
  - Uploads results

**To change the time**, edit the workflow file:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Change 9 to your preferred hour (0-23)
```

Examples:
- `0 6 * * *` = 6 AM UTC
- `0 12 * * *` = 12 PM UTC (noon)
- `0 18 * * *` = 6 PM UTC

---

## Step 8: Download Results

### Option 1: From GitHub Actions

1. Go to "Actions" tab
2. Click the latest workflow run
3. Scroll to "Artifacts"
4. Download "excel-files"

### Option 2: From Repository

1. Go to your repository
2. Click "output" folder
3. Download `FSSAI_Restaurants_Maharashtra.xlsx`

---

## Monitoring

### View Workflow Runs

1. Go to "Actions" tab
2. See all past runs
3. Click any run to see details

### View Logs

1. Click a workflow run
2. Click "scrape" job
3. Expand steps to see logs

### Check for Errors

If workflow fails:
1. Click the failed run
2. Expand "Run scraper" step
3. Read the error message
4. Fix the issue
5. Push the fix to GitHub
6. Workflow will run again

---

## Troubleshooting

### Workflow Not Running?

**Check:**
1. Go to "Actions" tab
2. Is the workflow enabled? (Should show green checkmark)
3. Check the schedule time

**Fix:**
1. Click "Actions"
2. Click "FSSAI Restaurant Scraper"
3. Click "Enable workflow"

### Workflow Fails?

**Common issues:**

1. **Missing requirements.txt**
   - Make sure `requirements.txt` is in your repository root

2. **Python version mismatch**
   - Edit workflow, change `python-version: '3.11'` to `'3.9'` or `'3.10'`

3. **Playwright not installed**
   - Already handled in the workflow (included in the code above)

### Excel File Not Updating?

**Check:**
1. Go to "Actions" tab
2. Click latest run
3. Scroll to "Artifacts"
4. Is "excel-files" there?
5. Download and check the file

---

## Advanced: Store Excel Files in GitHub

The workflow automatically commits Excel files to your repository.

**To see them:**
1. Go to your repository
2. Click "output" folder
3. See all Excel files

**To download all files:**
```bash
git clone https://github.com/YOUR-USERNAME/fssai-restaurant-scraper.git
cd fssai-restaurant-scraper
# All files are in output/ folder
```

---

## Advanced: Email Notifications

To get email when workflow completes:

1. Go to "Actions" tab
2. Click "FSSAI Restaurant Scraper"
3. Click "..." (three dots)
4. Click "Create status badge"
5. Copy the markdown
6. Paste in your README.md

---

## Summary

✅ **What's Happening:**
- Your code is on GitHub
- GitHub Actions runs your scraper daily
- Results are saved to your repository
- You can download Excel files anytime

✅ **No Cost:**
- GitHub is free
- GitHub Actions is free (up to 2000 minutes/month)
- Your scraper runs in the cloud

✅ **Automatic:**
- Runs every day at 9 AM UTC
- No manual intervention needed
- Logs are saved for monitoring

---

## Next Steps

1. ✅ Create GitHub account
2. ✅ Create repository
3. ✅ Upload your project
4. ✅ Create workflow file
5. ✅ Test manually
6. ✅ Wait for automatic daily runs

**That's it! Your scraper is now deployed in the cloud!**

---

## Useful Links

- GitHub: https://github.com
- GitHub Actions Docs: https://docs.github.com/en/actions
- Cron Syntax: https://crontab.guru/
- Your Repository: https://github.com/YOUR-USERNAME/fssai-restaurant-scraper

---

## Questions?

Check these files:
- `README.md` - Full documentation
- `QUICK_START.md` - Quick reference
- `DEPLOYMENT_GUIDE.md` - All deployment options
- `REAL_DATA_GUIDE.md` - Real data information
