#!/usr/bin/env python3
"""
Update MVYSA B09-3 Division with Real Game Scores
Based on actual MVYSA schedule data from website
"""

import pandas as pd
from datetime import datetime

def update_mvysa_with_real_scores():
    """Update MVYSA division with actual game scores from website"""
    
    print("="*60)
    print("UPDATING MVYSA B09-3 WITH REAL GAME SCORES")
    print("="*60)
    
    # Real game results from MVYSA website
    real_games = [
        # BSA Celtic 18B City games
        {"team": "BSA Celtic 18B City", "opponent": "Warrior White B17/18", "gf": 8, "ga": 3, "result": "W"},
        {"team": "BSA Celtic 18B City", "opponent": "BSA Celtic 18B United", "gf": 4, "ga": 2, "result": "W"},
        {"team": "BSA Celtic 18B City", "opponent": "Southstars SC B17", "gf": 1, "ga": 8, "result": "L"},
        {"team": "BSA Celtic 18B City", "opponent": "Springfield Thunder SC Navy B2017", "gf": 1, "ga": 9, "result": "L"},
        {"team": "BSA Celtic 18B City", "opponent": "Troy Rattlers B17/18", "gf": 3, "ga": 6, "result": "L"},
        {"team": "BSA Celtic 18B City", "opponent": "Warrior White B17/18", "gf": 4, "ga": 3, "result": "W"},
        {"team": "BSA Celtic 18B City", "opponent": "BSA Celtic 18B United", "gf": 1, "ga": 1, "result": "D"},
        {"team": "BSA Celtic 18B City", "opponent": "Springfield Thunder SC Navy B2017", "gf": 1, "ga": 7, "result": "L"},
        
        # BSA Celtic 18B United games
        {"team": "BSA Celtic 18B United", "opponent": "Springfield Thunder SC Navy B2017", "gf": 1, "ga": 13, "result": "L"},
        {"team": "BSA Celtic 18B United", "opponent": "Troy Rattlers B17/18", "gf": 1, "ga": 1, "result": "D"},
        {"team": "BSA Celtic 18B United", "opponent": "BSA Celtic 18B City", "gf": 2, "ga": 4, "result": "L"},
        {"team": "BSA Celtic 18B United", "opponent": "Warrior White B17/18", "gf": 7, "ga": 2, "result": "W"},
        {"team": "BSA Celtic 18B United", "opponent": "Southstars SC B17", "gf": 2, "ga": 4, "result": "L"},
        {"team": "BSA Celtic 18B United", "opponent": "Warrior White B17/18", "gf": 1, "ga": 1, "result": "D"},
        {"team": "BSA Celtic 18B United", "opponent": "Southstars SC B17", "gf": 0, "ga": 6, "result": "L"},
        {"team": "BSA Celtic 18B United", "opponent": "BSA Celtic 18B City", "gf": 1, "ga": 1, "result": "D"},
    ]
    
    # Calculate team stats
    team_stats = {}
    
    for game in real_games:
        team = game["team"]
        if team not in team_stats:
            team_stats[team] = {"w": 0, "l": 0, "d": 0, "gf": 0, "ga": 0, "gp": 0}
        
        team_stats[team]["gp"] += 1
        team_stats[team]["gf"] += game["gf"]
        team_stats[team]["ga"] += game["ga"]
        
        if game["result"] == "W":
            team_stats[team]["w"] += 1
        elif game["result"] == "L":
            team_stats[team]["l"] += 1
        else:
            team_stats[team]["d"] += 1
    
    # Create updated division standings
    teams = [
        {"team": "Southstars SC B17", "w": 8, "l": 0, "d": 0, "gf": 0, "ga": 0, "gp": 8},  # No data available
        {"team": "Springfield Thunder SC Navy B2017", "w": 5, "l": 2, "d": 0, "gf": 0, "ga": 0, "gp": 7},  # No data available
        {"team": "BSA Celtic 18B City", "w": 3, "l": 4, "d": 1, "gf": 23, "ga": 38, "gp": 8},
        {"team": "Troy Rattlers B17/18", "w": 3, "l": 4, "d": 1, "gf": 0, "ga": 0, "gp": 8},  # No data available
        {"team": "BSA Celtic 18B United", "w": 1, "l": 5, "d": 2, "gf": 15, "ga": 28, "gp": 8},
        {"team": "Warrior White B17/18", "w": 0, "l": 7, "d": 1, "gf": 0, "ga": 0, "gp": 8},  # No data available
    ]
    
    # Update with real stats where available
    for team in teams:
        if team["team"] in team_stats:
            stats = team_stats[team["team"]]
            team["w"] = stats["w"]
            team["l"] = stats["l"]
            team["d"] = stats["d"]
            team["gf"] = stats["gf"]
            team["ga"] = stats["ga"]
            team["gp"] = stats["gp"]
    
    # Calculate additional stats
    for team in teams:
        team["gd"] = team["gf"] - team["ga"]
        team["pts"] = (team["w"] * 3) + team["d"]
        team["ppg"] = team["pts"] / team["gp"] if team["gp"] > 0 else 0
        team["gf_pg"] = team["gf"] / team["gp"] if team["gp"] > 0 else 0
        team["ga_pg"] = team["ga"] / team["gp"] if team["gp"] > 0 else 0
        team["gd_pg"] = team["gd"] / team["gp"] if team["gp"] > 0 else 0
        
        # Calculate Strength Index
        ppg_norm = max(0.0, min(3.0, team["ppg"])) / 3.0 * 100.0
        gdpg_norm = (max(-5.0, min(5.0, team["gd_pg"])) + 5.0) / 10.0 * 100.0
        team["strength_index"] = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
    
    # Sort by PPG then Strength Index
    teams.sort(key=lambda x: (x["ppg"], x["strength_index"]), reverse=True)
    
    # Add rank
    for i, team in enumerate(teams, 1):
        team["rank"] = i
    
    # Create DataFrame
    df = pd.DataFrame(teams)
    
    # Reorder columns
    columns = ["rank", "team", "gp", "w", "l", "d", "gf", "ga", "gd", "pts", "ppg", "strength_index", "gf_pg", "ga_pg", "gd_pg"]
    df = df[columns]
    
    # Save to CSV
    output_file = "MVYSA_B09_3_Division_Rankings.csv"
    df.to_csv(output_file, index=False)
    
    print(f"[OK] Saved updated {output_file}")
    print()
    print("="*60)
    print("UPDATED DIVISION STANDINGS")
    print("="*60)
    print()
    
    # Display results
    display_cols = ["rank", "team", "gp", "w", "l", "d", "gf", "ga", "gd", "ppg", "strength_index"]
    print(df[display_cols].to_string(index=False))
    
    print()
    print("="*60)
    print("KEY INSIGHTS")
    print("="*60)
    print()
    
    # Find BSA Celtic teams
    celtic_city = df[df["team"] == "BSA Celtic 18B City"].iloc[0]
    celtic_united = df[df["team"] == "BSA Celtic 18B United"].iloc[0]
    
    print(f"BSA Celtic 18B City:")
    print(f"  Rank: #{int(celtic_city['rank'])} of {len(df)}")
    print(f"  Record: {int(celtic_city['w'])}-{int(celtic_city['l'])}-{int(celtic_city['d'])}")
    print(f"  Goals: {int(celtic_city['gf'])}-{int(celtic_city['ga'])} (GD: {int(celtic_city['gd'])})")
    print(f"  PPG: {celtic_city['ppg']:.2f}")
    print(f"  Strength Index: {celtic_city['strength_index']:.1f}")
    print()
    
    print(f"BSA Celtic 18B United:")
    print(f"  Rank: #{int(celtic_united['rank'])} of {len(df)}")
    print(f"  Record: {int(celtic_united['w'])}-{int(celtic_united['l'])}-{int(celtic_united['d'])}")
    print(f"  Goals: {int(celtic_united['gf'])}-{int(celtic_united['ga'])} (GD: {int(celtic_united['gd'])})")
    print(f"  PPG: {celtic_united['ppg']:.2f}")
    print(f"  Strength Index: {celtic_united['strength_index']:.1f}")
    print()
    
    print("="*60)
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)

if __name__ == "__main__":
    update_mvysa_with_real_scores()
