# Quick Start Guide - FSSAI Restaurant Scraper

## Installation (One-time)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
python -m playwright install chromium
```

## Usage

### Option 1: Create New Excel File Each Time

```bash
python main.py --state Maharashtra
```

Creates: `FSSAI_Restaurants_Maharashtra_20260409_123456.xlsx`

### Option 2: Append to One Excel File (Recommended)

```bash
python main.py --state Maharashtra --append-mode
```

Creates/Updates: `FSSAI_Restaurants_Maharashtra.xlsx`

**First run**: Creates file with 45 records
**Second run**: Appends 45 more records (now 90 total)
**Third run**: Appends 45 more records (now 135 total)

### Option 3: Test with Mock Data

```bash
python main.py --state Maharashtra --mock --append-mode
```

## View the Excel File

### Windows
```bash
start output/FSSAI_Restaurants_Maharashtra.xlsx
```

### Mac
```bash
open output/FSSAI_Restaurants_Maharashtra.xlsx
```

### Linux
```bash
libreoffice output/FSSAI_Restaurants_Maharashtra.xlsx
```

### Command Line
```bash
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra.xlsx')
ws = wb['Data']
print(f'Total records: {ws.max_row - 1}')
for row in ws.iter_rows(min_row=2, max_row=6, values_only=True):
    print(row)
wb.close()
"
```

## Advanced Options

```bash
# Custom output directory
python main.py --state Maharashtra --output ./my_data --append-mode

# Longer timeout (for slow connections)
python main.py --state Maharashtra --timeout 60 --append-mode

# Debug mode (verbose logging)
python main.py --state Maharashtra --log-level DEBUG --append-mode

# Combine options
python main.py --state Maharashtra --output ./data --timeout 60 --log-level INFO --append-mode
```

## Workflow Examples

### Daily Updates

```bash
# Day 1
python main.py --state Maharashtra --append-mode
# File: FSSAI_Restaurants_Maharashtra.xlsx (45 records)

# Day 2
python main.py --state Maharashtra --append-mode
# File: FSSAI_Restaurants_Maharashtra.xlsx (90 records)

# Day 3
python main.py --state Maharashtra --append-mode
# File: FSSAI_Restaurants_Maharashtra.xlsx (135 records)
```

### Multiple States

```bash
# Maharashtra
python main.py --state Maharashtra --append-mode
# Creates: FSSAI_Restaurants_Maharashtra.xlsx

# Pune (if available)
python main.py --state Pune --append-mode
# Creates: FSSAI_Restaurants_Pune.xlsx

# Nagpur (if available)
python main.py --state Nagpur --append-mode
# Creates: FSSAI_Restaurants_Nagpur.xlsx
```

### Testing Before Real Data

```bash
# Test with mock data
python main.py --state Maharashtra --mock --append-mode

# When portal is online, run without --mock
python main.py --state Maharashtra --append-mode
```

## File Structure

```
output/
├── FSSAI_Restaurants_Maharashtra.xlsx    ← Main file (append mode)
├── FSSAI_Restaurants_Maharashtra_20260409_001411.xlsx  ← Old files (new mode)
└── FSSAI_Restaurants_Maharashtra_20260409_003810.xlsx  ← Old files (new mode)

logs/
└── scraper.log                           ← Execution logs
```

## Excel File Contents

### Sheet 1: Data
- Business Name
- License Number
- License Type
- Business Type
- District
- City/Town
- Pin Code
- Issue Date
- Valid Till
- Owner/Contact
- Mobile
- Email
- Address
- State

### Sheet 2: Metadata
- Generation Date
- Total Records Extracted
- Total Records Validated
- Total Records Rejected
- Duplicates Removed
- State Filter Applied
- Extraction Status

## Troubleshooting

### Portal Under Maintenance?

Use mock data for testing:
```bash
python main.py --state Maharashtra --mock --append-mode
```

### Check Portal Status

```bash
python -c "
import requests
try:
    resp = requests.get('https://foscos.fssai.gov.in/', timeout=5)
    print(f'Portal Status: {resp.status_code}')
except Exception as e:
    print(f'Error: {e}')
"
```

### View Logs

```bash
# Last 20 lines
tail -20 logs/scraper.log

# Search for errors
grep ERROR logs/scraper.log
```

### Check Record Count

```bash
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/FSSAI_Restaurants_Maharashtra.xlsx')
ws = wb['Data']
print(f'Records: {ws.max_row - 1}')
wb.close()
"
```

## When FSSAI Portal Comes Online

The scraper will automatically:
1. Connect to the portal
2. Fetch real restaurant data
3. Validate and deduplicate
4. Append to your Excel file

**No code changes needed!** Just run:
```bash
python main.py --state Maharashtra --append-mode
```

## Support

- Check `README.md` for detailed documentation
- Check `REAL_DATA_GUIDE.md` for real data information
- Check `INVESTIGATION_REPORT.md` for portal status
- Check `logs/scraper.log` for execution details
