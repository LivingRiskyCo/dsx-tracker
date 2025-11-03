#!/usr/bin/env python3
"""
Extract Schedules for Missing Opponent-of-Opponent Teams
Focuses on the 238 teams identified as missing game data to complete DSX analytics
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from urllib.parse import urljoin

class MissingTeamScheduleExtractor:
    """Extract game schedules/results for missing opponent-of-opponent teams"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.gotsport_base = "https://system.gotsport.com"
    
    def load_missing_teams(self):
        """Load the missing teams that need game data"""
        try:
            df = pd.read_csv('Missing_Opponent_Opponent_Teams_20251103.csv')
            print(f"[OK] Loaded {len(df)} missing teams")
            return df
        except Exception as e:
            print(f"[ERROR] Could not load missing teams: {e}")
            return pd.DataFrame()
    
    def extract_schedule_from_group(self, event_id, group_id, team_name):
        """Extract schedule/results for a team from a tournament group"""
        print(f"\n  Extracting schedule for: {team_name}")
        print(f"    Event: {event_id}, Group: {group_id}")
        
        # Try schedule URL
        schedule_url = f"{self.gotsport_base}/org_event/events/{event_id}/schedules?group={group_id}"
        
        try:
            response = self.session.get(schedule_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches = []
            
            # Look for schedule table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Check if this looks like a schedule table
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # Schedule tables usually have: Date, Time, Home, Away, Score, Location
                if any(h.lower() in ['date', 'time', 'home', 'away', 'team', 'vs', 'score'] for h in headers):
                    # Parse schedule rows
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 3:
                            continue
                        
                        try:
                            # Extract match data - this will vary by tournament structure
                            # Common patterns:
                            # - Date, Time, Home Team, Away Team, Score, Location
                            # - Date, Time, Match, Teams, Score
                            
                            match_data = {}
                            
                            for i, header in enumerate(headers):
                                if i < len(cells):
                                    value = cells[i].get_text(strip=True)
                                    header_lower = header.lower()
                                    
                                    if 'date' in header_lower:
                                        match_data['Date'] = value
                                    elif 'time' in header_lower:
                                        match_data['Time'] = value
                                    elif 'home' in header_lower or 'team' in header_lower:
                                        if 'home' not in match_data:
                                            match_data['HomeTeam'] = value
                                        else:
                                            match_data['AwayTeam'] = value
                                    elif 'away' in header_lower:
                                        match_data['AwayTeam'] = value
                                    elif 'score' in header_lower or 'result' in header_lower:
                                        match_data['Score'] = value
                                    elif 'location' in header_lower or 'field' in header_lower:
                                        match_data['Location'] = value
                            
                            # Check if this match involves our target team
                            home_team = match_data.get('HomeTeam', '')
                            away_team = match_data.get('AwayTeam', '')
                            
                            # Normalize team names for matching
                            def normalize_team(name):
                                if not name:
                                    return ""
                                normalized = ' '.join(str(name).strip().split()).lower()
                                normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
                                return normalized.strip()
                            
                            target_normalized = normalize_team(team_name)
                            home_normalized = normalize_team(home_team)
                            away_normalized = normalize_team(away_team)
                            
                            # Check if team is in this match
                            if (target_normalized in home_normalized or 
                                target_normalized in away_normalized or
                                home_normalized in target_normalized or
                                away_normalized in target_normalized):
                                
                                # Determine opponent
                                if target_normalized in home_normalized or home_normalized in target_normalized:
                                    opponent = away_team
                                    is_home = True
                                else:
                                    opponent = home_team
                                    is_home = False
                                
                                # Parse score if available
                                score = match_data.get('Score', '')
                                gf = None
                                ga = None
                                result = None
                                
                                if score:
                                    # Try to parse score like "3-1", "2-2", etc.
                                    score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', score)
                                    if score_match:
                                        if is_home:
                                            gf = int(score_match.group(1))
                                            ga = int(score_match.group(2))
                                        else:
                                            gf = int(score_match.group(2))
                                            ga = int(score_match.group(1))
                                        
                                        if gf > ga:
                                            result = 'W'
                                        elif ga > gf:
                                            result = 'L'
                                        else:
                                            result = 'D'
                                
                                match_info = {
                                    'Team': team_name,
                                    'Opponent': opponent,
                                    'Date': match_data.get('Date', ''),
                                    'Time': match_data.get('Time', ''),
                                    'Location': match_data.get('Location', ''),
                                    'Score': score,
                                    'GF': gf,
                                    'GA': ga,
                                    'Result': result,
                                    'IsHome': is_home,
                                    'EventID': event_id,
                                    'GroupID': group_id,
                                    'SourceURL': schedule_url
                                }
                                
                                matches.append(match_info)
                                
                        except Exception as e:
                            continue
            
            print(f"    [OK] Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            print(f"    [ERROR] Could not extract schedule: {e}")
            return []
    
    def extract_results_from_group(self, event_id, group_id, team_name):
        """Extract results/standings for a team from a tournament group"""
        results_url = f"{self.gotsport_base}/org_event/events/{event_id}/results?group={group_id}"
        
        try:
            response = self.session.get(results_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for standings table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Check headers
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # Standings tables have: Team, GP, W, L, D, GF, GA, GD, Pts
                if any(h.lower() in ['team', 'gp', 'mp', 'w', 'l', 'd', 'pts', 'gf', 'ga'] for h in headers):
                    # Find our team's row
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 3:
                            continue
                        
                        # Get team name (usually first cell)
                        team_cell = cells[0]
                        team_link = team_cell.find('a')
                        row_team_name = team_link.get_text(strip=True) if team_link else team_cell.get_text(strip=True)
                        
                        # Normalize for matching
                        def normalize(name):
                            if not name:
                                return ""
                            normalized = ' '.join(str(name).strip().split()).lower()
                            normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
                            return normalized.strip()
                        
                        if normalize(row_team_name) in normalize(team_name) or normalize(team_name) in normalize(row_team_name):
                            # Found our team - extract stats
                            stats = {}
                            
                            for i, header in enumerate(headers):
                                if i < len(cells):
                                    value = cells[i].get_text(strip=True)
                                    header_lower = header.lower()
                                    
                                    if 'team' in header_lower:
                                        continue
                                    elif 'gp' in header_lower or 'mp' in header_lower:
                                        stats['GP'] = int(value or 0)
                                    elif header_lower == 'w':
                                        stats['W'] = int(value or 0)
                                    elif header_lower == 'l':
                                        stats['L'] = int(value or 0)
                                    elif header_lower == 'd':
                                        stats['D'] = int(value or 0)
                                    elif 'gf' in header_lower:
                                        stats['GF'] = int(value or 0)
                                    elif 'ga' in header_lower:
                                        stats['GA'] = int(value or 0)
                                    elif 'pts' in header_lower:
                                        stats['Pts'] = int(value or 0)
                            
                            return stats
            
            return {}
            
        except Exception as e:
            return {}
    
    def extract_all_missing_teams_data(self):
        """Extract schedules and results for all missing teams"""
        print("="*70)
        print("EXTRACTING SCHEDULES FOR MISSING OPPONENT-OF-OPPONENT TEAMS")
        print("="*70)
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load missing teams
        missing_df = self.load_missing_teams()
        
        if missing_df.empty:
            print("\n[ERROR] No missing teams found")
            return
        
        print(f"\nProcessing {len(missing_df)} missing teams...")
        print("This will extract game schedules/results from GotSport")
        print("\nNote: This may take 10-20 minutes due to rate limiting\n")
        
        all_matches = []
        all_stats = []
        
        for idx, row in missing_df.iterrows():
            team_name = row['Discovered_Team']
            event_id = row['EventID']
            group_id = row['GroupID']
            
            print(f"\n[{idx+1}/{len(missing_df)}] Processing: {team_name}")
            
            # Try to extract schedule
            matches = self.extract_schedule_from_group(event_id, group_id, team_name)
            if matches:
                all_matches.extend(matches)
            
            # Try to extract results/standings
            stats = self.extract_results_from_group(event_id, group_id, team_name)
            if stats:
                stats['Team'] = team_name
                stats['EventID'] = event_id
                stats['GroupID'] = group_id
                all_stats.append(stats)
            
            time.sleep(2)  # Rate limiting
        
        # Save extracted data
        if all_matches:
            matches_df = pd.DataFrame(all_matches)
            matches_file = f"Missing_Teams_Matches_Extracted_{datetime.now().strftime('%Y%m%d')}.csv"
            matches_df.to_csv(matches_file, index=False)
            print(f"\n[OK] Saved {len(all_matches)} matches to: {matches_file}")
        
        if all_stats:
            stats_df = pd.DataFrame(all_stats)
            stats_file = f"Missing_Teams_Stats_Extracted_{datetime.now().strftime('%Y%m%d')}.csv"
            stats_df.to_csv(stats_file, index=False)
            print(f"[OK] Saved {len(all_stats)} team stats to: {stats_file}")
        
        print("\n" + "="*70)
        print("EXTRACTION COMPLETE")
        print("="*70)
        print(f"\nTotal matches extracted: {len(all_matches)}")
        print(f"Total teams with stats: {len(all_stats)}")
        print(f"\nNext Steps:")
        print("1. Review extracted matches and stats")
        print("2. Integrate into opponent-of-opponent analytics")
        print("3. Update DSX match predictions and rankings")
        
        return all_matches, all_stats


def main():
    extractor = MissingTeamScheduleExtractor()
    matches, stats = extractor.extract_all_missing_teams_data()
    return matches, stats


if __name__ == "__main__":
    matches, stats = main()

