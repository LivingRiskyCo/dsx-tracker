"""
Fetch Opponents' Opponents - Complete Dataset Builder
This script fetches schedules for all DSX opponents, then tracks who THOSE teams have played
to build the most complete dataset possible
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from collections import defaultdict
import os


class OpponentOpponentTracker:
    """Track all opponents' opponents to build comprehensive dataset"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.gotsport_base = "https://system.gotsport.com"
        self.event_id = "45535"  # OCL Fall 2025
    
    def load_dsx_opponents(self):
        """Load all unique opponents from DSX match history"""
        try:
            matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
            opponents = matches['Opponent'].dropna().unique().tolist()
            print(f"[OK] Found {len(opponents)} unique opponents in DSX match history")
            return opponents
        except Exception as e:
            print(f"[ERROR] Error loading DSX match history: {e}")
            return []
    
    def find_team_id_from_standings(self, team_name):
        """Find a team's GotSport ID from the standings page"""
        # Try all relevant group IDs
        group_ids = [
            "418528",  # OCL BU08 Stripes
            "418523",  # OCL BU08 White
            "418525",  # OCL BU08 Stars 5v5
            "418537",  # OCL BU09 7v7 Stripes (2017 boys)
        ]
        
        for group_id in group_ids:
            url = f"{self.gotsport_base}/org_event/events/{self.event_id}/results?group={group_id}"
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for team links
                team_links = soup.find_all('a', href=True)
                for link in team_links:
                    link_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Normalize names for comparison
                    if self._normalize_name(team_name) in self._normalize_name(link_text):
                        # Extract team ID from URL
                        if 'team=' in href:
                            team_id = href.split('team=')[1].split('&')[0]
                            return team_id, group_id
                        elif '/team/' in href or '/schedules?team=' in href:
                            # Try to extract from various URL patterns
                            match = re.search(r'team[=_](\d+)', href)
                            if match:
                                return match.group(1), group_id
                
                time.sleep(0.5)  # Be polite
            except Exception as e:
                continue
        
        return None, None
    
    def _normalize_name(self, name):
        """Normalize team name for comparison"""
        if pd.isna(name):
            return ""
        # Remove common suffixes, normalize spaces
        normalized = ' '.join(str(name).strip().split()).lower()
        # Remove common words that vary
        normalized = re.sub(r'\b(boys|b|2018|18b|18|u8|u09|bu08|bu09)\b', '', normalized)
        return normalized.strip()
    
    def fetch_team_schedule(self, team_id, team_name):
        """Fetch a team's schedule from GotSport"""
        # Try schedule URL
        url = f"{self.gotsport_base}/org_event/events/{self.event_id}/schedules?team={team_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches = []
            # Parse schedule tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        match = self._parse_match_row(cells, team_name)
                        if match:
                            matches.append(match)
            
            return matches
        except Exception as e:
            print(f"    [WARN] Error fetching schedule: {e}")
            return []
    
    def _parse_match_row(self, cells, team_name):
        """Parse a match row from GotSport schedule table"""
        try:
            # GotSport schedule format varies, try to find opponent and score
            opponent = None
            date = None
            score = None
            
            # Look for opponent name (usually in a link)
            for cell in cells:
                links = cell.find_all('a', href=True)
                for link in links:
                    link_text = link.get_text(strip=True)
                    # Make sure it's not the team itself
                    if link_text and self._normalize_name(link_text) != self._normalize_name(team_name):
                        opponent = link_text
                        break
                if opponent:
                    break
            
            # Look for date
            for cell in cells:
                text = cell.get_text(strip=True)
                # Look for date pattern (MM/DD/YYYY or similar)
                date_match = re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)
                if date_match:
                    date = date_match.group()
                    break
            
            # Look for score
            for cell in cells:
                text = cell.get_text(strip=True)
                # Look for score pattern (e.g., "3-2" or "3:2")
                score_match = re.search(r'(\d+)[-:](\d+)', text)
                if score_match:
                    score = f"{score_match.group(1)}-{score_match.group(2)}"
                    break
            
            if opponent:
                return {
                    'Date': date or 'Unknown',
                    'Opponent': opponent,
                    'Team': team_name,
                    'Score': score or 'Unknown'
                }
        except Exception:
            pass
        
        return None
    
    def fetch_from_division_schedules(self, team_name):
        """Alternative: Extract from full division schedule page"""
        # Try to get all matches from division schedule and filter by team
        group_ids = [
            ("418528", "OCL BU08 Stripes"),
            ("418523", "OCL BU08 White"),
            ("418525", "OCL BU08 Stars"),
        ]
        
        all_matches = []
        for group_id, division_name in group_ids:
            url = f"{self.gotsport_base}/org_event/events/{self.event_id}/schedule?group={group_id}"
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse all matches
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 4:
                            # Check if this match involves our team
                            row_text = row.get_text()
                            if self._normalize_name(team_name) in self._normalize_name(row_text):
                                match = self._parse_match_row(cells, team_name)
                                if match:
                                    match['Division'] = division_name
                                    all_matches.append(match)
                
                time.sleep(0.5)
            except Exception:
                continue
        
        return all_matches
    
    def build_complete_opponent_list(self):
        """Build complete list of all opponents' opponents"""
        print("=" * 70)
        print("BUILDING COMPLETE OPPONENT DATASET")
        print("=" * 70)
        print()
        
        # Step 1: Get DSX opponents
        dsx_opponents = self.load_dsx_opponents()
        if not dsx_opponents:
            return {}
        
        print(f"Step 1: Analyzing {len(dsx_opponents)} DSX opponents")
        print()
        
        # Step 2: For each opponent, find their schedule
        opponent_opponents = defaultdict(set)
        all_matches = []
        
        for i, opponent in enumerate(dsx_opponents, 1):
            print(f"[{i}/{len(dsx_opponents)}] Processing: {opponent}")
            
            # Try to find team ID
            team_id, group_id = self.find_team_id_from_standings(opponent)
            
            matches = []
            if team_id:
                print(f"    [OK] Found team ID: {team_id} in group {group_id}")
                matches = self.fetch_team_schedule(team_id, opponent)
                print(f"    [OK] Found {len(matches)} matches from schedule page")
            else:
                print(f"    [WARN] Could not find team ID, trying division schedule")
                matches = self.fetch_from_division_schedules(opponent)
                print(f"    [OK] Found {len(matches)} matches from division schedule")
            
            # Extract opponents
            for match in matches:
                opp_name = match.get('Opponent')
                if opp_name and self._normalize_name(opp_name) != self._normalize_name(opponent):
                    opponent_opponents[opponent].add(opp_name)
                    all_matches.append(match)
            
            if matches:
                print(f"    [OK] Found {len(opponent_opponents[opponent])} unique opponents")
            else:
                print(f"    [WARN] No matches found")
            
            print()
            time.sleep(1)  # Be polite to the server
        
        # Step 3: Create comprehensive dataset
        print("=" * 70)
        print("DATASET SUMMARY")
        print("=" * 70)
        print()
        
        total_opponents = set()
        for opp, opp_opps in opponent_opponents.items():
            total_opponents.update(opp_opps)
            print(f"{opp}:")
            print(f"  Played {len(opp_opps)} unique opponents")
            for opp_opp in sorted(opp_opps):
                print(f"    - {opp_opp}")
            print()
        
        print(f"[INFO] Total unique opponents of opponents: {len(total_opponents)}")
        print()
        
        # Save results
        self._save_results(opponent_opponents, all_matches, total_opponents)
        
        return opponent_opponents
    
    def _save_results(self, opponent_opponents, all_matches, total_opponents):
        """Save results to CSV files"""
        # Save opponent-opponent mapping
        opp_opp_df = []
        for opp, opp_opps in opponent_opponents.items():
            for opp_opp in opp_opps:
                opp_opp_df.append({
                    'DSX_Opponent': opp,
                    'Opponent_of_Opponent': opp_opp
                })
        
        if opp_opp_df:
            df = pd.DataFrame(opp_opp_df)
            df.to_csv("Opponents_of_Opponents.csv", index=False)
            print(f"[OK] Saved to Opponents_of_Opponents.csv ({len(df)} entries)")
        
        # Save all matches found
        if all_matches:
            matches_df = pd.DataFrame(all_matches)
            matches_df.to_csv("Opponent_Schedules.csv", index=False)
            print(f"[OK] Saved to Opponent_Schedules.csv ({len(matches_df)} matches)")
        
        # Save complete list of all teams to track
        if total_opponents:
            teams_to_track = pd.DataFrame({
                'Team': sorted(total_opponents),
                'Source': 'Opponent of Opponent',
                'Date_Added': datetime.now().strftime('%Y-%m-%d')
            })
            teams_to_track.to_csv("Teams_to_Track.csv", index=False)
            print(f"[OK] Saved to Teams_to_Track.csv ({len(teams_to_track)} teams)")
        
        print()


def main():
    """Main execution"""
    tracker = OpponentOpponentTracker()
    opponent_opponents = tracker.build_complete_opponent_list()
    
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)
    print()
    print("[INFO] Files created:")
    print("  - Opponents_of_Opponents.csv - Mapping of who each opponent played")
    print("  - Opponent_Schedules.csv - All matches found")
    print("  - Teams_to_Track.csv - Complete list of teams to add to tracking")
    print()
    print("[INFO] Next steps:")
    print("  1. Review Teams_to_Track.csv")
    print("  2. Add these teams to your division tracking scripts")
    print("  3. Run update_all_data.py to fetch their data")
    print()


if __name__ == "__main__":
    main()

