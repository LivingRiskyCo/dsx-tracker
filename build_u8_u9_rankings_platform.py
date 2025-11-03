#!/usr/bin/env python3
"""
Build a comprehensive U8/U9 Boys rankings platform
Creates public-facing rankings similar to GotSport but for ages GotSport doesn't cover
"""

import pandas as pd
import os
from datetime import datetime

print("="*70)
print("U8/U9 BOYS RANKINGS PLATFORM - BUILDER")
print("="*70)
print()
print("Building comprehensive rankings for:")
print("  - U8 Boys (2018 Birth Year)")
print("  - U9 Boys (2017 Birth Year)")
print()
print("Note: GotSport rankings start at U10 - we're filling the gap!")
print()

# Load U8 rankings
u8_file = 'Rankings_2018_Teams_3Plus_Games.csv'
u9_file = 'Rankings_2017_Teams_3Plus_Games.csv'

u8_teams = pd.DataFrame()
u9_teams = pd.DataFrame()

if os.path.exists(u8_file):
    u8_teams = pd.read_csv(u8_file)
    print(f"[OK] Loaded {len(u8_teams)} U8 Boys teams (2018)")

if os.path.exists(u9_file):
    u9_teams = pd.read_csv(u9_file)
    print(f"[OK] Loaded {len(u9_teams)} U9 Boys teams (2017)")

print()

# Create Top 50 rankings for each age group
print("Creating Top 50 Rankings...")
print()

if not u8_teams.empty:
    # Top 50 U8 Boys
    u8_top50 = u8_teams.head(50).copy()
    u8_top50['Rank'] = range(1, len(u8_top50) + 1)
    
    # Create public-friendly format
    u8_public = u8_top50[['Rank', 'Team', 'GP', 'W', 'L', 'D', 'PPG', 'StrengthIndex']].copy()
    u8_public.columns = ['Rank', 'Team', 'Games', 'Wins', 'Losses', 'Draws', 'PPG', 'Strength Index']
    
    u8_output = 'Ohio_U8_Boys_Rankings_Top50.csv'
    u8_public.to_csv(u8_output, index=False)
    print(f"[OK] Created {u8_output}")
    print(f"   Top 5 U8 Teams:")
    for idx, row in u8_top50.head(5).iterrows():
        print(f"   {row['Rank']}. {row['Team']} - SI: {row['StrengthIndex']:.1f}, PPG: {row['PPG']:.2f}")

if not u9_teams.empty:
    # Top 50 U9 Boys
    u9_top50 = u9_teams.head(50).copy()
    u9_top50['Rank'] = range(1, len(u9_top50) + 1)
    
    # Create public-friendly format
    u9_public = u9_top50[['Rank', 'Team', 'GP', 'W', 'L', 'D', 'PPG', 'StrengthIndex']].copy()
    u9_public.columns = ['Rank', 'Team', 'Games', 'Wins', 'Losses', 'Draws', 'PPG', 'Strength Index']
    
    u9_output = 'Ohio_U9_Boys_Rankings_Top50.csv'
    u9_public.to_csv(u9_output, index=False)
    print(f"\n[OK] Created {u9_output}")
    print(f"   Top 5 U9 Teams:")
    for idx, row in u9_top50.head(5).iterrows():
        print(f"   {row['Rank']}. {row['Team']} - SI: {row['StrengthIndex']:.1f}, PPG: {row['PPG']:.2f}")

print()
print("="*70)
print("NEXT STEPS TO BUILD FULL PLATFORM:")
print("="*70)
print()
print("1. Create public-facing rankings page (HTML/Streamlit)")
print("2. Add team profile pages with match history")
print("3. Implement search and filter functionality")
print("4. Add comparison tools (team vs team)")
print("5. Set up automated tournament discovery")
print("6. Add real-time updates from GotSport")
print("7. Create regional breakdowns (Northeast, Northwest, etc.)")
print("8. Add historical tracking (season-to-season)")
print()
print("Current Advantage: GotSport doesn't provide U8/U9 rankings!")
print("We're building what they don't offer.")
print("="*70)

