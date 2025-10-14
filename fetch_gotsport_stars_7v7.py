#!/usr/bin/env python3
"""
Fetch OCL BU08 Stars 7v7 Division standings from GotSport
Includes Elite FC Arsenal (DSX opponent)
"""

import pandas as pd
from datetime import datetime

def calculate_strength_index(row):
    """
    Calculate StrengthIndex using PPG and GD/GP
    Formula: 70% PPG-based + 30% GD-based
    """
    try:
        ppg = float(row.get('PPG', 0))
        gp = float(row.get('GP', 1))
        gd = float(row.get('GD', 0))
        
        gdpg = (gd / gp) if gp > 0 else 0.0
        
        # Normalize PPG (0-3 range) to 0-100
        ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
        
        # Normalize GD per game (-5 to +5 range) to 0-100
        gdpg_norm = (max(-5.0, min(5.0, gdpg)) + 5.0) / 10.0 * 100.0
        
        # Weighted average: 70% PPG, 30% GD
        strength = 0.7 * ppg_norm + 0.3 * gdpg_norm
        return round(strength, 1)
    except Exception:
        return 0.0

def main():
    print("="*70)
    print("OCL BU08 STARS 7v7 DIVISION ANALYZER")
    print("Fall 2025 Season")
    print("="*70)
    
    # Data from GotSport standings (as of Oct 14, 2025)
    # Source: https://system.gotsport.com/org_event/events/45535/results
    teams_data = [
        {
            'Rank': 1,
            'Team': 'Grasshoppers FC Grasshoppers FC - 2018B Pool 1 Black',
            'GP': 6,
            'W': 6,
            'L': 0,
            'D': 0,
            'GF': 8.67,
            'GA': 0.83,
            'GD': 7.84,
            'Pts': 18,
            'PPG': 3.0
        },
        {
            'Rank': 2,
            'Team': 'Sporting Columbus Sporting Columbus Boys 2018 I',
            'GP': 8,
            'W': 5,
            'L': 3,
            'D': 0,
            'GF': 3.0,
            'GA': 3.13,
            'GD': -0.13,
            'Pts': 15,
            'PPG': 1.88
        },
        {
            'Rank': 3,
            'Team': 'Club Oranje Club Oranje Raptors 2018 BU08 Oranje',
            'GP': 8,
            'W': 5,
            'L': 3,
            'D': 0,
            'GF': 3.5,
            'GA': 3.13,
            'GD': 0.37,
            'Pts': 15,
            'PPG': 1.88
        },
        {
            'Rank': 4,
            'Team': 'Ohio Premier 2018 Boys Academy Dublin Grey',
            'GP': 6,
            'W': 3,
            'L': 3,
            'D': 0,
            'GF': 3.5,
            'GA': 3.17,
            'GD': 0.33,
            'Pts': 9,
            'PPG': 1.5
        },
        {
            'Rank': 5,
            'Team': 'Northwest FC Northwest FC 2018B Academy Orange',
            'GP': 6,
            'W': 2,
            'L': 4,
            'D': 0,
            'GF': 3.0,
            'GA': 5.0,
            'GD': -2.0,
            'Pts': 6,
            'PPG': 1.0
        },
        {
            'Rank': 6,
            'Team': 'Elite FC Elite FC 2018 Boys Arsenal',
            'GP': 8,
            'W': 2,
            'L': 5,
            'D': 1,
            'GF': 1.38,
            'GA': 3.0,
            'GD': -1.62,
            'Pts': 7,
            'PPG': 0.88
        },
        {
            'Rank': 7,
            'Team': 'Ohio Premier 2018 Boys Academy UA Grey',
            'GP': 4,
            'W': 0,
            'L': 4,
            'D': 0,
            'GF': 1.0,
            'GA': 6.0,
            'GD': -5.0,
            'Pts': 0,
            'PPG': 0.0
        }
    ]
    
    # Calculate Strength Index for each team
    for team in teams_data:
        team['League/Division'] = 'OCL BU08 Stars (7v7)'
        team['SourceURL'] = 'https://system.gotsport.com/org_event/events/45535/results'
    
    df = pd.DataFrame(teams_data)
    
    # Calculate StrengthIndex
    df['StrengthIndex'] = df.apply(calculate_strength_index, axis=1)
    
    # Save to CSV
    output_file = "OCL_BU08_Stars_7v7_Division_Rankings.csv"
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
    print(f"Data Source: GotSport OCL BU08 Stars 7v7 Division")
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    
    # Check for DSX opponent match
    print("\n" + "="*70)
    print("DSX OPPONENT CHECK")
    print("="*70)
    
    # Elite FC Arsenal is a known DSX opponent
    arsenal = df[df['Team'].str.contains('Arsenal', case=False)]
    if not arsenal.empty:
        team = arsenal.iloc[0]
        print(f"\n[OK] MATCH FOUND: {team['Team']}")
        print(f"   DSX played: 'Elite FC 2018 Boys Arsenal'")
        print()
        print(f"   Division Rank: #{int(team['Rank'])} of {len(df)}")
        print(f"   Record: {int(team['W'])}-{int(team['D'])}-{int(team['L'])}")
        print(f"   Strength Index: {team['StrengthIndex']:.1f}")
        print(f"   PPG: {team['PPG']:.2f}")
        print()
        print(f"   [OK] This team is now tracked in your dashboard!")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

