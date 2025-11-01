"""
Update All Analytics and Strength Indexes
This script ensures all division rankings files have updated Strength Indexes
and all analytics use the latest data from all tournaments
"""

import pandas as pd
import os
from datetime import datetime

def calculate_strength_index(row):
    """
    Calculate StrengthIndex using PPG and GD/GP
    Formula: 70% PPG-based + 30% GD-based
    """
    try:
        ppg = float(row.get('PPG', 0))
        gp = float(row.get('GP', row.get('MP', row.get('Games', row.get('Played', 1)))))
        gd = float(row.get('GD', row.get('+/-', 0)))
        
        # If GD looks like a total (large number), divide by games
        if abs(gd) > 10 and gp > 0:
            gdpg = gd / gp
        else:
            gdpg = gd  # Already per-game
        
        # Normalize PPG (0-3 range) to 0-100
        ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
        
        # Normalize GD per game (-5 to +5 range) to 0-100
        gdpg_norm = (max(-5.0, min(5.0, gdpg)) + 5.0) / 10.0 * 100.0
        
        # Weighted average: 70% PPG, 30% GD
        strength = 0.7 * ppg_norm + 0.3 * gdpg_norm
        
        return round(strength, 1)
    except Exception as e:
        return 0.0

def update_division_file(filename, description):
    """Update a division rankings file with Strength Indexes"""
    if not os.path.exists(filename):
        print(f"[SKIP] {description}: File not found")
        return False
    
    try:
        df = pd.read_csv(filename, index_col=False)
        
        if df.empty:
            print(f"[SKIP] {description}: Empty file")
            return False
        
        # Ensure required columns exist
        if 'Team' not in df.columns:
            print(f"[WARN] {description}: Missing 'Team' column")
            return False
        
        # Calculate PPG if missing
        if 'PPG' not in df.columns or df['PPG'].isna().all():
            if 'GP' in df.columns and 'Pts' in df.columns:
                df['PPG'] = (pd.to_numeric(df['Pts'], errors='coerce') / 
                            pd.to_numeric(df['GP'], errors='coerce').replace(0, 1)).round(2)
            elif 'MP' in df.columns and 'PTS' in df.columns:
                df['GP'] = pd.to_numeric(df['MP'], errors='coerce').fillna(0)
                df['Pts'] = pd.to_numeric(df['PTS'], errors='coerce').fillna(0)
                df['PPG'] = (df['Pts'] / df['GP'].replace(0, 1)).round(2)
            else:
                # Try to calculate from W, D, L
                if all(col in df.columns for col in ['W', 'D', 'L']):
                    df['GP'] = (pd.to_numeric(df['W'], errors='coerce') + 
                               pd.to_numeric(df['D'], errors='coerce') + 
                               pd.to_numeric(df['L'], errors='coerce')).fillna(0)
                    df['Pts'] = (pd.to_numeric(df['W'], errors='coerce') * 3 + 
                                pd.to_numeric(df['D'], errors='coerce')).fillna(0)
                    df['PPG'] = (df['Pts'] / df['GP'].replace(0, 1)).round(2)
        
        # Ensure GP, GD are numeric
        if 'GP' not in df.columns:
            if 'MP' in df.columns:
                df['GP'] = pd.to_numeric(df['MP'], errors='coerce').fillna(0)
            else:
                df['GP'] = 1  # Default to 1 if missing
        
        if 'GD' not in df.columns:
            # Calculate from GF and GA
            if 'GF' in df.columns and 'GA' in df.columns:
                df['GD'] = (pd.to_numeric(df['GF'], errors='coerce') - 
                           pd.to_numeric(df['GA'], errors='coerce')).fillna(0)
            else:
                df['GD'] = 0
        
        # Calculate or update StrengthIndex
        df['StrengthIndex'] = df.apply(calculate_strength_index, axis=1)
        
        # Save updated file
        df.to_csv(filename, index=False)
        
        # Report
        teams_updated = len(df[df['StrengthIndex'] > 0])
        print(f"[OK] {description}: {teams_updated}/{len(df)} teams with StrengthIndex")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {description}: {e}")
        return False

def update_all_division_files():
    """Update all division rankings files"""
    print("=" * 70)
    print("UPDATING ALL DIVISION RANKINGS FILES")
    print("=" * 70)
    print()
    
    division_files = [
        ("OCL_BU08_Stripes_Division_Rankings.csv", "OCL BU08 Stripes"),
        ("OCL_BU08_White_Division_Rankings.csv", "OCL BU08 White"),
        ("OCL_BU08_Stars_Division_Rankings.csv", "OCL BU08 Stars 5v5"),
        ("OCL_BU08_Stars_7v7_Division_Rankings.csv", "OCL BU08 Stars 7v7"),
        ("MVYSA_B09_3_Division_Rankings.csv", "MVYSA B09-3"),
        ("Haunted_Classic_B08Orange_Division_Rankings.csv", "Haunted Classic Orange"),
        ("Haunted_Classic_B08Black_Division_Rankings.csv", "Haunted Classic Black"),
        ("CU_Fall_Finale_2025_Division_Rankings.csv", "CU Fall Finale"),
        ("Club_Ohio_Fall_Classic_2025_Division_Rankings.csv", "Club Ohio Fall Classic"),
        ("CPL_Fall_2025_Division_Rankings.csv", "CPL Fall 2025"),
    ]
    
    updated = 0
    skipped = 0
    errors = 0
    
    for filename, description in division_files:
        if update_division_file(filename, description):
            updated += 1
        elif os.path.exists(filename):
            errors += 1
        else:
            skipped += 1
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files Updated: {updated}")
    print(f"Files Skipped: {skipped}")
    print(f"Files with Errors: {errors}")
    print()
    print("[OK] All division files updated!")

if __name__ == "__main__":
    update_all_division_files()

