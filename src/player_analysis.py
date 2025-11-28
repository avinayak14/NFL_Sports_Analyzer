import pandas as pd
import numpy as np

def analyze_players(pbp_df, roster_df):
    """
    Analyzes player performance to determine the most impressive players.
    """
    print("Analyzing player performance...")
    
    # Filter for relevant plays (passes and runs)
    plays = pbp_df[pbp_df['play_type'].isin(['pass', 'run'])]
    
    # --- QB Analysis ---
    # Filter for QBs with at least 100 plays
    qb_stats = plays.groupby(['passer_player_id', 'passer_player_name']).agg({
        'epa': 'mean',
        'cpoe': 'mean',
        'play_id': 'count',
        'posteam': 'first'
    }).reset_index()
    
    qb_stats = qb_stats[qb_stats['play_id'] >= 100].copy()
    
    # Normalize metrics
    qb_stats['epa_z'] = (qb_stats['epa'] - qb_stats['epa'].mean()) / qb_stats['epa'].std()
    qb_stats['cpoe_z'] = (qb_stats['cpoe'] - qb_stats['cpoe'].mean()) / qb_stats['cpoe'].std()
    
    # Composite score for QBs (60% EPA, 40% CPOE)
    qb_stats['impressiveness_score'] = (0.6 * qb_stats['epa_z']) + (0.4 * qb_stats['cpoe_z'])
    qb_stats['position'] = 'QB'
    
    # --- RB/WR/TE Analysis ---
    # Group by receiver/rusher
    # Note: 'fantasy_player_id' or similar might be better, but we'll use rusher/receiver IDs
    
    # Rusher stats
    run_plays = plays[plays['play_type'] == 'run']
    rb_stats = run_plays.groupby(['rusher_player_id', 'rusher_player_name']).agg({
        'epa': 'mean',
        'success': 'mean',
        'play_id': 'count',
        'posteam': 'first'
    }).reset_index()
    rb_stats = rb_stats[rb_stats['play_id'] >= 50].copy() # Lower threshold for RBs
    
    # Receiver stats
    pass_plays = plays[plays['play_type'] == 'pass']
    wr_stats = pass_plays.groupby(['receiver_player_id', 'receiver_player_name']).agg({
        'epa': 'mean',
        'xyac_epa': 'mean', # Expected YAC EPA
        'play_id': 'count',
        'posteam': 'first'
    }).reset_index()
    wr_stats = wr_stats[wr_stats['play_id'] >= 30].copy() # Targets
    
    # Normalize and score RBs
    rb_stats['epa_z'] = (rb_stats['epa'] - rb_stats['epa'].mean()) / rb_stats['epa'].std()
    rb_stats['success_z'] = (rb_stats['success'] - rb_stats['success'].mean()) / rb_stats['success'].std()
    rb_stats['impressiveness_score'] = (0.5 * rb_stats['epa_z']) + (0.5 * rb_stats['success_z'])
    rb_stats['position'] = 'RB' # Simplified, could check roster for actual pos
    
    # Normalize and score WRs
    wr_stats['epa_z'] = (wr_stats['epa'] - wr_stats['epa'].mean()) / wr_stats['epa'].std()
    # Handle missing xyac_epa
    wr_stats['xyac_epa'] = wr_stats['xyac_epa'].fillna(0)
    wr_stats['xyac_z'] = (wr_stats['xyac_epa'] - wr_stats['xyac_epa'].mean()) / wr_stats['xyac_epa'].std()
    wr_stats['impressiveness_score'] = (0.6 * wr_stats['epa_z']) + (0.4 * wr_stats['xyac_z'])
    wr_stats['position'] = 'WR/TE'
    
    # Combine all
    # Rename columns to match
    qb_final = qb_stats[['passer_player_name', 'position', 'impressiveness_score', 'posteam']].rename(columns={'passer_player_name': 'player_name'})
    rb_final = rb_stats[['rusher_player_name', 'position', 'impressiveness_score', 'posteam']].rename(columns={'rusher_player_name': 'player_name'})
    wr_final = wr_stats[['receiver_player_name', 'position', 'impressiveness_score', 'posteam']].rename(columns={'receiver_player_name': 'player_name'})
    
    all_players = pd.concat([qb_final, rb_final, wr_final], ignore_index=True)
    
    # Sort by score
    top_10 = all_players.sort_values('impressiveness_score', ascending=False).head(10)
    
    return top_10, qb_stats, all_players
