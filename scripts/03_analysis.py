#!/usr/bin/env python
"""
Exploratory analysis and visualization of UPL goal data.

Usage:
    python scripts/03_analysis.py
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLEANED_CSV, FIGURES_DIR
from src.plots import set_style


def load_and_prepare_data() -> pd.DataFrame:
    """Load and prepare cleaned data for analysis."""
    print("Loading cleaned data...")
    df = pd.read_csv(CLEANED_CSV)
    print(f"✓ Loaded {len(df)} rows from {CLEANED_CSV}\n")

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

    # Parse dates and numerics
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df['goal_minute_num'] = pd.to_numeric(df['goal_minute_num'], errors='coerce')

    # Strip whitespace from object columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # Clean empty strings
    df.replace("", np.nan, inplace=True)

    # Filter out incomplete seasons
    df = df[df['season'] != '2025/26']

    return df


def generate_summary_stats(df: pd.DataFrame):
    """Generate and print summary statistics."""
    print("="*60)
    print("DATA SUMMARY")
    print("="*60)
    print(f"\nShape: {df.shape}")
    print(f"Seasons: {sorted(df['season'].unique().tolist())}")
    print(f"Teams (unique): {df['home_team'].nunique()}")
    print(f"Matches (estimated): {df.groupby('season')['match_id'].nunique().sum()}")
    print(f"\nGoals with valid minute: {df['goal_minute_num'].notna().sum()}")
    print(f"Missing values:\n{df.isna().sum()}\n")


def create_visualizations(df: pd.DataFrame):
    """Create and save key visualizations."""
    print("="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)

    # Ensure figures directory exists
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    set_style()

    # 1. Goals by 15-minute intervals
    print("\n1. Goal distribution by time interval...")
    bins = [0, 15, 30, 45, 60, 75, 90, 105]
    labels = ['0-15', '15-30', '30-45', '45-60', '60-75', '75-90', '90+']
    df['goal_interval'] = pd.cut(df['goal_minute_num'], bins=bins, labels=labels, right=False)

    plt.figure(figsize=(10, 6))
    ax = sns.histplot(data=df, x='goal_interval', discrete=True, kde=False, color='steelblue')
    for patch in ax.patches:
        height = patch.get_height()
        ax.text(patch.get_x() + patch.get_width()/2., height, f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])
    plt.title('Goals by 15-Minute Intervals')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / '01_goals_by_interval.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 01_goals_by_interval.png")

    # 2. Average goal minute by season
    print("2. Average goal minute by season...")
    avg_goal_minute = df.groupby('season', as_index=False)['goal_minute_num'].mean().round(1)
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=avg_goal_minute, x='season', y='goal_minute_num')
    for patch in ax.patches:
        height = patch.get_height()
        ax.text(patch.get_x() + patch.get_width()/2., height, f'{height}',
                ha='center', va='bottom', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])
    plt.title("Average Goal Minute per Season")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / '02_avg_goal_minute_season.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 02_avg_goal_minute_season.png")

    # 3. Goal type distribution
    print("3. Goal type distribution...")
    plt.figure(figsize=(10, 6))
    goal_types = df[df['goal_minute'].notna()]['goal_type'].value_counts()
    goal_types.plot(kind='pie', autopct='%1.1f%%', colors=['lightblue', 'orange', 'red'])
    plt.title('Distribution of Goal Types')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / '03_goal_type_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 03_goal_type_distribution.png")

    # 4. Home vs Away goals
    print("4. Home vs Away goals...")
    plt.figure(figsize=(10, 6))
    side_goals = df[df['goal_minute'].notna()]['team_side'].value_counts()
    side_goals.plot(kind='bar', color=['skyblue', 'orange'])
    plt.title('Home Team vs Away Team Goals')
    plt.ylabel('Number of Goals')
    plt.xlabel('Team Side')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / '04_home_vs_away.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 04_home_vs_away.png")

    # 5. Match half distribution
    print("5. Goals by match half...")
    plt.figure(figsize=(10, 6))
    half_goals = df[df['goal_minute'].notna()]['match_half'].value_counts()
    half_goals.plot(kind='bar', color=['steelblue', 'coral'])
    plt.title('Goals by Match Half')
    plt.ylabel('Number of Goals')
    plt.xlabel('Match Half')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / '05_goals_by_half.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 05_goals_by_half.png")

    print(f"\n✓ All visualizations saved to: {FIGURES_DIR}\n")


def analyze_team_patterns(df: pd.DataFrame):
    """Analyze team-based patterns."""
    print("="*60)
    print("TEAM-BASED INSIGHTS")
    print("="*60)

    print("\nTop 5 teams by average goal minute (home):")
    home_avg = df[df['team_side'] == 'home'].groupby('home_team')['goal_minute_num'].mean().round(1).sort_values(ascending=False).head()
    print(home_avg)

    print("\nTop 5 teams by average goal minute (away):")
    away_avg = df[df['team_side'] == 'away'].groupby('away_team')['goal_minute_num'].mean().round(1).sort_values(ascending=False).head()
    print(away_avg)

    print("\nGoals in added time by team:")
    home_added = df[df['team_side'] == 'home'].groupby('home_team')['in_added_time'].sum()
    away_added = df[df['team_side'] == 'away'].groupby('away_team')['in_added_time'].sum()
    print(f"  Home teams with most added-time goals: {home_added.nlargest(3).to_dict()}")
    print(f"  Away teams with most added-time goals: {away_added.nlargest(3).to_dict()}")


def main():
    """Main entry point."""
    print(f"\n{'='*60}")
    print("UPL Goal Data - Analysis & Visualization")
    print(f"{'='*60}\n")

    try:
        # Load and prepare data
        df = load_and_prepare_data()

        # Generate summary
        generate_summary_stats(df)

        # Create visualizations
        create_visualizations(df)

        # Analyze patterns
        analyze_team_patterns(df)

        print("\n✓ Analysis complete!")
        return 0

    except Exception as e:
        print(f"\n✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
