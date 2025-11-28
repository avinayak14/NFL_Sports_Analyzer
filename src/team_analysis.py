import pandas as pd
import numpy as np

def analyze_teams(pbp_df):
    """
    Analyzes team performance to predict the Super Bowl winner.
    """
    print("Analyzing team performance...")
    
    # Filter for regular season (optional, but usually better for prediction base)
    # pbp_df = pbp_df[pbp_df['season_type'] == 'REG'] # Assuming data might have post-season if late in year
    
    # Offensive EPA
    off_stats = pbp_df.groupby('posteam')['epa'].mean().reset_index().rename(columns={'epa': 'off_epa'})
    
    # Defensive EPA (lower is better)
    def_stats = pbp_df.groupby('defteam')['epa'].mean().reset_index().rename(columns={'epa': 'def_epa', 'defteam': 'team'})
    
    # Merge
    team_stats = off_stats.rename(columns={'posteam': 'team'}).merge(def_stats, on='team')
    
    # Normalize
    team_stats['off_z'] = (team_stats['off_epa'] - team_stats['off_epa'].mean()) / team_stats['off_epa'].std()
    team_stats['def_z'] = (team_stats['def_epa'] - team_stats['def_epa'].mean()) / team_stats['def_epa'].std()
    
    # Prediction Score: Higher Offense is good, Lower Defense is good
    # We negate def_z because negative EPA is good for defense.
    # If def_z is -2 (very good), -(-2) = +2.
    team_stats['prediction_score'] = (0.6 * team_stats['off_z']) + (0.4 * (team_stats['def_z'] * -1))
    
    # Sort by prediction score
    team_rankings = team_stats.sort_values('prediction_score', ascending=False)
    
    return team_rankings
