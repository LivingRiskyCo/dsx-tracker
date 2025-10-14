"""Quick health check for DSX tracker data completeness"""
import pandas as pd

print("=" * 60)
print("DSX TRACKER DATA COMPLETENESS CHECK")
print("=" * 60)
print()

# Load upcoming opponents
try:
    upcoming = pd.read_csv('DSX_Upcoming_Opponents.csv')
    print(f"[OK] Loaded {len(upcoming)} upcoming games\n")
except:
    upcoming = pd.DataFrame()
    print("[!] No upcoming opponents file\n")

# Load all division data
division_files = [
    'OCL_BU08_Stripes_Division_Rankings.csv',
    'OCL_BU08_White_Division_Rankings.csv',
    'OCL_BU08_Stars_7v7_Division_Rankings.csv',
    'MVYSA_B09_3_Division_Rankings.csv'
]

all_divs = []
for f in division_files:
    try:
        df = pd.read_csv(f)
        all_divs.append(df)
        print(f"[OK] {f}: {len(df)} teams")
    except:
        print(f"[!] {f}: Not found")

print()
print("=" * 60)
print("UPCOMING OPPONENTS DATA CHECK")
print("=" * 60)
print()

if not upcoming.empty and all_divs:
    divs = pd.concat(all_divs, ignore_index=True)
    
    for opp in upcoming['Opponent'].unique():
        if opp in divs['Team'].values:
            opp_data = divs[divs['Team'] == opp].iloc[0]
            has_goals = opp_data.get('GF', 0) > 0
            status = "[OK] Complete" if has_goals else "[!] No Goals"
            print(f"{opp}: {status}")
        else:
            print(f"{opp}: [X] Not Found")

print()
print("=" * 60)
print("DIVISION DATA SUMMARY")
print("=" * 60)
print()

if all_divs:
    divs = pd.concat(all_divs, ignore_index=True)
    teams_with_goals = len(divs[divs['GF'] > 0])
    total_teams = len(divs)
    
    print(f"Total teams tracked: {total_teams}")
    print(f"Teams with GF/GA data: {teams_with_goals} ({teams_with_goals/total_teams*100:.0f}%)")
    print(f"Teams without goals: {total_teams - teams_with_goals}")
    print()
    
    if teams_with_goals < total_teams:
        print("Teams without goal data:")
        no_goals = divs[divs['GF'] == 0]['Team'].tolist()
        for team in no_goals[:10]:  # Show first 10
            print(f"  - {team}")

print()
print("=" * 60)
print("[OK] Data check complete!")
print("=" * 60)

