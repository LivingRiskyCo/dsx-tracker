#!/usr/bin/env python3
"""
Fetch OCL BU09 7v7 Stripes Division standings from GotSport
OSPL/COPL/OCL Fall 2025 Regular Season
Multiple groups: North, Northeast, West
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime


def fetch_gotsport_division(event_id, group_id):
    """
    Fetch division standings from GotSport
    
    Args:
        event_id: GotSport event ID (e.g., '45535' for Fall 2025)
        group_id: Group/division ID (e.g., '418537' for BU09 7v7 Stripes)
    
    Returns:
        DataFrame with standings
    """
    url = f"https://system.gotsport.com/org_event/events/{event_id}/results?group={group_id}"
    
    print(f"Fetching OCL BU09 7v7 Stripes Division...")
    print(f"URL: {url}\n")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # GotSport uses tables for standings - this page has multiple groups
        standings_df = parse_gotsport_standings(soup, url)
        
        if not standings_df.empty:
            print(f"[OK] Found {len(standings_df)} teams in division\n")
            return standings_df
        else:
            print("[WARNING] No standings data found")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"[ERROR] Could not fetch standings: {e}")
        return pd.DataFrame()


def parse_gotsport_standings(soup, source_url):
    """Parse standings from GotSport HTML - handles multiple regional groups"""
    
    # Try to find ALL standings tables (North, Northeast, West)
    tables = soup.find_all('table')
    
    all_teams = []
    
    for table in tables:
        # Look for header row with standings columns
        headers = []
        header_row = table.find('tr')
        
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Check if this looks like a standings table
            if any(h.lower() in ['team', 'gp', 'pts', 'gf', 'ga', 'w', 'l', 'd', 'mp'] for h in headers):
                # This is likely a standings table
                data = []
                region = "Unknown"
                
                # Try to find region name from preceding heading
                prev_element = table.find_previous(['h4', 'h5', 'strong', 'b'])
                if prev_element:
                    region_text = prev_element.get_text(strip=True)
                    if any(r in region_text.lower() for r in ['north', 'northeast', 'west', 'south', 'east']):
                        region = region_text
                
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all('td')
                    if cells and len(cells) >= 8:  # Need at least Rank, Team, MP, W, L, D, GF, GA, GD, PTS, PPG
                        try:
                            # Column 0: Rank
                            rank_text = cells[0].get_text(strip=True)
                            try:
                                rank = int(rank_text) if rank_text.isdigit() else None
                            except:
                                rank = None
                            
                            # Column 1: Team name (usually has a link)
                            team_cell = cells[1]
                            team_link = team_cell.find('a')
                            if team_link:
                                team_name = team_link.get_text(strip=True)
                            else:
                                team_name = team_cell.get_text(strip=True)
                            
                            # Skip header rows
                            if team_name.lower() in ['team', 'team name'] or not team_name:
                                continue
                            
                            # Parse numeric columns (MP, W, L, D, GF, GA, GD, PTS, PPG)
                            def parse_numeric(cell_text):
                                """Parse numeric value from cell, handling per-game averages"""
                                clean = re.sub(r'[^\d.\-]', '', str(cell_text))
                                if clean:
                                    try:
                                        return float(clean)
                                    except:
                                        return 0.0
                                return 0.0
                            
                            mp = parse_numeric(cells[2].get_text(strip=True)) if len(cells) > 2 else 0
                            w = parse_numeric(cells[3].get_text(strip=True)) if len(cells) > 3 else 0
                            l = parse_numeric(cells[4].get_text(strip=True)) if len(cells) > 4 else 0
                            d = parse_numeric(cells[5].get_text(strip=True)) if len(cells) > 5 else 0
                            gf = parse_numeric(cells[6].get_text(strip=True)) if len(cells) > 6 else 0
                            ga = parse_numeric(cells[7].get_text(strip=True)) if len(cells) > 7 else 0
                            gd = parse_numeric(cells[8].get_text(strip=True)) if len(cells) > 8 else 0
                            pts = parse_numeric(cells[9].get_text(strip=True)) if len(cells) > 9 else 0
                            ppg = parse_numeric(cells[10].get_text(strip=True)) if len(cells) > 10 else 0
                            
                            # Create team record
                            team_record = {
                                'Rank': rank if rank else len(all_teams) + 1,
                                'Team': team_name,
                                'MP': mp,
                                'W': int(w) if w else 0,
                                'L': int(l) if l else 0,
                                'D': int(d) if d else 0,
                                'GF': gf,
                                'GA': ga,
                                'GD': gd,
                                'PTS': int(pts) if pts else 0,
                                'PPG': ppg,
                                'Region': region
                            }
                            
                            all_teams.append(team_record)
                        except Exception as e:
                            # Skip rows that can't be parsed
                            continue
    
    # Convert to DataFrame
    if all_teams:
        df = pd.DataFrame(all_teams)
        df['SourceURL'] = source_url
        df['League/Division'] = 'OCL BU09 7v7 Stripes'
        return df
    
    return pd.DataFrame()


def enrich_standings(df):
    """Add calculated fields to standings"""
    
    if df.empty:
        return df
    
    # Standardize column names
    if 'MP' in df.columns:
        df['GP'] = pd.to_numeric(df['MP'], errors='coerce').fillna(0)
    elif 'GP' not in df.columns:
        df['GP'] = 0
    
    if 'PTS' in df.columns:
        df['Pts'] = pd.to_numeric(df['PTS'], errors='coerce').fillna(0)
    elif 'Pts' not in df.columns:
        df['Pts'] = 0
    
    # Ensure W, D, L are numeric
    for col in ['W', 'D', 'L']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    
    # Ensure GF, GA, GD are numeric
    for col in ['GF', 'GA', 'GD']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    
    # Calculate PPG if not present
    if 'PPG' not in df.columns or df['PPG'].isna().all():
        df['PPG'] = (df['Pts'] / df['GP'].replace(0, 1)).round(2)
    else:
        df['PPG'] = pd.to_numeric(df['PPG'], errors='coerce').fillna(0)
    
    # Calculate StrengthIndex
    def calculate_strength_index(row):
        try:
            ppg = float(row.get('PPG', 0))
            gdpg = float(row.get('GD', 0))
            
            # Normalize PPG (0-3 pts -> 0-100)
            ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
            
            # Normalize GDPG (-5 to +5 -> 0-100)
            gdpg_norm = (max(-5.0, min(5.0, gdpg)) + 5.0) / 10.0 * 100.0
            
            # Calculate StrengthIndex
            strength = 0.7 * ppg_norm + 0.3 * gdpg_norm
            
            return round(strength, 1)
        except:
            return 0.0
    
    df['StrengthIndex'] = df.apply(calculate_strength_index, axis=1)
    
    # Sort by StrengthIndex descending
    df = df.sort_values('StrengthIndex', ascending=False).reset_index(drop=True)
    
    # Add rank (if not already present)
    if 'Rank' not in df.columns:
        df.insert(0, 'Rank', range(1, len(df) + 1))
    else:
        # Reassign ranks based on StrengthIndex
        df['Rank'] = range(1, len(df) + 1)
    
    return df


def main():
    """Fetch and analyze OCL BU09 7v7 Stripes division"""
    
    print("=" * 60)
    print("OCL BU09 7v7 STRIPES DIVISION ANALYZER")
    print("OSPL/COPL/OCL Fall 2025 Regular Season")
    print("=" * 60)
    print()
    
    # GotSport event and group IDs for OCL BU09 7v7 Stripes
    event_id = "45535"
    group_id = "418537"
    
    # Fetch standings
    standings_df = fetch_gotsport_division(event_id, group_id)
    
    if standings_df.empty:
        print("[ERROR] Could not fetch division standings")
        return None
    
    # Enrich with calculated fields
    print("Calculating strength rankings...")
    enriched_df = enrich_standings(standings_df)
    print("[OK] Rankings calculated\n")
    
    # Save to CSV - This is for benchmarking 2017 teams, not main rankings
    output_file = "OCL_BU09_7v7_Stripes_Benchmarking_2017.csv"
    enriched_df.to_csv(output_file, index=False)
    print(f"[OK] Saved to {output_file} (2017 Boys Benchmarking Data)\n")
    print("[INFO] These are 2017 boys teams - used for benchmarking only, not main rankings\n")
    
    # Display rankings
    print("=" * 60)
    print("DIVISION STRENGTH RANKINGS")
    print("=" * 60)
    print()
    
    # Select key columns for display
    display_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex', 'Region']
    display_cols = [col for col in display_cols if col in enriched_df.columns]
    
    if 'Team' in enriched_df.columns:
        print(enriched_df[display_cols].to_string(index=False, max_colwidth=40))
    else:
        print(enriched_df.to_string(index=False))
    
    print()
    print("=" * 60)
    print(f"Total Teams: {len(enriched_df)}")
    print(f"Data Source: GotSport OCL BU09 7v7 Stripes Division")
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    return enriched_df


if __name__ == "__main__":
    df = main()

