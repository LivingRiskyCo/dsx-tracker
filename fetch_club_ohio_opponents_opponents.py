"""
Fetch Opponents' Opponents from Club Ohio Fall Classic Tournament
This script analyzes the tournament to find all teams that the Club Ohio Fall Classic
opponents have played in other leagues/divisions to enhance our analytics
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

class ClubOhioOpponentAnalyzer:
    """Analyze Club Ohio Fall Classic opponents to find their other opponents"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.gotsport_base = "https://system.gotsport.com"
        self.event_id = "45535"  # OCL Fall 2025
    
    def load_club_ohio_opponents(self):
        """Load opponents from Club Ohio Fall Classic"""
        try:
            matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
            # Filter to Club Ohio Fall Classic opponents
            club_ohio_matches = matches[matches['Tournament'] == '2025 Club Ohio Fall Classic']
            opponents = club_ohio_matches['Opponent'].dropna().unique().tolist()
            print(f"[OK] Found {len(opponents)} Club Ohio Fall Classic opponents:")
            for opp in opponents:
                print(f"  - {opp}")
            return opponents
        except Exception as e:
            print(f"[ERROR] Error loading match history: {e}")
            return []
    
    def find_team_id_from_standings(self, team_name):
        """Find a team's GotSport ID from various standings pages"""
        # Try all relevant group IDs
        group_ids = [
            ("418528", "OCL BU08 Stripes"),
            ("418523", "OCL BU08 White"),
            ("418525", "OCL BU08 Stars 5v5"),
            ("418537", "OCL BU09 7v7 Stripes"),
            ("418530", "OCL BU08 Stars 7v7"),
        ]
        
        for group_id, division_name in group_ids:
            url = f"{self.gotsport_base}/org_event/events/{self.event_id}/results?group={group_id}"
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Look for team name in standings table
                    tables = soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                # Check if team name appears in any cell
                                for cell in cells:
                                    link = cell.find('a')
                                    if link:
                                        link_text = link.get_text(strip=True)
                                        if team_name.lower() in link_text.lower() or link_text.lower() in team_name.lower():
                                            # Extract team ID from link href
                                            href = link.get('href', '')
                                            if 'team=' in href:
                                                team_id = href.split('team=')[1].split('&')[0].split('/')[-1]
                                                print(f"    [OK] Found {team_name} in {division_name} (ID: {team_id})")
                                                return team_id, group_id
                time.sleep(0.5)  # Be nice to server
            except Exception as e:
                continue
        
        return None, None
    
    def fetch_team_schedule(self, team_id, team_name):
        """Fetch a team's schedule from GotSport"""
        url = f"{self.gotsport_base}/org_event/events/{self.event_id}/schedules?team={team_id}"
        matches = []
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 4:
                            # Try to extract match data
                            try:
                                # Look for opponent name and score
                                opponent = None
                                our_score = None
                                opp_score = None
                                
                                for i, cell in enumerate(cells):
                                    text = cell.get_text(strip=True)
                                    # Look for opponent name (usually in a link or specific cell)
                                    link = cell.find('a')
                                    if link and 'team=' in link.get('href', ''):
                                        opponent = link.get_text(strip=True)
                                    
                                    # Look for scores (format: X-Y or X-Y)
                                    if '-' in text and any(c.isdigit() for c in text):
                                        parts = text.split('-')
                                        if len(parts) == 2:
                                            try:
                                                our_score = int(parts[0].strip())
                                                opp_score = int(parts[1].strip())
                                            except:
                                                pass
                                
                                if opponent and opponent != team_name:
                                    matches.append({
                                        'Opponent': opponent,
                                        'GF': our_score,
                                        'GA': opp_score,
                                        'SourceURL': url
                                    })
                            except Exception:
                                continue
                
                print(f"    [OK] Found {len(matches)} matches for {team_name}")
            time.sleep(0.5)  # Be nice to server
        except Exception as e:
            print(f"    [ERROR] Error fetching schedule for {team_name}: {e}")
        
        return matches
    
    def analyze_opponents_opponents(self):
        """Analyze all Club Ohio Fall Classic opponents to find their other opponents"""
        print("=" * 70)
        print("CLUB OHIO FALL CLASSIC - OPPONENTS' OPPONENTS ANALYSIS")
        print("=" * 70)
        print()
        
        # Load Club Ohio opponents
        club_ohio_opponents = self.load_club_ohio_opponents()
        if not club_ohio_opponents:
            print("[ERROR] No opponents found")
            return
        
        print()
        print("=" * 70)
        print("ANALYZING OPPONENTS' SCHEDULES")
        print("=" * 70)
        print()
        
        all_opponents_opponents = {}
        all_matches = []
        
        for i, opponent in enumerate(club_ohio_opponents, 1):
            print(f"[{i}/{len(club_ohio_opponents)}] Processing: {opponent}")
            
            # Try to find team ID
            team_id, group_id = self.find_team_id_from_standings(opponent)
            
            opponents_of_this_opponent = set()
            if team_id:
                matches = self.fetch_team_schedule(team_id, opponent)
                for match in matches:
                    opp_name = match.get('Opponent')
                    if opp_name and opp_name not in club_ohio_opponents:  # Exclude Club Ohio teams
                        opponents_of_this_opponent.add(opp_name)
                        all_matches.append({
                            'ClubOhioOpponent': opponent,
                            'TheirOpponent': opp_name,
                            'GF': match.get('GF'),
                            'GA': match.get('GA'),
                            'SourceURL': match.get('SourceURL')
                        })
                
                all_opponents_opponents[opponent] = list(opponents_of_this_opponent)
                print(f"    [OK] Found {len(opponents_of_this_opponent)} unique opponents")
            else:
                print(f"    [WARN] Could not find team ID for {opponent}")
            
            print()
            time.sleep(1)  # Be nice to server
        
        # Save results
        print("=" * 70)
        print("SAVING RESULTS")
        print("=" * 70)
        print()
        
        # Save opponents' opponents list
        if all_opponents_opponents:
            opp_opp_df = pd.DataFrame([
                {'ClubOhioOpponent': opp, 'TheirOpponent': their_opp}
                for opp, their_opps in all_opponents_opponents.items()
                for their_opp in their_opps
            ])
            opp_opp_df.to_csv("Club_Ohio_Opponents_Opponents.csv", index=False)
            print(f"[OK] Saved {len(opp_opp_df)} opponent-opponent relationships to Club_Ohio_Opponents_Opponents.csv")
        
        # Save all matches
        if all_matches:
            matches_df = pd.DataFrame(all_matches)
            matches_df.to_csv("Club_Ohio_Opponents_Schedules.csv", index=False)
            print(f"[OK] Saved {len(matches_df)} matches to Club_Ohio_Opponents_Schedules.csv")
        
        # Summary
        unique_opponents = set()
        for opps in all_opponents_opponents.values():
            unique_opponents.update(opps)
        
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Club Ohio Fall Classic Opponents Analyzed: {len(club_ohio_opponents)}")
        print(f"Unique Opponents' Opponents Found: {len(unique_opponents)}")
        print(f"Total Matches Discovered: {len(all_matches)}")
        print()
        print("Opponents' Opponents:")
        for opp in sorted(unique_opponents):
            print(f"  - {opp}")


if __name__ == "__main__":
    analyzer = ClubOhioOpponentAnalyzer()
    analyzer.analyze_opponents_opponents()

