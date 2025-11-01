"""
Quick check: Which new teams from opponents' opponents are already tracked vs need to be added
"""

import pandas as pd
import os

print("=" * 70)
print("CHECKING NEW TEAMS STATUS")
print("=" * 70)
print()

# Load cleaned teams list
try:
    clean_teams = pd.read_csv('Teams_to_Track_Clean.csv')
    print(f"[OK] Loaded {len(clean_teams)} valid teams from Teams_to_Track_Clean.csv")
except Exception as e:
    print(f"[ERROR] Could not load Teams_to_Track_Clean.csv: {e}")
    exit(1)

# Load all tracked division files
division_files = [
    'OCL_BU08_Stripes_Division_Rankings.csv',
    'OCL_BU08_White_Division_Rankings.csv',
    'OCL_BU08_Stars_Division_Rankings.csv',
    'OCL_BU08_Stars_7v7_Division_Rankings.csv',
    'CPL_Fall_2025_Division_Rankings.csv',
    'MVYSA_B09_3_Division_Rankings.csv',
    'Haunted_Classic_B08Orange_Division_Rankings.csv',
    'Haunted_Classic_B08Black_Division_Rankings.csv',
    'CU_Fall_Finale_2025_Division_Rankings.csv',
    'Club_Ohio_Fall_Classic_2025_Division_Rankings.csv',
]

all_tracked_teams = set()

for f in division_files:
    if os.path.exists(f):
        try:
            df = pd.read_csv(f)
            if 'Team' in df.columns:
                teams = df['Team'].dropna().unique().tolist()
                all_tracked_teams.update(teams)
                print(f"[OK] {f}: {len(teams)} teams")
        except Exception as e:
            print(f"[WARN] {f}: Error reading - {e}")

print()
print(f"[INFO] Total tracked teams: {len(all_tracked_teams)}")
print()

# Check each new team
already_tracked = []
need_to_add = []

for team in clean_teams['Team']:
    # Try exact match first
    if team in all_tracked_teams:
        already_tracked.append(team)
    else:
        # Try fuzzy matching (case-insensitive, remove extra spaces)
        team_normalized = ' '.join(str(team).strip().split()).lower()
        found = False
        for tracked in all_tracked_teams:
            tracked_normalized = ' '.join(str(tracked).strip().split()).lower()
            if team_normalized == tracked_normalized:
                already_tracked.append(team)
                found = True
                break
        if not found:
            need_to_add.append(team)

# Print results
print("=" * 70)
print("RESULTS")
print("=" * 70)
print()

print(f"[OK] Already Tracked: {len(already_tracked)}")
for team in sorted(already_tracked):
    print(f"   [OK] {team}")

print()
print(f"[!] Need to Add: {len(need_to_add)}")
for team in sorted(need_to_add):
    print(f"   [!] {team}")

print()
print("=" * 70)
print("NEXT STEPS")
print("=" * 70)
print()

if need_to_add:
    print("For teams that need to be added:")
    print("1. Find their division on GotSport")
    print("2. Check if they're in an existing division file")
    print("3. Create a new fetch script if needed")
    print("4. Add to update_all_data.py workflow")
    print()
    print("Teams to investigate:")
    for team in sorted(need_to_add):
        print(f"   - {team}")
else:
    print("[OK] All teams are already tracked!")
    print("   No action needed.")

