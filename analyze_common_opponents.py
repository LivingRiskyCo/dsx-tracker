"""
Complete Common Opponent Analysis
Compares DSX performance vs division teams through common opponents
"""

import pandas as pd
from collections import defaultdict

def load_dsx_matches():
    """Load DSX match data"""
    # Hardcoded DSX match data from your season
    matches = [
        {"Date": "2025-08-30", "Opponent": "Blast FC Soccer Academy Blast FC 2018B", "GF": 3, "GA": 5, "Result": "L"},
        {"Date": "2025-09-01", "Opponent": "Polaris Soccer Club Polaris SC 18B Navy", "GF": 1, "GA": 5, "Result": "L"},
        {"Date": "2025-09-07", "Opponent": "Columbus Force SC CE 2018B Net Ninjas", "GF": 11, "GA": 0, "Result": "W"},
        {"Date": "2025-09-08", "Opponent": "Sporting Columbus Sporting Columbus Boys 2018 II", "GF": 5, "GA": 5, "Result": "D"},
        {"Date": "2025-09-14", "Opponent": "Delaware Knights Delaware Knights 2018 BU08", "GF": 7, "GA": 2, "Result": "W"},
        {"Date": "2025-09-15", "Opponent": "Johnstown FC Johnstown FC 2018 Boys", "GF": 4, "GA": 0, "Result": "W"},
        {"Date": "2025-09-21", "Opponent": "Blast FC Soccer Academy Blast FC 2018B", "GF": 0, "GA": 3, "Result": "L"},
        {"Date": "2025-09-22", "Opponent": "Polaris Soccer Club Polaris SC 18B Navy", "GF": 2, "GA": 4, "Result": "L"},
        {"Date": "2025-09-28", "Opponent": "Columbus Force SC CE 2018B Net Ninjas", "GF": 1, "GA": 1, "Result": "D"},
        {"Date": "2025-09-29", "Opponent": "Sporting Columbus Sporting Columbus Boys 2018 II", "GF": 0, "GA": 13, "Result": "L"},
        {"Date": "2025-10-05", "Opponent": "Delaware Knights Delaware Knights 2018 BU08", "GF": 8, "GA": 10, "Result": "L"},
        {"Date": "2025-10-06", "Opponent": "Columbus Force SC CE 2018B Net Ninjas", "GF": 8, "GA": 13, "Result": "L"},
    ]
    return pd.DataFrame(matches)


def analyze_common_opponents():
    """Analyze common opponents between DSX and division teams"""
    
    print("=" * 70)
    print("COMMON OPPONENT ANALYSIS")
    print("=" * 70)
    print()
    
    # Load DSX matches
    dsx_matches = load_dsx_matches()
    
    # Load division standings
    try:
        division = pd.read_csv("OCL_BU08_Stripes_Division_with_DSX.csv")
    except:
        print("[ERROR] Could not load division data. Run fetch_gotsport_division.py first.")
        return
    
    # DSX opponents (teams we've played)
    dsx_opponents = set(dsx_matches['Opponent'].unique())
    
    print(f"DSX has played {len(dsx_opponents)} teams in the division:")
    for opp in sorted(dsx_opponents):
        # Shortened name
        short_name = opp.split()[-2] if len(opp.split()) > 2 else opp
        wins = len(dsx_matches[(dsx_matches['Opponent'] == opp) & (dsx_matches['Result'] == 'W')])
        draws = len(dsx_matches[(dsx_matches['Opponent'] == opp) & (dsx_matches['Result'] == 'D')])
        losses = len(dsx_matches[(dsx_matches['Opponent'] == opp) & (dsx_matches['Result'] == 'L')])
        gf = dsx_matches[dsx_matches['Opponent'] == opp]['GF'].sum()
        ga = dsx_matches[dsx_matches['Opponent'] == opp]['GA'].sum()
        print(f"  - {short_name}: {wins}-{draws}-{losses} ({gf}-{ga})")
    
    print()
    print("=" * 70)
    print("HEAD-TO-HEAD SUMMARY")
    print("=" * 70)
    print()
    
    # Analyze head-to-head
    h2h_summary = []
    
    for _, team_row in division.iterrows():
        team = team_row['Team'].strip()
        
        # Skip DSX itself
        if 'DSX' in team:
            continue
        
        # Check if we played this team
        if team in dsx_opponents:
            team_matches = dsx_matches[dsx_matches['Opponent'] == team]
            wins = len(team_matches[team_matches['Result'] == 'W'])
            draws = len(team_matches[team_matches['Result'] == 'D'])
            losses = len(team_matches[team_matches['Result'] == 'L'])
            gf = team_matches['GF'].sum()
            ga = team_matches['GA'].sum()
            gd = gf - ga
            
            # Points
            points = wins * 3 + draws
            games = len(team_matches)
            ppg = points / games if games > 0 else 0
            
            h2h_summary.append({
                'Opponent': team.split()[-2] if len(team.split()) > 2 else team,
                'Full_Name': team,
                'Rank': int(team_row['Rank']),
                'TheirSI': team_row['StrengthIndex'],
                'Games': games,
                'W-D-L': f"{wins}-{draws}-{losses}",
                'GF': gf,
                'GA': ga,
                'GD': gd,
                'Pts': points,
                'PPG': ppg,
                'Analysis': ''
            })
    
    # Sort by rank
    h2h_summary = sorted(h2h_summary, key=lambda x: x['Rank'])
    
    # Print table
    print(f"{'Rank':<6}{'Opponent':<30}{'W-D-L':<10}{'GF-GA':<10}{'GD':<6}{'PPG':<6}{'Analysis'}")
    print("-" * 70)
    
    for h2h in h2h_summary:
        # Analysis
        if h2h['PPG'] >= 2.0:
            analysis = "Dominated [OK]"
        elif h2h['PPG'] >= 1.5:
            analysis = "Strong"
        elif h2h['PPG'] >= 1.0:
            analysis = "Competitive"
        elif h2h['PPG'] > 0:
            analysis = "Struggled"
        else:
            analysis = "Overmatched"
        
        print(f"#{h2h['Rank']:<5}{h2h['Opponent']:<30}{h2h['W-D-L']:<10}{h2h['GF']}-{h2h['GA']:<7}{h2h['GD']:+3}   {h2h['PPG']:.2f}  {analysis}")
    
    print()
    print("=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print()
    
    # Calculate insights
    vs_top_3 = [h for h in h2h_summary if h['Rank'] <= 3]
    vs_bottom_3 = [h for h in h2h_summary if h['Rank'] >= 4]
    
    if vs_top_3:
        top_3_ppg = sum(h['PPG'] for h in vs_top_3) / len(vs_top_3)
        print(f"VS TOP 3 TEAMS:")
        print(f"  Average PPG: {top_3_ppg:.2f}")
        print(f"  Total record: {sum(h['GF'] for h in vs_top_3)}-{sum(h['GA'] for h in vs_top_3)}")
        if top_3_ppg < 0.5:
            print(f"  -> Big gap to overcome")
        elif top_3_ppg < 1.0:
            print(f"  -> Competitive but need improvement")
        else:
            print(f"  -> Holding your own! [OK]")
        print()
    
    if vs_bottom_3:
        bottom_3_ppg = sum(h['PPG'] for h in vs_bottom_3) / len(vs_bottom_3)
        print(f"VS BOTTOM 3 TEAMS:")
        print(f"  Average PPG: {bottom_3_ppg:.2f}")
        print(f"  Total record: {sum(h['GF'] for h in vs_bottom_3)}-{sum(h['GA'] for h in vs_bottom_3)}")
        if bottom_3_ppg >= 2.0:
            print(f"  -> Dominant! [OK]")
        elif bottom_3_ppg >= 1.5:
            print(f"  -> Strong performance")
        elif bottom_3_ppg >= 1.0:
            print(f"  -> Earning points")
        else:
            print(f"  -> Opportunity for improvement")
        print()
    
    # Overall trend
    print(f"OVERALL TREND:")
    total_ppg = sum(h['PPG'] for h in h2h_summary) / len(h2h_summary) if h2h_summary else 0
    print(f"  Average PPG across all opponents: {total_ppg:.2f}")
    
    if total_ppg >= 1.5:
        print(f"  -> Strong season performance [OK]")
    elif total_ppg >= 1.0:
        print(f"  -> Middle-of-pack, room to grow")
    else:
        print(f"  -> Challenging season, focus on fundamentals")
    
    print()
    print("=" * 70)
    print("COMMON OPPONENT OPPORTUNITIES")
    print("=" * 70)
    print()
    print("To enable true common opponent analysis, we need schedules for:")
    print()
    
    other_teams = division[~division['Team'].str.contains('DSX', na=False)]['Team'].tolist()
    for i, team in enumerate(other_teams, 1):
        short_name = team.split()[-2] if len(team.split()) > 2 else team
        print(f"  {i}. {short_name}")
        print(f"     -> Find their schedule on GotSport")
        print(f"     -> Compare: Who did THEY play that's NOT in our division?")
        print(f"     -> If they played Team X with result A, and DSX also played Team X with result B")
        print(f"     -> We can calculate: DSX performed BETTER/WORSE than {short_name} vs common opponent Team X")
        print()
    
    print("=" * 70)
    print("WHY COMMON OPPONENTS MATTER")
    print("=" * 70)
    print()
    print("Example scenario:")
    print("  - DSX played 'Ohio United' (not in division) and won 3-1")
    print("  - Blast FC also played 'Ohio United' and won 8-0")
    print("  -> This suggests Blast FC is significantly stronger than DSX")
    print()
    print("  - DSX played 'Westerville Knights' and lost 2-4")
    print("  - Delaware Knights played 'Westerville Knights' and lost 1-7")
    print("  -> This suggests DSX performed BETTER than Delaware vs same opponent")
    print()
    print("This gives us a more accurate strength comparison than just division records!")
    print()
    
    # Save CSV
    if h2h_summary:
        df_h2h = pd.DataFrame(h2h_summary)
        df_h2h.to_csv("DSX_Head_to_Head_Analysis.csv", index=False)
        print("[OK] Saved head-to-head analysis to DSX_Head_to_Head_Analysis.csv")
        print()


if __name__ == "__main__":
    analyze_common_opponents()

