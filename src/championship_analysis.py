import nfl_data_py as nfl
import pandas as pd
import ssl

# Fix SSL issue for mac
ssl._create_default_https_context = ssl._create_unverified_context

def get_roster_config():
    """
    Returns the user's specific roster configuration.
    """
    return {
        'QB': ['B.Purdy'],
        'RB': ['C.McCaffrey', 'A.Jeanty', 'T.Henderson', 'T.Tracy'],
        'WR': ['J.Smith-Njigba', 'C.Olave'],
        'TE': ['T.McBride'],
        'K': ['C.Santos'],
        'DST': ['Buf'] # Abbreviation for Bills
    }

def load_data():
    """
    Loads 2025 Play-by-Play and Schedule data.
    """
    print("Loading 2025 Data...")
    pbp = nfl.import_pbp_data([2025])
    schedule = nfl.import_schedules([2025])
    return pbp, schedule

def analyze_recent_form(pbp, player_names, weeks=5):
    """
    Calculates EPA and Success Rate for the last N weeks for the given players.
    """
    # Get max week
    current_week = pbp['week'].max()
    start_week = max(1, current_week - weeks + 1)
    
    print(f"Analyzing form from Week {start_week} to {current_week}...")
    
    recent_data = pbp[pbp['week'] >= start_week]
    
    player_stats = []
    
    for player in player_names:
        # Check as passer
        pass_stats = recent_data[(recent_data['passer_player_name'] == player) & (recent_data['play_type'] == 'pass')]
        # Check as rusher
        rush_stats = recent_data[(recent_data['rusher_player_name'] == player) & (recent_data['play_type'] == 'run')]
        # Check as receiver
        rec_stats = recent_data[(recent_data['receiver_player_name'] == player) & (recent_data['play_type'] == 'pass')]
        
        # Combine distinct play IDs to get total involvement
        # Note: receiver plays are subset of pass plays, but we care about the specific player's EPA
        
        # Calculate Weighted EPA
        total_plays = len(pass_stats) + len(rush_stats) + len(rec_stats)
        
        if total_plays == 0:
            print(f"No recent data for {player}")
            continue
            
        avg_epa = 0
        success_rate = 0
        
        # Aggregate stats
        # Simply average EPA across all opportunities (Pass + Rush + Target)
        # For receivers, we use their EPA on targets
        
        # Collect all relevant EPA values
        epas = pd.concat([
            pass_stats['epa'],
            rush_stats['epa'],
            rec_stats['epa']
        ])
        
        successes = pd.concat([
            pass_stats['success'],
            rush_stats['success'],
            rec_stats['success']
        ])
        
        avg_epa = epas.mean()
        success_rate = successes.mean()
        
        team = None
        if not pass_stats.empty: team = pass_stats['posteam'].iloc[0]
        elif not rush_stats.empty: team = rush_stats['posteam'].iloc[0]
        elif not rec_stats.empty: team = rec_stats['posteam'].iloc[0]
        
        player_stats.append({
            'player': player,
            'team': team,
            'avg_epa': avg_epa,
            'success_rate': success_rate,
            'usage_count': total_plays
        })
        
    return pd.DataFrame(player_stats)

def get_week_17_opponents(schedule, player_teams):
    """
    Finds the opponent for Week 17 for each player's team.
    """
    w17 = schedule[schedule['week'] == 17]
    matchups = {}
    
    for team in player_teams:
        if not team: continue
        
        # Find game where team is home or away
        game = w17[(w17['home_team'] == team) | (w17['away_team'] == team)]
        if game.empty:
            matchups[team] = 'BYE' # Should not happen in week 17 usually
            continue
            
        row = game.iloc[0]
        if row['home_team'] == team:
            matchups[team] = row['away_team']
        else:
            matchups[team] = row['home_team']
            
    return matchups

def analyze_matchup_difficulty(pbp, opponent, position):
    """
    Calculates how the opponent defense performs against this position.
    Returns Avg EPA allowed. Lower is harder for offense.
    """
    # Simply get avg EPA allowed by this team when on defense
    def_plays = pbp[pbp['defteam'] == opponent]
    
    if position == 'QB':
        # EPA on pass plays
        return def_plays[def_plays['play_type'] == 'pass']['epa'].mean()
    elif position == 'RB':
        # EPA on run plays
        return def_plays[def_plays['play_type'] == 'run']['epa'].mean()
    elif position in ['WR', 'TE']:
        # EPA on pass plays (general secondary strength)
        return def_plays[def_plays['play_type'] == 'pass']['epa'].mean()
        
    return 0

def main():
    try:
        pbp, schedule = load_data()
        roster = get_roster_config()
        
        # Flatten roster for easy iteration
        all_players = []
        player_pos = {}
        for pos, names in roster.items():
            for name in names:
                all_players.append(name)
                player_pos[name] = pos
        
        # 1. Recent Form
        form_df = analyze_recent_form(pbp, all_players)
        
        if form_df.empty:
            print("No player data found to analyze.")
            return

        # 2. Matchups
        unique_teams = form_df['team'].unique()
        opponents = get_week_17_opponents(schedule, unique_teams)
        
        results = []
        
        print("\n--- Championship Matchup Analysis ---\n")
        
        for _, row in form_df.iterrows():
            player = row['player']
            team = row['team']
            pos = player_pos.get(player, 'FLEX')
            
            opp = opponents.get(team, 'N/A')
            
            # Defense strength (EPA allowed)
            # Higher EPA allowed = Easier matchup
            def_epa = analyze_matchup_difficulty(pbp, opp, pos)
            
            # Score Calculation (Primitive)
            # Form (0.6) + Matchup (0.4)
            # Normalize inputs roughly? 
            # EPA ranges -0.5 to 0.5 roughly.
            
            score = (row['avg_epa'] * 0.7) + (def_epa * 0.3)
            
            results.append({
                'Player': player,
                'Position': pos,
                'Team': team,
                'Opponent': opp,
                'Form_EPA': round(row['avg_epa'], 3),
                'Success_Rate': round(row['success_rate'], 3),
                'Opp_EPA_Allowed': round(def_epa, 3),
                'Composite_Score': round(score, 3)
            })
            
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('Composite_Score', ascending=False)
        
        print(results_df.to_string(index=False))
        
        # Recommendation Logic
        print("\n--- RECOMMENDATIONS ---")
        print("Based on Composite Score (High = Better Start)\n")
        
        # RB Choice
        rbs = results_df[results_df['Position'] == 'RB']
        print("Running Backs:")
        print(rbs[['Player', 'Opponent', 'Composite_Score']].to_string(index=False))
        
        # WR Choice
        wrs = results_df[results_df['Position'] == 'WR']
        print("\nWide Receivers:")
        print(wrs[['Player', 'Opponent', 'Composite_Score']].to_string(index=False))
        
        # Flex Candidates (RB + WR + TE)
        flex = results_df[results_df['Position'].isin(['RB', 'WR', 'TE'])]
        print("\nFlex Rankings (All Eligible):")
        print(flex[['Player', 'Position', 'Composite_Score']].head(5).to_string(index=False))

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
