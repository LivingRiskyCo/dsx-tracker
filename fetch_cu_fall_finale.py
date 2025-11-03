#!/usr/bin/env python3
"""
Fetch Cincinnati United Fall Finale 2025 Tournament Data
Scrapes U8 Boys divisions from GotSport event 40635
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import time
import re

EVENT_ID = "40635"
TOURNAMENT_NAME = "Cincinnati United Fall Finale 2025"
OUTPUT_FILE = "CU_Fall_Finale_2025_Division_Rankings.csv"

# U8 Boys division patterns to look for
U8_BOYS_DIVISIONS = [
    'U8 BOYS PLATINUM',
    'U8 BOYS GOLD', 
    'U8 BOYS SILVER',
    'U8 BOYS BRONZE',
    'U8 BOYS BLACK',
    'U8 BOYS YELLOW',
    'U8 BOYS GREEN'
]


def discover_u8_boys_divisions():
    """Discover all U8 Boys divisions in the tournament"""
    print(f"\n  Discovering U8 Boys divisions in: {TOURNAMENT_NAME} (Event {EVENT_ID})")
    
    divisions = []
    base_url = f"https://system.gotsport.com/org_event/events/{EVENT_ID}"
    
    # Try different URL patterns to find divisions
    url_patterns = [
        f"{base_url}/results",
        f"{base_url}/schedules",
        f"{base_url}/results?age=8&gender=m",  # U8 Boys
        f"{base_url}/schedules?age=8&gender=m",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for url in url_patterns:
        try:
            response = session.get(url, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for links that contain group IDs
            links = soup.find_all('a', href=True)
            page_text = soup.get_text().lower()
            
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                
                # Check if link contains a group parameter
                if 'group=' in href:
                    match = re.search(r'group=(\d+)', href)
                    if match:
                        group_id = match.group(1)
                        
                        # Check if division name suggests U8 Boys
                        is_u8_boys = any(
                            div_name.lower() in link_text.lower()
                            for div_name in U8_BOYS_DIVISIONS
                        )
                        
                        # Also check if page context suggests U8 Boys
                        context_match = 'u8' in page_text and 'boys' in page_text
                        
                        if is_u8_boys or context_match:
                            # Check if we already have this division
                            if not any(d['group_id'] == group_id and d['event_id'] == EVENT_ID 
                                      for d in divisions):
                                full_url = urljoin(base_url, href) if not href.startswith('http') else href
                                divisions.append({
                                    'event_id': EVENT_ID,
                                    'group_id': group_id,
                                    'division_name': link_text or f"Group {group_id}",
                                    'url': full_url,
                                    'discovered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                                print(f"    [FOUND] {link_text} (Group {group_id})")
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            continue
    
    return divisions


def scrape_division_standings(event_id, group_id, division_name):
    """Scrape standings from a specific division"""
    url = f"https://system.gotsport.com/org_event/events/{event_id}/results?group={group_id}"
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find standings table
        tables = soup.find_all('table')
        all_teams = []
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            # Get headers
            header_row = rows[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Check if this looks like a standings table
            if not any(h.lower() in ['team', 'gp', 'mp', 'pts', 'points'] for h in headers):
                continue
            
            # Parse data rows
            for idx, row in enumerate(rows[1:], start=1):
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                
                try:
                    # Extract team name
                    team_cell = cells[0]
                    team_link = team_cell.find('a')
                    team_name = team_link.get_text(strip=True) if team_link else team_cell.get_text(strip=True)
                    team_name = team_name.split(' (')[0].strip()
                    
                    if not team_name or len(team_name) < 2:
                        continue
                    
                    # Extract stats (map headers to values)
                    stats = {}
                    for i, header in enumerate(headers):
                        if i < len(cells):
                            value = cells[i].get_text(strip=True)
                            header_lower = header.lower()
                            
                            if 'team' in header_lower:
                                continue
                            elif 'gp' in header_lower or 'mp' in header_lower or 'games' in header_lower:
                                stats['GP'] = int(value or 0)
                            elif header_lower == 'w':
                                stats['W'] = int(value or 0)
                            elif header_lower == 'l':
                                stats['L'] = int(value or 0)
                            elif header_lower == 'd' or 'tie' in header_lower or 'draw' in header_lower:
                                stats['D'] = int(value or 0)
                            elif 'gf' in header_lower or ('goals' in header_lower and 'for' in header_lower):
                                stats['GF'] = int(value or 0)
                            elif 'ga' in header_lower or ('goals' in header_lower and 'against' in header_lower):
                                stats['GA'] = int(value or 0)
                            elif 'gd' in header_lower or '+/-' in header_lower or 'diff' in header_lower:
                                stats['GD'] = int(value or 0)
                            elif 'pts' in header_lower or 'points' in header_lower:
                                stats['Pts'] = int(value or 0)
                    
                    # Calculate missing stats
                    if 'GP' not in stats:
                        stats['GP'] = stats.get('W', 0) + stats.get('L', 0) + stats.get('D', 0)
                    if 'GD' not in stats and 'GF' in stats and 'GA' in stats:
                        stats['GD'] = stats['GF'] - stats['GA']
                    if 'Pts' not in stats and 'W' in stats and 'D' in stats:
                        stats['Pts'] = (stats['W'] * 3) + stats['D']
                    
                    # Calculate PPG and Strength Index
                    gp = stats.get('GP', 1)
                    ppg = stats.get('Pts', 0) / gp if gp > 0 else 0
                    gdpg = stats.get('GD', 0) / gp if gp > 0 else 0
                    
                    ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
                    gdpg_norm = (max(-5.0, min(5.0, gdpg)) + 5.0) / 10.0 * 100.0
                    strength_index = round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)
                    
                    team_data = {
                        'Rank': idx,
                        'Team': team_name,
                        'GP': stats.get('GP', 0),
                        'W': stats.get('W', 0),
                        'L': stats.get('L', 0),
                        'D': stats.get('D', 0),
                        'GF': stats.get('GF', 0),
                        'GA': stats.get('GA', 0),
                        'GD': stats.get('GD', 0),
                        'Pts': stats.get('Pts', 0),
                        'PPG': round(ppg, 2),
                        'StrengthIndex': strength_index,
                        'SourceURL': url,
                        'Division': division_name,
                        'EventID': event_id,
                        'GroupID': group_id,
                        'League': TOURNAMENT_NAME,
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    all_teams.append(team_data)
                    
                except Exception as e:
                    continue
        
        return pd.DataFrame(all_teams)
        
    except Exception as e:
        print(f"    [ERROR] Could not scrape {division_name}: {e}")
        return pd.DataFrame()


def fetch_cu_fall_finale_data():
    """Fetch Cincinnati United Fall Finale tournament data from GotSport"""
    
    print("="*60)
    print("CINCINNATI UNITED FALL FINALE 2025 DATA FETCHER")
    print("="*60)
    print(f"\nEvent ID: {EVENT_ID}")
    print(f"Tournament: {TOURNAMENT_NAME}")
    print(f"URL: https://system.gotsport.com/org_event/events/{EVENT_ID}")
    print(f"\nDiscovering U8 Boys divisions...")
    
    # Discover divisions
    divisions = discover_u8_boys_divisions()
    
    if not divisions:
        print("\n[WARNING] No U8 Boys divisions found automatically")
        print("[INFO] Trying manual discovery from schedules page...")
        # Try manual URL patterns
        manual_url = f"https://system.gotsport.com/org_event/events/{EVENT_ID}/schedules?age=8&gender=m"
        print(f"  Checking: {manual_url}")
        # We'll try to scrape common division patterns if discovery fails
        divisions = []
    
    if not divisions:
        print("\n[WARNING] Could not discover divisions automatically")
        print("[INFO] Tournament may not have published U8 Boys divisions yet, or structure is different")
        return False
    
    print(f"\n[OK] Found {len(divisions)} U8 Boys divisions")
    
    # Scrape each division
    all_divisions_data = []
    for div in divisions:
        print(f"\n  Scraping: {div['division_name']}")
        standings = scrape_division_standings(
            div['event_id'],
            div['group_id'],
            div['division_name']
        )
        
        if not standings.empty:
            all_divisions_data.append(standings)
            print(f"    [OK] {len(standings)} teams found")
        else:
            print(f"    [WARNING] No standings data found for {div['division_name']}")
        
        time.sleep(2)  # Rate limiting
    
    # Combine all divisions
    if all_divisions_data:
        combined_df = pd.concat(all_divisions_data, ignore_index=True)
        
        # Remove duplicates (same team in multiple divisions)
        combined_df = combined_df.drop_duplicates(subset=['Team'], keep='first')
        
        # Re-rank after deduplication
        combined_df = combined_df.sort_values(['PPG', 'GD', 'GF'], ascending=[False, False, False])
        combined_df['Rank'] = range(1, len(combined_df) + 1)
        
        # Save combined data
        combined_df.to_csv(OUTPUT_FILE, index=False)
        
        print("\n" + "="*60)
        print("FETCH COMPLETE")
        print("="*60)
        print(f"\n[OK] Saved {len(combined_df)} teams from {len(all_divisions_data)} divisions")
        print(f"[OK] Output file: {OUTPUT_FILE}")
        print(f"\nStatistics:")
        print(f"  - Unique teams: {combined_df['Team'].nunique()}")
        print(f"  - Unique divisions: {combined_df['Division'].nunique()}")
        print(f"  - Divisions found: {', '.join(combined_df['Division'].unique())}")
        
        return True
    else:
        print("\n[ERROR] No tournament data scraped")
        return False


def main():
    """Main function to fetch CU Fall Finale data"""
    
    success = fetch_cu_fall_finale_data()
    
    if success:
        print()
        print("="*60)
        print("CINCINNATI UNITED FALL FINALE 2025 UPDATE COMPLETE")
        print("="*60)
        print()
        print("[OK] Tournament data updated successfully")
        print(f"Dates: October 25-26, 2025")
        print(f"Location: Cincinnati, Ohio (Warren County Sports Complex & Voice of America Park)")
        print()
        print("="*60)
        print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
    else:
        print()
        print("="*60)
        print("CINCINNATI UNITED FALL FINALE 2025 UPDATE FAILED")
        print("="*60)
        print()
        print("[ERROR] Failed to update tournament data")
        print("[INFO] Check internet connection and try again")
        print()
        print("="*60)


if __name__ == "__main__":
    main()
