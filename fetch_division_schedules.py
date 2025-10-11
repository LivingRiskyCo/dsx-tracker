"""
Fetch schedules for all teams in OCL BU08 Stripes division
Build comprehensive Common Opponent Matrix
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


def fetch_team_schedule_from_gotsport(event_id, team_name):
    """
    Try to fetch a team's schedule from GotSport
    
    This is tricky because we need the team's specific URL/ID
    GotSport URLs are like: /org_event/events/{event_id}/schedule?team={team_id}
    """
    # For now, we'll extract what we can from the results page
    # A more complete solution would need to scrape each team's page
    print(f"  Attempting to find schedule for: {team_name}")
    
    # Try the group results page and look for this team's matches
    url = f"https://system.gotsport.com/org_event/events/{event_id}/schedule"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse match results
        matches = parse_gotsport_matches(soup, team_name)
        
        print(f"    Found {len(matches)} matches")
        return matches
        
    except Exception as e:
        print(f"    Error: {e}")
        return []


def parse_gotsport_matches(soup, team_name):
    """Parse matches involving a specific team"""
    matches = []
    
    # GotSport shows matches in tables or divs
    # Look for rows containing the team name
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            text = row.get_text()
            
            # If this row mentions our team
            if team_name.lower() in text.lower():
                cells = row.find_all('td')
                
                if len(cells) >= 4:
                    # Try to extract match data
                    # Typical format: Date | Home | Away | Score
                    match = {
                        'team': team_name,
                        'date': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                        'home': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                        'away': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                        'score': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                    }
                    matches.append(match)
    
    return matches


def build_common_opponent_matrix(dsx_matches, division_teams):
    """
    Build Common Opponent Matrix showing how DSX compares to division teams
    
    Args:
        dsx_matches: DataFrame with DSX match results
        division_teams: List of division team names
    
    Returns:
        DataFrame with common opponent analysis
    """
    print("\nBuilding Common Opponent Matrix...")
    
    matrix_rows = []
    
    # For each division team
    for team in division_teams:
        print(f"  Analyzing: {team}")
        
        # Find common opponents
        # (This requires opponent schedules - for now we'll create placeholders)
        
        common_count = 0
        dsx_avg_gd = 0.0
        opp_avg_gd = 0.0
        
        matrix_rows.append({
            'Opponent': team,
            '#CommonOpp': common_count,
            'DSX_Avg_GD_vs_Common': dsx_avg_gd,
            'Opp_Avg_GD_vs_Common': opp_avg_gd,
            'Relative_Gap(DSX - Opp)': dsx_avg_gd - opp_avg_gd,
            'Notes': 'Awaiting opponent schedule data'
        })
    
    return pd.DataFrame(matrix_rows)


def load_dsx_matches():
    """Load DSX matches from existing workbook or data"""
    # For now, return the matches from the conversation
    dsx_matches = [
        {'Date': '2025-08-09', 'Opponent': '2017 Boys Premier OCL', 'GF': 3, 'GA': 15},
        {'Date': '2025-08-16', 'Opponent': 'Blast FC U8', 'GF': 4, 'GA': 5},
        {'Date': '2025-08-30', 'Opponent': 'Elite FC 2018 Boys Liverpool', 'GF': 5, 'GA': 6},
        {'Date': '2025-08-30', 'Opponent': 'Ohio Premier 2017 Boys Academy Dublin White', 'GF': 0, 'GA': 13},
        {'Date': '2025-08-31', 'Opponent': 'Elite FC 2018 Boys Arsenal', 'GF': 4, 'GA': 2},
        {'Date': '2025-09-05', 'Opponent': 'LFC United 2018B Elite 2', 'GF': 11, 'GA': 0},
        {'Date': '2025-09-06', 'Opponent': 'Elite FC 2018 Boys Tottenham', 'GF': 4, 'GA': 4},
        {'Date': '2025-09-07', 'Opponent': 'Northwest FC 2018B Academy Blue', 'GF': 1, 'GA': 4},
        {'Date': '2025-09-27', 'Opponent': 'Barcelona United Elite 18B', 'GF': 7, 'GA': 2},
        {'Date': '2025-09-27', 'Opponent': 'Columbus United U8B', 'GF': 5, 'GA': 5},
        {'Date': '2025-09-28', 'Opponent': 'Grove City Kids Association 2018B', 'GF': 2, 'GA': 2},
        {'Date': '2025-09-28', 'Opponent': 'Columbus United U8B', 'GF': 4, 'GA': 3},
    ]
    
    return pd.DataFrame(dsx_matches)


def main():
    """Fetch schedules for all division teams"""
    
    print("=" * 70)
    print("OCL BU08 STRIPES DIVISION - SCHEDULE & COMMON OPPONENT ANALYZER")
    print("=" * 70)
    print()
    
    # Load division rankings
    print("Loading division rankings...")
    rankings_df = pd.read_csv("OCL_BU08_Stripes_Division_Rankings.csv")
    teams = rankings_df['Team'].tolist()
    print(f"  Found {len(teams)} teams\n")
    
    # Load DSX matches
    print("Loading DSX matches...")
    dsx_matches = load_dsx_matches()
    print(f"  Loaded {len(dsx_matches)} DSX matches\n")
    
    # Calculate DSX's stats
    dsx_gf = dsx_matches['GF'].sum()
    dsx_ga = dsx_matches['GA'].sum()
    dsx_gd = dsx_gf - dsx_ga
    dsx_record = f"{(dsx_matches['GF'] > dsx_matches['GA']).sum()}-" \
                 f"{(dsx_matches['GF'] == dsx_matches['GA']).sum()}-" \
                 f"{(dsx_matches['GF'] < dsx_matches['GA']).sum()}"
    
    print(f"Dublin DSX Orange 2018 Boys:")
    print(f"  Record: {dsx_record}")
    print(f"  Goals: {dsx_gf} - {dsx_ga} (GD: {dsx_gd:+d})")
    print(f"  PPG: {(dsx_matches['GF'] > dsx_matches['GA']).sum() * 3 / len(dsx_matches):.2f}")
    print()
    
    # Note: Fetching full schedules from GotSport requires team IDs
    # For now, we'll create a template and show what data we have
    
    print("=" * 70)
    print("DIVISION COMPARISON")
    print("=" * 70)
    print()
    
    # Add DSX to rankings for comparison
    dsx_row = {
        'Rank': 0,
        'Team': '>>> Dublin DSX Orange 2018 Boys <<<',
        'GP': len(dsx_matches),
        'W': (dsx_matches['GF'] > dsx_matches['GA']).sum(),
        'D': (dsx_matches['GF'] == dsx_matches['GA']).sum(),
        'L': (dsx_matches['GF'] < dsx_matches['GA']).sum(),
        'GF': round(dsx_gf / len(dsx_matches), 2),
        'GA': round(dsx_ga / len(dsx_matches), 2),
        'GD': round(dsx_gd / len(dsx_matches), 2),
        'Pts': (dsx_matches['GF'] > dsx_matches['GA']).sum() * 3 + (dsx_matches['GF'] == dsx_matches['GA']).sum(),
        'PPG': round((dsx_matches['GF'] > dsx_matches['GA']).sum() * 3 / len(dsx_matches), 2),
    }
    
    # Calculate DSX StrengthIndex
    ppg = dsx_row['PPG']
    gdpg = dsx_row['GD']
    ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
    gdpg_norm = (max(-5.0, min(5.0, gdpg)) + 5.0) / 10.0 * 100.0
    dsx_row['StrengthIndex'] = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
    
    # Combine and sort by StrengthIndex
    combined_df = pd.concat([
        pd.DataFrame([dsx_row]),
        rankings_df
    ], ignore_index=True)
    
    combined_df = combined_df.sort_values('StrengthIndex', ascending=False).reset_index(drop=True)
    combined_df['Rank'] = range(1, len(combined_df) + 1)
    
    # Display
    display_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
    print(combined_df[display_cols].to_string(index=False))
    
    print()
    print("=" * 70)
    
    # Save comprehensive report
    output_file = "OCL_BU08_Stripes_Division_with_DSX.csv"
    combined_df.to_csv(output_file, index=False)
    print(f"\n[OK] Saved comprehensive report to {output_file}")
    
    # Build Common Opponent Matrix
    common_matrix = build_common_opponent_matrix(dsx_matches, teams)
    
    matrix_file = "Common_Opponent_Matrix_Template.csv"
    common_matrix.to_csv(matrix_file, index=False)
    print(f"[OK] Saved common opponent template to {matrix_file}")
    
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("To complete the Common Opponent Matrix:")
    print("  1. Use BSA_Celtic_Schedules.csv (already generated)")
    print("  2. Find opponent schedules for other division teams")
    print("  3. Import all schedules to Excel 'OppSchedules (Paste)' sheet")
    print("  4. Matrix will auto-calculate common opponents vs DSX")
    print()
    print("Division teams to track:")
    for i, team in enumerate(teams, 1):
        print(f"  {i}. {team}")
    print()
    
    return combined_df


if __name__ == "__main__":
    df = main()

