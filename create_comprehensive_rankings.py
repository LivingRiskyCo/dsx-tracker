#!/usr/bin/env python3
import pandas as pd
import os

print("Creating comprehensive rankings CSV files...")
print()

# Load DSX match history
try:
    dsx_matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False).reset_index(drop=True)
    result_col = 'Result' if 'Result' in dsx_matches.columns else 'Outcome'
    completed = dsx_matches[dsx_matches[result_col].notna()].copy()
    
    dsx_gp = len(completed)
    dsx_w = len(completed[completed[result_col].str.contains('W', case=False, na=False)])
    dsx_d = len(completed[completed[result_col].str.contains('D', case=False, na=False)])
    dsx_l = len(completed[completed[result_col].str.contains('L', case=False, na=False)])
    dsx_gf = pd.to_numeric(completed['GF'], errors='coerce').fillna(0).sum()
    dsx_ga = pd.to_numeric(completed['GA'], errors='coerce').fillna(0).sum()
    dsx_gd = dsx_gf - dsx_ga
    dsx_pts = (dsx_w * 3) + dsx_d
    dsx_ppg = dsx_pts / dsx_gp if dsx_gp > 0 else 0
    dsx_gf_pg = dsx_gf / dsx_gp if dsx_gp > 0 else 0
    dsx_ga_pg = dsx_ga / dsx_gp if dsx_gp > 0 else 0
    dsx_gd_pg = dsx_gd / dsx_gp if dsx_gp > 0 else 0
    
    # Calculate DSX Strength Index
    ppg_norm = max(0.0, min(3.0, dsx_ppg)) / 3.0 * 100.0
    gdpg_norm = (max(-5.0, min(5.0, dsx_gd_pg)) + 5.0) / 10.0 * 100.0
    dsx_strength = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
    
    dsx_row = {
        'Rank': 0,  # Will be set after sorting
        'Team': 'DSX Orange 2018',
        'GP': dsx_gp,
        'W': dsx_w,
        'D': dsx_d,
        'L': dsx_l,
        'GF': round(dsx_gf_pg, 2),
        'GA': round(dsx_ga_pg, 2),
        'GD': round(dsx_gd_pg, 2),
        'Pts': dsx_pts,
        'PPG': dsx_ppg,
        'StrengthIndex': dsx_strength
    }
except Exception as e:
    print(f"Error loading DSX matches: {e}")
    dsx_row = None

# Load all division data
division_files = [
    'OCL_BU08_Stripes_Division_Rankings.csv',
    'OCL_BU08_White_Division_Rankings.csv',
    'OCL_BU08_Stars_Division_Rankings.csv',
    'OCL_BU08_Stars_7v7_Division_Rankings.csv',
    'MVYSA_B09_3_Division_Rankings.csv',
    'Club_Ohio_Fall_Classic_2025_Division_Rankings.csv',
    'CU_Fall_Finale_2025_Division_Rankings.csv',
    'Haunted_Classic_B08Orange_Division_Rankings.csv',
    'Haunted_Classic_B08Black_Division_Rankings.csv',
    'CPL_Fall_2025_Division_Rankings.csv'
]

all_divisions = []
for file in division_files:
    if os.path.exists(file):
        try:
            df = pd.read_csv(file, index_col=False).reset_index(drop=True)
            all_divisions.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")

if all_divisions:
    combined = pd.concat(all_divisions, ignore_index=True)
    
    # Apply filters
    combined = combined[~combined['Team'].str.contains('2017', case=False, na=False)]
    combined = combined[~combined['Team'].str.contains('DSX', case=False, na=False)]  # Exclude DSX
    combined['GP'] = pd.to_numeric(combined['GP'], errors='coerce').fillna(0)
    combined = combined[combined['GP'] >= 3].copy()
    
    # Add DSX if we have it
    if dsx_row:
        dsx_df = pd.DataFrame([dsx_row])
        combined = pd.concat([combined, dsx_df], ignore_index=True)
    
    # Sort and rank
    combined = combined.sort_values(['PPG', 'StrengthIndex'], ascending=[False, False])
    combined['Rank'] = range(1, len(combined) + 1)
    
    # Ensure all required columns exist
    required_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
    for col in required_cols:
        if col not in combined.columns:
            combined[col] = 0
    
    # Save comprehensive rankings (all teams 3+ games)
    output_file = 'Comprehensive_All_Teams_Rankings.csv'
    combined[required_cols].to_csv(output_file, index=False)
    print(f"[OK] Created {output_file}")
    print(f"   Total teams: {len(combined)}")
    print()
    
    # Save top 93 teams (6+ games) - most accurate rankings
    teams_6plus = combined[combined['GP'] >= 6].copy()
    teams_6plus = teams_6plus.sort_values(['PPG', 'StrengthIndex'], ascending=[False, False])
    teams_6plus['Rank'] = range(1, len(teams_6plus) + 1)
    
    output_file_6plus = 'Top_93_Teams_Rankings_6Plus_Games.csv'
    teams_6plus[required_cols].to_csv(output_file_6plus, index=False)
    print(f"[OK] Created {output_file_6plus}")
    print(f"   Total teams (6+ games): {len(teams_6plus)}")
    
    # Find DSX position
    if dsx_row:
        dsx_ranked = combined[combined['Team'].str.contains('DSX', case=False, na=False)]
        if not dsx_ranked.empty:
            dsx_rank = int(dsx_ranked.iloc[0]['Rank'])
                    print(f"\nDSX Position: #{dsx_rank} of {len(combined)} teams (3+ games)")
                    
                    dsx_6plus = teams_6plus[teams_6plus['Team'].str.contains('DSX', case=False, na=False)]
                    if not dsx_6plus.empty:
                        dsx_rank_6plus = int(dsx_6plus.iloc[0]['Rank'])
                        print(f"DSX Position (6+ games): #{dsx_rank_6plus} of {len(teams_6plus)} teams")
    
    print()
    print("[OK] Rankings CSV files created successfully!")
else:
    print("[ERROR] No division data found!")

