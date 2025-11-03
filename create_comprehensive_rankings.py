#!/usr/bin/env python3
import pandas as pd
import os
import re

print("Creating comprehensive rankings CSV files...")
print("(Now enhanced with extracted matches data)")
print()

# Team name aliases for matching (from dsx_dashboard.py)
TEAM_NAME_ALIASES = {
    "Club Ohio West 18B Academy": ["Club Ohio Club Ohio West 18B Academy", "Club Ohio West 18B Academy", "Club Ohio West 18B"],
    "Club Ohio West 18B Academy II": ["Club Ohio Club Ohio West 18B Academy II", "Club Ohio West 18B Academy II"],
    "Lakota FC 2018 Black": ["Lakota FC 2018 Black", "Lakota 2018 Black"],
    "Lakota FC 2018 Red": ["Lakota FC 2018 Red", "Lakota 2018 Red"],
}

# Helper function to normalize team names for matching
def normalize_team_name(team_name):
    """Normalize team name for matching"""
    if pd.isna(team_name):
        return ""
    name = str(team_name).strip()
    
    # Remove duplicate "Club Ohio" prefix
    name = re.sub(r'^Club\s+Ohio\s+Club\s+Ohio\s+', 'Club Ohio ', name, flags=re.IGNORECASE)
    
    # Remove common suffixes for matching
    normalized = name.lower()
    normalized = re.sub(r'\s+2018\s*$', '', normalized)
    normalized = re.sub(r'\s+b18\s*$', '', normalized)
    normalized = re.sub(r'\s+u8\s*$', '', normalized)
    normalized = re.sub(r'\s+boys\s*$', '', normalized)
    
    return normalized

# Helper function to resolve aliases
def resolve_alias(team_name):
    """Resolve team name aliases"""
    if pd.isna(team_name):
        return ""
    
    name = str(team_name).strip()
    
    # Check aliases
    for canonical, aliases in TEAM_NAME_ALIASES.items():
        if name == canonical or name in aliases:
            return canonical
    
    # Check if name matches any alias (fuzzy)
    name_lower = name.lower()
    for canonical, aliases in TEAM_NAME_ALIASES.items():
        for alias in aliases:
            if name_lower == alias.lower() or name_lower in alias.lower() or alias.lower() in name_lower:
                return canonical
    
    return name

# Helper function to check if two team names match
def team_names_match(name1, name2):
    """Check if two team names refer to the same team"""
    if pd.isna(name1) or pd.isna(name2):
        return False
    
    name1 = str(name1).strip()
    name2 = str(name2).strip()
    
    # Exact match
    if name1 == name2:
        return True
    
    # Check aliases
    resolved1 = resolve_alias(name1)
    resolved2 = resolve_alias(name2)
    if resolved1 == resolved2 and resolved1:
        return True
    
    # Normalized match
    norm1 = normalize_team_name(name1)
    norm2 = normalize_team_name(name2)
    
    # Check if one normalized name contains the other (but not too short)
    if len(norm1) > 10 and len(norm2) > 10:
        if norm1 in norm2 or norm2 in norm1:
            # Check for distinguishing suffixes like "II" vs no "II"
            if " ii" in name1.lower() or " 2" in name1.lower():
                if " ii" not in name2.lower() and " 2" not in name2.lower():
                    return False
            if " ii" in name2.lower() or " 2" in name2.lower():
                if " ii" not in name1.lower() and " 2" not in name1.lower():
                    return False
            return True
    
    return False

# Function to calculate team stats from extracted matches (from dsx_dashboard.py)
def calculate_team_stats_from_extracted_matches(extracted_matches_df, team_name):
    """Calculate team statistics from extracted matches"""
    if extracted_matches_df is None or extracted_matches_df.empty:
        return None
    
    target_normalized = normalize_team_name(team_name)
    team_matches = []
    
    for idx, match in extracted_matches_df.iterrows():
        match_team = str(match.get('Team', ''))
        match_opp = str(match.get('Opponent', ''))
        
        # Check if this match involves our target team
        if (team_names_match(team_name, match_team) or 
            team_names_match(team_name, match_opp)):
            
            # Determine if team was home or away
            is_home = team_names_match(team_name, match_team)
            
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
                'Opponent': match_opp if is_home else match_team,
                'GF': gf if not pd.isna(gf) else None,
                'GA': ga if not pd.isna(ga) else None,
                'Result': result,
            })
    
    if not team_matches:
        return None
    
    # Calculate stats
    matches_df = pd.DataFrame(team_matches)
    
    # Filter out matches without valid scores
    valid_matches = matches_df[
        (matches_df['GF'].notna()) & 
        (matches_df['GA'].notna()) &
        (matches_df['Result'].notna())
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
        'GF': round(gf_pg, 2),
        'GA': round(ga_pg, 2),
        'GD': round(gd_pg, 2),
        'Pts': pts,
        'PPG': round(ppg, 2),
        'StrengthIndex': strength_index,
        'Source': 'Extracted Matches'
    }

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

# Load extracted matches for enhancement
print("Loading extracted matches data...")
extracted_matches = None
if os.path.exists("Opponents_of_Opponents_Matches_Expanded.csv"):
    try:
        extracted_matches = pd.read_csv("Opponents_of_Opponents_Matches_Expanded.csv", index_col=False).reset_index(drop=True)
        print(f"   Loaded {len(extracted_matches)} extracted matches")
    except Exception as e:
        print(f"   Warning: Could not load extracted matches: {e}")
else:
    print("   No extracted matches file found")

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
    
    # DEDUPLICATE TEAMS: Consolidate teams with similar names
    print("\nDeduplicating teams with similar names...")
    unique_teams = {}
    consolidated_count = 0
    
    for idx, row in combined.iterrows():
        team_name = str(row['Team']).strip()
        
        # Try to find a matching team we've already seen
        matched_key = None
        for key in unique_teams.keys():
            if team_names_match(team_name, key):
                matched_key = key
                break
        
        if matched_key:
            # Consolidate stats - add games together
            existing = unique_teams[matched_key]
            
            # Combine games (take max GP, sum wins/losses, etc.)
            existing_gp = pd.to_numeric(existing.get('GP', 0), errors='coerce')
            new_gp = pd.to_numeric(row.get('GP', 0), errors='coerce')
            
            if new_gp > existing_gp:
                # If new team has more games, use it as the primary data
                unique_teams[matched_key] = row.to_dict()
                unique_teams[matched_key]['Team'] = matched_key  # Keep the canonical name
                consolidated_count += 1
                print(f"   Consolidated: {team_name} -> {matched_key} ({existing_gp:.0f} + {new_gp:.0f} games)")
        else:
            # New team - add it
            canonical_name = resolve_alias(team_name)
            if canonical_name != team_name:
                row_dict = row.to_dict()
                row_dict['Team'] = canonical_name
                unique_teams[canonical_name] = row_dict
            else:
                unique_teams[team_name] = row.to_dict()
    
    # Convert back to DataFrame
    if unique_teams:
        combined = pd.DataFrame(list(unique_teams.values()))
        print(f"   Consolidated {consolidated_count} duplicate teams into {len(combined)} unique teams")
        print()
    
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
    
    # ENHANCE WITH EXTRACTED MATCHES
    print("\nEnhancing team stats with extracted matches...")
    enhanced_teams = []
    teams_with_more_games = 0
    
    for idx, team_row in combined.iterrows():
        team_name = team_row['Team']
        division_gp = team_row['GP']
        
        # Try to get stats from extracted matches
        if extracted_matches is not None:
            extracted_stats = calculate_team_stats_from_extracted_matches(extracted_matches, team_name)
            
            if extracted_stats and extracted_stats['GP'] > division_gp:
                # Use extracted matches stats if they have more games
                team_row['GP'] = extracted_stats['GP']
                team_row['W'] = extracted_stats['W']
                team_row['L'] = extracted_stats['L']
                team_row['D'] = extracted_stats['D']
                team_row['GF'] = extracted_stats['GF']
                team_row['GA'] = extracted_stats['GA']
                team_row['GD'] = extracted_stats['GD']
                team_row['Pts'] = extracted_stats['Pts']
                team_row['PPG'] = extracted_stats['PPG']
                team_row['StrengthIndex'] = extracted_stats['StrengthIndex']
                teams_with_more_games += 1
                print(f"   Enhanced {team_name}: {division_gp} -> {extracted_stats['GP']} games")
        
        enhanced_teams.append(team_row)
    
    combined = pd.DataFrame(enhanced_teams).reset_index(drop=True)
    print(f"   Enhanced {teams_with_more_games} teams with extracted matches data")
    print()
    
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