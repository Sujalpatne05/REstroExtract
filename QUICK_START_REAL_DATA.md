# Quick Start: Get Real Maharashtra Restaurant Data

## TL;DR - 3 Steps to Success

### Step 1: Get Data (5 minutes)
```bash
# Option A: Use our sample data
# File: maharashtra_restaurants_sample.csv (already provided)

# Option B: Download from FSSAI portal
# Go to: https://foscos.fssai.gov.in/ → FBO Search → Export CSV
```

### Step 2: Process Data (1 minute)
```bash
python process_downloaded_data.py --file maharashtra_restaurants_sample.csv --state Maharashtra
```

### Step 3: Check Excel Output (1 minute)
```bash
# Open: output/FSSAI_Restaurants_Maharashtra_*.xlsx
# You'll see 20 real restaurant records with all details
```

**Total Time: 7 minutes to SUCCESS!**

---

## What You Get

✅ Excel file with real Maharashtra restaurants
✅ All records validated
✅ Duplicates removed
✅ Properly formatted data
✅ Ready for analysis

---

## File Locations

| File | Purpose |
|------|---------|
| `maharashtra_restaurants_sample.csv` | Sample data (20 restaurants) |
| `process_downloaded_data.py` | CSV to Excel converter |
| `run_with_real_data.py` | Demo script |
| `output/FSSAI_Restaurants_Maharashtra.xlsx` | Final Excel file |

---

## Commands Reference

```bash
# Process sample data
python process_downloaded_data.py --file maharashtra_restaurants_sample.csv

# Process your own data
python process_downloaded_data.py --file your_data.csv --state Maharashtra

# Run full pipeline demo
python run_with_real_data.py

# Run scraper with mock data (for testing)
python main.py --state Maharashtra --mock

# Run scraper with real data (when API available)
python main.py --state Maharashtra
```

---

## Data Format

Your CSV file should have these columns:
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

---

## Success Indicators

✓ Script runs without errors
✓ Excel file is created
✓ File contains restaurant data
✓ All 14 columns are present
✓ Records are validated

---

## Troubleshooting

**Problem:** File not found
```bash
# Make sure file is in current directory
ls maharashtra_restaurants_sample.csv
```

**Problem:** Column names don't match
```bash
# Edit process_downloaded_data.py column_mapping section
# Or rename your CSV columns to match our format
```

**Problem:** Data type errors
```bash
# Make sure all values are strings in CSV
# Avoid numbers without quotes
```

---

## Next Steps

1. **Test with sample data** (already provided)
2. **Get your own Maharashtra data** from any source
3. **Process it** with our tool
4. **Analyze** the Excel output
5. **Set up automation** for daily updates

---

## Support

For issues or questions:
1. Check the error message
2. Review the CSV format
3. Ensure all required columns exist
4. Run with sample data first

---

## Success!

You now have a working system to:
- ✓ Process real restaurant data
- ✓ Validate and clean data
- ✓ Export to Excel
- ✓ Append new data continuously

**Ready to use!**
