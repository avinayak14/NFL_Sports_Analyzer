import nfl_data_py as nfl
import pandas as pd
import os

def load_data(years=[2024]):
    """
    Loads play-by-play data for the specified years.
    """
    print(f"Loading data for years: {years}...")
    try:
        pbp = nfl.import_pbp_data(years)
        print("Data loaded successfully.")
        return pbp
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def load_roster(years=[2024]):
    """
    Loads roster data to identify player positions.
    """
    print(f"Loading roster for years: {years}...")
    try:
        roster = nfl.import_seasonal_rosters(years)
        return roster
    except Exception as e:
        print(f"Error loading roster: {e}")
        return None

if __name__ == "__main__":
    # Test the loader
    df = load_data()
    if df is not None:
        print(df.head())
