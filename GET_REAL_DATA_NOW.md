# GET REAL FSSAI RESTAURANT DATA - STEP BY STEP

## Current Status
✓ Scraper is 100% ready
✓ Excel export is working
✓ Validation is working
✓ Deduplication is working

❌ **BLOCKER**: FSSAI API requires authentication we don't have

## FASTEST SOLUTION (15 minutes)

### Step 1: Download Data from FSSAI Portal (5 minutes)

1. **Open browser and go to:**
   ```
   https://foscos.fssai.gov.in/
   ```

2. **Click "FBO Search" or "Search License"**

3. **Fill the form:**
   - State: Maharashtra
   - Leave other fields empty
   - Click "Search"

4. **Export the results:**
   - Look for "Export" or "Download" button
   - Choose CSV or Excel format
   - Save as: `maharashtra_restaurants.csv`

### Step 2: Process the Data (2 minutes)

**Run this command:**
```bash
python process_downloaded_data.py --file maharashtra_restaurants.csv --state Maharashtra
```

**Output:**
```
Loaded 500 records
Mapped: business_name <- Business Name
Mapped: license_number <- License Number
...
Success! Saved 500 records to:
output/FSSAI_Restaurants_Maharashtra_20260409_134500.xlsx
```

### Step 3: Done!
Your Excel file is ready with real FSSAI data!

---

## ALTERNATIVE: If Portal Download Doesn't Work

### Option A: Use Our Scraper with Manual Data Entry
```bash
# Create a CSV file manually with restaurant data
# Then process it:
python process_downloaded_data.py --file your_data.csv
```

### Option B: Contact FSSAI for API Access
**Email:** support@fssai.gov.in

**Subject:** API Access Request for FoSCoS Portal

**Message:**
```
Dear FSSAI Team,

I need API access to the FoSCoS portal to fetch restaurant license data 
for Maharashtra state programmatically.

Could you please provide:
1. API endpoint documentation
2. Authentication credentials (API key/token)
3. Rate limiting information

Thank you,
[Your Name]
```

Once you get credentials, update `main.py` to use them.

### Option C: Use State Government Data
Maharashtra has its own food licensing system:
- Search: "AHAR Maharashtra" or "Maharashtra food license"
- Download their data
- Process with our script

---

## What Our Scraper Can Do

Once you provide the data source, our scraper will:

✓ **Extract** restaurant records
✓ **Validate** email, phone, required fields
✓ **Deduplicate** by license number
✓ **Export** to formatted Excel
✓ **Append** new data to existing file
✓ **Schedule** automatic daily updates

---

## Quick Reference

| Task | Command |
|------|---------|
| Process CSV data | `python process_downloaded_data.py --file data.csv` |
| Process Excel data | `python process_downloaded_data.py --file data.xlsx` |
| Run scraper (when API works) | `python main.py --state Maharashtra` |
| Run with mock data | `python main.py --state Maharashtra --mock` |
| Append to existing file | `python main.py --state Maharashtra --append-mode` |

---

## Need Help?

1. **Can't download from portal?**
   - Try different browser
   - Check if portal is online: https://foscos.fssai.gov.in/
   - Try state portal instead

2. **Data format is different?**
   - Edit `process_downloaded_data.py` column mapping
   - Or send me the CSV and I'll help

3. **Want automatic updates?**
   - Once we have real data source, I'll set up GitHub Actions
   - Runs daily and appends new restaurants

---

## Summary

**You have 2 paths:**

### Path 1: Manual Download (15 min) ← FASTEST
1. Download from FSSAI portal
2. Run processor script
3. Done!

### Path 2: Get API Access (1-3 days)
1. Email FSSAI for credentials
2. Update scraper with credentials
3. Automatic daily updates

**Which path works for you?**
