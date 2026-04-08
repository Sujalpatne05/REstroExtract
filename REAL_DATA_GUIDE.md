# Getting Real Data from FSSAI Portal

## Current Status

The FSSAI portal (https://foscos.fssai.gov.in/) is currently under maintenance (503 Service Unavailable). When it comes back online, the scraper will automatically fetch real data.

## How Real Data Will Be Fetched

When the portal is working, the scraper will:

1. **Connect to FSSAI Portal** → https://foscos.fssai.gov.in/fbo-search
2. **Use Playwright** → Render JavaScript to load dynamic content
3. **Call API Endpoint** → `/gateway/api/fbo/search` with state filter
4. **Extract Records** → Parse all 14 fields per restaurant
5. **Validate Data** → Check email, phone, required fields
6. **Remove Duplicates** → Keep most recent by License Number
7. **Export to Excel** → Create formatted Excel file

## Step-by-Step: Getting Real Data

### Step 1: Wait for Portal to Come Online

Check if portal is working:
```bash
# Open in browser
https://foscos.fssai.gov.in/

# Or check via command line
curl -I https://foscos.fssai.gov.in/
```

When you see status 200 (not 503), the portal is ready.

### Step 2: Run the Scraper

Once portal is online, simply run:
```bash
python main.py --state Maharashtra
```

The scraper will:
- Automatically detect the portal is online
- Fetch real restaurant data
- Validate and deduplicate
- Export to Excel

### Step 3: Check the Output

Excel file will be created in `./output/`:
```
FSSAI_Restaurants_Maharashtra_20260409_123456.xlsx
```

## How to View the Excel Sheet

### Option 1: Open in Excel/LibreOffice

```bash
# Windows
start output/FSSAI_Restaurants_Maharashtra_*.xlsx

# Mac
open output/FSSAI_Restaurants_Maharashtra_*.xlsx

# Linux
libreoffice output/FSSAI_Restaurants_Maharashtra_*.xlsx
```

### Option 2: View in Python

```python
import openpyxl

# Open the file
wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra_20260409_003810.xlsx')

# Read data sheet
ws = wb['Data']
print(f"Total records: {ws.max_row - 1}")

# Print first 5 records
for row in ws.iter_rows(min_row=2, max_row=6, values_only=True):
    print(row)

wb.close()
```

### Option 3: View in Command Line

```bash
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra_20260409_003810.xlsx')
ws = wb['Data']
for row in ws.iter_rows(min_row=1, max_row=10, values_only=True):
    print(' | '.join(str(v)[:20] for v in row))
"
```

## Continuous Update: Append Data to One Excel Sheet

I've created a new feature to **append data to an existing Excel sheet** instead of creating a new file each time.

### How It Works

```bash
# First run - creates new Excel file
python main.py --state Maharashtra --append-mode

# Second run - appends new records to existing file
python main.py --state Maharashtra --append-mode

# Third run - appends more records
python main.py --state Maharashtra --append-mode
```

### What Happens

1. **First Run**: Creates `FSSAI_Restaurants_Maharashtra.xlsx` with 50 records
2. **Second Run**: Adds 50 more records (now 100 total)
3. **Third Run**: Adds 50 more records (now 150 total)
4. **And so on...** - Keeps appending to the same file

### Example Workflow

```bash
# Day 1: Initial scrape
python main.py --state Maharashtra --append-mode
# Creates: FSSAI_Restaurants_Maharashtra.xlsx (50 records)

# Day 2: Update with new restaurants
python main.py --state Maharashtra --append-mode
# Updates: FSSAI_Restaurants_Maharashtra.xlsx (100 records)

# Day 3: Another update
python main.py --state Maharashtra --append-mode
# Updates: FSSAI_Restaurants_Maharashtra.xlsx (150 records)
```

### View Appended Data

```bash
# See how many records are in the file
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra.xlsx')
ws = wb['Data']
print(f'Total records: {ws.max_row - 1}')
wb.close()
"
```

## Automatic Updates (Scheduled Scraping)

To automatically scrape every day and append data:

### Windows - Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Set action: Run `python main.py --state Maharashtra --append-mode`

### Linux/Mac - Cron Job

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/scraper && python main.py --state Maharashtra --append-mode
```

### Python - Scheduled Task

```python
import schedule
import time
import subprocess

def scrape_daily():
    subprocess.run(['python', 'main.py', '--state', 'Maharashtra', '--append-mode'])

# Schedule to run every day at 9 AM
schedule.every().day.at("09:00").do(scrape_daily)

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Monitoring Updates

### Check Last Update

```bash
python -c "
import openpyxl
from datetime import datetime
import os

filepath = 'output/FSSAI_Restaurants_Maharashtra.xlsx'
mod_time = os.path.getmtime(filepath)
mod_datetime = datetime.fromtimestamp(mod_time)

wb = openpyxl.load_workbook(filepath)
ws = wb['Data']
total_records = ws.max_row - 1

print(f'File: {filepath}')
print(f'Last Updated: {mod_datetime}')
print(f'Total Records: {total_records}')
wb.close()
"
```

### Track Updates Over Time

```bash
# Create a log file
echo 'Date,Records' > update_log.csv

# After each run, append the count
python -c "
import openpyxl
from datetime import datetime
wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra.xlsx')
ws = wb['Data']
count = ws.max_row - 1
print(f'{datetime.now().date()},{count}')
" >> update_log.csv
```

## Deduplication with Continuous Updates

When appending data, the scraper automatically:

1. **Detects duplicates** by License Number
2. **Keeps most recent** record (by Issue Date)
3. **Removes old versions** of the same restaurant

Example:
```
Day 1: Restaurant A (License 123) - Issue Date: 01/01/2025
Day 2: Restaurant A (License 123) - Issue Date: 02/01/2025 ← Kept (newer)
       Old version removed automatically
```

## Troubleshooting

### Portal Still Under Maintenance?

```bash
# Check status
python -c "
import requests
try:
    resp = requests.get('https://foscos.fssai.gov.in/gateway/api/fbo/search', timeout=5)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 503:
        print('Portal is under maintenance')
    elif resp.status_code == 200:
        print('Portal is online!')
except Exception as e:
    print(f'Error: {e}')
"
```

### Use Mock Data While Waiting

```bash
# Test with mock data
python main.py --state Maharashtra --mock --append-mode

# This will append mock data to the Excel file for testing
```

## Summary

| Task | Command |
|------|---------|
| Get real data (one-time) | `python main.py --state Maharashtra` |
| Append to existing file | `python main.py --state Maharashtra --append-mode` |
| Test with mock data | `python main.py --state Maharashtra --mock` |
| View Excel file | Open `output/FSSAI_Restaurants_Maharashtra.xlsx` |
| Check record count | `python -c "import openpyxl; wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra.xlsx'); print(wb['Data'].max_row - 1)"` |

## When Portal Comes Online

The scraper is ready. Just run:
```bash
python main.py --state Maharashtra --append-mode
```

And it will automatically:
1. Connect to the portal
2. Fetch real restaurant data
3. Validate and deduplicate
4. Append to your Excel file
5. Update metadata

No code changes needed!
