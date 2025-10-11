"""
Scrape Full Schedules for All Division Teams
Find common opponents that DSX and other teams have both played
"""

import pandas as pd
from opponent_scraper import GotSportScraper, OpponentScheduleProcessor
import time
from collections import defaultdict
import requests
from bs4 import BeautifulSoup

# GotSport team schedule URLs for OCL BU08 Stripes Division
TEAM_SCHEDULE_URLS = {
    "Blast FC Soccer Academy Blast FC 2018B": {
        "team_id": "1234567",  # Need to find actual IDs
        "urls": []  # Will try to find from GotSport
    },
    "Polaris Soccer Club Polaris SC 18B Navy": {
        "team_id": "unknown",
        "urls": []
    },
    "Sporting Columbus Sporting Columbus Boys 2018 II": {
        "team_id": "unknown",
        "urls": []
    },
    "Delaware Knights Delaware Knights 2018 BU08": {
        "team_id": "unknown",
        "urls": []
    },
    "Columbus Force SC CE 2018B Net Ninjas": {
        "team_id": "unknown",
        "urls": []
    },
    "Johnstown FC Johnstown FC 2018 Boys": {
        "team_id": "unknown",
        "urls": []
    }
}


def scrape_gotsport_division_schedules():
    """
    Scrape schedules from GotSport division page
    The division standings page should have links to team schedules
    """
    scraper = OpponentScraper()
    
    print("=" * 70)
    print("SCRAPING DIVISION TEAM SCHEDULES")
    print("=" * 70)
    print()
    
    # GotSport division URL
    division_url = "https://system.gotsport.com/org_event/events/45535/results?group=418528"
    
    print(f"Fetching division page: {division_url}")
    print()
    
    # Try to extract team links from the division page
    import requests
    from bs4 import BeautifulSoup
    
    try:
        response = requests.get(division_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find team links (GotSport usually has team names as links)
        team_links = soup.find_all('a', href=True)
        
        schedule_urls = {}
        for link in team_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Look for schedule links
            if 'schedule' in href.lower() or 'team' in href.lower():
                if text:
                    schedule_urls[text] = href
        
        print(f"Found {len(schedule_urls)} potential team schedule links")
        print()
        
        if schedule_urls:
            print("Team schedule URLs found:")
            for team, url in schedule_urls.items():
                print(f"  - {team}")
                print(f"    {url}")
                print()
        
    except Exception as e:
        print(f"[ERROR] Could not scrape division page: {e}")
        print()
    
    return schedule_urls


def scrape_team_schedules_manual():
    """
    Manual approach: Try common GotSport URL patterns
    """
    print("=" * 70)
    print("ATTEMPTING TO FIND TEAM SCHEDULES")
    print("=" * 70)
    print()
    
    # Load division data
    try:
        division = pd.read_csv("OCL_BU08_Stripes_Division_with_DSX.csv")
    except:
        print("[ERROR] Could not load division data")
        return None
    
    all_schedules = []
    scraper = GotSportScraper()
    
    # Get team names (excluding DSX)
    teams = division[~division['Team'].str.contains('DSX', na=False)]['Team'].tolist()
    
    print("Division teams to scrape:")
    for i, team in enumerate(teams, 1):
        print(f"  {i}. {team}")
    print()
    
    # For each team, try to scrape their schedule
    print("Attempting to scrape schedules...")
    print("(This will try common GotSport URL patterns)")
    print()
    
    # Common GotSport event ID (OCL Fall 2025)
    event_id = "45535"
    
    # Try to find team IDs by searching the standings page
    print("Step 1: Finding team IDs from standings page...")
    standings_url = f"https://system.gotsport.com/org_event/events/{event_id}/results?group=418528"
    
    try:
        response = requests.get(standings_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save HTML for inspection
        with open("gotsport_standings.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        
        print("[OK] Saved standings page HTML to gotsport_standings.html")
        print()
        
        # Look for team links
        team_data = []
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Look for team name and potential link
                for cell in cells:
                    link = cell.find('a', href=True)
                    if link:
                        text = link.get_text(strip=True)
                        href = link.get('href')
                        
                        # Check if this looks like a team name
                        if any(team_keyword in text.lower() for team_keyword in 
                               ['fc', 'soccer', 'united', 'academy', 'club', 'sc', 'knights']):
                            
                            # Extract team ID if in URL
                            if 'team' in href.lower() or 'schedule' in href.lower():
                                team_data.append({
                                    'name': text,
                                    'url': href if href.startswith('http') else f"https://system.gotsport.com{href}"
                                })
        
        if team_data:
            print(f"Found {len(team_data)} team links:")
            for td in team_data:
                print(f"  - {td['name']}")
                print(f"    {td['url']}")
            print()
            
            # Try to scrape each team's schedule
            for td in team_data:
                print(f"Scraping: {td['name']}")
                try:
                    # GotSport uses specific URL patterns for team schedules
                    # Try to fetch and parse
                    resp = requests.get(td['url'], timeout=30)
                    soup_team = BeautifulSoup(resp.content, 'html.parser')
                    
                    # Save for debugging
                    with open(f"team_page_{td['name'][:20].replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                        f.write(soup_team.prettify())
                    
                    print(f"  [OK] Saved team page HTML")
                    print(f"  [INFO] Manual inspection needed - GotSport structure varies")
                    
                except Exception as e:
                    print(f"  [ERROR] {e}")
                
                time.sleep(1)  # Be nice to the server
                print()
        else:
            print("[WARN] No team links found in standings page")
            print()
            
    except Exception as e:
        print(f"[ERROR] Could not process standings page: {e}")
        print()
    
    # Save what we found
    if all_schedules:
        df = pd.DataFrame(all_schedules)
        df.to_csv("Division_Teams_All_Schedules.csv", index=False)
        print(f"[OK] Saved {len(all_schedules)} matches to Division_Teams_All_Schedules.csv")
        return df
    else:
        print("[WARN] No schedules found")
        print()
        print("MANUAL STEP REQUIRED:")
        print("-" * 70)
        print("Please visit GotSport and find team schedule URLs:")
        print()
        print("1. Go to: https://system.gotsport.com/org_event/events/45535/results?group=418528")
        print("2. Click on each team name")
        print("3. Look for 'Schedule' or 'Matches' link")
        print("4. Copy the URL")
        print()
        print("Then update this script with the team schedule URLs")
        print()
        return None


def find_common_opponents(dsx_matches, division_schedules):
    """
    Find opponents that both DSX and other division teams have played
    """
    print("=" * 70)
    print("ANALYZING COMMON OPPONENTS")
    print("=" * 70)
    print()
    
    # Get DSX opponents
    dsx_opponents = set(dsx_matches['Opponent'].unique())
    
    print("DSX has played against:")
    for opp in sorted(dsx_opponents):
        print(f"  - {opp}")
    print()
    
    # For each division team, find their opponents
    division_teams = division_schedules['OpponentTeam'].unique()
    
    common_opponent_matrix = []
    
    for team in division_teams:
        team_schedule = division_schedules[division_schedules['OpponentTeam'] == team]
        their_opponents = set(team_schedule['TheirOpponent'].unique())
        
        # Find common opponents (opponents both teams played)
        common = dsx_opponents.intersection(their_opponents)
        
        if common:
            print(f"{team}:")
            print(f"  Common opponents: {len(common)}")
            for opp in sorted(common):
                # Get DSX's result vs this opponent
                dsx_vs_opp = dsx_matches[dsx_matches['Opponent'] == opp]
                dsx_gf = dsx_vs_opp['GF'].sum()
                dsx_ga = dsx_vs_opp['GA'].sum()
                dsx_gd = dsx_gf - dsx_ga
                dsx_games = len(dsx_vs_opp)
                dsx_avg_gd = dsx_gd / dsx_games if dsx_games > 0 else 0
                
                # Get their result vs this opponent
                their_vs_opp = team_schedule[team_schedule['TheirOpponent'] == opp]
                their_gf = their_vs_opp['GF'].sum()
                their_ga = their_vs_opp['GA'].sum()
                their_gd = their_gf - their_ga
                their_games = len(their_vs_opp)
                their_avg_gd = their_gd / their_games if their_games > 0 else 0
                
                # Calculate relative performance
                relative_gd = dsx_avg_gd - their_avg_gd
                
                print(f"    vs {opp}:")
                print(f"      DSX: {dsx_gf}-{dsx_ga} (GD: {dsx_gd:+.1f}, Avg: {dsx_avg_gd:+.2f})")
                print(f"      {team}: {their_gf}-{their_ga} (GD: {their_gd:+.1f}, Avg: {their_avg_gd:+.2f})")
                print(f"      Relative: DSX {relative_gd:+.2f} better per game")
                
                common_opponent_matrix.append({
                    'Division_Team': team,
                    'Common_Opponent': opp,
                    'DSX_GF': dsx_gf,
                    'DSX_GA': dsx_ga,
                    'DSX_GD': dsx_gd,
                    'DSX_Avg_GD': dsx_avg_gd,
                    'Their_GF': their_gf,
                    'Their_GA': their_ga,
                    'Their_GD': their_gd,
                    'Their_Avg_GD': their_avg_gd,
                    'Relative_GD': relative_gd
                })
            print()
        else:
            print(f"{team}: No common opponents found")
            print()
    
    if common_opponent_matrix:
        df = pd.DataFrame(common_opponent_matrix)
        df.to_csv("Common_Opponent_Analysis.csv", index=False)
        print("[OK] Saved common opponent analysis to Common_Opponent_Analysis.csv")
        return df
    else:
        print("[WARN] No common opponents found")
        return None


def main():
    print()
    print("=" * 70)
    print("DIVISION TEAM SCHEDULE SCRAPER")
    print("Finding Common Opponents for Better Analysis")
    print("=" * 70)
    print()
    
    # Load DSX matches
    dsx_matches = pd.DataFrame([
        {"Date": "2025-08-30", "Opponent": "Blast FC Soccer Academy Blast FC 2018B", "GF": 3, "GA": 5},
        {"Date": "2025-09-01", "Opponent": "Polaris Soccer Club Polaris SC 18B Navy", "GF": 1, "GA": 5},
        {"Date": "2025-09-07", "Opponent": "Columbus Force SC CE 2018B Net Ninjas", "GF": 11, "GA": 0},
        {"Date": "2025-09-08", "Opponent": "Sporting Columbus Sporting Columbus Boys 2018 II", "GF": 5, "GA": 5},
        {"Date": "2025-09-14", "Opponent": "Delaware Knights Delaware Knights 2018 BU08", "GF": 7, "GA": 2},
        {"Date": "2025-09-15", "Opponent": "Johnstown FC Johnstown FC 2018 Boys", "GF": 4, "GA": 0},
        {"Date": "2025-09-21", "Opponent": "Blast FC Soccer Academy Blast FC 2018B", "GF": 0, "GA": 3},
        {"Date": "2025-09-22", "Opponent": "Polaris Soccer Club Polaris SC 18B Navy", "GF": 2, "GA": 4},
        {"Date": "2025-09-28", "Opponent": "Columbus Force SC CE 2018B Net Ninjas", "GF": 1, "GA": 1},
        {"Date": "2025-09-29", "Opponent": "Sporting Columbus Sporting Columbus Boys 2018 II", "GF": 0, "GA": 13},
        {"Date": "2025-10-05", "Opponent": "Delaware Knights Delaware Knights 2018 BU08", "GF": 8, "GA": 10},
        {"Date": "2025-10-06", "Opponent": "Columbus Force SC CE 2018B Net Ninjas", "GF": 8, "GA": 13},
    ])
    
    print(f"DSX has played {len(dsx_matches)} matches this season")
    print()
    
    # Try to scrape division team schedules
    division_schedules = scrape_team_schedules_manual()
    
    if division_schedules is not None and not division_schedules.empty:
        # Find common opponents
        common_analysis = find_common_opponents(dsx_matches, division_schedules)
    else:
        print()
        print("=" * 70)
        print("UNABLE TO AUTO-SCRAPE")
        print("=" * 70)
        print()
        print("GotSport requires manual navigation to find team schedule pages.")
        print()
        print("NEXT STEPS:")
        print("1. Open: https://system.gotsport.com/org_event/events/45535/results?group=418528")
        print("2. Click on team names to find their schedule pages")
        print("3. Save the schedule URLs")
        print("4. Re-run this script with updated URLs")
        print()
        print("OR:")
        print("Focus on head-to-head analysis (which we already have!)")
        print("Run: python analyze_common_opponents.py")
        print()


if __name__ == "__main__":
    main()

