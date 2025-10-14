#!/usr/bin/env python3
"""
Import TeamSnap CSV schedule into DSX team_schedule.csv format
Based on TeamSnap's export format: https://helpme.teamsnap.com/article/1839-importing-team-schedules
"""

import pandas as pd
import sys
from datetime import datetime

def import_teamsnap_csv(teamsnap_file, output_file='team_schedule.csv'):
    """
    Import TeamSnap CSV and convert to DSX team_schedule format
    
    TeamSnap columns (expected):
    - Event Name or Game Title
    - Date (MM/DD/YYYY)
    - Start Time (HH:MM AM/PM)
    - End Time (optional)
    - Arrival Time (minutes before start, or specific time)
    - Location Name
    - Opponent (blank = practice)
    - Uniform
    - Notes
    """
    
    print("="*70)
    print("TEAMSNAP SCHEDULE IMPORTER")
    print("="*70)
    print()
    
    try:
        # Read TeamSnap CSV
        print(f"Reading {teamsnap_file}...")
        df = pd.read_csv(teamsnap_file)
        
        print(f"Found {len(df)} events")
        print()
        
        # Map TeamSnap columns to DSX format
        # This is flexible - it tries to find the right columns
        schedule_data = []
        
        for idx, row in df.iterrows():
            # Determine event type (practice vs game)
            opponent = str(row.get('Opponent', row.get('opponent', '')))
            if pd.isna(opponent) or opponent == '' or opponent.lower() == 'nan':
                event_type = 'Practice'
                opponent = ''
            else:
                event_type = 'Game'
            
            # Parse date
            date_col = row.get('Date', row.get('date', row.get('Game Date', '')))
            try:
                date = pd.to_datetime(date_col).strftime('%Y-%m-%d')
            except:
                date = '2025-01-01'  # Default
            
            # Parse time
            time_col = row.get('Start Time', row.get('time', row.get('Time', '')))
            time = str(time_col) if time_col else 'TBD'
            
            # Parse arrival time
            arrival_col = row.get('Arrival Time', row.get('arrival', ''))
            if arrival_col and str(arrival_col) != 'nan':
                # If it's a number, assume minutes before
                try:
                    mins = int(arrival_col)
                    arrival = f"{mins} min before"
                except:
                    arrival = str(arrival_col)
            else:
                arrival = '15 min before'
            
            # Location
            location = str(row.get('Location', row.get('location', row.get('Location Name', 'TBD'))))
            
            # Uniform
            uniform = str(row.get('Uniform', row.get('uniform', '')))
            if uniform == '' or uniform.lower() == 'nan':
                uniform = 'Blue Jerseys' if event_type == 'Game' else 'Practice Gear'
            
            # Tournament/League
            tournament = str(row.get('Tournament', row.get('tournament', row.get('Division', 'MVYSA Fall 2025'))))
            
            # Notes
            notes = str(row.get('Notes', row.get('notes', '')))
            if notes.lower() == 'nan':
                notes = ''
            
            event = {
                'EventID': idx + 1,
                'EventType': event_type,
                'Date': date,
                'Time': time,
                'Opponent': opponent,
                'Location': location,
                'FieldNumber': '',
                'ArrivalTime': arrival,
                'UniformColor': uniform,
                'Tournament': tournament,
                'HomeAway': 'Away' if event_type == 'Game' else 'Home',
                'Status': 'Upcoming',
                'Notes': notes,
                'OpponentStrengthIndex': ''
            }
            
            schedule_data.append(event)
            
            # Preview
            event_icon = "⚽" if event_type == "Game" else "🏃"
            opp_text = opponent if opponent else "Practice"
            print(f"{event_icon} {date} @ {time} - {opp_text} @ {location}")
        
        # Create DataFrame
        schedule_df = pd.DataFrame(schedule_data)
        
        # Sort by date
        schedule_df['Date'] = pd.to_datetime(schedule_df['Date'])
        schedule_df = schedule_df.sort_values('Date')
        schedule_df['Date'] = schedule_df['Date'].dt.strftime('%Y-%m-%d')
        
        # Save to DSX format
        schedule_df.to_csv(output_file, index=False)
        
        print()
        print("="*70)
        print(f"✅ SUCCESS! Imported {len(schedule_df)} events")
        print(f"   Saved to: {output_file}")
        print()
        print(f"   Games: {len(schedule_df[schedule_df['EventType']=='Game'])}")
        print(f"   Practices: {len(schedule_df[schedule_df['EventType']=='Practice'])}")
        print()
        print("Next steps:")
        print("  1. Review the schedule in Data Manager")
        print("  2. Edit field numbers, uniforms, etc. as needed")
        print("  3. Push to GitHub to sync with team")
        print("="*70)
        
        return True
        
    except FileNotFoundError:
        print(f"❌ ERROR: File '{teamsnap_file}' not found")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("="*70)
        print("TEAMSNAP SCHEDULE IMPORTER")
        print("="*70)
        print()
        print("Usage:")
        print("  python import_teamsnap_schedule.py <teamsnap_file.csv>")
        print()
        print("Example:")
        print("  python import_teamsnap_schedule.py my_teamsnap_export.csv")
        print()
        print("Expected TeamSnap CSV columns:")
        print("  - Date (MM/DD/YYYY)")
        print("  - Start Time (HH:MM AM/PM)")
        print("  - Location")
        print("  - Opponent (blank = practice)")
        print("  - Arrival Time")
        print("  - Uniform")
        print("  - Notes")
        print()
        print("Output:")
        print("  Creates/updates team_schedule.csv in DSX format")
        print("="*70)
        sys.exit(1)
    
    teamsnap_file = sys.argv[1]
    success = import_teamsnap_csv(teamsnap_file)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

