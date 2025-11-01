"""
Comprehensive Opponents Coverage Analysis
Check data coverage gaps across all tournaments DSX has played
"""

import pandas as pd
import os
from datetime import datetime

def analyze_coverage():
    """Analyze comprehensive opponents coverage"""

    print("=" * 80)
    print("COMPREHENSIVE OPPONENTS COVERAGE ANALYSIS")
    print("=" * 80)

    # 1. Load DSX match history
    try:
        matches = pd.read_csv("DSX_Matches_Fall2025.csv", index_col=False)
        tournaments = matches['Tournament'].dropna().unique()
        print(f"\n[OK] DSX played in {len(tournaments)} tournaments:")
        for tour in sorted(tournaments):
            tour_matches = matches[matches['Tournament'] == tour]
            opp_count = tour_matches['Opponent'].nunique()
            print(f"  - {tour}: {opp_count} opponents")

        total_opponents = matches['Opponent'].nunique()
        print(f"\n[OK] Total unique opponents faced: {total_opponents}")

    except Exception as e:
        print(f"[ERROR] Failed to load match history: {e}")
        return

    # 2. Check division data coverage
    division_files = [
        "OCL_BU08_Stripes_Division_Rankings.csv",
        "OCL_BU08_White_Division_Rankings.csv",
        "OCL_BU08_Stars_Division_Rankings.csv",
        "OCL_BU08_Stars_7v7_Division_Rankings.csv",
        "MVYSA_B09_3_Division_Rankings.csv",
        "Haunted_Classic_B08Orange_Division_Rankings.csv",
        "Haunted_Classic_B08Black_Division_Rankings.csv",
        "CU_Fall_Finale_2025_Division_Rankings.csv",
        "Club_Ohio_Fall_Classic_2025_Division_Rankings.csv",
        "CPL_Fall_2025_Division_Rankings.csv",
    ]

    all_division_teams = set()
    for file in division_files:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file, index_col=False)
                if 'Team' in df.columns:
                    all_division_teams.update(df['Team'].dropna().unique())
            except:
                pass

    print(f"\n[OK] Total teams tracked in division files: {len(all_division_teams)}")

    # 3. Check opponents' opponents coverage
    opp_opp_files = ["Opponents_of_Opponents.csv", "Club_Ohio_Opponents_Opponents.csv"]
    all_opp_opp_teams = set()

    for file in opp_opp_files:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file, index_col=False)
                # Handle different column names
                opp_col = 'Opponent_of_Opponent' if 'Opponent_of_Opponent' in df.columns else 'TheirOpponent'
                if opp_col in df.columns:
                    all_opp_opp_teams.update(df[opp_col].dropna().unique())
            except:
                pass

    print(f"[OK] Total opponents-of-opponents tracked: {len(all_opp_opp_teams)}")

    # 4. Analyze coverage by tournament
    print(f"\n" + "=" * 80)
    print("TOURNAMENT-BY-TOURNAMENT COVERAGE ANALYSIS")
    print("=" * 80)

    coverage_report = []

    for tournament in sorted(tournaments):
        tour_matches = matches[matches['Tournament'] == tournament]
        tour_opponents = set(tour_matches['Opponent'].dropna().unique())

        # Check how many opponents have division data
        opp_with_division = 0
        opp_with_opp_opp = 0

        for opp in tour_opponents:
            # Check division data
            opp_normalized = opp.lower().strip()
            for div_team in all_division_teams:
                if opp_normalized in div_team.lower() or div_team.lower() in opp_normalized:
                    opp_with_division += 1
                    break

            # Check opponents of opponents data
            for opp_opp_team in all_opp_opp_teams:
                if opp_normalized in str(opp_opp_team).lower() or str(opp_opp_team).lower() in opp_normalized:
                    opp_with_opp_opp += 1
                    break

        coverage_report.append({
            'tournament': tournament,
            'opponents': len(tour_opponents),
            'division_coverage': opp_with_division,
            'opp_opp_coverage': opp_with_opp_opp
        })

        print(f"\n{tournament}:")
        print(f"  Opponents: {len(tour_opponents)}")
        print(f"  With division data: {opp_with_division} ({opp_with_division/len(tour_opponents)*100:.1f}%)")
        print(f"  With opponents-of-opponents data: {opp_with_opp_coverage} ({opp_with_opp_coverage/len(tour_opponents)*100:.1f}%)")

    # 5. Overall summary
    total_opp_with_division = sum(r['division_coverage'] for r in coverage_report)
    total_opp_with_opp_opp = sum(r['opp_opp_coverage'] for r in coverage_report)

    print(f"\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Total opponents faced: {total_opponents}")
    print(f"Opponents with division data: {total_opp_with_division} ({total_opp_with_division/total_opponents*100:.1f}%)")
    print(f"Opponents with opponents-of-opponents data: {total_opp_with_opp_coverage} ({total_opp_with_opp_coverage/total_opponents*100:.1f}%)")
    print(f"Teams tracked in division files: {len(all_division_teams)}")
    print(f"Opponents-of-opponents tracked: {len(all_opp_opp_teams)}")

    # 6. Recommendations
    print(f"\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if total_opp_with_division < total_opponents * 0.8:
        print("⚠️  Division data coverage is low. Consider:")
        print("   - Adding more division fetch scripts")
        print("   - Expanding existing division coverage")
        print("   - Creating manual data entry for missing teams")

    if total_opp_with_opp_opp < total_opponents * 0.5:
        print("⚠️  Opponents-of-opponents coverage is low. Consider:")
        print("   - Running opponents-of-opponents scripts for all tournaments")
        print("   - Creating systematic tracking for missing tournaments")
        print("   - Improving GotSport schedule parsing")

    if len(all_division_teams) < 100:
        print("⚠️  Total division teams tracked is low. Consider:")
        print("   - Adding more GotSport divisions to tracking")
        print("   - Including regional leagues and tournaments")
        print("   - Expanding to more age groups for benchmarking")

    print(f"\n[OK] Analysis complete - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")

if __name__ == "__main__":
    analyze_coverage()
