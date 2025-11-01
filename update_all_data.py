#!/usr/bin/env python3
"""
Comprehensive Data Update Script
Updates all opponent tracking data from all sources
"""

import subprocess
import sys
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and report status"""
    print(f"\n{'='*70}")
    print(f"[UPDATING] {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"[OK] {description} - Complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} - Failed")
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print(f"[SKIP] {script_name} not found")
        return False

def main():
    print("\n" + "="*70)
    print("DSX OPPONENT TRACKER - COMPREHENSIVE DATA UPDATE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print("="*70)
    
    updates = []
    
    # 1. Update OCL Division Standings (GotSport)
    updates.append(run_script(
        "fetch_gotsport_division.py",
        "OCL BU08 Stripes Division Rankings"
    ))
    
    # 1b. Update OCL White Division (Club Ohio West)
    updates.append(run_script(
        "fetch_gotsport_white_division.py",
        "OCL BU08 White Division Rankings (Club Ohio West)"
    ))
    
    # 1c. Update OCL Stars 5v5 Division
    updates.append(run_script(
        "fetch_gotsport_stars_division.py",
        "OCL BU08 Stars 5v5 Division Rankings"
    ))
    
    # 1d. Update OCL Stars 7v7 Division (Elite FC Arsenal)
    updates.append(run_script(
        "fetch_gotsport_stars_7v7.py",
        "OCL BU08 Stars 7v7 Division Rankings (Elite FC Arsenal)"
    ))
    
    # 2. Update BSA Celtic Schedules (MVYSA)
    updates.append(run_script(
        "fetch_bsa_celtic.py",
        "BSA Celtic Team Schedules (United & City)"
    ))
    
    # 2b. Update MVYSA B09-3 Division Standings (BSA Celtic Division)
    updates.append(run_script(
        "fetch_mvysa_division.py",
        "MVYSA B09-3 Division Rankings (BSA Celtic Division)"
    ))
    
    # 2c. Add actual goals to MVYSA Division (from schedule data)
    updates.append(run_script(
        "update_mvysa_division_with_goals.py",
        "MVYSA Division Goals (Calculate from BSA Celtic Schedules)"
    ))
    
    # 3. Update All Division Team Schedules
    updates.append(run_script(
        "fetch_division_schedules.py",
        "OCL Division Team Schedules (Common Opponents)"
    ))
    
    # 4. Analyze Upcoming Opponents
    updates.append(run_script(
        "analyze_upcoming_opponents.py",
        "Upcoming Opponent Analysis & Scouting Reports"
    ))
    
    # 5. Update CU Fall Finale Tournament Data
    updates.append(run_script(
        "fetch_cu_fall_finale.py",
        "CU Fall Finale 2025 Tournament Data"
    ))
    
    # 5b. Update OCL BU09 7v7 Stripes Division (2017 Boys - Benchmarking Only)
    updates.append(run_script(
        "fetch_ocl_bu09_7v7_stripes.py",
        "OCL BU09 7v7 Stripes - 2017 Boys Benchmarking Data (Not in main rankings)"
    ))
    
    # 5b. Update Club Ohio Fall Classic Tournament Data
    updates.append(run_script(
        "fetch_club_ohio_fall_classic.py",
        "Club Ohio Fall Classic 2025 Tournament Data"
    ))
    
    # 5c. Update OCL Stripes Live Results
    updates.append(run_script(
        "fetch_ocl_stripes_results.py",
        "OCL Stripes Fall 2025 Live Results"
    ))
    
    # 6. Update Common Opponent Analysis
    updates.append(run_script(
        "analyze_common_opponents.py",
        "Common Opponent Matrix & Comparisons"
    ))
    
    # 7. Update Opponents' Opponents Data (Complete Dataset)
    updates.append(run_script(
        "fetch_opponent_opponents.py",
        "Opponents' Opponents - Complete Dataset Builder"
    ))

    # 8. Update Club Ohio Opponents' Opponents Data
    updates.append(run_script(
        "fetch_club_ohio_opponents_opponents.py",
        "Club Ohio Opponents' Opponents - Tournament-Specific"
    ))

    # 9. Analyze Comprehensive Coverage
    updates.append(run_script(
        "comprehensive_opponents_coverage.py",
        "Comprehensive Opponents Coverage Analysis"
    ))

    # Print Summary
    print("\n" + "="*70)
    print("UPDATE SUMMARY")
    print("="*70)

    successful = sum(updates)
    total = len(updates)

    print(f"\nCompleted: {successful}/{total} update tasks")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")

    if successful == total:
        print("\n[SUCCESS] All data sources updated successfully!")
        print("\nNext Steps:")
        print("  1. Review updated data in dashboard: python -m streamlit run dsx_dashboard.py")
        print("  2. Check scouting reports for upcoming games")
        print("  3. Push to GitHub: git add . && git commit -m 'Data update' && git push")
    else:
        print(f"\n[WARNING] {total - successful} update(s) failed or skipped")
        print("Check error messages above for details")

    print("="*70 + "\n")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

