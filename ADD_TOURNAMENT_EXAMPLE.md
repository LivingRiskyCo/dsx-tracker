# Adding New Tournament Example: "Spring Classic Tournament"

## Step-by-Step Process

### 1. Add Games to team_schedule.csv

Add these lines to the end of `team_schedule.csv`:

```csv
8,Game,2025-04-15,9:00 AM,Springfield Thunder SC,Springfield Sports Complex,Field 2,8:45 AM,Blue Jerseys,Spring Classic Tournament,Neutral,Upcoming,Pool Play Game 1,
9,Game,2025-04-15,2:00 PM,Columbus United U8B,Springfield Sports Complex,Field 3,1:45 PM,White Jerseys,Spring Classic Tournament,Neutral,Upcoming,Pool Play Game 2,
10,Game,2025-04-16,10:30 AM,Championship Game TBD,Springfield Sports Complex,Field 1,10:15 AM,Blue Jerseys,Spring Classic Tournament,Neutral,Upcoming,Championship Game,
```

### 2. Add to DSX_Upcoming_Opponents.csv

Add these lines to the end of `DSX_Upcoming_Opponents.csv`:

```csv
2025-04-15,Springfield Thunder SC,Springfield Sports Complex,Spring Classic Tournament,9:00 AM,Upcoming,Pool Play Game 1
2025-04-15,Columbus United U8B,Springfield Sports Complex,Spring Classic Tournament,2:00 PM,Upcoming,Pool Play Game 2
2025-04-16,Championship Game TBD,Springfield Sports Complex,Spring Classic Tournament,10:30 AM,Upcoming,Championship Game
```

### 3. Create Division Rankings (if needed)

If these teams are in a tracked division, create `Spring_Classic_Division_Rankings.csv`:

```csv
Rank,Team,GP,W,L,D,GF,GA,GD,Pts,PPG,StrengthIndex,SourceURL,Division,League
1,Springfield Thunder SC,3,3,0,0,12,3,9,9,3.0,85.0,https://example.com,Spring Classic,Spring Classic Tournament
2,Columbus United U8B,3,2,1,0,8,5,3,6,2.0,70.0,https://example.com,Spring Classic,Spring Classic Tournament
3,DSX Orange 2018,3,1,2,0,6,8,-2,3,1.0,50.0,https://example.com,Spring Classic,Spring Classic Tournament
```

### 4. Update Dashboard Configuration

In `dsx_dashboard.py`, add the new division file to the list (around line 173):

```python
division_files = [
    "OCL_BU08_Stripes_Division_Rankings.csv",
    "OCL_BU08_White_Division_Rankings.csv", 
    "OCL_BU08_Stars_Division_Rankings.csv",
    "OCL_BU08_Stars_7v7_Division_Rankings.csv",
    "MVYSA_B09_3_Division_Rankings.csv",
    "Spring_Classic_Division_Rankings.csv",  # Add this line
]
```

### 5. Refresh Data

Run the update script:
```bash
python update_all_data.py
```

### 6. Launch Dashboard

```bash
streamlit run dsx_dashboard.py
```

## Result

- ✅ New tournament games appear in "📅 Team Schedule"
- ✅ Opponents show up in "🔍 Opponent Intel" 
- ✅ Division rankings include new teams
- ✅ Strength indices calculated automatically
- ✅ All analytics updated with new data

## Pro Tips

1. **Use consistent naming** - Keep team names identical across all files
2. **Include all required fields** - Missing fields can break the dashboard
3. **Test with one game first** - Add one game, test, then add more
4. **Backup your data** - Copy CSV files before making changes
5. **Check the dashboard** - Always verify changes appear correctly
