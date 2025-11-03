#!/usr/bin/env python3
"""
Discover and Scrape All Ohio Tournaments with 2018 Boys Teams
Expands GotSport scraping to find tournaments automatically

Strategy:
1. Check known Ohio tournament organizer pages
2. Scan event ID ranges for Ohio tournaments
3. Parse tournament pages for 2018 Boys divisions
4. Save all discovered tournaments for tracking
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse

# Known Ohio tournament organizers on GotSport
KNOWN_OHIO_TOURNAMENTS = [
    {
        'name': 'Club Ohio Fall Classic',
        'event_id': '44565',
        'base_url': 'https://system.gotsport.com/org_event/events/44565',
        'year': 2025
    },
    {
        'name': 'CU Fall Finale',
        'event_id': '45535',
        'base_url': 'https://system.gotsport.com/org_event/events/45535',
        'year': 2025
    },
    {
        'name': 'Haunted Classic',
        'event_id': '418537',
        'base_url': 'https://system.gotsport.com/org_event/events/418537',
        'year': 2025
    },
]

# Keywords that indicate Ohio tournaments
OHIO_KEYWORDS = [
    'ohio', 'columbus', 'cincinnati', 'cleveland', 'dayton',
    'club ohio', 'ossl', 'ospl', 'ocl', 'cpl', 'mvysa'
]

# Patterns for 2018 Boys divisions
AGE_PATTERNS = [
    r'2018.*[Bb]oys?',
    r'U9.*[Bb]oys?',
    r'U09.*[Bb]oys?',
    r'BU08',
    r'BU09',
    r'Male.*U9',
    r'Male.*2018',
    r'B.*2018',
    r'Boys.*2018'
]


def discover_divisions_in_event(event_id, event_name):
    """Discover all 2018 Boys divisions in a GotSport event"""
    print(f"\n  Discovering divisions in: {event_name} (Event {event_id})")
    
    divisions = []
    base_url = f"https://system.gotsport.com/org_event/events/{event_id}"
    
    # Try different URL patterns to find divisions
    url_patterns = [
        f"{base_url}/results",
        f"{base_url}/schedules",
        f"{base_url}/results?age=9&gender=m",  # U9 Boys
        f"{base_url}/results?age=8&gender=m",  # U8 Boys
        f"{base_url}/schedules?age=9&gender=m",
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
                        
                        # Check if division name suggests 2018 Boys
                        is_2018_boys = any(
                            re.search(pattern, link_text, re.IGNORECASE) 
                            for pattern in AGE_PATTERNS
                        )
                        
                        # Also check if page context suggests 2018 Boys
                        context_match = any(
                            re.search(pattern, page_text, re.IGNORECASE) 
                            for pattern in AGE_PATTERNS
                        )
                        
                        if is_2018_boys or context_match:
                            # Check if we already have this division
                            if not any(d['group_id'] == group_id and d['event_id'] == event_id 
                                      for d in divisions):
                                full_url = urljoin(base_url, href)
                                divisions.append({
                                    'event_id': event_id,
                                    'event_name': event_name,
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
                        'League': f'GotSport Tournament',
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    all_teams.append(team_data)
                    
                except Exception as e:
                    continue
        
        return pd.DataFrame(all_teams)
        
    except Exception as e:
        print(f"    [ERROR] Could not scrape {division_name}: {e}")
        return pd.DataFrame()


def scan_event_id_range(start_id=44000, end_id=46000, step=50):
    """Scan a range of event IDs for Ohio tournaments"""
    print(f"\n  Scanning event ID range {start_id} to {end_id}...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    found_events = []
    
    # Sample IDs from each range instead of checking all
    for base_id in range(start_id, end_id, step):
        # Check a few IDs in each range
        for offset in [0, 1, 25]:
            event_id = base_id + offset
            
            try:
                url = f"https://system.gotsport.com/org_event/events/{event_id}"
                response = session.get(url, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_text = soup.get_text().lower()
                    
                    # Check if it's an Ohio tournament
                    is_ohio = any(kw.lower() in page_text for kw in OHIO_KEYWORDS)
                    
                    # Check if it has 2018 Boys
                    has_2018_boys = any(
                        re.search(pattern, page_text, re.IGNORECASE) 
                        for pattern in AGE_PATTERNS
                    )
                    
                    if is_ohio and has_2018_boys:
                        title_tag = soup.find('title')
                        title = title_tag.get_text(strip=True) if title_tag else f"Event {event_id}"
                        
                        found_events.append({
                            'event_id': str(event_id),
                            'name': title,
                            'url': url,
                            'method': 'ID_scan'
                        })
                        print(f"    [FOUND] Event {event_id}: {title}")
                
                time.sleep(0.5)  # Rate limiting
                
            except:
                continue
            
            if len(found_events) >= 30:  # Limit to prevent too many requests
                break
        
        if len(found_events) >= 30:
            break
    
    return found_events


def main():
    """Main discovery function"""
    print("="*70)
    print("OHIO TOURNAMENT DISCOVERY - 2018 BOYS TEAMS")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nStrategy:")
    print("1. Check known Ohio tournaments")
    print("2. Scan event ID ranges for Ohio tournaments")
    print("3. Discover 2018 Boys divisions in each tournament")
    print("4. Scrape standings for all discovered divisions\n")
    
    all_divisions_data = []
    discovered_tournaments = []
    
    # Step 1: Check known tournaments
    print("="*70)
    print("STEP 1: Checking Known Ohio Tournaments")
    print("="*70)
    
    for tournament in KNOWN_OHIO_TOURNAMENTS:
        print(f"\n  Processing: {tournament['name']} ({tournament['year']})")
        divisions = discover_divisions_in_event(
            tournament['event_id'],
            tournament['name']
        )
        
        discovered_tournaments.append({
            'name': tournament['name'],
            'event_id': tournament['event_id'],
            'year': tournament['year'],
            'divisions_found': len(divisions)
        })
        
        for div in divisions:
            print(f"    Scraping: {div['division_name']}")
            standings = scrape_division_standings(
                div['event_id'],
                div['group_id'],
                div['division_name']
            )
            
            if not standings.empty:
                all_divisions_data.append(standings)
                print(f"      [OK] {len(standings)} teams found")
            
            time.sleep(2)  # Rate limiting
    
    # Step 2: Scan event ID range for additional tournaments
    print("\n" + "="*70)
    print("STEP 2: Scanning Event ID Ranges for Additional Tournaments")
    print("="*70)
    print("\n  (This may take a few minutes due to rate limiting...)")
    
    # Check for command-line argument or default to 'n'
    import sys
    scan_choice = 'n'  # Default to no scanning (safer, faster)
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['scan', 'y', 'yes', 'true']:
        scan_choice = 'y'
    else:
        # Try to get user input, but catch EOFError for non-interactive mode
        try:
            scan_choice = input("\n  Do you want to scan event ID ranges? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            scan_choice = 'n'
            print("\n  (Non-interactive mode - skipping event ID scan)")
    
    if scan_choice == 'y':
        additional_events = scan_event_id_range(44000, 46000, 50)
        
        print(f"\n  Found {len(additional_events)} additional events")
        
        for event in additional_events[:10]:  # Limit to first 10
            print(f"\n  Processing: {event['name']} (Event {event['event_id']})")
            divisions = discover_divisions_in_event(
                event['event_id'],
                event['name']
            )
            
            for div in divisions:
                print(f"    Scraping: {div['division_name']}")
                standings = scrape_division_standings(
                    div['event_id'],
                    div['group_id'],
                    div['division_name']
                )
                
                if not standings.empty:
                    all_divisions_data.append(standings)
                    print(f"      [OK] {len(standings)} teams found")
                
                time.sleep(2)
    
    # Combine all data
    if all_divisions_data:
        combined_df = pd.concat(all_divisions_data, ignore_index=True)
        
        # Save combined data
        output_file = f"Ohio_Tournaments_2018_Boys_Discovered_{datetime.now().strftime('%Y%m%d')}.csv"
        combined_df.to_csv(output_file, index=False)
        
        # Save tournament summary
        tournaments_df = pd.DataFrame(discovered_tournaments)
        tournaments_file = f"Ohio_Tournaments_Summary_{datetime.now().strftime('%Y%m%d')}.csv"
        tournaments_df.to_csv(tournaments_file, index=False)
        
        print("\n" + "="*70)
        print("DISCOVERY COMPLETE")
        print("="*70)
        print(f"\n[OK] Found {len(combined_df)} teams across {len(all_divisions_data)} divisions")
        print(f"[OK] Found {len(discovered_tournaments)} tournaments")
        print(f"\nOutput Files:")
        print(f"   - Team Data: {output_file}")
        print(f"   - Tournament Summary: {tournaments_file}")
        print(f"\nStatistics:")
        print(f"   - Unique teams: {combined_df['Team'].nunique()}")
        print(f"   - Unique divisions: {combined_df['Division'].nunique() if 'Division' in combined_df.columns else 'N/A'}")
        print(f"   - Unique tournaments: {combined_df['EventID'].nunique() if 'EventID' in combined_df.columns else 'N/A'}")
        
        return combined_df
    else:
        print("\n[WARNING] No tournament data discovered")
        return pd.DataFrame()


if __name__ == "__main__":
    df = main()
