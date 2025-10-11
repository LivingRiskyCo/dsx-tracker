# DSX Opponent Tracker - Quick Start Guide

## What You Have

I've built an automated opponent tracker system for Dublin DSX Orange 2018 Boys that scrapes schedules from MVYSA and GotSport and formats them for your Excel workbook's Common Opponent Analysis.

## Files Created

### Core Tools
1. **`opponent_scraper.py`** - Main scraper library
   - `MVYSAScraper` - Fetches MVYSA schedules
   - `GotSportScraper` - Fetches GotSport schedules
   - `OpponentScheduleProcessor` - Formats for Excel

2. **`fetch_bsa_celtic.py`** - Quick script for BSA Celtic teams
   - Already configured for your Oct 18-19 opponents
   - Run this anytime to refresh their schedules

3. **`update_workbook_auto.py`** - Automated workbook updater
   - Fetches schedules AND updates Excel directly
   - Handles duplicates automatically

### Output Files
4. **`BSA_Celtic_Schedules.csv`** - Ready to import!
   - 16 matches from both BSA Celtic teams
   - Formatted for your "OppSchedules (Paste)" sheet

5. **`requirements.txt`** - Dependencies

## How to Use

### 🚀 ONE-CLICK UPDATE (Recommended!)

**Update ALL data sources at once:**

```bash
# Windows - Double-click this file:
update_all_data.bat

# Or run directly:
python update_all_data.py
```

**This updates:**
- ✅ OCL BU08 Stripes Division Rankings (GotSport)
- ✅ BSA Celtic Schedules (MVYSA)
- ✅ All Division Team Schedules
- ✅ Upcoming Opponent Analysis
- ✅ Common Opponent Matrix

**Then refresh your dashboard to see the new data!**

---

### Option 1: Quick Import (Manual)

```bash
# Already done! Just import the CSV:
# 1. Open BSA_Celtic_Schedules.csv
# 2. Copy all rows
# 3. Paste into "OppSchedules (Paste)" sheet in your Excel workbook
```

The file contains:
- **BSA Celtic 18B United** - 8 matches (your Oct 18 opponent)
- **BSA Celtic 18B City** - 8 matches (your Oct 19 opponent)

### Option 2: Fetch Fresh Data (Individual Sources)

```bash
# Refresh BSA Celtic schedules only
python fetch_bsa_celtic.py

# Then import the updated BSA_Celtic_Schedules.csv
```

### Option 3: Auto-Update Workbook

```bash
# Update Excel workbook directly (no manual import!)
python update_workbook_auto.py
```

This will:
- Fetch latest BSA Celtic schedules
- Open your workbook
- Update "OppSchedules (Paste)" sheet
- Remove duplicates
- Save the workbook

## Adding More Opponents

### For MVYSA Teams

1. Find the team on https://www.mvysa.com/cgi-bin/teams.cgi
2. Click their schedule link
3. Look at the URL: `bt=4263` → team_id is `4263`
4. Add to `fetch_bsa_celtic.py` or create a new script:

```python
opponents = [
    {
        'name': 'Team Name Exactly As It Appears',
        'source': 'mvysa',
        'team_id': '4263',
        'season': '202509',  # Fall 2025
        'division': 'MVYSA Fall 2025'
    },
]
```

### For GotSport Teams

The GotSport scraper is built but needs team IDs, which are harder to find. Options:

1. **Use the standings scraper** to get all team IDs in a division:
   ```python
   from opponent_scraper import GotSportScraper
   scraper = GotSportScraper()
   standings = scraper.get_division_standings('45535', '418528')
   print(standings)
   ```

2. **Inspect the page** - Right-click the team page, View Source, search for team ID

## What Gets Tracked

For each opponent match, you'll get:
- **OpponentTeam** - The team you're tracking (e.g., "BSA Celtic 18B City")
- **TheirOpponent** - Who they played
- **Date** - When they played
- **GF** - Goals For (from tracked team's perspective)
- **GA** - Goals Against
- **Venue/Div** - League/Division
- **SourceURL** - Where the data came from
- **Notes** - Field location

## Common Opponent Analysis

Once you paste opponent schedules into your Excel workbook:

1. Open your workbook
2. Review "OppSchedules (Paste)" sheet
3. Your Common Opponent Matrix will auto-calculate:
   - Which opponents you both faced
   - Your avg goal differential vs common opponents
   - Their avg goal differential vs common opponents
   - Relative performance gap

### Example Insight

If DSX and BSA Celtic 18B City both played:
- **Warrior White B17/18**
- **Springfield Thunder SC Navy B2017**
- **Troy Rattlers B17/18**

The matrix will show:
- **Common opponents**: 3
- **DSX avg GD vs common**: +2.3
- **BSA Celtic avg GD vs common**: -1.7
- **Relative gap**: +4.0 (DSX advantage)

This tells you DSX performs ~4 goals better per game against shared opponents!

## Current Data Summary

### BSA Celtic 18B United (Oct 18 Opponent)
- Record: 2-2-4 (W-D-L)
- Goals For: 14
- Goals Against: 22
- Goal Differential: -8

Notable results:
- Beat Warrior White 7-2 (Sep 12)
- Lost to Southstars SC 0-6 (Oct 5)

### BSA Celtic 18B City (Oct 19 Opponent)
- Record: 2-1-4
- Goals For: 14
- Goals Against: 32
- Goal Differential: -18

Notable results:
- Lost to Springfield Thunder 1-9 (Sep 18)
- Beat Warrior White 4-3 (Oct 2)

### Shared Opponents

Both teams have played:
- **Warrior White B17/18**
- **Southstars SC B17**
- **Springfield Thunder SC Navy B2017**
- **Troy Rattlers B17/18**

Once you add **DSX's** results against any of these teams to your main workbook, you'll see direct comparisons!

## Automation Ideas

### Weekly Updates

Create a Windows Task or cron job to run `python fetch_bsa_celtic.py` weekly and email you the CSV.

### Pre-Game Reports

Before each game, run:
```bash
python fetch_bsa_celtic.py
python update_workbook_auto.py
```

Then open your Excel dashboard to see updated opponent analysis.

### Expand to Full Division

Add all OCL BU08 Stripes teams to track everyone:
- Elite FC 2018 Boys Liverpool
- Club Ohio West 18B Academy
- Northwest FC 2018B Academy Blue
- LFC United 2018B Elite 2
- Grove City Kids Association 2018B
- etc.

## Troubleshooting

### "No matches found"
- Check the team_id is correct
- Verify the season code (202509 = Fall 2025)
- Some teams may not have public schedules

### "Workbook not found"
- Update the path in `update_workbook_auto.py`
- Make sure you're in the correct directory

### Scores look wrong
- MVYSA sometimes updates scores after games
- Re-run the scraper to get latest

## Next Steps

1. ✅ **Import BSA_Celtic_Schedules.csv** into your Excel workbook
2. **Add more opponents** - Find team IDs for:
   - Elite FC 2018 Boys Liverpool
   - Northwest FC 2018B Academy Blue
   - LFC United 2018B Elite 2
   - Club Ohio West 18B Academy
3. **Automate weekly updates** - Set up a scheduled task
4. **Expand Common Opponent Matrix** - More data = better insights!

## Questions?

Let me know what opponents you want to track next and I'll help you find their team IDs!

