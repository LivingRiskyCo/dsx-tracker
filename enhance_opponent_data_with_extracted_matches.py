#!/usr/bin/env python3
"""
Enhance opponent data using extracted opponent-of-opponent matches
Calculates strength indexes and stats from match history when division data is missing
"""

import pandas as pd
import re
from collections import defaultdict

def load_extracted_matches():
    """Load the extracted opponent-of-opponent matches"""
    try:
        df = pd.read_csv('Opponents_of_Opponents_Matches_Expanded.csv')
        return df
    except:
        return pd.DataFrame()

def normalize_team_name(name):
    """Normalize team name for matching"""
    if pd.isna(name):
        return ""
    normalized = ' '.join(str(name).strip().split()).lower()
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    return normalized.strip()

def calculate_team_stats_from_matches(matches_df, team_name):
    """Calculate team statistics from match history"""
    if matches_df.empty:
        return None
    
    # Normalize target team name
    target_normalized = normalize_team_name(team_name)
    
    # Find all matches involving this team
    team_matches = []
    
    for _, match in matches_df.iterrows():
        match_team = str(match.get('Team', '')).strip()
        match_opp = str(match.get('Opponent', '')).strip()
        
        if not match_team or not match_opp:
            continue
        
        match_team_norm = normalize_team_name(match_team)
        match_opp_norm = normalize_team_name(match_opp)
        
        # Check if this match involves our target team
        if (target_normalized in match_team_norm or 
            match_team_norm in target_normalized or
            target_normalized in match_opp_norm or
            match_opp_norm in target_normalized):
            
            # Determine if team was home or away
            is_home = target_normalized in match_team_norm or match_team_norm in target_normalized
            
            # Get score
            gf = match.get('GF')
            ga = match.get('GA')
            
            # If GF/GA not directly available, try to parse from Score
            if pd.isna(gf) or pd.isna(ga):
                score = str(match.get('Score', ''))
                score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', score)
                if score_match:
                    if is_home:
                        gf = int(score_match.group(1))
                        ga = int(score_match.group(2))
                    else:
                        gf = int(score_match.group(2))
                        ga = int(score_match.group(1))
            
            # Get result
            result = match.get('Result')
            if pd.isna(result):
                if gf is not None and ga is not None:
                    if gf > ga:
                        result = 'W'
                    elif ga > gf:
                        result = 'L'
                    else:
                        result = 'D'
            
            team_matches.append({
                'Date': match.get('Date', ''),
                'Opponent': match_opp if is_home else match_team,
                'GF': gf if not pd.isna(gf) else None,
                'GA': ga if not pd.isna(ga) else None,
                'Result': result,
                'IsHome': is_home
            })
    
    if not team_matches:
        return None
    
    # Calculate stats
    matches_df_calc = pd.DataFrame(team_matches)
    
    # Filter out matches without valid scores
    valid_matches = matches_df_calc[
        (matches_df_calc['GF'].notna()) & 
        (matches_df_calc['GA'].notna()) &
        (matches_df_calc['Result'].notna())
    ].copy()
    
    if valid_matches.empty:
        return None
    
    gp = len(valid_matches)
    w = len(valid_matches[valid_matches['Result'] == 'W'])
    l = len(valid_matches[valid_matches['Result'] == 'L'])
    d = len(valid_matches[valid_matches['Result'] == 'D'])
    
    gf_total = valid_matches['GF'].sum()
    ga_total = valid_matches['GA'].sum()
    gd_total = gf_total - ga_total
    
    pts = (w * 3) + d
    ppg = pts / gp if gp > 0 else 0
    gf_pg = gf_total / gp if gp > 0 else 0
    ga_pg = ga_total / gp if gp > 0 else 0
    gd_pg = gd_total / gp if gp > 0 else 0
    
    # Calculate Strength Index
    ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
    gdpg_norm = (max(-5.0, min(5.0, gd_pg)) + 5.0) / 10.0 * 100.0
    strength_index = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
    
    return {
        'GP': gp,
        'W': w,
        'L': l,
        'D': d,
        'GF': round(gf_pg, 2),  # Per game
        'GA': round(ga_pg, 2),  # Per game
        'GD': round(gd_pg, 2),   # Per game
        'Pts': pts,
        'PPG': round(ppg, 2),
        'StrengthIndex': strength_index,
        'Source': 'Extracted Matches',
        'MatchCount': gp
    }

def get_opponent_coverage_info(opponent_name):
    """Get coverage information for an opponent"""
    matches_df = load_extracted_matches()
    
    if matches_df.empty:
        return {
            'has_extracted_data': False,
            'match_count': 0
        }
    
    # Normalize opponent name
    opp_normalized = normalize_team_name(opponent_name)
    
    # Count matches for this opponent
    match_count = 0
    team_matches = []
    
    for _, match in matches_df.iterrows():
        match_team = str(match.get('Team', '')).strip()
        match_opp = str(match.get('Opponent', '')).strip()
        
        if not match_team or not match_opp:
            continue
        
        match_team_norm = normalize_team_name(match_team)
        match_opp_norm = normalize_team_name(match_opp)
        
        if (opp_normalized in match_team_norm or 
            match_team_norm in opp_normalized or
            opp_normalized in match_opp_norm or
            match_opp_norm in opp_normalized):
            match_count += 1
            team_matches.append(match)
    
    return {
        'has_extracted_data': match_count > 0,
        'match_count': match_count,
        'matches': team_matches[:10] if team_matches else []  # Sample of matches
    }

if __name__ == "__main__":
    # Test the functions
    test_team = "Blast FC Soccer Academy Blast FC 2018B"
    
    matches_df = load_extracted_matches()
    print(f"Loaded {len(matches_df)} extracted matches")
    
    stats = calculate_team_stats_from_matches(matches_df, test_team)
    if stats:
        print(f"\nStats for {test_team}:")
        print(f"  GP: {stats['GP']}")
        print(f"  Record: {stats['W']}-{stats['L']}-{stats['D']}")
        print(f"  PPG: {stats['PPG']}")
        print(f"  Strength Index: {stats['StrengthIndex']}")
    else:
        print(f"No stats found for {test_team}")
    
    coverage = get_opponent_coverage_info(test_team)
    print(f"\nCoverage info: {coverage}")

