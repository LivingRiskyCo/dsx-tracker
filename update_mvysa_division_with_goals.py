"""
Update MVYSA B09-3 Division Rankings with actual goals from BSA Celtic schedules
"""

import pandas as pd

print("=" * 60)
print("UPDATING MVYSA B09-3 DIVISION WITH ACTUAL GOALS")
print("=" * 60)
print()

# Load the division rankings (has W-L-D but no goals)
division = pd.read_csv("MVYSA_B09_3_Division_Rankings.csv")
print(f"[OK] Loaded {len(division)} teams from MVYSA B09-3 division\n")

# Load BSA Celtic schedules (has actual game scores)
try:
    schedules = pd.read_csv("BSA_Celtic_Schedules.csv")
    print(f"[OK] Loaded {len(schedules)} games from BSA Celtic schedules\n")
    
    # Calculate actual goals for each team
    for idx, team_row in division.iterrows():
        team_name = team_row['Team']
        
        # Get all games for this team
        team_games = schedules[schedules['OpponentTeam'] == team_name].copy()
        
        # Filter completed games (has scores)
        completed = team_games[team_games['GF'].notna() & (team_games['GF'] != '')].copy()
        
        if len(completed) > 0:
            # Convert to numeric
            completed['GF'] = pd.to_numeric(completed['GF'], errors='coerce')
            completed['GA'] = pd.to_numeric(completed['GA'], errors='coerce')
            
            # Calculate totals
            total_gf = completed['GF'].sum()
            total_ga = completed['GA'].sum()
            total_gd = total_gf - total_ga
            
            # Update division data
            division.at[idx, 'GF'] = total_gf
            division.at[idx, 'GA'] = total_ga
            division.at[idx, 'GD'] = total_gd
            
            print(f"[OK] {team_name}")
            print(f"     Games: {len(completed)}, GF: {total_gf}, GA: {total_ga}, GD: {total_gd:+.0f}")
        else:
            print(f"[!] {team_name} - No schedule data available")
    
    print()
    print("=" * 60)
    print("SAVING UPDATED DIVISION FILE")
    print("=" * 60)
    
    # Save updated division file
    division.to_csv("MVYSA_B09_3_Division_Rankings.csv", index=False)
    print(f"\n[OK] Saved updated MVYSA_B09_3_Division_Rankings.csv")
    
    # Display updated data
    print()
    print("=" * 60)
    print("UPDATED DIVISION STANDINGS")
    print("=" * 60)
    print()
    
    display_cols = ['Rank', 'Team', 'GP', 'W', 'L', 'D', 'GF', 'GA', 'GD', 'PPG', 'StrengthIndex']
    print(division[display_cols].to_string(index=False))
    print()
    
except FileNotFoundError:
    print("[ERROR] BSA_Celtic_Schedules.csv not found!")
    print("Cannot calculate actual goals without schedule data.")

