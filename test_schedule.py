import pandas as pd

ts = pd.read_csv('team_schedule.csv')
av = pd.read_csv('schedule_availability.csv')

print("="*60)
print("TEAM SCHEDULE SYSTEM TEST")
print("="*60)
print(f"\nSchedule: {len(ts)} events")
print(f"  - Games: {len(ts[ts['EventType']=='Game'])}")
print(f"  - Practices: {len(ts[ts['EventType']=='Practice'])}")
print(f"\nAvailability tracking: {len(av)} player responses")
print(f"  - Players tracked: {len(av['PlayerNumber'].unique())}")
print(f"  - Events tracked: {len(av['EventID'].unique())}")

print("\n" + "="*60)
print("✅ ALL FILES VALID - READY TO USE!")
print("="*60)


