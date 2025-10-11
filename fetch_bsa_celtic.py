"""
Quick script to fetch BSA Celtic schedules (your Oct 18-19 opponents)
"""

from opponent_scraper import OpponentScheduleProcessor
import pandas as pd


def main():
    print("=== Fetching BSA Celtic Schedules ===\n")
    
    processor = OpponentScheduleProcessor()
    
    # Your upcoming opponents on Oct 18-19
    bsa_teams = [
        {
            'name': 'BSA Celtic 18B United',
            'source': 'mvysa',
            'team_id': '4264',
            'season': '202509',
            'division': 'MVYSA Fall 2025'
        },
        {
            'name': 'BSA Celtic 18B City',
            'source': 'mvysa',
            'team_id': '4263',
            'season': '202509',
            'division': 'MVYSA Fall 2025'
        }
    ]
    
    # Fetch schedules
    schedules_df = processor.process_opponent_schedules(bsa_teams)
    
    # Save to CSV
    output_file = 'BSA_Celtic_Schedules.csv'
    schedules_df.to_csv(output_file, index=False)
    
    print(f"\n[OK] Saved {len(schedules_df)} matches to {output_file}")
    print(f"\n[SUMMARY]")
    print(f"   Total matches: {len(schedules_df)}")
    print(f"   BSA Celtic 18B United: {len(schedules_df[schedules_df['OpponentTeam'] == 'BSA Celtic 18B United'])} matches")
    print(f"   BSA Celtic 18B City: {len(schedules_df[schedules_df['OpponentTeam'] == 'BSA Celtic 18B City'])} matches")
    
    # Show preview
    print("\n[PREVIEW]")
    print(schedules_df.to_string(index=False, max_rows=10))
    
    # Check for common opponents with DSX
    print("\n[SEARCH] Looking for potential common opponents...")
    their_opponents = schedules_df['TheirOpponent'].unique()
    
    # Known DSX opponents (from the conversation data)
    dsx_opponents = [
        "Elite FC 2018 Boys Liverpool",
        "Elite FC 2018 Boys Arsenal",
        "Elite FC 2018 Boys Tottenham",
        "Northwest FC 2018B Academy Blue",
        "LFC United 2018B Elite 2",
        "Club Ohio West 18B Academy",
        "Grove City Kids Association 2018B",
        "Columbus United U8B",
        "Barcelona United Elite 18B"
    ]
    
    common = []
    for opp in their_opponents:
        for dsx_opp in dsx_opponents:
            if opp.lower().strip() in dsx_opp.lower().strip() or dsx_opp.lower().strip() in opp.lower().strip():
                common.append((opp, dsx_opp))
    
    if common:
        print(f"   Found {len(common)} potential common opponents!")
        for their, yours in common:
            print(f"   - {their} ≈ {yours}")
    else:
        print("   No direct common opponents found (different divisions)")
    
    print(f"\n[NEXT] Import {output_file} into 'OppSchedules (Paste)' sheet")
    
    return schedules_df


if __name__ == "__main__":
    df = main()

