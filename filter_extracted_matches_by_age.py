#!/usr/bin/env python3
"""
Filter Opponents_of_Opponents_Matches_Expanded.csv by age group
Creates separate files for different age groups and confidence levels
"""

import pandas as pd
import re
from collections import Counter

def detect_team_age(team_name, source_url=None, division=None):
    """
    Detect team age from multiple sources
    Returns: '2018', '2017', '2016', '2015', 'Unknown'
    """
    if pd.isna(team_name):
        return 'Unknown'
    
    team_str = str(team_name).upper()
    
    # Check for explicit year in team name (2015-2020)
    year_match = re.search(r'(20(1[5-9]|20))', team_str)
    if year_match:
        year = year_match.group(1)
        return year
    
    # Check for U8/U9/U10/U11 patterns
    if re.search(r'\b(U8|BU8|U-8|B-8)\b', team_str):
        return '2018'
    if re.search(r'\b(U9|BU9|U-9|B-9)\b', team_str):
        return '2017'
    if re.search(r'\b(U10|BU10|U-10|B-10)\b', team_str):
        return '2016'
    if re.search(r'\b(U11|BU11|U-11|B-11)\b', team_str):
        return '2015'
    
    # Check source URL for age indicators
    if source_url and not pd.isna(source_url):
        url_str = str(source_url).upper()
        if 'U8' in url_str or 'B08' in url_str or 'BU08' in url_str:
            return '2018'
        if 'U9' in url_str or 'B09' in url_str or 'BU09' in url_str:
            return '2017'
        if 'U10' in url_str or 'B10' in url_str or 'BU10' in url_str:
            return '2016'
        if 'U11' in url_str or 'B11' in url_str or 'BU11' in url_str:
            return '2015'
    
    # Check division name for age indicators
    if division and not pd.isna(division):
        div_str = str(division).upper()
        if 'U8' in div_str or 'B08' in div_str or 'BU08' in div_str:
            return '2018'
        if 'U9' in div_str or 'B09' in div_str or 'BU09' in div_str:
            return '2017'
        if 'U10' in div_str or 'B10' in div_str or 'BU10' in div_str:
            return '2016'
        if 'U11' in div_str or 'B11' in div_str or 'BU11' in div_str:
            return '2015'
    
    return 'Unknown'

def calculate_confidence(team_age, opp_age, source_url=None):
    """
    Calculate confidence score for match
    High (90%+): Both teams clearly identified as same age
    Medium (70-90%): One team identified, other unknown (but from same tournament)
    Low (<70%): Both unknown or cross-age
    """
    if team_age == opp_age and team_age != 'Unknown':
        return 'High'
    elif team_age != 'Unknown' and opp_age == 'Unknown':
        # Check if from same tournament - medium confidence
        if source_url:
            return 'Medium'
        return 'Medium'
    elif team_age == 'Unknown' and opp_age != 'Unknown':
        if source_url:
            return 'Medium'
        return 'Medium'
    else:
        return 'Low'

# Load the extracted matches
print("Loading extracted matches...")
df = pd.read_csv('Opponents_of_Opponents_Matches_Expanded.csv')

print(f"Total matches loaded: {len(df)}")

# Detect ages for both Team and Opponent
print("\nDetecting ages for teams...")
df['Team_Age'] = df.apply(lambda row: detect_team_age(
    row.get('Team'), 
    row.get('SourceURL'), 
    row.get('Division', None)
), axis=1)

df['Opponent_Age'] = df.apply(lambda row: detect_team_age(
    row.get('Opponent'), 
    row.get('SourceURL'), 
    row.get('Division', None)
), axis=1)

# Calculate confidence
df['Confidence'] = df.apply(lambda row: calculate_confidence(
    row['Team_Age'],
    row['Opponent_Age'],
    row.get('SourceURL')
), axis=1)

# Filter by age groups
print("\nFiltering matches by age group...")

# 2018 Only (high confidence)
matches_2018_only = df[
    (df['Team_Age'] == '2018') & 
    (df['Opponent_Age'] == '2018')
].copy()

# 2018 Plus Unknown (medium-high confidence)
matches_2018_plus = df[
    ((df['Team_Age'] == '2018') | (df['Opponent_Age'] == '2018')) &
    ((df['Team_Age'] == '2018') | (df['Team_Age'] == 'Unknown')) &
    ((df['Opponent_Age'] == '2018') | (df['Opponent_Age'] == 'Unknown'))
].copy()

# 2017 (for benchmarking)
matches_2017_only = df[
    (df['Team_Age'] == '2017') & 
    (df['Opponent_Age'] == '2017')
].copy()

# Other ages (2015, 2016)
matches_other = df[
    ((df['Team_Age'].isin(['2015', '2016'])) | 
     (df['Opponent_Age'].isin(['2015', '2016']))) &
    ~((df['Team_Age'] == '2018') | (df['Opponent_Age'] == '2018')) &
    ~((df['Team_Age'] == '2017') | (df['Opponent_Age'] == '2017'))
].copy()

# Save filtered files
print("\nSaving filtered files...")

matches_2018_only.to_csv('Extracted_Matches_2018_Only.csv', index=False)
print(f"[OK] Extracted_Matches_2018_Only.csv: {len(matches_2018_only)} matches")

matches_2018_plus.to_csv('Extracted_Matches_2018_Plus_Unknown.csv', index=False)
print(f"[OK] Extracted_Matches_2018_Plus_Unknown.csv: {len(matches_2018_plus)} matches")

matches_2017_only.to_csv('Extracted_Matches_2017_Benchmarking.csv', index=False)
print(f"[OK] Extracted_Matches_2017_Benchmarking.csv: {len(matches_2017_only)} matches")

matches_other.to_csv('Extracted_Matches_Other_Ages.csv', index=False)
print(f"[OK] Extracted_Matches_Other_Ages.csv: {len(matches_other)} matches")

# Summary statistics
print("\n" + "="*60)
print("FILTERING SUMMARY")
print("="*60)
print(f"\n2018 Only (High Confidence): {len(matches_2018_only):,} matches")
print(f"2018 Plus Unknown (Medium Confidence): {len(matches_2018_plus):,} matches")
print(f"2017 (Benchmarking): {len(matches_2017_only):,} matches")
print(f"Other Ages (2015-2016): {len(matches_other):,} matches")
print(f"Remaining Unknown: {len(df) - len(matches_2018_only) - len(matches_2018_plus) - len(matches_2017_only) - len(matches_other):,} matches")

# Age distribution
print("\n" + "="*60)
print("AGE DISTRIBUTION")
print("="*60)
team_ages = df['Team_Age'].value_counts()
opp_ages = df['Opponent_Age'].value_counts()

print("\nTeam Ages:")
for age, count in team_ages.items():
    print(f"  {age}: {count:,} teams")

print("\nOpponent Ages:")
for age, count in opp_ages.items():
    print(f"  {age}: {count:,} teams")

# Confidence distribution
print("\n" + "="*60)
print("CONFIDENCE DISTRIBUTION")
print("="*60)
conf_counts = df['Confidence'].value_counts()
for conf, count in conf_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {conf}: {count:,} matches ({pct:.1f}%)")

print("\n" + "="*60)
print("[OK] Filtering complete!")
print("="*60)

