# 🔄 Data Update Workflow

## How Automatic Updates Work

### ✅ **YES! Streamlit Cloud Auto-Updates from GitHub**

When you deploy to Streamlit Cloud, it watches your GitHub repository. Every time you push changes, it automatically redeploys within 1-2 minutes!

---

## 📊 **Weekly Update Workflow**

### Step 1: Update Division Data (5 minutes)

```bash
# In your DSX folder
python fetch_gotsport_division.py
```

**What this does:**
- Fetches latest standings from GotSport
- Updates `OCL_BU08_Stripes_Division_with_DSX.csv`
- Recalculates Strength Index for all teams
- Updates DSX's rank and comparison

**Result:** Fresh division data with current standings

---

### Step 2: Update Opponent Schedules (Optional, 2 minutes)

```bash
python fetch_bsa_celtic.py
```

**What this does:**
- Fetches latest BSA Celtic team schedules
- Updates `BSA_Celtic_Schedules.csv`
- Shows recent match results

**Result:** Latest opponent match data

---

### Step 3: Generate New HTML Report (1 minute)

```bash
python create_html_report.py
```

**What this does:**
- Creates dated HTML report (e.g., `DSX_Division_Report_20251018.html`)
- Includes all latest data
- Ready to email to coaches/parents

**Result:** Shareable HTML file with current stats

---

### Step 4: Push to GitHub (1 minute)

```bash
git add .
git commit -m "Updated division data for Oct 18"
git push
```

**What happens next:**
1. Code pushes to GitHub ✅
2. Streamlit Cloud detects the change 🔔
3. Automatically redeploys (1-2 minutes) 🚀
4. Dashboard shows fresh data! 📊

**Your teammates see the update automatically - they don't need to do anything!**

---

## 🔄 Complete Update Script

Create a file called `update_all.bat`:

```batch
@echo off
echo ========================================
echo DSX Data Updater
echo ========================================
echo.

echo [1/4] Updating division standings...
python fetch_gotsport_division.py
echo.

echo [2/4] Generating HTML report...
python create_html_report.py
echo.

echo [3/4] Committing to Git...
git add *.csv *.html
git commit -m "Data update %date%"
echo.

echo [4/4] Pushing to GitHub...
git push
echo.

echo ========================================
echo [DONE] Update complete!
echo ========================================
echo.
echo Streamlit Cloud will auto-deploy in 1-2 minutes.
echo Dashboard URL: https://livingriskyco-dsx-tracker.streamlit.app
echo.
pause
```

**Then just run:**
```bash
update_all.bat
```

**Done in under 2 minutes!** ⚡

---

## 📱 What Your Teammates See

### **Before Your Update:**
- Dashboard shows data from Oct 11
- Rankings are from previous week

### **After You Push to GitHub:**
- ⏳ **Wait 1-2 minutes** (Streamlit Cloud redeploys)
- 🔄 **They refresh the page** (F5)
- ✅ **See new data automatically!**

**No app update needed. No reinstall. Just refresh!** 🎉

---

## 🎯 Update Schedule Recommendations

### **Weekly Updates (Recommended):**
- **When:** Sunday evening after weekend games
- **Takes:** 5-10 minutes total
- **Includes:**
  - Division standings
  - HTML report
  - Git push

### **After Big Games:**
- Update immediately after key matchups
- Show the team how rankings changed
- Keep momentum going!

### **End of Season:**
- Final update with complete stats
- Generate season summary
- Archive for next year

---

## 🔍 Verify Your Update Worked

### Check Locally (Immediate):
1. Look at CSV file timestamps
2. Open dashboard: http://localhost:8503
3. Refresh page (F5)
4. See new data!

### Check on Streamlit Cloud (2 minutes later):
1. Go to your deployed URL
2. Check "Deploy status" (click hamburger menu → Settings)
3. Should show "Last deployed: Just now"
4. Refresh page - see new data!

---

## 🐛 Troubleshooting

### **"My push didn't trigger a deploy"**

**Solution 1:** Check Streamlit Cloud dashboard
- Go to https://share.streamlit.io
- Click on your app
- Check deploy logs

**Solution 2:** Manual redeploy
- In Streamlit Cloud app settings
- Click "Reboot app"
- Forces fresh deployment

**Solution 3:** Verify CSV files were pushed
```bash
git status
# Make sure no uncommitted CSV files
```

---

### **"Dashboard shows old data after update"**

**Solution 1:** Hard refresh
- Press `Ctrl+Shift+R` (clears cache)
- Or `Ctrl+F5`

**Solution 2:** Check file timestamps
```bash
# In Streamlit Cloud logs
ls -la *.csv
# Verify modified dates are recent
```

**Solution 3:** Clear Streamlit cache
- Dashboard has caching (`@st.cache_data`)
- Redeploy clears cache automatically
- Or update `ttl=3600` parameter

---

### **"Data fetching failed"**

**If `fetch_gotsport_division.py` fails:**
```
[ERROR] Could not fetch standings
```

**Possible causes:**
1. GotSport website down → Try again later
2. URL changed → Check event URL is still correct
3. Network issue → Check internet connection

**Workaround:**
- Keep using previous CSV file
- Dashboard still works with old data
- Note the update date in commit message

---

## 📊 What Gets Auto-Updated

### **Files that update automatically on push:**
- ✅ `dsx_dashboard.py` (code changes)
- ✅ `*.csv` files (data updates)
- ✅ `requirements.txt` (if you add packages)
- ✅ All markdown files (documentation)

### **Files that DON'T deploy:**
- ❌ Excel files (too large, not needed)
- ❌ HTML reports (generated locally, email them)
- ❌ `.bat` files (Windows-specific, cloud uses Linux)

---

## 🚀 Pro Tips

### **Tip 1: Commit messages matter**
```bash
# Good commit messages:
git commit -m "Updated standings after Oct 18 games - DSX moved to 4th!"
git commit -m "Added 3 new matches, updated Blast FC record"

# Bad commit messages:
git commit -m "update"
git commit -m "stuff"
```

### **Tip 2: Use branches for experiments**
```bash
# Create test branch
git checkout -b test-new-feature

# Make changes, test locally
# If good:
git checkout main
git merge test-new-feature
git push

# Production dashboard only updates from main branch!
```

### **Tip 3: Schedule reminders**
- Set phone reminder: "Sunday 6pm - Update DSX tracker"
- Takes 5 minutes
- Keeps team engaged!

### **Tip 4: Announce updates**
```
Text to team group:
"Updated division standings! Check the dashboard:
[Your Streamlit URL]

Key changes:
- We moved up to 5th
- Blast FC extended lead
- Next game is crucial!

Go DSX! 🟧⚽"
```

---

## 📅 Sample Update Log

Keep track of your updates:

| Date | Changes | Rank | Notes |
|------|---------|------|-------|
| Oct 11 | Initial deploy | 5th | First version! |
| Oct 18 | Updated standings | 5th | Added week 8 results |
| Oct 25 | Added 2 matches | 4th | Moved up! 🎉 |
| Nov 1 | Season finale | 4th | Final standings |

---

## ✅ **Your Deployment Checklist**

### **One-Time Setup (Do Once):**
- [x] Code on GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Share URL with team
- [ ] Bookmark the dashboard

### **Weekly Updates (Do Every Week):**
- [ ] Run `fetch_gotsport_division.py`
- [ ] Generate HTML report
- [ ] Commit and push to GitHub
- [ ] Wait 2 minutes for auto-deploy
- [ ] Verify dashboard updated
- [ ] Announce to team

---

## 🎯 Bottom Line

**Q: "Will data update automatically on Streamlit Cloud?"**

**A: YES! Just push to GitHub and:**
1. ⏱️ **1-2 minutes** → Streamlit Cloud auto-redeploys
2. 🔄 **Teammates refresh** → See new data
3. ✅ **Zero manual work** → Happens automatically!

**Your workflow:**
```
Update local data → Git push → Streamlit auto-updates → Team sees fresh data
     (5 min)          (1 min)         (2 min)              (instant)
```

**Total: 8 minutes from data fetch to live dashboard!** ⚡

---

## 🚀 **Ready to Deploy?**

When you're ready to make it live:

1. **Go to:** https://share.streamlit.io
2. **Sign in** with your GitHub account
3. **Deploy:** `LivingRiskyCo/dsx-tracker` → `main` → `dsx_dashboard.py`
4. **Get your URL** (like `https://dsx-tracker.streamlit.app`)
5. **Test:** Push a small change to verify auto-deploy works
6. **Share** with your team!

**Your dashboard will auto-update every time you push to GitHub!** 🎉

