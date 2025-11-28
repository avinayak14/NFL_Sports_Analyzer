import sys
import os
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src import data_loader, player_analysis, team_analysis, visualizer

def generate_report(top_players, team_rankings, output_file='ANALYSIS_REPORT.md'):
    """
    Generates a markdown report with the analysis results.
    """
    print("Generating report...")
    
    predicted_winner = team_rankings.iloc[0]
    
    with open(output_file, 'w') as f:
        f.write("# NFL 2024 Quantitative Analysis Report\n\n")
        
        f.write("## Top 10 Most Impressive Players\n")
        f.write("This ranking is based on a composite score of Advanced Metrics:\n")
        f.write("- **QBs**: EPA/Play (60%) + CPOE (40%)\n")
        f.write("- **RBs**: EPA/Play (50%) + Success Rate (50%)\n")
        f.write("- **WRs/TEs**: EPA/Target (60%) + Expected YAC EPA (40%)\n\n")
        
        f.write("| Rank | Player | Position | Team | Impressiveness Score |\n")
        f.write("|---|---|---|---|---|\n")
        for i, (index, row) in enumerate(top_players.iterrows()):
            f.write(f"| {i+1} | {row['player_name']} | {row['position']} | {row['posteam']} | {row['impressiveness_score']:.2f} |\n")
        
        f.write("\n![Top 10 Players](output/top_10_players.png)\n\n")
        
        f.write("## Super Bowl Prediction Thesis\n")
        f.write(f"### Predicted Winner: **{predicted_winner['team']}**\n\n")
        
        f.write("**Quantitative Reasoning:**\n")
        f.write("The prediction model values a balanced team with a slight bias towards elite offense.\n")
        f.write(f"- **Offensive EPA/Play**: {predicted_winner['off_epa']:.3f} (Z-Score: {predicted_winner['off_z']:.2f})\n")
        f.write(f"- **Defensive EPA/Play**: {predicted_winner['def_epa']:.3f} (Z-Score: {predicted_winner['def_z']:.2f})\n")
        f.write(f"- **Composite Prediction Score**: {predicted_winner['prediction_score']:.2f}\n\n")
        
        f.write("Historically, teams with top-tier efficiency in both passing offense and pass defense correlate strongly with Super Bowl success.\n")
        f.write(f"The **{predicted_winner['team']}** currently exhibit the best combination of these metrics.\n\n")
        
        f.write("### Team Tiers\n")
        f.write("The following chart visualizes the offensive vs defensive efficiency of all teams.\n")
        f.write("![Team Tiers](output/team_tiers.png)\n\n")
        
        f.write("### QB Efficiency\n")
        f.write("Quarterback play is the single most important factor. Here is how the league's QBs stack up:\n")
        f.write("![QB Efficiency](output/qb_efficiency.png)\n")
        
    print(f"Report generated at {output_file}")

def main():
    # 1. Load Data
    pbp = data_loader.load_data([2024])
    if pbp is None:
        return
    
    roster = data_loader.load_roster([2024])
    
    # 2. Player Analysis
    top_10, qb_stats, all_players = player_analysis.analyze_players(pbp, roster)
    print("\nTop 10 Players:")
    print(top_10[['player_name', 'position', 'impressiveness_score']])
    
    # 3. Team Analysis
    team_rankings = team_analysis.analyze_teams(pbp)
    print("\nTop 5 Teams:")
    print(team_rankings[['team', 'off_epa', 'def_epa', 'prediction_score']].head())
    
    # 4. Visualization
    visualizer.plot_top_players(top_10)
    visualizer.plot_qb_efficiency(qb_stats)
    visualizer.plot_team_tiers(team_rankings) # Pass full stats for plotting
    
    # 5. Generate Report
    generate_report(top_10, team_rankings)

if __name__ == "__main__":
    main()
