# DSX Opponent Tracker - Automated Scraper

Automated tools to fetch opponent schedules from MVYSA and GotSport for the Dublin DSX Orange 2018 Boys team analysis.

## Quick Start

### 🎯 NEW: One-Click Data Update

**Update ALL opponent data sources at once:**

```bash
# Windows - Double-click:
update_all_data.bat

# Or run directly:
python update_all_data.py
```

This automatically updates:
- ✅ OCL BU08 Stripes Division Rankings
- ✅ BSA Celtic Schedules (all upcoming opponents)
- ✅ All Division Team Schedules
- ✅ Upcoming Opponent Analysis
- ✅ Common Opponent Matrix

**Then view in the dashboard:**
```bash
python -m streamlit run dsx_dashboard.py
```

---

## 🎮 NEW: Live Game Tracker

**Record games in real-time with automatic stat tracking!**

### 🚀 Quick Launch (Game Day)

```bash
# Windows - Double-click:
launch_game_tracker.bat

# Or run directly:
streamlit run live_game_tracker.py
```

### ✨ Features

**Pre-Game:**
- Select starting 7 lineup
- Enter opponent and game details
- 2-minute setup time

**During Game:**
- ⏱️ 25-minute countdown timer (auto per half)
- ⚽ Track goals with scorer + assist
- 🎯 Record shots, saves, corners
- 🔄 Track substitutions (who's on field)
- 📋 Live event feed with timestamps
- 📊 Real-time stats display

**Post-Game:**
- 🎉 Automatic game summary
- 💾 One-click save to CSVs
- 📈 Auto-updates main dashboard
- 📥 Download detailed event log

**For Parents:**
- 📱 Share live link for real-time score updates
- 👀 Read-only viewing mode
- 🔄 Auto-refreshing score and events

### 🎯 Perfect For:
- Sideline recording (tablet/phone optimized)
- Parent volunteers
- Accurate stat tracking
- No more forgotten scorers!
- Playing time fairness (sub tracking)

---

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. View Your Dashboard

```bash
# Launch interactive dashboard
python -m streamlit run dsx_dashboard.py

# Or double-click:
launch_dashboard.bat
```

### 3. Update Data Before Games

```bash
# Update everything (recommended)
python update_all_data.py

# Or update individual sources:
python fetch_bsa_celtic.py          # BSA Celtic only
python fetch_gotsport_division.py   # OCL division only
```

### 4. Push Updates to GitHub

**After updating CSVs or Excel files:**

```bash
# Quick push (Windows) - Double-click:
push_updates.bat

# Or manually:
git add .
git commit -m "Update match data"
git push
```

**From the Dashboard:**
- ⚙️ Go to **Data Manager**
- ✏️ Edit your data in any tab
- 💾 Click **Save Locally** (on Streamlit Cloud)
- 📥 Download the updated CSV
- Replace local file and push with `push_updates.bat`

**OR** (if running locally):
- 🚀 Click **Save & Push to GitHub** (auto-commits and pushes!)

**📖 See [QUICKSTART.md](QUICKSTART.md) for detailed guide, opponent insights, and automation tips.**

## Tools Included

### `opponent_scraper.py`
Main scraper library with classes for:
- **MVYSAScraper** - Fetches schedules from MVYSA.com
- **GotSportScraper** - Fetches schedules and standings from GotSport
- **OpponentScheduleProcessor** - Formats data for Excel import

### `fetch_bsa_celtic.py`
Quick script to fetch the BSA Celtic teams you're facing Oct 18-19.

### Custom Usage

```python
from opponent_scraper import OpponentScheduleProcessor

processor = OpponentScheduleProcessor()

# Define opponents to track
opponents = [
    {
        'name': 'Elite FC 2018 Boys Liverpool',
        'source': 'mvysa',  # or 'gotsport'
        'team_id': 'XXXXX',
        'season': '202509',
        'division': 'OCL BU08'
    },
    # Add more...
]

# Fetch and format
schedules_df = processor.process_opponent_schedules(opponents)
schedules_df.to_csv('output.csv', index=False)
```

## Data Format

The scraper outputs CSV files matching your Excel **OppSchedules (Paste)** sheet format:

| Column | Description |
|--------|-------------|
| OpponentTeam | The team you're tracking |
| TheirOpponent | Who they played |
| Date | Match date |
| GF | Goals For (from their perspective) |
| GA | Goals Against |
| Venue/Div | League/Division |
| SourceURL | Where the data came from |
| Notes | Optional notes |

## Finding Team IDs

### MVYSA Team IDs
1. Go to https://www.mvysa.com/cgi-bin/teams.cgi
2. Find the team
3. Click their schedule link
4. The URL will show: `bt=XXXX` (that's the team_id)

Example: `bt=4263` → team_id is `'4263'`

### GotSport Team IDs
GotSport IDs are trickier - they're not always in the URL. Options:
1. Use the division standings scraper to get all teams
2. Inspect the page HTML for team links
3. Use browser dev tools to find the team ID in API calls

## Automation Ideas

### 1. Auto-Update Your Workbook

Create a script that:
- Fetches all opponent schedules
- Updates the Excel workbook directly (using `openpyxl`)
- Recalculates Common Opponent Matrix
- Emails you when done

### 2. Schedule Weekly Updates

Use Windows Task Scheduler or cron to run the scraper weekly and email updated data.

### 3. Build a Dashboard

- Flask/Streamlit web app
- Auto-refresh data from GotSport/MVYSA
- Live Common Opponent Matrix
- Mobile-friendly for reviewing before games

## Troubleshooting

### "No matches found"
- Check that the team_id is correct
- Verify the season code (202509 = Fall 2025)
- Some teams may not have public schedules

### "Connection timeout"
- MVYSA/GotSport may be temporarily down
- Try again in a few minutes
- Check your internet connection

### "Score parsing errors"
- Some sites format scores differently
- The scraper will still capture the matchup
- You can manually add scores later

## Next Steps

1. **Expand to more opponents** - Add Elite FC, Northwest FC, LFC United, etc.
2. **Automate GotSport** - Find team IDs for the BU08 Stripes division teams
3. **Build Common Opponent Calculator** - Python script to compute the matrix directly
4. **Create update workflow** - One-click update all data

## Support

Need help finding team IDs or want to add more sources? Let's discuss!

