#!/usr/bin/env python3
import pandas as pd
import os

print("=== ANALYZING RANKINGS DATA QUALITY ===")
print()

# Load all division data
all_divisions = []

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

for file in division_files:
    if os.path.exists(file):
        try:
            df = pd.read_csv(file, index_col=False).reset_index(drop=True)
            all_divisions.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")

if all_divisions:
    combined = pd.concat(all_divisions, ignore_index=True)
    
    # Filter out 2017 teams
    combined = combined[~combined['Team'].str.contains('2017', case=False, na=False)]
    
    print(f"Total teams tracked: {len(combined)}")
    print()
    
    # Analyze games played distribution
    if 'GP' in combined.columns:
        gp_series = pd.to_numeric(combined['GP'], errors='coerce').fillna(0)
        
        print("=== GAMES PLAYED DISTRIBUTION ===")
        print(f"Teams with 0 games: {len(combined[gp_series == 0])}")
        print(f"Teams with 1-2 games: {len(combined[(gp_series >= 1) & (gp_series <= 2)])}")
        print(f"Teams with 3 games: {len(combined[gp_series == 3])}")
        print(f"Teams with 4-5 games: {len(combined[(gp_series >= 4) & (gp_series <= 5)])}")
        print(f"Teams with 6-8 games: {len(combined[(gp_series >= 6) & (gp_series <= 8)])}")
        print(f"Teams with 9+ games: {len(combined[gp_series >= 9])}")
        print()
        
        print("=== DATA QUALITY ASSESSMENT ===")
        
        # Teams with sufficient data (6+ games recommended for accurate ranking)
        sufficient_data = combined[gp_series >= 6]
        limited_data = combined[(gp_series >= 3) & (gp_series < 6)]
        insufficient_data = combined[gp_series < 3]
        no_data = combined[gp_series == 0]
        
        print(f"Teams with sufficient data (6+ games): {len(sufficient_data)}")
        print(f"Teams with limited data (3-5 games): {len(limited_data)}")
        print(f"Teams with insufficient data (1-2 games): {len(insufficient_data)}")
        print(f"Teams with no data (0 games): {len(no_data)}")
        print()
        
        if len(no_data) > 0:
            print("Teams with NO game data:")
            for _, row in no_data.head(10).iterrows():
                print(f"  - {row['Team']} (GP: {row['GP']})")
            print()
        
        if len(insufficient_data) > 0:
            print("Teams with insufficient data (1-2 games):")
            for _, row in insufficient_data.head(10).iterrows():
                try:
                    gp_val = int(float(row['GP'])) if not pd.isna(row['GP']) else 0
                    print(f"  - {row['Team']} (GP: {gp_val})")
                except:
                    print(f"  - {row['Team']} (GP: 0)")
            print()
        
        if len(limited_data) > 0:
            print(f"Teams with limited data (3-5 games) - Tournament-only teams:")
            for _, row in limited_data.head(10).iterrows():
                team = str(row['Team'])[:50]
                print(f"  - {team} (GP: {int(row['GP'])}, PPG: {row['PPG']:.2f})")
            print()
        
        # Calculate accurate ranking threshold
        print("=== RANKING RECOMMENDATIONS ===")
        print()
        print("For ACCURATE rankings, we should use:")
        print(f"  - Minimum: 3 games (tournament teams) - {len(combined[gp_series >= 3])} teams")
        print(f"  - Recommended: 6+ games (league teams) - {len(sufficient_data)} teams")
        print()
        
        # Show top teams by data quality
        print("=== TOP RANKED TEAMS (6+ GAMES) ===")
        sufficient_sorted = sufficient_data.sort_values(['PPG', 'StrengthIndex'], ascending=[False, False])
        sufficient_sorted['Rank'] = range(1, len(sufficient_sorted) + 1)
        
        for idx, row in sufficient_sorted.head(15).iterrows():
            team = str(row['Team'])[:45]
            if 'DSX' in team:
                team = f'***{team}***'
            print(f'{int(row["Rank"]):2d}. {team}: {int(row["GP"])} games, PPG {row["PPG"]:.2f}, SI {row["StrengthIndex"]:.1f}')
        
        # Check DSX position
        dsx_row = sufficient_sorted[sufficient_sorted['Team'].str.contains('DSX', case=False, na=False)]
        if not dsx_row.empty:
            dsx_rank = int(dsx_row.iloc[0]['Rank'])
            print(f'\n***DSX Position (among teams with 6+ games): #{dsx_rank} of {len(sufficient_sorted)} teams***')
        
        print()
        print("=== SUMMARY ===")
        print(f"We can accurately rank {len(sufficient_data)} teams (6+ games)")
        print(f"We can reasonably rank {len(combined[gp_series >= 3])} teams (3+ games including tournaments)")
        print(f"We should exclude {len(combined[gp_series < 3])} teams from rankings (insufficient data)")
    else:
        print("ERROR: No 'GP' column found in combined data")
else:
    print("ERROR: No division data loaded")

