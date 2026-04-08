# Quick Deployment Reference Card

## 🎯 Your GitHub Repository

**URL**: https://github.com/Sujalpatne05/REstroExtract

---

## ⚡ 30-Minute Deployment

### Phase 1: Google Cloud (10 min)
```
1. https://console.cloud.google.com/
2. Create project: "FSSAI Restaurant Scraper"
3. Enable Google Drive API
4. Create service account: "fssai-scraper"
5. Download JSON key (SAVE SAFELY!)
6. Copy service account email
```

### Phase 2: Google Drive (5 min)
```
1. https://drive.google.com
2. Create folder: "FSSAI Restaurant Data"
3. Share with service account email
4. Copy folder ID from URL
```

### Phase 3: GitHub Secrets (5 min)
```
1. GitHub Repository → Settings
2. Secrets and variables → Actions
3. Add GOOGLE_SERVICE_ACCOUNT_KEY (JSON contents)
4. Add GOOGLE_DRIVE_FOLDER_ID (folder ID)
```

### Phase 4: Test & Share (10 min)
```
1. GitHub Actions tab
2. Run workflow manually
3. Wait for completion
4. Check Google Drive for Excel file
5. Share folder link with sir
```

---

## 📋 Deployment Guides (Read in Order)

1. **DEPLOYMENT_START_HERE.md** - Start here!
2. **DEPLOYMENT_CHECKLIST.md** - Step-by-step
3. **GOOGLE_DRIVE_INTEGRATION.md** - Detailed setup
4. **DEPLOYMENT_VISUAL_GUIDE.md** - Diagrams
5. **DEPLOYMENT_READY.md** - Final summary

---

## 🔑 Important Information to Save

```
GitHub Username: _________________
Repository: https://github.com/Sujalpatne05/REstroExtract
Google Project ID: _________________
Service Account Email: _________________
Google Drive Folder ID: _________________
Google Drive Link: _________________
```

---

## 🚀 What Happens Daily

**9 AM UTC:**
1. GitHub Actions runs
2. Scraper fetches data
3. Excel file created
4. Uploaded to Google Drive
5. Your sir can download

---

## 💻 Local Testing

```bash
# Run with mock data
python main.py --state Maharashtra --append-mode --mock

# Run tests
python -m pytest tests/ -v

# View logs
tail -f logs/scraper.log
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflow not running | Check Actions tab - enable if disabled |
| Excel not in Drive | Check GitHub Actions logs for errors |
| Can't access link | Verify link is "Anyone with the link" |
| JSON key error | Verify JSON file contents are correct |
| Folder ID error | Copy ID from URL: /folders/FOLDER_ID |

---

## 📊 What Your Sir Gets

- Google Drive folder link
- Excel file with restaurant data
- Updated daily at 9 AM UTC
- Can download or view online
- Can share with others

---

## 💰 Cost

**FREE** - Everything is free tier

---

## ✅ Deployment Checklist

- [ ] Create Google Cloud project
- [ ] Enable Google Drive API
- [ ] Create service account
- [ ] Download JSON key
- [ ] Create Google Drive folder
- [ ] Share folder with service account
- [ ] Get folder ID
- [ ] Add GitHub secrets
- [ ] Test workflow manually
- [ ] Share link with sir

---

## 🎓 Files in Repository

**Deployment:**
- `.github/workflows/scraper.yml` - GitHub Actions
- `scripts/upload_to_drive.py` - Google Drive upload

**Scraper:**
- `main.py` - Entry point
- `src/scraper.py` - Scraper engine
- `src/exporter.py` - Excel export
- `src/deduplicator.py` - Duplicate removal
- `src/validator.py` - Data validation

**Tests:**
- `tests/` - 211 passing tests

**Guides:**
- `DEPLOYMENT_START_HERE.md` - Quick start
- `DEPLOYMENT_CHECKLIST.md` - Detailed steps
- `GOOGLE_DRIVE_INTEGRATION.md` - Google Drive setup
- `DEPLOYMENT_VISUAL_GUIDE.md` - Visual diagrams
- `README.md` - Full documentation

---

## 🔗 Useful Links

- GitHub: https://github.com/Sujalpatne05/REstroExtract
- Google Cloud: https://console.cloud.google.com/
- Google Drive: https://drive.google.com/
- GitHub Actions: https://github.com/Sujalpatne05/REstroExtract/actions

---

## 📞 Need Help?

1. Read DEPLOYMENT_START_HERE.md
2. Check DEPLOYMENT_CHECKLIST.md
3. Check GOOGLE_DRIVE_INTEGRATION.md
4. Check DEPLOYMENT_VISUAL_GUIDE.md
5. Check README.md

**Everything is documented!**

---

## 🎉 Status

✅ **Code**: Complete (211 tests passing)
✅ **GitHub**: Uploaded and ready
✅ **Workflow**: Created and ready
✅ **Guides**: Comprehensive and ready
✅ **Deployment**: Ready to start

**You're all set! Follow the guides and deploy in 30 minutes!**

</content>
