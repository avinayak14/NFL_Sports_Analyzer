# NFL Sports Analyzer

A quantitative analysis tool to identify the most impressive NFL players and predict the Super Bowl winner using advanced metrics.

## Overview

This project uses Python and `nfl_data_py` to fetch play-by-play data and calculate advanced statistics such as:
- **EPA (Expected Points Added)** per play
- **CPOE (Completion Percentage Over Expected)** for Quarterbacks
- **Success Rate** for Rushers
- **Expected YAC EPA** for Receivers

It generates a top 10 list of players based on a composite "Impressiveness Score" and predicts the Super Bowl winner based on team offensive and defensive efficiency.

## Results

**Predicted Super Bowl Winner (2024):** Detroit Lions

For the full analysis and rankings, see [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md).

### Visualizations
Generated charts can be found in the `output/` directory:
- `top_10_players.png`: Bar chart of the top 10 players.
- `qb_efficiency.png`: Scatter plot of QB EPA vs CPOE.
- `team_tiers.png`: Scatter plot of Team Offense vs Defense EPA.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/avinayak14/NFL_Sports_Analyzer.git
   cd NFL_Sports_Analyzer
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main analysis script:

```bash
python main.py
```

This will:
1. Fetch the latest NFL data.
2. Perform player and team analysis.
3. Generate visualization images in `output/`.
4. Create/Update `ANALYSIS_REPORT.md`.

## Project Structure

- `src/`: Source code for data loading, analysis, and visualization.
- `output/`: Generated images.
- `main.py`: Entry point for the analysis.
- `requirements.txt`: Python dependencies.
