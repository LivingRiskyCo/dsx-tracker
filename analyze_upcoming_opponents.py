"""
Analyze Upcoming Opponents
Scout teams DSX will face soon
"""

import pandas as pd
from datetime import datetime

print("=" * 70)
print("DSX UPCOMING OPPONENTS ANALYSIS")
print("=" * 70)
print()

# Load upcoming schedule
upcoming = pd.read_csv("DSX_Upcoming_Opponents.csv")

print("NEXT GAMES:")
print()

for _, game in upcoming.iterrows():
    print(f"[DATE] {game['Date']}: {game['Opponent']}")
    print(f"   Location: {game['Location']}")
    print(f"   League: {game['League']}")
    print()

print("=" * 70)
print("OPPONENT SCOUTING REPORTS")
print("=" * 70)
print()

# Analyze BSA Celtic teams
print("1. BSA CELTIC TEAMS (MVYSA)")
print("-" * 70)
print()

try:
    bsa_schedules = pd.read_csv("BSA_Celtic_Schedules.csv")
    
    for team in ["BSA Celtic 18B United", "BSA Celtic 18B City"]:
        team_matches = bsa_schedules[bsa_schedules['OpponentTeam'] == team]
        
        # Filter completed matches (have scores)
        completed = team_matches[team_matches['GF'] != ''].copy()
        
        if len(completed) > 0:
            completed['GF'] = pd.to_numeric(completed['GF'])
            completed['GA'] = pd.to_numeric(completed['GA'])
            completed['GD'] = completed['GF'] - completed['GA']
            
            # Calculate record
            wins = (completed['GD'] > 0).sum()
            draws = (completed['GD'] == 0).sum()
            losses = (completed['GD'] < 0).sum()
            
            print(f"[TEAM] {team}")
            print(f"   Record: {wins}-{losses}-{draws} (W-L-D)")
            print(f"   Games Played: {len(completed)}")
            print(f"   Goals For: {completed['GF'].sum()} ({completed['GF'].mean():.2f}/game)")
            print(f"   Goals Against: {completed['GA'].sum()} ({completed['GA'].mean():.2f}/game)")
            print(f"   Goal Diff: {completed['GD'].sum():+} ({completed['GD'].mean():+.2f}/game)")
            print()
            
            # Strength assessment
            ppg = (wins * 3 + draws) / len(completed)
            gd_per_game = completed['GD'].mean()
            
            # Calculate approximate Strength Index
            ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
            gd_norm = (max(-5.0, min(5.0, gd_per_game)) + 5.0) / 10.0 * 100.0
            strength_index = 0.7 * ppg_norm + 0.3 * gd_norm
            
            print(f"   PPG: {ppg:.2f}")
            print(f"   Estimated Strength Index: {strength_index:.1f}")
            print()
            
            # DSX comparison
            dsx_si = 35.6  # From season data
            dsx_ppg = 1.25
            
            if strength_index > dsx_si + 10:
                print(f"   [WARN] STRONGER than DSX (SI: {strength_index:.1f} vs {dsx_si:.1f})")
                print(f"   -> Defensive focus, stay organized")
            elif strength_index < dsx_si - 10:
                print(f"   [OK] WEAKER than DSX (SI: {strength_index:.1f} vs {dsx_si:.1f})")
                print(f"   -> Offensive pressure, get 3 points")
            else:
                print(f"   [EVEN] SIMILAR to DSX (SI: {strength_index:.1f} vs {dsx_si:.1f})")
                print(f"   -> Balanced approach, competitive match")
            print()
            
            # Recent form
            recent_5 = completed.tail(5) if len(completed) >= 5 else completed
            recent_wins = (recent_5['GD'] > 0).sum()
            recent_points = recent_wins * 3 + (recent_5['GD'] == 0).sum()
            
            print(f"   Recent Form (last {len(recent_5)} games):")
            print(f"   Points: {recent_points}/{len(recent_5)*3} ({recent_points/len(recent_5):.2f} PPG)")
            
            if recent_points / len(recent_5) > ppg:
                print(f"   [UP] Improving form!")
            elif recent_points / len(recent_5) < ppg:
                print(f"   [DOWN] Declining form")
            else:
                print(f"   [STABLE] Consistent form")
            
            print()
            print(f"   Recent Results:")
            for _, match in recent_5.iterrows():
                if pd.notna(match['GF']) and pd.notna(match['GA']):
                    result = "W" if match['GD'] > 0 else "D" if match['GD'] == 0 else "L"
                    print(f"   {result} {int(match['GF'])}-{int(match['GA'])} vs {match['TheirOpponent']}")
                else:
                    print(f"   Scheduled vs {match['TheirOpponent']}")
            
            print()
            print("-" * 70)
            print()
        else:
            print(f"[TEAM] {team}")
            print(f"   No completed matches available")
            print()

except FileNotFoundError:
    print("[WARN] BSA Celtic schedules not found. Run: python fetch_bsa_celtic.py")
    print()

# Analyze Club Ohio West (from White division data)
print("2. CLUB OHIO WEST 18B ACADEMY (OCL BU08 WHITE)")
print("-" * 70)
print()

try:
    # Club Ohio West is in the WHITE division, not Stripes
    division = pd.read_csv("OCL_BU08_White_Division_Rankings.csv")
    
    # Try to find Club Ohio West
    club_ohio = division[division['Team'].str.contains("Club Ohio", na=False, case=False)]
    
    if not club_ohio.empty:
        team = club_ohio.iloc[0]
        print(f"[TEAM] {team['Team']}")
        print(f"   Division: OCL BU08 7v7 White (NOT Stripes)")
        print(f"   Rank: #{int(team['Rank'])} of {len(division)}")
        print(f"   Record: {int(team['W'])}-{int(team['D'])}-{int(team['L'])}")
        print(f"   Games Played: {int(team['GP'])}")
        print(f"   Goals/Game: {team['GF']:.2f} for, {team['GA']:.2f} against")
        print(f"   Goal Diff/Game: {team['GD']:+.2f}")
        print(f"   PPG: {team['PPG']:.2f}")
        print(f"   Strength Index: {team['StrengthIndex']:.1f}")
        print()
        
        # DSX comparison
        dsx_si = 35.6
        si_diff = dsx_si - team['StrengthIndex']
        
        if si_diff > 10:
            print(f"   [OK] DSX is STRONGER (SI: {dsx_si:.1f} vs {team['StrengthIndex']:.1f})")
            print(f"   -> Target: Win (3 points)")
        elif si_diff < -10:
            print(f"   [WARN] Opponent is STRONGER (SI: {team['StrengthIndex']:.1f} vs {dsx_si:.1f})")
            print(f"   -> Target: Defensive focus, earn a point")
        else:
            print(f"   [EVEN] EVENLY MATCHED (SI: {team['StrengthIndex']:.1f} vs {dsx_si:.1f})")
            print(f"   -> Target: Fight for all 3 points")
        print()
    else:
        print("   [WARN] Not found in White division data")
        print("   Run: python fetch_gotsport_white_division.py")
        print()
        
except FileNotFoundError:
    print("[WARN] White division data not found. Run: python fetch_gotsport_white_division.py")
    print()

print("=" * 70)
print("PREPARATION RECOMMENDATIONS")
print("=" * 70)
print()

print("WEEK 1 (Oct 18-19):")
print("  1. Review BSA Celtic United results (run analysis above)")
print("  2. Check Club Ohio West division standing")
print("  3. Focus training:")
print("     - Defensive organization (if facing stronger team)")
print("     - Finishing chances (if facing similar team)")
print("     - Build confidence (if facing weaker team)")
print()

print("WEEK 2 (Nov 1):")
print("  1. Review BSA Celtic City results")
print("  2. Learn from first BSA Celtic matchup")
print("  3. Adjust tactics based on Week 1 performance")
print()

print("=" * 70)
print("SCOUT MORE")
print("=" * 70)
print()

print("To get latest opponent data:")
print("  python fetch_bsa_celtic.py")
print("  python fetch_gotsport_division.py")
print()

print("[OK] Analysis complete")

