"""
Fix Opponent Tracking - Update with DSX's ACTUAL opponents
Not the OCL division teams (those are just benchmarks)
"""

import pandas as pd

# Load actual DSX matches
matches = pd.read_csv("DSX_Matches_Fall2025.csv")

print("=" * 70)
print("DSX ACTUAL OPPONENTS - Fall 2025")
print("=" * 70)
print()

# Calculate summary stats
summary = matches.groupby('Opponent').agg({
    'Opponent': 'count',  # GP
    'Points': 'sum',
    'GF': 'sum',
    'GA': 'sum',
    'GoalDiff': 'sum'
}).rename(columns={'Opponent': 'GP'})

# Calculate record (W-D-L)
records = []
for opp in matches['Opponent'].unique():
    opp_matches = matches[matches['Opponent'] == opp]
    wins = (opp_matches['Outcome'] == 'W').sum()
    draws = (opp_matches['Outcome'] == 'D').sum()
    losses = (opp_matches['Outcome'] == 'L').sum()
    gp = len(opp_matches)
    gf = opp_matches['GF'].sum()
    ga = opp_matches['GA'].sum()
    gd = gf - ga
    pts = opp_matches['Points'].sum()
    ppg = pts / gp
    
    records.append({
        'Opponent': opp,
        'GP': gp,
        'W': wins,
        'D': draws,
        'L': losses,
        'Record': f"{wins}-{draws}-{losses}",
        'GF': gf,
        'GA': ga,
        'GD': gd,
        'Pts': pts,
        'PPG': ppg
    })

df = pd.DataFrame(records).sort_values('PPG', ascending=False)

print("DSX Record vs Each Opponent:")
print()
print(f"{'Opponent':<45} {'Record':<10} {'GF-GA':<8} {'GD':<6} {'PPG':<6}")
print("-" * 80)

for _, row in df.iterrows():
    opp_short = row['Opponent'][:40] if len(row['Opponent']) > 40 else row['Opponent']
    print(f"{opp_short:<45} {row['Record']:<10} {row['GF']}-{row['GA']:<6} {row['GD']:+4}   {row['PPG']:.2f}")

print()
print("=" * 70)
print("SEASON SUMMARY")
print("=" * 70)
print()

total_gp = len(matches)
total_w = (matches['Outcome'] == 'W').sum()
total_d = (matches['Outcome'] == 'D').sum()
total_l = (matches['Outcome'] == 'L').sum()
total_gf = matches['GF'].sum()
total_ga = matches['GA'].sum()
total_gd = total_gf - total_ga
total_pts = matches['Points'].sum()
total_ppg = total_pts / total_gp

print(f"Games Played: {total_gp}")
print(f"Record: {total_w}-{total_d}-{total_l} (W-D-L)")
print(f"Goals: {total_gf}-{total_ga} (GD: {total_gd:+})")
print(f"Points: {total_pts} (PPG: {total_ppg:.2f})")
print(f"GF/Game: {total_gf/total_gp:.2f}")
print(f"GA/Game: {total_ga/total_gp:.2f}")
print(f"GD/Game: {total_gd/total_gp:+.2f}")
print()

# Save opponent summary
df.to_csv("DSX_Actual_Opponents.csv", index=False)
print("[OK] Saved to DSX_Actual_Opponents.csv")
print()

print("=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
print()

# Best performances
best = df.head(3)
print("STRONGEST PERFORMANCES:")
for _, row in best.iterrows():
    print(f"  vs {row['Opponent']}: {row['Record']} (PPG: {row['PPG']:.2f})")
print()

# Toughest opponents
worst = df.tail(3)
print("TOUGHEST OPPONENTS:")
for _, row in worst.iterrows():
    print(f"  vs {row['Opponent']}: {row['Record']} (PPG: {row['PPG']:.2f})")
print()

# Upcoming opponents
print("=" * 70)
print("UPCOMING GAMES (From your schedule)")
print("=" * 70)
print()
print("Oct 18: BSA Celtic 18B United")
print("Oct 19: Club Ohio West 18B Academy")
print("Nov 01: BSA Celtic 18B City")
print()
print("Use fetch_bsa_celtic.py to get their recent results!")
print()

