"""
Comprehensive Tournament Opponents' Opponents Verification
This script verifies that we're tracking opponents' opponents for ALL tournaments
and ensures all analytics are using the latest data
"""

import pandas as pd
import os
from datetime import datetime

def get_tournaments_from_matches():
    """Get all unique tournaments from DSX match history"""
    try:
        matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
        tournaments = matches['Tournament'].dropna().unique().tolist()
        print(f"[OK] Found {len(tournaments)} tournaments in DSX match history:")
        for tour in tournaments:
            print(f"  - {tour}")
        return tournaments
    except Exception as e:
        print(f"[ERROR] Error loading match history: {e}")
        return []

def get_tournament_opponents(tournament_name):
    """Get all opponents from a specific tournament"""
    try:
        matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
        tour_matches = matches[matches['Tournament'] == tournament_name]
        opponents = tour_matches['Opponent'].dropna().unique().tolist()
        return opponents
    except Exception:
        return []

def check_opponents_opponents_files():
    """Check what opponents' opponents data we have"""
    print("=" * 70)
    print("CHECKING OPPONENTS' OPPONENTS FILES")
    print("=" * 70)
    print()
    
    files_to_check = [
        "Opponents_of_Opponents.csv",
        "Club_Ohio_Opponents_Opponents.csv",
        "Opponent_Schedules.csv",
        "Club_Ohio_Opponents_Schedules.csv",
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, index_col=False)
                print(f"[OK] {filename}: {len(df)} records")
                if len(df) > 0:
                    print(f"     Columns: {', '.join(df.columns.tolist())}")
            except Exception as e:
                print(f"[ERROR] {filename}: {e}")
        else:
            print(f"[MISSING] {filename}")

def check_division_rankings_files():
    """Check all division rankings files for completeness"""
    print()
    print("=" * 70)
    print("CHECKING DIVISION RANKINGS FILES")
    print("=" * 70)
    print()
    
    division_files = [
        ("OCL_BU08_Stripes_Division_Rankings.csv", "OCL BU08 Stripes"),
        ("OCL_BU08_White_Division_Rankings.csv", "OCL BU08 White"),
        ("OCL_BU08_Stars_Division_Rankings.csv", "OCL BU08 Stars 5v5"),
        ("OCL_BU08_Stars_7v7_Division_Rankings.csv", "OCL BU08 Stars 7v7"),
        ("MVYSA_B09_3_Division_Rankings.csv", "MVYSA B09-3"),
        ("Haunted_Classic_B08Orange_Division_Rankings.csv", "Haunted Classic Orange"),
        ("Haunted_Classic_B08Black_Division_Rankings.csv", "Haunted Classic Black"),
        ("CU_Fall_Finale_2025_Division_Rankings.csv", "CU Fall Finale"),
        ("Club_Ohio_Fall_Classic_2025_Division_Rankings.csv", "Club Ohio Fall Classic"),
        ("CPL_Fall_2025_Division_Rankings.csv", "CPL Fall 2025"),
    ]
    
    all_teams = set()
    for filename, description in division_files:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, index_col=False)
                if 'Team' in df.columns:
                    teams = df['Team'].dropna().unique().tolist()
                    all_teams.update(teams)
                    
                    # Check if StrengthIndex is calculated
                    has_strength = 'StrengthIndex' in df.columns
                    strength_status = "[OK]" if has_strength else "[MISSING]"
                    
                    print(f"[OK] {description}: {len(teams)} teams {strength_status} StrengthIndex")
                    
                    # Check for missing StrengthIndex values
                    if has_strength:
                        missing_strength = df['StrengthIndex'].isna().sum()
                        if missing_strength > 0:
                            print(f"     [WARN] {missing_strength} teams missing StrengthIndex")
                else:
                    print(f"[WARN] {description}: Missing 'Team' column")
            except Exception as e:
                print(f"[ERROR] {description}: {e}")
        else:
            print(f"[MISSING] {description}: {filename}")
    
    print()
    print(f"[INFO] Total unique teams tracked: {len(all_teams)}")
    return all_teams

def verify_tournament_coverage():
    """Verify opponents' opponents coverage for all tournaments"""
    print()
    print("=" * 70)
    print("VERIFYING TOURNAMENT OPPONENTS' OPPONENTS COVERAGE")
    print("=" * 70)
    print()
    
    tournaments = get_tournaments_from_matches()
    
    # Load all opponents' opponents data
    all_opponents_opponents = {}
    if os.path.exists("Opponents_of_Opponents.csv"):
        try:
            opp_opp_df = pd.read_csv("Opponents_of_Opponents.csv", index_col=False)
            # Handle both column name formats
            opponent_col = 'DSX_Opponent' if 'DSX_Opponent' in opp_opp_df.columns else 'Opponent'
            their_opponent_col = 'Opponent_of_Opponent' if 'Opponent_of_Opponent' in opp_opp_df.columns else 'TheirOpponent'
            
            for _, row in opp_opp_df.iterrows():
                opponent = row.get(opponent_col, '')
                their_opponent = row.get(their_opponent_col, '')
                # Filter out score strings like "4 - 4" or "-"
                if opponent and their_opponent and not their_opponent.strip().startswith(('-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                    if opponent not in all_opponents_opponents:
                        all_opponents_opponents[opponent] = set()
                    all_opponents_opponents[opponent].add(their_opponent)
        except Exception as e:
            print(f"[ERROR] Error loading Opponents_of_Opponents.csv: {e}")
    
    # Load Club Ohio specific data
    if os.path.exists("Club_Ohio_Opponents_Opponents.csv"):
        try:
            club_ohio_df = pd.read_csv("Club_Ohio_Opponents_Opponents.csv", index_col=False)
            for _, row in club_ohio_df.iterrows():
                opponent = row.get('ClubOhioOpponent', '')
                their_opponent = row.get('TheirOpponent', '')
                if opponent not in all_opponents_opponents:
                    all_opponents_opponents[opponent] = set()
                all_opponents_opponents[opponent].add(their_opponent)
        except Exception as e:
            print(f"[ERROR] Error loading Club_Ohio_Opponents_Opponents.csv: {e}")
    
    print(f"[INFO] Loaded opponents' opponents data for {len(all_opponents_opponents)} opponents")
    print()
    
    # Check each tournament
    for tournament in tournaments:
        print(f"[TOURNAMENT] {tournament}")
        opponents = get_tournament_opponents(tournament)
        print(f"   Opponents: {len(opponents)}")
        
        covered = 0
        missing = []
        for opponent in opponents:
            if opponent in all_opponents_opponents:
                num_opponents = len(all_opponents_opponents[opponent])
                print(f"   [OK] {opponent}: {num_opponents} opponents' opponents tracked")
                covered += 1
            else:
                print(f"   [MISSING] {opponent}: No opponents' opponents data")
                missing.append(opponent)
        
        if missing:
            print(f"   [WARN] Missing data for {len(missing)} opponents")
        else:
            print(f"   [OK] All opponents have opponents' opponents data")
        print()

def generate_report():
    """Generate comprehensive report"""
    print("=" * 70)
    print("COMPREHENSIVE TOURNAMENT OPPONENTS VERIFICATION")
    print("=" * 70)
    print()
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check tournaments
    tournaments = get_tournaments_from_matches()
    
    # Check files
    check_opponents_opponents_files()
    
    # Check division rankings
    all_teams = check_division_rankings_files()
    
    # Verify coverage
    verify_tournament_coverage()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Tournaments Analyzed: {len(tournaments)}")
    print(f"Total Teams Tracked: {len(all_teams)}")
    print()
    print("[OK] Verification complete!")

if __name__ == "__main__":
    generate_report()

