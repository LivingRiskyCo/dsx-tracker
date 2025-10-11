"""
Opponent Tracker Scraper for DSX Soccer Team
Fetches schedules from MVYSA and GotSport to populate the opponent analysis workbook
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from typing import List, Dict, Optional
import time


class MVYSAScraper:
    """Scraper for MVYSA schedules"""
    
    BASE_URL = "https://www.mvysa.com/cgi-bin"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_team_schedule(self, team_id: str, season: str = "202509") -> List[Dict]:
        """
        Fetch schedule for a specific team
        
        Args:
            team_id: MVYSA team ID (e.g., '4263' for BSA Celtic 18B City)
            season: Season code (e.g., '202509' for Fall 2025)
        
        Returns:
            List of match dictionaries
        """
        url = f"{self.BASE_URL}/sked.cgi?fnc=sked2&bt={team_id}&season={season}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = self._parse_schedule(soup, url)
            
            print(f"[OK] Fetched {len(matches)} matches for team {team_id}")
            return matches
            
        except requests.RequestException as e:
            print(f"[ERROR] Error fetching team {team_id}: {e}")
            return []
    
    def _parse_schedule(self, soup: BeautifulSoup, source_url: str) -> List[Dict]:
        """Parse the schedule table from MVYSA HTML"""
        matches = []
        
        # Find all table rows - MVYSA uses TR elements with class='body' TDs
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td', class_='body')
            
            # A game row has at least 4 cells: Game#, Date/Time, Field, Teams, (Ref), Score
            if len(cells) >= 4:
                match = self._parse_match_row(cells, source_url)
                if match:
                    matches.append(match)
        
        return matches
    
    def _parse_match_row(self, cells, source_url: str) -> Optional[Dict]:
        """Parse a single MVYSA match row
        
        MVYSA format:
        - Cell 0: Game # and Division
        - Cell 1: Date and Time
        - Cell 2: Field/Location
        - Cell 3: Teams (home and away as separate <a> links)
        - Cell 4: (optional) Referee
        - Cell 5: Score (two lines: home then away)
        """
        try:
            # Date and time (cell 1)
            date_text = cells[1].get_text(' ', strip=True)
            
            # Teams (cell 3) - look for <a> tags
            team_links = cells[3].find_all('a')
            
            if len(team_links) < 2:
                return None  # Need both home and away teams
            
            home_team = team_links[0].get_text(strip=True)
            away_team = team_links[1].get_text(strip=True)
            
            # Score (cell 5 if present, otherwise cell 4 or later)
            # Look for the rightmost cell that has numbers
            score_cell = None
            for i in range(len(cells) - 1, 2, -1):  # Check from right to left
                text = cells[i].get_text(strip=True)
                if text and any(c.isdigit() for c in text):
                    score_cell = cells[i]
                    break
            
            home_score = None
            away_score = None
            
            if score_cell:
                # Score is on two lines: home<br>away
                score_lines = score_cell.get_text('\n', strip=True).split('\n')
                if len(score_lines) >= 2:
                    try:
                        home_score = int(score_lines[0].strip())
                        away_score = int(score_lines[1].strip())
                    except ValueError:
                        pass
            
            # Field (cell 2)
            field_text = cells[2].get_text(' ', strip=True)
            
            return {
                'date': date_text,
                'home_team': home_team,
                'away_team': away_team,
                'gf': home_score,
                'ga': away_score,
                'field': field_text,
                'source_url': source_url
            }
            
        except Exception as e:
            # Silently skip rows that don't match expected format
            return None
    
    def _parse_date(self, date_text: str) -> str:
        """Parse various date formats to YYYY-MM-DD"""
        try:
            # Try common formats
            for fmt in ['%b %d', '%m/%d/%Y', '%Y-%m-%d', '%m/%d']:
                try:
                    dt = datetime.strptime(date_text, fmt)
                    # If year not specified, assume current year
                    if dt.year == 1900:
                        dt = dt.replace(year=2025)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return as-is
            return date_text
            
        except Exception:
            return date_text


class GotSportScraper:
    """Scraper for GotSport schedules"""
    
    BASE_URL = "https://system.gotsport.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_division_standings(self, event_id: str, group_id: str) -> pd.DataFrame:
        """
        Fetch division standings and team stats
        
        Args:
            event_id: GotSport event ID (e.g., '45535')
            group_id: Group/division ID (e.g., '418528' for BU08 Stripes)
        
        Returns:
            DataFrame with team standings
        """
        url = f"{self.BASE_URL}/org_event/events/{event_id}/results?group={group_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            standings = self._parse_standings(soup, url)
            
            print(f"[OK] Fetched standings for group {group_id}")
            return standings
            
        except requests.RequestException as e:
            print(f"[ERROR] Error fetching standings: {e}")
            return pd.DataFrame()
    
    def _parse_standings(self, soup: BeautifulSoup, source_url: str) -> pd.DataFrame:
        """Parse standings table from GotSport"""
        # GotSport uses tables with class 'table' or 'standings'
        tables = soup.find_all('table')
        
        for table in tables:
            # Look for standings headers
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            
            if any(h.lower() in ['team', 'gp', 'pts', 'gf', 'ga'] for h in headers):
                # Found the standings table
                data = []
                
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = [td.get_text(strip=True) for td in row.find_all('td')]
                    if cells:
                        data.append(cells)
                
                if data:
                    df = pd.DataFrame(data, columns=headers if headers else None)
                    df['SourceURL'] = source_url
                    return df
        
        return pd.DataFrame()
    
    def get_team_schedule(self, event_id: str, team_id: str) -> List[Dict]:
        """
        Fetch schedule for a specific team
        
        Args:
            event_id: GotSport event ID
            team_id: Team ID in the system
        
        Returns:
            List of match dictionaries
        """
        url = f"{self.BASE_URL}/org_event/events/{event_id}/schedule?team={team_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = self._parse_team_schedule(soup, url)
            
            print(f"[OK] Fetched {len(matches)} matches for team {team_id}")
            return matches
            
        except requests.RequestException as e:
            print(f"[ERROR] Error fetching team schedule: {e}")
            return []
    
    def _parse_team_schedule(self, soup: BeautifulSoup, source_url: str) -> List[Dict]:
        """Parse team schedule from GotSport"""
        matches = []
        
        # GotSport schedule tables
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                
                if len(cells) >= 4:  # Date, Time, Home, Away, Score
                    match = self._parse_gotsport_match(cells, source_url)
                    if match:
                        matches.append(match)
        
        return matches
    
    def _parse_gotsport_match(self, cells, source_url: str) -> Optional[Dict]:
        """Parse a GotSport match row"""
        try:
            date_text = cells[0].get_text(strip=True)
            home_team = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            away_team = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            score_text = cells[4].get_text(strip=True) if len(cells) > 4 else ""
            
            # Parse score
            gf, ga = None, None
            if score_text and '-' in score_text:
                score_parts = score_text.split('-')
                if len(score_parts) == 2:
                    try:
                        gf = int(score_parts[0].strip())
                        ga = int(score_parts[1].strip())
                    except ValueError:
                        pass
            
            return {
                'date': date_text,
                'home_team': home_team,
                'away_team': away_team,
                'gf': gf,
                'ga': ga,
                'source_url': source_url
            }
            
        except Exception as e:
            print(f"  Warning: Could not parse GotSport match: {e}")
            return None


class OpponentScheduleProcessor:
    """Process scraped schedules for Excel import"""
    
    def __init__(self):
        self.mvysa = MVYSAScraper()
        self.gotsport = GotSportScraper()
    
    def process_opponent_schedules(self, opponent_configs: List[Dict]) -> pd.DataFrame:
        """
        Process multiple opponent schedules
        
        Args:
            opponent_configs: List of dicts with 'name', 'source', 'team_id', etc.
        
        Returns:
            DataFrame formatted for OppSchedules (Paste) sheet
        """
        all_schedules = []
        
        for config in opponent_configs:
            print(f"\nProcessing: {config['name']}")
            
            if config['source'] == 'mvysa':
                matches = self.mvysa.get_team_schedule(
                    config['team_id'],
                    config.get('season', '202509')
                )
            elif config['source'] == 'gotsport':
                matches = self.gotsport.get_team_schedule(
                    config['event_id'],
                    config['team_id']
                )
            else:
                print(f"  [ERROR] Unknown source: {config['source']}")
                continue
            
            # Convert to OppSchedules format
            for match in matches:
                schedule_entry = self._format_for_excel(config['name'], match, config)
                if schedule_entry:  # Only add if format was successful
                    all_schedules.append(schedule_entry)
            
            # Be nice to servers
            time.sleep(1)
        
        # Create DataFrame
        df = pd.DataFrame(all_schedules)
        
        # Ensure columns match Excel sheet
        column_order = [
            'OpponentTeam', 'TheirOpponent', 'Date', 
            'GF', 'GA', 'Venue/Div', 'SourceURL', 'Notes'
        ]
        
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
        
        # Remove duplicates based on key columns
        df = df.drop_duplicates(subset=['OpponentTeam', 'TheirOpponent', 'Date'], keep='first')
        
        return df[column_order]
    
    def _format_for_excel(self, opponent_name: str, match: Dict, config: Dict) -> Dict:
        """Format a single match for Excel import"""
        
        # Normalize team names for comparison
        opponent_norm = opponent_name.lower().strip()
        home_norm = str(match.get('home_team', '')).lower().strip()
        away_norm = str(match.get('away_team', '')).lower().strip()
        
        # Determine which team is the opponent we're tracking
        if home_norm == opponent_norm:
            their_opponent = match['away_team']
            gf = match.get('gf', '')
            ga = match.get('ga', '')
        elif away_norm == opponent_norm:
            their_opponent = match['home_team']
            # Flip score if opponent was away
            gf = match.get('ga', '')
            ga = match.get('gf', '')
        else:
            # Team name doesn't match - skip
            return None
        
        return {
            'OpponentTeam': opponent_name,
            'TheirOpponent': their_opponent,
            'Date': match.get('date', ''),
            'GF': gf if gf is not None else '',
            'GA': ga if ga is not None else '',
            'Venue/Div': config.get('division', ''),
            'SourceURL': match.get('source_url', ''),
            'Notes': match.get('field', '')
        }


def main():
    """Example usage"""
    
    processor = OpponentScheduleProcessor()
    
    # Define opponents to track
    opponents = [
        {
            'name': 'BSA Celtic 18B City',
            'source': 'mvysa',
            'team_id': '4263',
            'season': '202509',
            'division': 'MVYSA Fall 2025'
        },
        {
            'name': 'BSA Celtic 18B United',
            'source': 'mvysa',
            'team_id': '4264',
            'season': '202509',
            'division': 'MVYSA Fall 2025'
        },
        # Add more opponents as needed
        # {
        #     'name': 'Elite FC 2018 Boys Liverpool',
        #     'source': 'gotsport',
        #     'event_id': '45535',
        #     'team_id': 'XXXXX',  # Need to find this
        #     'division': 'OCL BU08 Stripes'
        # }
    ]
    
    print("=== Opponent Schedule Scraper ===\n")
    
    # Process all opponents
    schedules_df = processor.process_opponent_schedules(opponents)
    
    # Save to CSV for import into Excel
    output_file = 'opponent_schedules_import.csv'
    schedules_df.to_csv(output_file, index=False)
    
    print(f"\n[OK] Complete! Saved {len(schedules_df)} matches to {output_file}")
    print(f"\nNext steps:")
    print(f"  1. Open {output_file}")
    print(f"  2. Copy all rows")
    print(f"  3. Paste into 'OppSchedules (Paste)' sheet in your Excel workbook")
    print(f"  4. Common Opponent Matrix will auto-calculate")
    
    return schedules_df


if __name__ == "__main__":
    df = main()
    print("\nPreview of scraped data:")
    print(df.head(10))

