#!/usr/bin/env python3
"""
Analyze discovered tournament data quality
"""

import pandas as pd

df = pd.read_csv('Ohio_Tournaments_2018_Boys_Discovered_20251102.csv')

print('='*70)
print('DATA QUALITY ANALYSIS - DISCOVERED OHIO TOURNAMENTS')
print('='*70)

print(f'\nTotal teams discovered: {len(df)}')
print(f'Unique teams: {df["Team"].nunique()}')

print(f'\nGames Played (GP) Distribution:')
print(df['GP'].describe())

print(f'\nTeams by Games Played Range:')
gp_ranges = {
    '0 games': len(df[df['GP'] == 0]),
    '1-2 games': len(df[(df['GP'] >= 1) & (df['GP'] <= 2)]),
    '3-5 games': len(df[(df['GP'] >= 3) & (df['GP'] <= 5)]),
    '6-8 games': len(df[(df['GP'] >= 6) & (df['GP'] <= 8)]),
    '9-15 games': len(df[(df['GP'] >= 9) & (df['GP'] <= 15)]),
    '16+ games': len(df[df['GP'] >= 16])
}

for range_name, count in gp_ranges.items():
    pct = (count / len(df)) * 100
    print(f'  {range_name}: {count} teams ({pct:.1f}%)')

print(f'\nSeason Data Quality:')
print(f'  Teams with 6+ games (partial season): {len(df[df["GP"] >= 6])} ({(len(df[df["GP"] >= 6])/len(df)*100):.1f}%)')
print(f'  Teams with 8+ games (good season): {len(df[df["GP"] >= 8])} ({(len(df[df["GP"] >= 8])/len(df)*100):.1f}%)')
print(f'  Teams with 10+ games (full season): {len(df[df["GP"] >= 10])} ({(len(df[df["GP"] >= 10])/len(df)*100):.1f}%)')
print(f'  Teams with 15+ games (very full): {len(df[df["GP"] >= 15])} ({(len(df[df["GP"] >= 15])/len(df)*100):.1f}%)')

print(f'\nBreakdown by Tournament:')
print('='*70)
for event_id in sorted(df['EventID'].unique()):
    event_df = df[df['EventID'] == event_id]
    print(f'\nEvent {event_id}:')
    print(f'  Total teams: {len(event_df)}')
    print(f'  Teams with 6+ games: {len(event_df[event_df["GP"] >= 6])} ({(len(event_df[event_df["GP"] >= 6])/len(event_df)*100):.1f}%)')
    print(f'  Teams with 8+ games: {len(event_df[event_df["GP"] >= 8])} ({(len(event_df[event_df["GP"] >= 8])/len(event_df)*100):.1f}%)')
    print(f'  Teams with 10+ games: {len(event_df[event_df["GP"] >= 10])} ({(len(event_df[event_df["GP"] >= 10])/len(event_df)*100):.1f}%)')
    print(f'  Avg GP: {event_df["GP"].mean():.1f}')
    print(f'  Median GP: {event_df["GP"].median():.1f}')
    print(f'  Max GP: {event_df["GP"].max()}')

print(f'\nAge Group Analysis:')
print('='*70)

# Check for 2018 Boys indicators
df_2018 = df[df['Team'].str.contains('2018|U8|BU08', case=False, na=False)]
df_2017 = df[df['Team'].str.contains('2017|U9|BU09', case=False, na=False)]

print(f'Teams with "2018/U8/BU08" in name: {len(df_2018)}')
print(f'  With 6+ games: {len(df_2018[df_2018["GP"] >= 6])} ({(len(df_2018[df_2018["GP"] >= 6])/len(df_2018)*100):.1f}%)')
print(f'  With 8+ games: {len(df_2018[df_2018["GP"] >= 8])} ({(len(df_2018[df_2018["GP"] >= 8])/len(df_2018)*100):.1f}%)')
print(f'  With 10+ games: {len(df_2018[df_2018["GP"] >= 10])} ({(len(df_2018[df_2018["GP"] >= 10])/len(df_2018)*100):.1f}%)')

print(f'\nTeams with "2017/U9/BU09" in name: {len(df_2017)}')
print(f'  With 6+ games: {len(df_2017[df_2017["GP"] >= 6])} ({(len(df_2017[df_2017["GP"] >= 6])/len(df_2017)*100):.1f}%)')
print(f'  With 8+ games: {len(df_2017[df_2017["GP"] >= 8])} ({(len(df_2017[df_2017["GP"] >= 8])/len(df_2017)*100):.1f}%)')
print(f'  With 10+ games: {len(df_2017[df_2017["GP"] >= 10])} ({(len(df_2017[df_2017["GP"] >= 10])/len(df_2017)*100):.1f}%)')

print(f'\nSample of 2018 Teams with 8+ Games:')
print('='*70)
sample_2018 = df_2018[df_2018['GP'] >= 8][['Team', 'GP', 'W', 'L', 'D', 'PPG', 'StrengthIndex']].head(20)
print(sample_2018.to_string(index=False))

print('\n' + '='*70)
print('SUMMARY')
print('='*70)
print(f'Of {df["Team"].nunique()} unique teams discovered:')
print(f'  - {len(df[df["GP"] >= 6])} have 6+ games (partial season data)')
print(f'  - {len(df[df["GP"] >= 8])} have 8+ games (good season data)')
print(f'  - {len(df[df["GP"] >= 10])} have 10+ games (full season data)')
print(f'\nFor 2018 Boys teams specifically:')
print(f'  - {len(df_2018[df_2018["GP"] >= 6])} have 6+ games')
print(f'  - {len(df_2018[df_2018["GP"] >= 8])} have 8+ games')
print(f'  - {len(df_2018[df_2018["GP"] >= 10])} have 10+ games')

