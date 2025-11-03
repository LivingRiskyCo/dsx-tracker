#!/usr/bin/env python3
import pandas as pd
import os
import re

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
    
    # Exclude DSX from division data (we'll add it separately)
    combined = combined[~combined['Team'].str.contains('DSX', case=False, na=False)]
    combined['GP'] = pd.to_numeric(combined['GP'], errors='coerce').fillna(0)
    combined = combined[combined['GP'] >= 3].copy()
    
    # Classify teams by age/year
    def classify_team_age(team_name):
        """Classify team as 2018, 2017, or 17/18 (mixed)"""
        team_str = str(team_name).lower()
        
        # Check for mixed age indicators (17/18, B17/18, B18/17, etc.)
        if re.search(r'17[/-]18|18[/-]17|b17[/-]18|b18[/-]17|17/18|18/17', team_str):
            return '17/18'
        # Check for 2017 indicators (2017, B17, U9)
        elif re.search(r'2017|b17\b|u9\b', team_str) or '2017' in team_str:
            return '2017'
        # Check for 2018 indicators (2018, B18, U8)
        elif re.search(r'2018|b18\b|u8\b|u08', team_str) or '2018' in team_str:
            return '2018'
        else:
            # Default to 2018 if unclear
            return '2018'
    
    # Add age classification column
    combined['AgeGroup'] = combined['Team'].apply(classify_team_age)
    
    # Separate teams by age group
    teams_2018 = combined[combined['AgeGroup'] == '2018'].copy()
    teams_2017 = combined[combined['AgeGroup'] == '2017'].copy()
    teams_17_18 = combined[combined['AgeGroup'] == '17/18'].copy()
    
    # Combine 17/18 teams with 2017 (as requested)
    if not teams_17_18.empty:
        teams_2017 = pd.concat([teams_2017, teams_17_18], ignore_index=True)
    
    # Add DSX to 2018 rankings if we have it
    if dsx_row:
        dsx_df = pd.DataFrame([dsx_row])
        teams_2018 = pd.concat([teams_2018, dsx_df], ignore_index=True)
    
    # Sort and rank each age group
    def rank_teams(df):
        """Sort and rank teams by PPG and Strength Index"""
        if df.empty:
            return df
        df = df.sort_values(['PPG', 'StrengthIndex'], ascending=[False, False])
        df['Rank'] = range(1, len(df) + 1)
        return df
    
    teams_2018 = rank_teams(teams_2018)
    teams_2017 = rank_teams(teams_2017)
    
    # Ensure all required columns exist
    required_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
    for col in required_cols:
        if col not in teams_2018.columns:
            teams_2018[col] = 0
        if col not in teams_2017.columns:
            teams_2017[col] = 0
    
    # Save 2018 rankings (all teams 3+ games)
    output_file_2018 = 'Rankings_2018_Teams_3Plus_Games.csv'
    teams_2018[required_cols].to_csv(output_file_2018, index=False)
    print(f"[OK] Created {output_file_2018}")
    print(f"   Total 2018 teams: {len(teams_2018)}")
    print()
    
    # Save 2017 rankings (includes 17/18 teams, all teams 3+ games)
    output_file_2017 = 'Rankings_2017_Teams_3Plus_Games.csv'
    teams_2017[required_cols].to_csv(output_file_2017, index=False)
    print(f"[OK] Created {output_file_2017}")
    print(f"   Total 2017 teams (including 17/18): {len(teams_2017)}")
    print()
    
    # Save 2018 teams with 6+ games (most accurate)
    teams_2018_6plus = teams_2018[teams_2018['GP'] >= 6].copy()
    teams_2018_6plus = rank_teams(teams_2018_6plus)
    
    output_file_2018_6plus = 'Rankings_2018_Teams_6Plus_Games.csv'
    teams_2018_6plus[required_cols].to_csv(output_file_2018_6plus, index=False)
    print(f"[OK] Created {output_file_2018_6plus}")
    print(f"   Total 2018 teams (6+ games): {len(teams_2018_6plus)}")
    print()
    
    # Also create combined rankings for backward compatibility
    combined_all = pd.concat([teams_2018, teams_2017], ignore_index=True)
    combined_all = combined_all.sort_values(['PPG', 'StrengthIndex'], ascending=[False, False])
    combined_all['Rank'] = range(1, len(combined_all) + 1)
    
    output_file = 'Comprehensive_All_Teams_Rankings.csv'
    combined_all[required_cols].to_csv(output_file, index=False)
    print(f"[OK] Created {output_file} (combined)")
    print(f"   Total teams: {len(combined_all)}")
    print()
    
    # Save top teams (6+ games) - most accurate rankings
    teams_6plus = combined_all[combined_all['GP'] >= 6].copy()
    teams_6plus = teams_6plus.sort_values(['PPG', 'StrengthIndex'], ascending=[False, False])
    teams_6plus['Rank'] = range(1, len(teams_6plus) + 1)
    
    output_file_6plus = 'Top_93_Teams_Rankings_6Plus_Games.csv'
    teams_6plus[required_cols].to_csv(output_file_6plus, index=False)
    print(f"[OK] Created {output_file_6plus}")
    print(f"   Total teams (6+ games): {len(teams_6plus)}")
    
    # Find DSX position in 2018 rankings
    if dsx_row:
        dsx_ranked_2018 = teams_2018[teams_2018['Team'].str.contains('DSX', case=False, na=False)]
        if not dsx_ranked_2018.empty:
            dsx_rank_2018 = int(dsx_ranked_2018.iloc[0]['Rank'])
            print(f"\nDSX Position (2018 teams): #{dsx_rank_2018} of {len(teams_2018)} teams (3+ games)")
            
            dsx_2018_6plus = teams_2018_6plus[teams_2018_6plus['Team'].str.contains('DSX', case=False, na=False)]
            if not dsx_2018_6plus.empty:
                dsx_rank_2018_6plus = int(dsx_2018_6plus.iloc[0]['Rank'])
                print(f"DSX Position (2018 teams, 6+ games): #{dsx_rank_2018_6plus} of {len(teams_2018_6plus)} teams")
    
    print()
    print("[OK] Rankings CSV files created successfully!")
else:
    print("[ERROR] No division data found!")
