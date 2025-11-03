#!/usr/bin/env python3
"""
Fill Missing Games for Opponents' Opponents using Discovered Tournaments
Uses the discovered tournament structure to find missing game data
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from collections import defaultdict

class OpponentGapFiller:
    """Use discovered tournaments to find missing opponent-of-opponent games"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.discovered_tournaments = None
        self.current_opponents_of_opponents = None
    
    def load_discovered_tournaments(self):
        """Load discovered tournament data"""
        try:
            df = pd.read_csv('Ohio_Tournaments_2018_Boys_Discovered_20251102.csv')
            print(f"[OK] Loaded {len(df)} teams from discovered tournaments")
            print(f"[OK] Found {df['EventID'].nunique()} unique tournaments")
            return df
        except Exception as e:
            print(f"[ERROR] Could not load discovered tournaments: {e}")
            return pd.DataFrame()
    
    def load_current_opponents_of_opponents(self):
        """Load current opponent-of-opponent data to find gaps"""
        try:
            df = pd.read_csv('Opponents_of_Opponents.csv')
            print(f"[OK] Loaded {len(df)} current opponent-of-opponent entries")
            return df
        except Exception as e:
            print(f"[WARN] Could not load Opponents_of_Opponents.csv: {e}")
            return pd.DataFrame()
    
    def load_dsx_opponents(self):
        """Load DSX's actual opponents"""
        try:
            df = pd.read_csv('DSX_Matches_Fall2025.csv')
            opponents = df['Opponent'].dropna().unique().tolist()
            print(f"[OK] Found {len(opponents)} DSX opponents")
            return opponents
        except Exception as e:
            print(f"[ERROR] Could not load DSX matches: {e}")
            return []
    
    def normalize_team_name(self, name):
        """Normalize team name for matching"""
        if pd.isna(name):
            return ""
        normalized = ' '.join(str(name).strip().split()).lower()
        # Remove common variations
        normalized = re.sub(r'\b(boys|b|2018|18b|18|u8|u09|bu08|bu09|fc|soccer|club)\b', '', normalized)
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        return normalized.strip()
    
    def match_teams(self, discovered_team, known_team):
        """Check if discovered team matches a known opponent-of-opponent"""
        disc_norm = self.normalize_team_name(discovered_team)
        known_norm = self.normalize_team_name(known_team)
        
        # Exact match after normalization
        if disc_norm == known_norm:
            return True
        
        # Check if one contains the other (for name variations)
        if disc_norm and known_norm:
            if disc_norm in known_norm or known_norm in disc_norm:
                return True
        
        # Check for key identifier matches (club name, location, etc.)
        disc_words = set(disc_norm.split())
        known_words = set(known_norm.split())
        
        if len(disc_words) > 0 and len(known_words) > 0:
            # If they share significant words
            common = disc_words & known_words
            if len(common) >= 2:  # At least 2 common words
                return True
        
        return False
    
    def find_missing_teams(self, discovered_df, current_opp_df, dsx_opponents):
        """Find teams in discovered tournaments that are opponents-of-opponents but missing game data"""
        
        print("\n" + "="*70)
        print("FINDING MISSING TEAMS")
        print("="*70)
        
        # Get list of all opponents-of-opponents we currently track
        if not current_opp_df.empty:
            known_opp_opp = current_opp_df['Opponent_of_Opponent'].dropna().unique().tolist()
            print(f"\nCurrently tracking {len(known_opp_opp)} opponents-of-opponents")
        else:
            known_opp_opp = []
            print("\nNo current opponent-of-opponent data found")
        
        # Get discovered teams that match our known opponents-of-opponents
        missing_teams = []
        
        print(f"\nChecking {len(discovered_df)} discovered teams...")
        
        for idx, row in discovered_df.iterrows():
            discovered_team = row['Team']
            
            # Check if this team is an opponent-of-opponent
            is_opp_opp = False
            matched_name = None
            
            for known_team in known_opp_opp:
                if self.match_teams(discovered_team, known_team):
                    is_opp_opp = True
                    matched_name = known_team
                    break
            
            # Also check if it's a direct DSX opponent (we have their data already)
            is_dsx_opp = False
            for dsx_opp in dsx_opponents:
                if self.match_teams(discovered_team, dsx_opp):
                    is_dsx_opp = True
                    break
            
            # If it's an opponent-of-opponent but not a DSX opponent, and we found it in a tournament
            if is_opp_opp and not is_dsx_opp:
                missing_teams.append({
                    'Discovered_Team': discovered_team,
                    'Matched_Known_Team': matched_name,
                    'EventID': row['EventID'],
                    'GroupID': row['GroupID'],
                    'SourceURL': row['SourceURL'],
                    'Division': row.get('Division', 'Unknown'),
                    'Current_GP': row.get('GP', 0),
                    'Has_Game_Data': row.get('GP', 0) > 0
                })
        
        missing_df = pd.DataFrame(missing_teams)
        
        if not missing_df.empty:
            print(f"\n[OK] Found {len(missing_df)} opponent-of-opponent teams in discovered tournaments")
            
            # Group by whether they have game data
            has_data = missing_df[missing_df['Has_Game_Data'] == True]
            no_data = missing_df[missing_df['Has_Game_Data'] == False]
            
            print(f"  - {len(has_data)} have game data (can use directly)")
            print(f"  - {len(no_data)} need game data extraction (need to scrape schedules)")
            
        else:
            print("\n[INFO] No matching opponent-of-opponent teams found in discovered tournaments")
        
        return missing_df
    
    def extract_game_schedule_for_team(self, event_id, group_id, team_name):
        """Extract actual game schedule/results for a team from a tournament"""
        # Try schedule URL
        url = f"https://system.gotsport.com/org_event/events/{event_id}/schedules?group={group_id}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for team name in the schedule
            # This would need to parse the schedule table to find games involving this team
            # Implementation would depend on GotSport's schedule page structure
            
            matches = []
            # TODO: Parse schedule table to extract games for this team
            # This is similar to what fetch_opponent_opponents.py does
            
            return matches
            
        except Exception as e:
            print(f"    [ERROR] Could not fetch schedule for {team_name}: {e}")
            return []
    
    def fill_gaps(self):
        """Main function to find and fill missing games"""
        print("="*70)
        print("FILLING OPPONENT-OF-OPPONENT GAPS FROM DISCOVERED TOURNAMENTS")
        print("="*70)
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load data
        discovered_df = self.load_discovered_tournaments()
        if discovered_df.empty:
            print("\n[ERROR] No discovered tournament data available")
            return
        
        current_opp_df = self.load_current_opponents_of_opponents()
        dsx_opponents = self.load_dsx_opponents()
        
        # Find missing teams
        missing_df = self.find_missing_teams(discovered_df, current_opp_df, dsx_opponents)
        
        if missing_df.empty:
            print("\n[INFO] No gaps to fill - all opponent-of-opponent teams are already tracked")
            return
        
        # Save missing teams report
        output_file = f"Missing_Opponent_Opponent_Teams_{datetime.now().strftime('%Y%m%d')}.csv"
        missing_df.to_csv(output_file, index=False)
        print(f"\n[OK] Saved missing teams report to: {output_file}")
        
        # Show summary
        print("\n" + "="*70)
        print("GAP ANALYSIS SUMMARY")
        print("="*70)
        
        if len(missing_df) > 0:
            print(f"\nTotal opponent-of-opponent teams found in tournaments: {len(missing_df)}")
            print(f"Teams with game data available: {len(missing_df[missing_df['Has_Game_Data'] == True])}")
            print(f"Teams needing schedule extraction: {len(missing_df[missing_df['Has_Game_Data'] == False])}")
            
            print("\nTournaments containing missing teams:")
            tournament_summary = missing_df.groupby('EventID').size()
            for event_id, count in tournament_summary.items():
                print(f"  Event {event_id}: {count} teams")
            
            print("\nNext Steps:")
            print("1. Review missing teams report to identify priority teams")
            print("2. For teams with Has_Game_Data=True, data is already in discovered CSV")
            print("3. For teams with Has_Game_Data=False, need to extract schedules from URLs")
            print("4. Run enhanced parsing on discovered tournaments to extract game data")
        
        print("\n" + "="*70)
        
        return missing_df


def main():
    filler = OpponentGapFiller()
    missing_df = filler.fill_gaps()
    return missing_df


if __name__ == "__main__":
    df = main()

