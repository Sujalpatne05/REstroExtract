# Deployment Guide - FSSAI Restaurant Scraper

## Deployment Options

Choose based on your needs:

1. **Local Machine** - Run on your computer
2. **Server/VPS** - Run on a cloud server (AWS, DigitalOcean, etc.)
3. **Scheduled Task** - Run automatically every day
4. **Docker** - Run in a container

---

## Option 1: Local Machine (Easiest)

### Setup (One-time)

```bash
# 1. Install Python (if not already installed)
# Download from: https://www.python.org/downloads/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
python -m playwright install chromium
```

### Run Anytime

```bash
python main.py --state Maharashtra --append-mode
```

**Pros:** Simple, no setup needed
**Cons:** Computer must be running

---

## Option 2: Windows Task Scheduler (Automatic Daily)

### Setup

1. **Open Task Scheduler**
   - Press `Windows Key + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create Basic Task**
   - Right-click "Task Scheduler Library"
   - Click "Create Basic Task"
   - Name: `FSSAI Restaurant Scraper`
   - Description: `Daily scraper for FSSAI restaurant data`

3. **Set Trigger**
   - Click "Trigger" tab
   - Click "New"
   - Select: "Daily"
   - Set time: 9:00 AM (or your preferred time)
   - Click OK

4. **Set Action**
   - Click "Action" tab
   - Click "New"
   - Program: `C:\Python313\python.exe` (your Python path)
   - Arguments: `main.py --state Maharashtra --append-mode`
   - Start in: `C:\Users\YourName\Desktop\REstroExtract` (your project folder)
   - Click OK

5. **Save**
   - Click OK to save the task

**Result:** Scraper runs automatically every day at 9 AM

---

## Option 3: Linux/Mac - Cron Job (Automatic Daily)

### Setup

1. **Open Terminal**

2. **Edit Crontab**
   ```bash
   crontab -e
   ```

3. **Add This Line**
   ```bash
   0 9 * * * cd /path/to/REstroExtract && python main.py --state Maharashtra --append-mode
   ```

   Replace `/path/to/REstroExtract` with your actual project path.

   Example:
   ```bash
   0 9 * * * cd /home/user/REstroExtract && python main.py --state Maharashtra --append-mode
   ```

4. **Save**
   - Press `Ctrl + X`
   - Press `Y`
   - Press Enter

**Result:** Scraper runs automatically every day at 9 AM

---

## Option 4: Cloud Server (AWS, DigitalOcean, etc.)

### Step 1: Create Server

1. Sign up for cloud provider (AWS, DigitalOcean, Heroku, etc.)
2. Create a new server/instance
3. Choose Ubuntu 20.04 or similar

### Step 2: Connect to Server

```bash
ssh user@your-server-ip
```

### Step 3: Install Python

```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 4: Upload Project

```bash
# From your local machine
scp -r REstroExtract user@your-server-ip:/home/user/
```

Or use Git:
```bash
git clone https://github.com/your-username/REstroExtract.git
cd REstroExtract
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### Step 6: Setup Cron Job

```bash
crontab -e
```

Add:
```bash
0 9 * * * cd /home/user/REstroExtract && python main.py --state Maharashtra --append-mode
```

### Step 7: Verify

```bash
# Test the scraper
python main.py --state Maharashtra --mock --append-mode

# Check cron logs
grep CRON /var/log/syslog
```

---

## Option 5: Docker (Container)

### Step 1: Create Dockerfile

Create file: `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python packages
RUN pip install -r requirements.txt

# Install Playwright
RUN python -m playwright install chromium

# Run scraper
CMD ["python", "main.py", "--state", "Maharashtra", "--append-mode"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  scraper:
    build: .
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

### Step 3: Build and Run

```bash
# Build image
docker build -t fssai-scraper .

# Run container
docker run -v $(pwd)/output:/app/output -v $(pwd)/logs:/app/logs fssai-scraper
```

---

## Option 6: GitHub Actions (Automatic Cloud)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create repository: `fssai-restaurant-scraper`
3. Push your code

### Step 2: Create Workflow File

Create: `.github/workflows/scraper.yml`

```yaml
name: FSSAI Scraper

on:
  schedule:
    - cron: '0 9 * * *'  # Run daily at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        python -m playwright install chromium
    
    - name: Run scraper
      run: python main.py --state Maharashtra --append-mode
    
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: excel-files
        path: output/
```

### Step 3: Push to GitHub

```bash
git add .github/workflows/scraper.yml
git commit -m "Add GitHub Actions workflow"
git push
```

**Result:** Scraper runs automatically every day in the cloud!

---

## Option 7: Heroku (Free Cloud)

### Step 1: Install Heroku CLI

Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Create Procfile

Create file: `Procfile`

```
worker: python main.py --state Maharashtra --append-mode
```

### Step 3: Create runtime.txt

Create file: `runtime.txt`

```
python-3.11.0
```

### Step 4: Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## Comparison Table

| Option | Setup | Cost | Automatic | Best For |
|--------|-------|------|-----------|----------|
| Local | Easy | Free | No | Testing |
| Task Scheduler | Medium | Free | Yes | Windows users |
| Cron Job | Medium | Free | Yes | Linux/Mac users |
| Cloud Server | Hard | $5-20/month | Yes | Production |
| Docker | Medium | Free | Yes | Scalability |
| GitHub Actions | Easy | Free | Yes | Open source |
| Heroku | Easy | Free | Yes | Quick deployment |

---

## Recommended Setup

### For Personal Use
**Option 1 (Local)** or **Option 2 (Task Scheduler)**
- Simple setup
- No cost
- Runs on your computer

### For Production
**Option 4 (Cloud Server)** or **Option 6 (GitHub Actions)**
- Reliable
- Always running
- Professional

### For Testing
**Option 5 (Docker)** or **Option 7 (Heroku)**
- Easy to manage
- Scalable
- Good for learning

---

## Monitoring & Maintenance

### Check if Scraper is Running

```bash
# View logs
tail -f logs/scraper.log

# Check last run
ls -lh output/FSSAI_Restaurants_Maharashtra.xlsx

# Count records
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra.xlsx')
print(f'Records: {wb[\"Data\"].max_row - 1}')
"
```

### Troubleshooting

**Scraper not running?**
```bash
# Test manually
python main.py --state Maharashtra --mock --append-mode

# Check logs
cat logs/scraper.log
```

**Portal still under maintenance?**
```bash
# Check status
curl -I https://foscos.fssai.gov.in/
```

---

## Next Steps

1. **Choose your deployment option** from above
2. **Follow the setup steps** for that option
3. **Test with mock data** first
4. **Monitor the logs** to ensure it's working
5. **When portal is online**, real data will be fetched automatically

---

## Support

- Check `README.md` for full documentation
- Check `QUICK_START.md` for quick reference
- Check `logs/scraper.log` for execution details
- Check `INVESTIGATION_REPORT.md` for portal status
