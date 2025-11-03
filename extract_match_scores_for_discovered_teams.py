#!/usr/bin/env python3
"""
Extract Match Scores for Discovered Teams
Extracts actual match results (with scores) from GotSport for teams in Ohio_Tournaments_2018_Boys_Discovered_20251102.csv
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import os

class MatchScoreExtractor:
    """Extract match scores/results from GotSport for discovered teams"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.gotsport_base = "https://system.gotsport.com"
    
    def load_discovered_teams(self):
        """Load discovered teams that need match scores"""
        try:
            df = pd.read_csv('Ohio_Tournaments_2018_Boys_Discovered_20251102.csv')
            # Focus on teams with GP=0 or teams we haven't extracted yet
            return df
        except Exception as e:
            print(f"[ERROR] Could not load discovered teams: {e}")
            return pd.DataFrame()
    
    def extract_matches_from_schedule_url(self, schedule_url, team_name=None):
        """Extract all matches with scores from a GotSport schedule URL"""
        print(f"\n  Extracting matches from: {schedule_url}")
        
        try:
            response = self.session.get(schedule_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches = []
            
            # Look for schedule/results tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Check if this is a schedule/results table
                headers_row = rows[0]
                headers = [th.get_text(strip=True).lower() for th in headers_row.find_all(['th', 'td'])]
                
                # Schedule/results tables typically have: Date, Time, Home, Away, Score, Location
                has_schedule_format = any(h in ['date', 'time', 'home', 'away', 'team', 'vs', 'score', 'result', 'location'] for h in headers)
                
                if has_schedule_format:
                    # Parse each row as a match
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 3:
                            continue
                        
                        try:
                            match = self._parse_match_row(cells, headers, schedule_url)
                            if match:
                                # If team_name is specified, filter for that team
                                if team_name:
                                    normalized_team = self._normalize_team_name(team_name)
                                    match_team1 = self._normalize_team_name(match.get('Team', ''))
                                    match_team2 = self._normalize_team_name(match.get('Opponent', ''))
                                    
                                    if normalized_team in match_team1 or normalized_team in match_team2:
                                        matches.append(match)
                                else:
                                    matches.append(match)
                        except Exception as e:
                            continue
            
            # Also try to find matches in div/span elements (some GotSport pages use divs)
            match_divs = soup.find_all(['div', 'span'], class_=re.compile(r'match|game|schedule|result', re.I))
            for div in match_divs:
                text = div.get_text()
                # Look for score pattern
                score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', text)
                if score_match:
                    # Try to extract teams and date from surrounding elements
                    parent = div.find_parent()
                    if parent:
                        match = self._parse_match_from_div(parent, schedule_url)
                        if match:
                            if not team_name or self._team_in_match(match, team_name):
                                matches.append(match)
            
            print(f"    [OK] Found {len(matches)} matches with scores")
            return matches
            
        except Exception as e:
            print(f"    [ERROR] Could not extract matches: {e}")
            return []
    
    def _parse_match_row(self, cells, headers, source_url):
        """Parse a match row from a schedule table"""
        match = {
            'Team': '',
            'Opponent': '',
            'Date': '',
            'Time': '',
            'Location': '',
            'Score': '',
            'GF': None,
            'GA': None,
            'Result': None,
            'IsHome': None,
            'SourceURL': source_url
        }
        
        # Try to map cells to match data based on headers
        for i, header in enumerate(headers):
            if i >= len(cells):
                break
            
            cell_text = cells[i].get_text(strip=True)
            
            if 'date' in header:
                match['Date'] = cell_text
            elif 'time' in header:
                match['Time'] = cell_text
            elif 'home' in header or ('team' in header and match['Team'] == ''):
                match['Team'] = cell_text
                # Check if there's a link with team name
                link = cells[i].find('a')
                if link:
                    match['Team'] = link.get_text(strip=True)
            elif 'away' in header or (match['Team'] != '' and match['Opponent'] == ''):
                match['Opponent'] = cell_text
                link = cells[i].find('a')
                if link:
                    match['Opponent'] = link.get_text(strip=True)
            elif 'score' in header or 'result' in header:
                match['Score'] = cell_text
                # Parse score
                score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', cell_text)
                if score_match:
                    match['GF'] = int(score_match.group(1))
                    match['GA'] = int(score_match.group(2))
                    match['Result'] = 'W' if match['GF'] > match['GA'] else ('L' if match['GA'] > match['GF'] else 'D')
            elif 'location' in header or 'field' in header:
                match['Location'] = cell_text
        
        # Alternative: if we have a "vs" pattern, parse it differently
        if match['Team'] == '' and match['Opponent'] == '':
            # Try to find team names in links
            for cell in cells:
                links = cell.find_all('a', href=True)
                for link in links:
                    link_text = link.get_text(strip=True)
                    if link_text and 'http' not in link_text.lower():
                        if match['Team'] == '':
                            match['Team'] = link_text
                        elif match['Opponent'] == '':
                            match['Opponent'] = link_text
                        break
        
        # Only return match if we have essential data
        if match['Team'] and match['Opponent'] and match.get('Score'):
            # Determine if Team is home (typically first team listed is home)
            match['IsHome'] = True  # Assume first team is home
            return match
        elif match['Team'] and match['Opponent']:
            # Match without score (scheduled but not played)
            return match
        else:
            return None
    
    def _parse_match_from_div(self, div, source_url):
        """Parse match info from a div element"""
        text = div.get_text(strip=True)
        
        # Look for score pattern
        score_match = re.search(r'(\d+)\s*[-:]\s*(\d+)', text)
        if not score_match:
            return None
        
        # Try to extract team names from links or text
        links = div.find_all('a', href=True)
        teams = [link.get_text(strip=True) for link in links if 'http' not in link.get_text(strip=True).lower()]
        
        if len(teams) >= 2:
            match = {
                'Team': teams[0],
                'Opponent': teams[1],
                'Date': '',
                'Time': '',
                'Location': '',
                'Score': score_match.group(0),
                'GF': int(score_match.group(1)),
                'GA': int(score_match.group(2)),
                'Result': 'W' if int(score_match.group(1)) > int(score_match.group(2)) else ('L' if int(score_match.group(2)) > int(score_match.group(1)) else 'D'),
                'IsHome': True,
                'SourceURL': source_url
            }
            return match
        
        return None
    
    def _normalize_team_name(self, name):
        """Normalize team name for matching"""
        if pd.isna(name) or not name:
            return ""
        normalized = ' '.join(str(name).strip().split()).lower()
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        return normalized.strip()
    
    def _team_in_match(self, match, team_name):
        """Check if team_name appears in match"""
        normalized_team = self._normalize_team_name(team_name)
        match_team1 = self._normalize_team_name(match.get('Team', ''))
        match_team2 = self._normalize_team_name(match.get('Opponent', ''))
        
        return (normalized_team in match_team1 or normalized_team in match_team2 or
                match_team1 in normalized_team or match_team2 in normalized_team)
    
    def extract_all_discovered_teams_scores(self):
        """Extract match scores for all discovered teams"""
        print("="*70)
        print("EXTRACTING MATCH SCORES FOR DISCOVERED TEAMS")
        print("="*70)
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load discovered teams
        discovered_df = self.load_discovered_teams()
        
        if discovered_df.empty:
            print("\n[ERROR] No discovered teams found")
            return
        
        print(f"\nProcessing {len(discovered_df)} discovered teams...")
        print("This will extract match results with scores from GotSport")
        print("\nNote: This may take 15-30 minutes due to rate limiting\n")
        
        all_matches = []
        processed_urls = set()  # Track which URLs we've already processed
        
        # Group by SourceURL to avoid duplicate extractions
        for idx, row in discovered_df.iterrows():
            team_name = row.get('Team', '')
            source_url = row.get('SourceURL', '')
            event_id = row.get('EventID', '')
            group_id = row.get('GroupID', '')
            
            if not source_url or source_url in processed_urls:
                continue
            
            # Convert results URL to schedules URL if needed
            if '/results?' in source_url:
                schedule_url = source_url.replace('/results?', '/schedules?')
            else:
                schedule_url = source_url
            
            print(f"\n[{idx+1}/{len(discovered_df)}] Processing: {team_name}")
            print(f"    URL: {schedule_url}")
            
            # Extract matches from this URL (all teams in group)
            matches = self.extract_matches_from_schedule_url(schedule_url, team_name=None)
            if matches:
                all_matches.extend(matches)
                processed_urls.add(source_url)
            
            time.sleep(2)  # Rate limiting
        
        # Save extracted matches
        if all_matches:
            # Load existing extracted matches
            existing_file = 'Opponents_of_Opponents_Matches_Expanded.csv'
            if os.path.exists(existing_file):
                try:
                    existing_df = pd.read_csv(existing_file)
                    print(f"\n[INFO] Loaded {len(existing_df)} existing matches")
                    
                    # Merge new matches with existing (avoid duplicates)
                    new_df = pd.DataFrame(all_matches)
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    
                    # Remove duplicates based on Team, Opponent, Date, Score
                    combined_df = combined_df.drop_duplicates(subset=['Team', 'Opponent', 'Date', 'Score'], keep='last')
                    print(f"[INFO] After deduplication: {len(combined_df)} total matches")
                    
                    # Update scores in existing matches where we have new data
                    for idx, new_match in new_df.iterrows():
                        # Find matching existing match without score
                        mask = (
                            (combined_df['Team'] == new_match['Team']) &
                            (combined_df['Opponent'] == new_match['Opponent']) &
                            (combined_df['Date'] == new_match['Date']) &
                            (combined_df['Score'].isna() | (combined_df['Score'] == ''))
                        )
                        if mask.any():
                            # Update with new score data
                            combined_df.loc[mask, 'Score'] = new_match.get('Score', '')
                            combined_df.loc[mask, 'GF'] = new_match.get('GF')
                            combined_df.loc[mask, 'GA'] = new_match.get('GA')
                            combined_df.loc[mask, 'Result'] = new_match.get('Result')
                    
                    combined_df.to_csv(existing_file, index=False)
                    print(f"[OK] Updated {existing_file} with {len(all_matches)} new matches")
                except Exception as e:
                    print(f"[ERROR] Could not merge with existing matches: {e}")
                    # Save new matches separately
                    new_file = f"New_Matches_Extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    pd.DataFrame(all_matches).to_csv(new_file, index=False)
                    print(f"[OK] Saved {len(all_matches)} new matches to: {new_file}")
            else:
                # Save as new file
                output_file = 'Opponents_of_Opponents_Matches_Expanded.csv'
                pd.DataFrame(all_matches).to_csv(output_file, index=False)
                print(f"\n[OK] Saved {len(all_matches)} matches to: {output_file}")
        
        print("\n" + "="*70)
        print("EXTRACTION COMPLETE")
        print("="*70)
        print(f"\nTotal matches extracted: {len(all_matches)}")
        print(f"Matches with scores: {sum(1 for m in all_matches if m.get('Score'))}")
        print(f"\nNext Steps:")
        print("1. Run create_comprehensive_rankings.py to regenerate rankings")
        print("2. Rankings will now include full season data for these teams")
        
        return all_matches


def main():
    extractor = MatchScoreExtractor()
    matches = extractor.extract_all_discovered_teams_scores()
    return matches


if __name__ == "__main__":
    matches = main()
