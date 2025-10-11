#!/usr/bin/env python3
"""
Fetch OCL BU08 Stars Division standings from GotSport
Check for potential DSX opponents
"""

import pandas as pd
from datetime import datetime

def main():
    print("="*70)
    print("OCL BU08 STARS DIVISION (5v5) ANALYZER")
    print("Fall 2025 Season")
    print("="*70)
    
    # Manual entry from the provided HTML
    teams_data = [
        {'Rank': 1, 'Team': 'Club Ohio Club Ohio East 18B Academy', 'GP': 6, 'W': 6, 'L': 0, 'D': 0, 'GF': 6.0, 'GA': 0.83, 'GD': 5.17, 'Pts': 18, 'PPG': 3.0},
        {'Rank': 2, 'Team': 'Worthington United Worthington United 94 2018 Boys Navy 1', 'GP': 4, 'W': 3, 'L': 1, 'D': 0, 'GF': 4.0, 'GA': 2.75, 'GD': 1.25, 'Pts': 9, 'PPG': 2.25},
        {'Rank': 3, 'Team': 'Grasshoppers FC Grasshoppers FC - 2018B Pool 2', 'GP': 6, 'W': 4, 'L': 2, 'D': 0, 'GF': 3.0, 'GA': 2.0, 'GD': 1.0, 'Pts': 12, 'PPG': 2.0},
        {'Rank': 4, 'Team': 'Columbus Force SC Columbus Force 18B Blue', 'GP': 6, 'W': 2, 'L': 3, 'D': 1, 'GF': 2.83, 'GA': 4.67, 'GD': -1.84, 'Pts': 7, 'PPG': 1.17},
        {'Rank': 5, 'Team': 'Columbus United Columbus United B\'18 Academy', 'GP': 6, 'W': 2, 'L': 3, 'D': 1, 'GF': 2.33, 'GA': 3.83, 'GD': -1.5, 'Pts': 7, 'PPG': 1.17},
        {'Rank': 6, 'Team': 'Xcel Sports Soccer Academy Xcel 2018', 'GP': 3, 'W': 1, 'L': 2, 'D': 0, 'GF': 4.33, 'GA': 5.0, 'GD': -0.67, 'Pts': 3, 'PPG': 1.0},
        {'Rank': 7, 'Team': 'Club Ohio Club Ohio West 19B Academy', 'GP': 7, 'W': 1, 'L': 6, 'D': 0, 'GF': 1.57, 'GA': 3.43, 'GD': -1.86, 'Pts': 3, 'PPG': 0.43},
        {'Rank': 8, 'Team': 'Club Ohio Club Ohio West 19B Academy II', 'GP': 4, 'W': 0, 'L': 4, 'D': 0, 'GF': 0.75, 'GA': 4.25, 'GD': -3.5, 'Pts': 0, 'PPG': 0.0}
    ]
    
    # Calculate Strength Index
    for team in teams_data:
        ppg = team['PPG']
        gd_per_game = team['GD'] / team['GP'] if team['GP'] > 0 else 0.0
        
        # Normalize PPG (0-3 range) to 0-100
        ppg_normalized = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
        
        # Normalize GD per game (-5 to +5 range) to 0-100
        gd_normalized = (max(-5.0, min(5.0, gd_per_game)) + 5.0) / 10.0 * 100.0
        
        # Weighted average: 70% PPG, 30% GD
        team['StrengthIndex'] = round(0.7 * ppg_normalized + 0.3 * gd_normalized, 1)
        team['League/Division'] = 'OCL BU08 Stars (5v5)'
        team['SourceURL'] = 'https://system.gotsport.com/org_event/events/45535/results?group=418525'
    
    df = pd.DataFrame(teams_data)
    
    # Save to CSV
    output_file = "OCL_BU08_Stars_Division_Rankings.csv"
    df.to_csv(output_file, index=False)
    print(f"\n[OK] Saved to {output_file}")
    
    # Display summary
    print("\n" + "="*70)
    print("DIVISION STRENGTH RANKINGS")
    print("="*70)
    print()
    
    display_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
    print(df[display_cols].to_string(index=False))
    
    print("\n" + "="*70)
    print(f"Total Teams: {len(df)}")
    print(f"Data Source: GotSport OCL BU08 Stars Division (5v5)")
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    
    # Check for potential DSX opponents
    print("\n" + "="*70)
    print("POTENTIAL DSX OPPONENT CHECK")
    print("="*70)
    
    # Columbus United might match DSX's "Columbus United U8B"
    columbus_united = df[df['Team'].str.contains('Columbus United', case=False)]
    if not columbus_united.empty:
        team = columbus_united.iloc[0]
        print(f"\n[WARNING] POSSIBLE MATCH: {team['Team']}")
        print(f"   DSX played: 'Columbus United U8B' (twice)")
        print(f"   This division has: '{team['Team']}'")
        print()
        print(f"   Division Rank: #{int(team['Rank'])} of {len(df)}")
        print(f"   Record: {int(team['W'])}-{int(team['D'])}-{int(team['L'])}")
        print(f"   Strength Index: {team['StrengthIndex']:.1f}")
        print()
        print(f"   DSX Results vs 'Columbus United U8B':")
        print(f"   - Sep 27: 5-5 Draw")
        print(f"   - Sep 28: 4-3 Win")
        print()
        
        dsx_si = 35.6
        si_diff = team['StrengthIndex'] - dsx_si
        
        if si_diff > 10:
            print(f"   [ANALYSIS] This team is STRONGER than DSX (SI: {team['StrengthIndex']:.1f} vs {dsx_si})")
        elif si_diff < -10:
            print(f"   [ANALYSIS] DSX is STRONGER than this team (SI: {dsx_si} vs {team['StrengthIndex']:.1f})")
        else:
            print(f"   [ANALYSIS] Evenly matched (SI: {team['StrengthIndex']:.1f} vs {dsx_si})")
        
        print()
        print(f"   [OK] Recommendation: Update DSX_Matches_Fall2025.csv to clarify")
        print(f"      which Columbus United team was played")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

