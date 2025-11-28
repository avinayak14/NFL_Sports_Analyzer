import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_top_players(top_10_df, output_dir='output'):
    """
    Plots a bar chart of the top 10 most impressive players.
    """
    plt.figure(figsize=(12, 8))
    sns.set_theme(style="whitegrid")
    
    # Create bar plot
    ax = sns.barplot(
        x='impressiveness_score', 
        y='player_name', 
        data=top_10_df, 
        hue='position', 
        dodge=False,
        palette='viridis'
    )
    
    plt.title('Top 10 Most Impressive NFL Players (2024)', fontsize=16)
    plt.xlabel('Impressiveness Score (Composite EPA & Efficiency)', fontsize=12)
    plt.ylabel('Player Name', fontsize=12)
    
    # Save
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/top_10_players.png')
    plt.close()

def plot_qb_efficiency(qb_stats, output_dir='output'):
    """
    Plots QB EPA/play vs CPOE.
    """
    plt.figure(figsize=(12, 8))
    sns.set_theme(style="whitegrid")
    
    # Scatter plot
    ax = sns.scatterplot(
        x='cpoe', 
        y='epa', 
        data=qb_stats, 
        s=100, 
        hue='passer_player_name', # Just to color, legend might be too big
        legend=False
    )
    
    # Add labels for top QBs
    for i, point in qb_stats.iterrows():
        if point['impressiveness_score'] > 1.0 or point['passer_player_name'] in ['P.Mahomes', 'J.Allen', 'L.Jackson', 'J.Burrow']:
            ax.text(point['cpoe']+0.1, point['epa'], point['passer_player_name'], fontsize=9)
            
    plt.title('QB Efficiency: EPA/Play vs CPOE (2024)', fontsize=16)
    plt.xlabel('Completion % Over Expected (CPOE)', fontsize=12)
    plt.ylabel('Expected Points Added (EPA) per Play', fontsize=12)
    
    # Add quadrants
    plt.axhline(y=qb_stats['epa'].mean(), color='r', linestyle='--')
    plt.axvline(x=qb_stats['cpoe'].mean(), color='r', linestyle='--')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/qb_efficiency.png')
    plt.close()

def plot_team_tiers(team_stats, output_dir='output'):
    """
    Plots Team Offense EPA vs Defense EPA.
    """
    plt.figure(figsize=(12, 8))
    sns.set_theme(style="whitegrid")
    
    # Scatter plot
    # Note: Invert Y axis for Defense? No, let's keep EPA as is but label it.
    # Actually, standard is usually: X=Offense, Y=Defense (reversed).
    
    ax = sns.scatterplot(
        x='off_epa', 
        y='def_epa', 
        data=team_stats, 
        s=100
    )
    
    # Add labels
    for i, point in team_stats.iterrows():
        ax.text(point['off_epa']+0.005, point['def_epa'], point['team'], fontsize=9)
        
    plt.title('Team Tiers: Offense vs Defense EPA (2024)', fontsize=16)
    plt.xlabel('Offensive EPA/Play (Higher is Better)', fontsize=12)
    plt.ylabel('Defensive EPA/Play (Lower is Better)', fontsize=12)
    
    # Invert Y axis so top-right is best (Good Offense, Good Defense)? 
    # No, usually Top-Right is Good Offense, Bad Defense.
    # Let's Invert Y axis so that "Up" is "Good Defense" (Lower EPA).
    plt.gca().invert_yaxis()
    
    # Add quadrants
    plt.axhline(y=team_stats['def_epa'].mean(), color='r', linestyle='--')
    plt.axvline(x=team_stats['off_epa'].mean(), color='r', linestyle='--')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/team_tiers.png')
    plt.close()
