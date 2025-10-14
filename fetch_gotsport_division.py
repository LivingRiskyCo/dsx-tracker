"""
Fetch entire OCL BU08 Stripes division from GotSport
Build comprehensive strength rankings
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
        group_id: Group/division ID (e.g., '418528' for BU08 Stripes)
    
    Returns:
        DataFrame with standings
    """
    url = f"https://system.gotsport.com/org_event/events/{event_id}/results?group={group_id}"
    
    print(f"Fetching OCL BU08 Stripes Division...")
    print(f"URL: {url}\n")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # GotSport uses tables for standings
        # Look for the standings table
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
    
    # Try to find ALL standings tables (Northeast, Northwest, Southeast)
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
                
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all('td')
                    if cells and len(cells) >= 3:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        # Skip empty rows and rows that don't have numeric data
                        if row_data and any(row_data) and len(row_data) > 5:
                            data.append(row_data)
                
                if data:
                    # Create DataFrame with appropriate headers
                    if len(headers) == len(data[0]):
                        df = pd.DataFrame(data, columns=headers)
                    else:
                        # Use generic column names if mismatch
                        df = pd.DataFrame(data)
                        df.columns = [f'Col{i}' for i in range(len(df.columns))]
                    
                    all_teams.append(df)
    
    # Combine all tables into one DataFrame
    if all_teams:
        combined_df = pd.concat(all_teams, ignore_index=True)
        combined_df['SourceURL'] = source_url
        return combined_df
    
    return pd.DataFrame()


def calculate_strength_index(row):
    """
    Calculate StrengthIndex using PPG and GD/GP
    
    Formula (from Excel workbook):
    - PPG normalized to 0-100 (0 pts = 0, 3 pts = 100)
    - GD per game normalized to 0-100 (-5 GD/GP = 0, +5 GD/GP = 100)
    - StrengthIndex = 0.7 * PPG_norm + 0.3 * GDPG_norm
    """
    try:
        # Extract PPG (already calculated or calculate it)
        ppg = row.get('PPG', 0)
        if ppg == 0 or pd.isna(ppg):
            # Calculate if not present
            gp = float(row.get('GP', row.get('MP', row.get('Games', row.get('Played', 1)))))
            pts = float(row.get('Pts', row.get('Points', 0)))
            ppg = pts / gp if gp > 0 else 0
        else:
            ppg = float(ppg)
        
        # Extract GDPG (GotSport provides GD as per-game already, or calculate it)
        gdpg = row.get('GD', row.get('+/-', 0))
        gdpg = float(gdpg) if gdpg is not None else 0.0
        
        # If GD looks like a total (large number), divide by games
        gp = float(row.get('GP', row.get('MP', row.get('Games', row.get('Played', 1)))))
        if abs(gdpg) > 10 and gp > 0:  # Likely a total, not per-game
            gdpg = gdpg / gp
        
        # Normalize PPG (0-3 pts -> 0-100)
        ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
        
        # Normalize GDPG (-5 to +5 -> 0-100)
        gdpg_norm = (max(-5.0, min(5.0, gdpg)) + 5.0) / 10.0 * 100.0
        
        # Calculate StrengthIndex
        strength = 0.7 * ppg_norm + 0.3 * gdpg_norm
        
        return round(strength, 1)
        
    except Exception as e:
        return 0.0


def enrich_standings(df):
    """Add calculated fields to standings"""
    
    # Standardize column names (try to find the right columns)
    column_mapping = {}
    
    for col in df.columns:
        col_lower = col.lower()
        if 'team' in col_lower or 'club' in col_lower:
            column_mapping[col] = 'Team'
        elif col_lower in ['gp', 'games', 'played', 'p', 'mp']:
            column_mapping[col] = 'GP'
        elif col_lower in ['w', 'win', 'wins']:
            column_mapping[col] = 'W'
        elif col_lower in ['d', 'draw', 'draws', 't', 'tie', 'ties']:
            column_mapping[col] = 'D'
        elif col_lower in ['l', 'loss', 'losses']:
            column_mapping[col] = 'L'
        elif col_lower in ['gf', 'goals for', 'f', 'for']:
            column_mapping[col] = 'GF'
        elif col_lower in ['ga', 'goals against', 'a', 'against']:
            column_mapping[col] = 'GA'
        elif col_lower in ['gd', '+/-', 'diff', 'goal diff']:
            column_mapping[col] = 'GD'
        elif col_lower in ['pts', 'points', 'pt']:
            column_mapping[col] = 'Pts'
        elif col_lower in ['ppg']:
            column_mapping[col] = 'PPG'
    
    df = df.rename(columns=column_mapping)
    
    # Calculate derived fields if not present
    if 'GP' in df.columns:
        df['GP'] = pd.to_numeric(df['GP'], errors='coerce').fillna(0)
    
    if 'Pts' in df.columns:
        df['Pts'] = pd.to_numeric(df['Pts'], errors='coerce').fillna(0)
    
    if 'GF' in df.columns and 'GA' in df.columns:
        df['GF'] = pd.to_numeric(df['GF'], errors='coerce').fillna(0)
        df['GA'] = pd.to_numeric(df['GA'], errors='coerce').fillna(0)
        
        if 'GD' not in df.columns:
            df['GD'] = df['GF'] - df['GA']
    
    if 'GD' in df.columns:
        df['GD'] = pd.to_numeric(df['GD'], errors='coerce').fillna(0)
    
    # Calculate PPG
    if 'GP' in df.columns and 'Pts' in df.columns:
        df['PPG'] = (df['Pts'] / df['GP'].replace(0, 1)).round(2)
    
    # Calculate StrengthIndex
    df['StrengthIndex'] = df.apply(calculate_strength_index, axis=1)
    
    # Sort by StrengthIndex descending
    df = df.sort_values('StrengthIndex', ascending=False).reset_index(drop=True)
    
    # Add rank
    df.insert(0, 'Rank', range(1, len(df) + 1))
    
    return df


def main():
    """Fetch and analyze OCL BU08 Stripes division"""
    
    print("=" * 60)
    print("OCL BU08 STRIPES DIVISION ANALYZER")
    print("Fall 2025 Season")
    print("=" * 60)
    print()
    
    # GotSport event and group IDs for OCL BU08 Stripes
    event_id = "45535"
    group_id = "418528"
    
    # Fetch standings
    standings_df = fetch_gotsport_division(event_id, group_id)
    
    if standings_df.empty:
        print("[ERROR] Could not fetch division standings")
        return None
    
    # Enrich with calculated fields
    print("Calculating strength rankings...")
    enriched_df = enrich_standings(standings_df)
    print("[OK] Rankings calculated\n")
    
    # Save to CSV
    output_file = "OCL_BU08_Stripes_Division_Rankings.csv"
    enriched_df.to_csv(output_file, index=False)
    print(f"[OK] Saved to {output_file}\n")
    
    # Display rankings
    print("=" * 60)
    print("DIVISION STRENGTH RANKINGS")
    print("=" * 60)
    print()
    
    # Select key columns for display
    display_cols = ['Rank', 'Team', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'PPG', 'StrengthIndex']
    display_cols = [col for col in display_cols if col in enriched_df.columns]
    
    if 'Team' in enriched_df.columns:
        print(enriched_df[display_cols].to_string(index=False, max_colwidth=40))
    else:
        print(enriched_df.to_string(index=False))
    
    print()
    print("=" * 60)
    print(f"Total Teams: {len(enriched_df)}")
    print(f"Data Source: GotSport OCL BU08 Stripes Division")
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    return enriched_df


if __name__ == "__main__":
    df = main()

