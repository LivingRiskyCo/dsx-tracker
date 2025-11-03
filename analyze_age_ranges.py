#!/usr/bin/env python3
"""Analyze age ranges in Opponents_of_Opponents_Matches_Expanded.csv"""

import pandas as pd
import re
from collections import Counter

# Load the extracted matches
df = pd.read_csv('Opponents_of_Opponents_Matches_Expanded.csv')

print(f"Total matches: {len(df)}")
print(f"Total unique teams: {len(df['Team'].unique())}")
print(f"Total unique opponents: {len(df['Opponent'].unique())}")

# Get all unique team names
all_teams = set(df['Team'].dropna().unique()) | set(df['Opponent'].dropna().unique())
print(f"\nUnique team names (combined): {len(all_teams)}")

# Extract age indicators from team names
age_patterns = {
    '2018': r'2018|U8|u8|BU8|bu8',
    '2017': r'2017|U9|u9|BU9|bu9',
    '2019': r'2019|U7|u7|BU7|bu7',
    '2016': r'2016|U10|u10|BU10|bu10',
    '2020': r'2020|U6|u6|BU6|bu6',
    '2015': r'2015|U11|u11|BU11|bu11',
}

age_counts = Counter()
age_teams = {}

for team in all_teams:
    team_str = str(team).upper()
    found_age = None
    
    # Check each age pattern
    for age_key, pattern in age_patterns.items():
        if re.search(pattern, team_str):
            age_counts[age_key] += 1
            found_age = age_key
            if age_key not in age_teams:
                age_teams[age_key] = []
            age_teams[age_key].append(team)
            break
    
    if not found_age:
        age_counts['Unknown'] += 1

print("\n" + "="*60)
print("AGE RANGE BREAKDOWN")
print("="*60)

for age in sorted(age_counts.keys(), key=lambda x: (x != 'Unknown', x)):
    count = age_counts[age]
    percentage = (count / len(all_teams)) * 100
    print(f"\n{age}: {count:,} teams ({percentage:.1f}%)")
    if age in age_teams and len(age_teams[age]) <= 10:
        print(f"  Examples: {', '.join(age_teams[age][:5])}")

print("\n" + "="*60)
print(f"Total teams with age indicator: {sum(age_counts[k] for k in age_counts if k != 'Unknown')}")
print(f"Teams without age indicator: {age_counts.get('Unknown', 0)}")
print("="*60)

# Also check matches by age (looking at both Team and Opponent columns)
print("\n" + "="*60)
print("MATCH BREAKDOWN BY AGE")
print("="*60)

age_match_counts = Counter()

for _, row in df.iterrows():
    team = str(row.get('Team', '')).upper()
    opponent = str(row.get('Opponent', '')).upper()
    
    team_age = None
    opp_age = None
    
    for age_key, pattern in age_patterns.items():
        if re.search(pattern, team):
            team_age = age_key
        if re.search(pattern, opponent):
            opp_age = age_key
        if team_age and opp_age:
            break
    
    # Categorize match
    if team_age and opp_age:
        if team_age == opp_age:
            age_match_counts[f'{team_age} vs {opp_age}'] += 1
        else:
            age_match_counts[f'{team_age} vs {opp_age}'] += 1
    elif team_age:
        age_match_counts[f'{team_age} vs Unknown'] += 1
    elif opp_age:
        age_match_counts[f'Unknown vs {opp_age}'] += 1
    else:
        age_match_counts['Unknown vs Unknown'] += 1

for match_type in sorted(age_match_counts.keys()):
    count = age_match_counts[match_type]
    percentage = (count / len(df)) * 100
    print(f"{match_type}: {count:,} matches ({percentage:.1f}%)")

