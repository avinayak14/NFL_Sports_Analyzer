
import nfl_data_py as nfl
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

print("Checking PBP 2025...")
try:
    pbp = nfl.import_pbp_data([2025])
    print(f"PBP 2025 Loaded. Rows: {len(pbp)}")
except Exception as e:
    print(f"PBP Failed: {e}")

print("\nChecking Schedule 2025...")
try:
    schedule = nfl.import_schedules([2025])
    print(f"Schedule Loaded. Rows: {len(schedule)}")
    w17 = schedule[schedule['week'] == 17]
    print(f"Week 17 games found: {len(w17)}")
    print(w17[['home_team', 'away_team']].head())
except Exception as e:
    print(f"Schedule Failed: {e}")
