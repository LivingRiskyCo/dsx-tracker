#!/usr/bin/env python3
"""
Fix Team Name Matching for Division Rankings
Updates team names to match between upcoming opponents and division data
"""

import pandas as pd
from datetime import datetime

def fix_team_name_matching():
    """Fix team name matching between upcoming opponents and division data"""
    
    print("="*60)
    print("FIXING TEAM NAME MATCHING")
    print("="*60)
    
    # Load upcoming opponents
    try:
        upcoming = pd.read_csv("DSX_Upcoming_Opponents.csv")
        print(f"[OK] Loaded {len(upcoming)} upcoming opponents")
    except:
        print("[ERROR] Could not load DSX_Upcoming_Opponents.csv")
        return
    
    # Load OCL Stripes data
    try:
        ocl_stripes = pd.read_csv("OCL_BU08_Stripes_Division_Rankings.csv")
        print(f"[OK] Loaded {len(ocl_stripes)} OCL Stripes teams")
    except:
        print("[ERROR] Could not load OCL_BU08_Stripes_Division_Rankings.csv")
        return
    
    # Team name mapping
    name_mappings = {
        'Sporting Columbus Boys 2018 I': 'Sporting Columbus Sporting Columbus Boys 2018 Bexley',
        'Worthington United 2018 Boys White': 'Worthington United Worthington United 94 2018 Boys White',
        'Club Ohio West 18B Academy II': 'Club Ohio Club Ohio North 18B Academy'  # This might be different
    }
    
    print("\n" + "="*60)
    print("TEAM NAME MAPPING ANALYSIS")
    print("="*60)
    
    for upcoming_name in upcoming['Opponent'].unique():
        if pd.isna(upcoming_name):
            continue
            
        print(f"\nUpcoming: '{upcoming_name}'")
        
        # Check for exact match
        exact_match = ocl_stripes[ocl_stripes['Team'] == upcoming_name]
        if not exact_match.empty:
            print(f"  [EXACT] Exact match found: {exact_match.iloc[0]['Team']}")
            print(f"     Record: {exact_match.iloc[0]['W']}-{exact_match.iloc[0]['L']}-{exact_match.iloc[0]['D']}")
            print(f"     Strength Index: {exact_match.iloc[0]['StrengthIndex']}")
            continue
        
        # Check for partial match
        upcoming_lower = str(upcoming_name).lower()
        partial_matches = []
        
        for idx, row in ocl_stripes.iterrows():
            team_lower = str(row['Team']).lower()
            
            # Extract key parts
            upcoming_parts = [p for p in upcoming_lower.split() if p not in ['boys', 'girls', 'academy', 'fc', 'sc', 'soccer', 'club', '2018', '2017', 'b', 'u8', 'u08', 'bu08', '18b', 'i', 'ii', 'iii']]
            team_parts = [p for p in team_lower.split() if p not in ['boys', 'girls', 'academy', 'fc', 'sc', 'soccer', 'club', '2018', '2017', 'b', 'u8', 'u08', 'bu08', '18b', 'i', 'ii', 'iii']]
            
            # Count matching parts
            match_count = sum(1 for part in upcoming_parts if part in team_lower)
            match_count += sum(1 for part in team_parts if part in upcoming_lower)
            
            if match_count >= 2:  # At least 2 matching parts
                partial_matches.append((row['Team'], match_count, row['W'], row['L'], row['D'], row['StrengthIndex']))
        
        if partial_matches:
            # Sort by match count
            partial_matches.sort(key=lambda x: x[1], reverse=True)
            best_match = partial_matches[0]
            
            print(f"  [MATCH] Best partial match: '{best_match[0]}' (score: {best_match[1]})")
            print(f"     Record: {best_match[2]}-{best_match[3]}-{best_match[4]}")
            print(f"     Strength Index: {best_match[5]}")
            
            # Suggest mapping
            if best_match[1] >= 3:  # High confidence match
                print(f"  [SUGGEST] Suggested mapping: '{upcoming_name}' -> '{best_match[0]}'")
        else:
            print(f"  [NONE] No matches found")
    
    print("\n" + "="*60)
    print("RECOMMENDED ACTIONS")
    print("="*60)
    
    print("\n1. Update DSX_Upcoming_Opponents.csv with correct team names:")
    print("   - Sporting Columbus Boys 2018 I -> Sporting Columbus Sporting Columbus Boys 2018 Bexley")
    print("   - Worthington United 2018 Boys White -> Worthington United Worthington United 94 2018 Boys White")
    print("   - Club Ohio West 18B Academy II -> Check if this is Club Ohio Club Ohio North 18B Academy")
    
    print("\n2. Alternative: Update the matching logic in dsx_dashboard.py to handle these name variations")
    
    print("\n3. Check if Club Ohio West 18B Academy II is in a different division (U09B Select III)")
    
    print("\n" + "="*60)
    print("DIVISION BREAKDOWN")
    print("="*60)
    
    print("\nOCL Stripes Division (BU08 5v5):")
    for idx, row in ocl_stripes.iterrows():
        print(f"  {row['Rank']}. {row['Team']} - SI: {row['StrengthIndex']:.1f}")
    
    print("\n" + "="*60)
    print(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)

if __name__ == "__main__":
    fix_team_name_matching()
