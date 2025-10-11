#!/usr/bin/env python3
"""
Fetch Club Ohio West 18B Academy schedule and stats from GotSport
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_gotsport_team_schedule(team_url):
    """Scrape a team's schedule from GotSport"""
    print(f"\n[FETCHING] Club Ohio West 18B Academy")
    print(f"URL: {team_url}")
    
    try:
        response = requests.get(team_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find schedule table
        matches = []
        
        # GotSport schedule tables typically have class 'table' or similar
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                
                if len(cells) >= 5:  # Typical schedule has: Date, Time, Opponent, Location, Score
                    try:
                        # Extract data (adjust indices based on actual structure)
                        date_text = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                        opponent = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        score = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                        
                        # Parse score (format like "3-2" or "W 3-2")
                        gf = None
                        ga = None
                        
                        if score and '-' in score:
                            score_parts = score.split()
                            score_clean = score_parts[-1] if score_parts else score
                            
                            if '-' in score_clean:
                                parts = score_clean.split('-')
                                if len(parts) == 2:
                                    try:
                                        gf = int(parts[0].strip())
                                        ga = int(parts[1].strip())
                                    except:
                                        pass
                        
                        if opponent and opponent.strip():
                            matches.append({
                                'Date': date_text,
                                'Opponent': opponent,
                                'GF': gf,
                                'GA': ga,
                                'Score': score
                            })
                    except Exception as e:
                        continue
        
        print(f"[OK] Found {len(matches)} matches")
        return matches
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch: {e}")
        return []

def calculate_team_stats(matches):
    """Calculate team statistics from matches"""
    
    # Filter completed matches
    completed = [m for m in matches if m['GF'] is not None and m['GA'] is not None]
    
    if not completed:
        return None
    
    gp = len(completed)
    wins = sum(1 for m in completed if m['GF'] > m['GA'])
    draws = sum(1 for m in completed if m['GF'] == m['GA'])
    losses = sum(1 for m in completed if m['GF'] < m['GA'])
    
    gf_total = sum(m['GF'] for m in completed)
    ga_total = sum(m['GA'] for m in completed)
    gd = gf_total - ga_total
    
    points = wins * 3 + draws
    ppg = points / gp if gp > 0 else 0
    
    gf_per_game = gf_total / gp if gp > 0 else 0
    ga_per_game = ga_total / gp if gp > 0 else 0
    gd_per_game = gd / gp if gp > 0 else 0
    
    # Calculate Strength Index
    ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
    gd_norm = (max(-5.0, min(5.0, gd_per_game)) + 5.0) / 10.0 * 100.0
    strength_index = 0.7 * ppg_norm + 0.3 * gd_norm
    
    return {
        'Team': 'Club Ohio West 18B Academy',
        'GP': gp,
        'W': wins,
        'D': draws,
        'L': losses,
        'Record': f"{wins}-{draws}-{losses}",
        'GF': gf_total,
        'GA': ga_total,
        'GD': gd,
        'GF_per_game': gf_per_game,
        'GA_per_game': ga_per_game,
        'GD_per_game': gd_per_game,
        'Points': points,
        'PPG': ppg,
        'StrengthIndex': strength_index
    }

def main():
    print("="*70)
    print("CLUB OHIO WEST 18B ACADEMY - GOTSPORT SCRAPER")
    print("="*70)
    
    team_url = "https://system.gotsport.com/org_event/events/45535/schedules?team=3201294"
    
    # Scrape matches
    matches = scrape_gotsport_team_schedule(team_url)
    
    if not matches:
        print("\n[ERROR] No matches found")
        print("\nThis could be because:")
        print("  1. The page structure is different than expected")
        print("  2. Team 3201294 is not in this event")
        print("  3. The schedule is not yet published")
        print("\n[MANUAL OPTION] Visit the URL and check if schedule is available:")
        print(f"  {team_url}")
        return
    
    # Save matches
    matches_df = pd.DataFrame(matches)
    matches_df.to_csv("Club_Ohio_West_Matches.csv", index=False)
    print(f"\n[OK] Saved {len(matches)} matches to Club_Ohio_West_Matches.csv")
    
    # Calculate stats
    stats = calculate_team_stats(matches)
    
    if stats:
        print("\n" + "="*70)
        print("CLUB OHIO WEST 18B ACADEMY - STATISTICS")
        print("="*70)
        print(f"\nRecord: {stats['Record']} (W-D-L)")
        print(f"Games Played: {stats['GP']}")
        print(f"Goals: {stats['GF']}-{stats['GA']} (GD: {stats['GD']:+d})")
        print(f"Goals/Game: {stats['GF_per_game']:.2f} for, {stats['GA_per_game']:.2f} against")
        print(f"Points: {stats['Points']} ({stats['PPG']:.2f} PPG)")
        print(f"Strength Index: {stats['StrengthIndex']:.1f}")
        
        # Compare to DSX
        dsx_si = 35.6
        si_diff = stats['StrengthIndex'] - dsx_si
        
        print(f"\n{'='*70}")
        print("COMPARISON TO DSX")
        print("="*70)
        print(f"Club Ohio West SI: {stats['StrengthIndex']:.1f}")
        print(f"DSX SI: {dsx_si}")
        print(f"Difference: {si_diff:+.1f}")
        
        if si_diff > 10:
            print("\n[ANALYSIS] Club Ohio West is STRONGER than DSX")
            print("  Recommendation: Defensive focus, look for counters")
        elif si_diff < -10:
            print("\n[ANALYSIS] DSX is STRONGER than Club Ohio West")
            print("  Recommendation: Press high, dominate possession")
        else:
            print("\n[ANALYSIS] EVENLY MATCHED teams")
            print("  Recommendation: Balanced approach, be clinical")
        
        # Save stats
        stats_df = pd.DataFrame([stats])
        stats_df.to_csv("Club_Ohio_West_Stats.csv", index=False)
        print(f"\n[OK] Saved stats to Club_Ohio_West_Stats.csv")
        
        # Recent form
        completed = [m for m in matches if m['GF'] is not None and m['GA'] is not None]
        if len(completed) >= 5:
            print("\n" + "="*70)
            print("RECENT FORM (Last 5 Games)")
            print("="*70)
            
            recent = completed[-5:]
            for match in recent:
                result = "W" if match['GF'] > match['GA'] else ("D" if match['GF'] == match['GA'] else "L")
                print(f"  {result} {match['GF']}-{match['GA']} vs {match['Opponent']}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

