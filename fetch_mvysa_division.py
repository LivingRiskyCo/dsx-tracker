"""
Fetch MVYSA B09-3 Division standings (BSA Celtic division)
Creates a division rankings file similar to OCL data
"""

import pandas as pd
from datetime import datetime


def create_mvysa_b09_3_standings():
    """
    Manually create MVYSA B09-3 standings from web scrape results
    Source: https://www.mvysa.com/cgi-bin/sked.cgi?fnc=sked2&bt=4264&season=202509
    
    Division B09-3 Standings for Fall 2025:
    Position  Team                                  Wins  Loses  Ties  Points
    1         Southstars SC B17                     8     0      0     24
    2         Springfield Thunder SC Navy B2017     5     2      0     15
    3         Troy Rattlers B17/18                  3     4      1     10
    3         BSA Celtic 18B City                   3     3      1     10
    5         BSA Celtic 18B United                 1     4      3     6
    6         Warrior White B17/18                  0     7      1     1
    """
    
    print("=" * 60)
    print("MVYSA B09-3 DIVISION ANALYZER")
    print("Fall 2025 Season")
    print("=" * 60)
    print()
    
    # Manual data from MVYSA website
    teams_data = [
        {
            'Team': 'Southstars SC B17',
            'GP': 8,
            'W': 8,
            'L': 0,
            'D': 0,
            'GF': 0,  # Not provided by MVYSA
            'GA': 0,  # Not provided by MVYSA
            'GD': 0,
            'Pts': 24,
            'PPG': 3.00
        },
        {
            'Team': 'Springfield Thunder SC Navy B2017',
            'GP': 7,
            'W': 5,
            'L': 2,
            'D': 0,
            'GF': 0,
            'GA': 0,
            'GD': 0,
            'Pts': 15,
            'PPG': 2.14
        },
        {
            'Team': 'Troy Rattlers B17/18',
            'GP': 8,
            'W': 3,
            'L': 4,
            'D': 1,
            'GF': 0,
            'GA': 0,
            'GD': 0,
            'Pts': 10,
            'PPG': 1.25
        },
        {
            'Team': 'BSA Celtic 18B City',
            'GP': 7,
            'W': 3,
            'L': 3,
            'D': 1,
            'GF': 0,
            'GA': 0,
            'GD': 0,
            'Pts': 10,
            'PPG': 1.43
        },
        {
            'Team': 'BSA Celtic 18B United',
            'GP': 8,
            'W': 1,
            'L': 4,
            'D': 3,
            'GF': 0,
            'GA': 0,
            'GD': 0,
            'Pts': 6,
            'PPG': 0.75
        },
        {
            'Team': 'Warrior White B17/18',
            'GP': 8,
            'W': 0,
            'L': 7,
            'D': 1,
            'GF': 0,
            'GA': 0,
            'GD': 0,
            'Pts': 1,
            'PPG': 0.13
        }
    ]
    
    df = pd.DataFrame(teams_data)
    
    # Calculate StrengthIndex (same formula as OCL)
    # Since MVYSA doesn't provide GF/GA, we'll use PPG-only StrengthIndex
    # StrengthIndex = 0.7 * PPG_norm + 0.3 * 50 (neutral GDPG)
    df['StrengthIndex'] = df['PPG'].apply(lambda ppg: 
        0.7 * (max(0.0, min(3.0, ppg)) / 3.0 * 100.0) + 0.3 * 50.0
    ).round(1)
    
    # Add metadata
    df['SourceURL'] = 'https://www.mvysa.com/cgi-bin/standings.cgi?fnc=choosed&season=202509'
    df['Division'] = 'MVYSA B09-3'
    df['League'] = 'MVYSA Fall 2025'
    
    # Sort by StrengthIndex
    df = df.sort_values('StrengthIndex', ascending=False).reset_index(drop=True)
    df.insert(0, 'Rank', range(1, len(df) + 1))
    
    # Save to CSV
    output_file = 'MVYSA_B09_3_Division_Rankings.csv'
    df.to_csv(output_file, index=False)
    
    print(f"[OK] Created MVYSA B09-3 division standings\n")
    print(f"[OK] Saved to {output_file}\n")
    
    # Display rankings
    print("=" * 60)
    print("DIVISION STRENGTH RANKINGS")
    print("=" * 60)
    print()
    
    display_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'Pts', 'PPG', 'StrengthIndex']
    print(df[display_cols].to_string(index=False))
    
    print()
    print("=" * 60)
    print(f"Total Teams: {len(df)}")
    print(f"Data Source: MVYSA Division B09-3")
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    return df


if __name__ == '__main__':
    df = create_mvysa_b09_3_standings()

