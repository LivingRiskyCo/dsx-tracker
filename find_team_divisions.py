"""
Find Teams in GotSport Divisions
Searches for specific teams across known GotSport divisions to find their group IDs
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re


class TeamDivisonFinder:
    """Find which GotSport division each team belongs to"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.gotsport_base = "https://system.gotsport.com"
        self.event_id = "45535"  # OSPL/COPL/OCL Fall 2025
        
        # Known group IDs to search
        self.group_ids = [
            ("418528", "OCL BU08 Stripes"),
            ("418523", "OCL BU08 White"),
            ("418525", "OCL BU08 Stars 5v5"),
            ("418526", "OCL BU08 Stars 7v7"),
            ("418537", "OCL BU09 7v7 Stripes (2017 boys)"),
        ]
    
    def normalize_name(self, name):
        """Normalize team name for comparison"""
        if pd.isna(name):
            return ""
        # Remove common suffixes, normalize spaces
        normalized = ' '.join(str(name).strip().split()).lower()
        # Remove common words that vary
        normalized = re.sub(r'\b(boys|b|2018|18b|18|u8|u09|bu08|bu09)\b', '', normalized)
        return normalized.strip()
    
    def search_group_for_team(self, group_id, division_name, team_name):
        """Search a specific GotSport group for a team"""
        url = f"{self.gotsport_base}/org_event/events/{self.event_id}/results?group={group_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for team names in the page
            page_text = soup.get_text().lower()
            team_normalized = self.normalize_name(team_name)
            
            # Try different matching strategies
            # 1. Check if normalized name appears in page
            if team_normalized and team_normalized in page_text:
                # Extract actual team names from links/tables
                team_links = soup.find_all('a', href=True)
                for link in team_links:
                    link_text = link.get_text(strip=True)
                    if link_text and self.normalize_name(link_text) == team_normalized:
                        # Found exact match!
                        return {
                            'found': True,
                            'division': division_name,
                            'group_id': group_id,
                            'team_name_found': link_text,
                            'url': url
                        }
            
            # 2. Try partial matching
            team_words = [w for w in team_normalized.split() if len(w) > 3]
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                link_normalized = self.normalize_name(link_text)
                # Check if at least 3 key words match
                matches = sum(1 for word in team_words if word in link_normalized)
                if matches >= 3 and len(team_words) >= 3:
                    return {
                        'found': True,
                        'division': division_name,
                        'group_id': group_id,
                        'team_name_found': link_text,
                        'url': url,
                        'match_type': 'partial'
                    }
            
            return {'found': False, 'division': division_name, 'group_id': group_id}
            
        except Exception as e:
            return {'found': False, 'division': division_name, 'group_id': group_id, 'error': str(e)}
    
    def find_teams(self, team_names):
        """Find divisions for multiple teams"""
        print("=" * 70)
        print("FINDING TEAMS IN GOTSPORT DIVISIONS")
        print("=" * 70)
        print()
        print(f"Searching for {len(team_names)} teams across {len(self.group_ids)} divisions...")
        print()
        
        results = []
        
        for i, team_name in enumerate(team_names, 1):
            print(f"[{i}/{len(team_names)}] Searching for: {team_name}")
            found = False
            
            for group_id, division_name in self.group_ids:
                result = self.search_group_for_team(group_id, division_name, team_name)
                
                if result.get('found'):
                    print(f"  [OK] Found in {division_name} (group={group_id})")
                    print(f"       Team name: {result.get('team_name_found', team_name)}")
                    results.append({
                        'search_name': team_name,
                        'found': True,
                        'division': result['division'],
                        'group_id': result['group_id'],
                        'actual_team_name': result.get('team_name_found', team_name),
                        'url': result.get('url', ''),
                        'match_type': result.get('match_type', 'exact')
                    })
                    found = True
                    break
                else:
                    time.sleep(0.3)  # Be polite
            
            if not found:
                print(f"  [WARN] Not found in any tracked division")
                results.append({
                    'search_name': team_name,
                    'found': False,
                    'division': 'Unknown',
                    'group_id': '',
                    'actual_team_name': team_name,
                    'url': '',
                    'match_type': 'not_found'
                })
            
            print()
            time.sleep(0.5)  # Be polite to server
        
        return results
    
    def save_results(self, results):
        """Save results to CSV"""
        df = pd.DataFrame(results)
        df.to_csv("Team_Division_Findings.csv", index=False)
        print("=" * 70)
        print("RESULTS SUMMARY")
        print("=" * 70)
        print()
        
        found_teams = df[df['found'] == True]
        not_found = df[df['found'] == False]
        
        print(f"[OK] Found: {len(found_teams)} teams")
        print(f"[!] Not Found: {len(not_found)} teams")
        print()
        
        if len(found_teams) > 0:
            print("Found Teams by Division:")
            for division in found_teams['division'].unique():
                div_teams = found_teams[found_teams['division'] == division]
                print(f"  {division}: {len(div_teams)} teams")
                for _, row in div_teams.iterrows():
                    print(f"    - {row['actual_team_name']} (searched as: {row['search_name']})")
                print()
        
        if len(not_found) > 0:
            print("Teams Not Found:")
            for _, row in not_found.iterrows():
                print(f"  - {row['search_name']}")
            print()
        
        print(f"[OK] Results saved to Team_Division_Findings.csv")
        print()


def main():
    """Main execution"""
    # Teams to search for
    teams_to_find = [
        "Blast FC Soccer Academy Blast FC 2018B",
        "Club Ohio Club Ohio West 18B Academy II",
        "Club Oranje Club Oranje Raptors 2018 BU08 Navy",
        "Columbus Force SC CE 2018B Net Ninjas",
        "Dublin United Soccer Club DUSC Sharks 2018 Boys",
        "Elite FC Elite FC 2018 Boys Liverpool",
        "Elite FC Elite FC 2018 Boys Tottenham",
        "Johnstown FC Johnstown FC 2018 Boys",
        "LFC United LFC United 2018 B Elite",
        "LFC United LFC United 2018 B Elite 2",
        "Lancaster Select Soccer Association (LSSA) LSSA 2018 Boys",
        "NASA Xtabi NASA Xtabi 2018 Boys",
        "Northwest FC Northwest FC 2018B Academy Blue",
        "Pataskala Futbol Club Extreme (PFC Extreme) PFC Extreme U8B Black",
        "Polaris Soccer Club Polaris SC 18B Navy",
        "Pride Soccer Club Pride SC 2019/2018 Boys Copa",
        "Sporting Columbus Sporting Columbus Boys 2018 II",
        "Upper Arlington United UAU 2018 BU U8 BLACK",
        "Worthington United WSP Hawkeyes Blue SC 2018 Boys",
        "Zanesville Arsenal SC Zanesville Arsenal SC 2018B",
    ]
    
    finder = TeamDivisonFinder()
    results = finder.find_teams(teams_to_find)
    finder.save_results(results)
    
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review Team_Division_Findings.csv")
    print("2. For found teams, ensure their division fetch scripts are up to date")
    print("3. For not found teams, check other GotSport groups or different event IDs")
    print()


if __name__ == "__main__":
    main()

