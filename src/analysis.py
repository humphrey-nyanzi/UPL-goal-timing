"""
Statistical analysis and hypothesis testing for UPL Goal Analysis.

This module provides functions to validate the core project hypotheses:
1. Critical Phase: More goals are scored late in the match (76-90+).
2. Early Leads: Teams that score first in the first 15 mins have higher win rates.
3. Fatigue/Discipline: Correlation between DDI and late-game goal concessions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def test_critical_phase_hypothesis(df: pd.DataFrame) -> Dict:
    """
    Test if the 'critical phase' (76-90+) has a statistically higher goal rate.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned goal dataset.

    Returns
    -------
    Dict
        Statistics comparing the late window to other 15-min windows.
    """

    # Group goals into 15-min windows
    def get_window(minute):
        if pd.isna(minute):
            return "Unknown"
        if minute <= 15:
            return "00-15"
        if minute <= 30:
            return "16-30"
        if minute <= 45:
            return "31-45"
        if minute <= 60:
            return "46-60"
        if minute <= 75:
            return "61-75"
        return "76-90+"

    df = df.copy()
    df["window"] = df["goal_minute_num"].apply(get_window)

    window_counts = df["window"].value_counts().sort_index()
    total_goals = len(df)

    # Calculate percentages
    window_pct = (window_counts / total_goals) * 100

    late_pct = window_pct.get("76-90+", 0)
    avg_other_pct = window_pct.drop("76-90+", errors="ignore").mean()

    return {
        "window_distribution_pct": window_pct.to_dict(),
        "late_window_pct": late_pct,
        "avg_other_windows_pct": avg_other_pct,
        "ratio_late_to_avg": late_pct / avg_other_pct if avg_other_pct > 0 else 0,
    }


def test_early_lead_hypothesis(df: pd.DataFrame) -> Dict:
    """
    Test if scoring in the first 15 minutes leads to a > 70% win probability.

    Requires data processed by calculate_match_evolution to identify first goals.

    Parameters
    ----------
    df : pd.DataFrame
        Goal dataset with score context and results.
        Note: Needs to know the final match result.
    """
    # This requires final scores per match.
    # Assuming match-level aggregation exists or can be derived.
    # For now, we calculate it based on goals if final score is not in DF.

    # 1. Identify first goal of every match
    first_goals = (
        df.sort_values(["match_id", "goal_minute_num"])
        .groupby("match_id")
        .first()
        .reset_index()
    )

    # 2. Filter for goals scored in 0-15 min
    early_leads = first_goals[first_goals["goal_minute_num"] <= 15]

    if len(early_leads) == 0:
        return {"error": "No early leads found in dataset"}

    # 3. Join with final match results
    # To get final results, we sum total goals per match per side
    results = (
        df.groupby("match_id")
        .agg({"is_home_goal": "sum", "is_away_goal": "sum"})
        .rename(columns={"is_home_goal": "final_home", "is_away_goal": "final_away"})
    )

    analysis_df = early_leads.merge(results, on="match_id")

    # Identify if the scoring team won
    def check_win(row):
        if row["is_home_goal"] == 1:
            return row["final_home"] > row["final_away"]
        else:
            return row["final_away"] > row["final_home"]

    analysis_df["lead_team_won"] = analysis_df.apply(check_win, axis=1)

    win_rate = analysis_df["lead_team_won"].mean()

    return {
        "total_early_leads": len(analysis_df),
        "lead_team_win_rate": win_rate,
        "hypothesis_validated": win_rate >= 0.70,
    }


def test_fatigue_discipline_correlation(df_goals: pd.DataFrame) -> Dict:
    """
    Analyze if teams with high DDI concede more late goals.
    """
    from src import features

    all_teams = pd.concat([df_goals["home_team"], df_goals["away_team"]]).unique()

    team_stats = []

    # We need match context for DDI
    df_context = features.calculate_match_evolution(df_goals)

    for team in all_teams:
        ddi = features.calculate_ddi(df_context, team)

        # Conceded late (76+)
        df_team_conceded = df_context[
            ((df_context["home_team"] == team) & (df_context["is_away_goal"] == 1))
            | ((df_context["away_team"] == team) & (df_context["is_home_goal"] == 1))
        ]

        if len(df_team_conceded) < 5:
            continue  # Skip teams with low data

        late_conceded_pct = len(
            df_team_conceded[df_team_conceded["goal_minute_num"] >= 76]
        ) / len(df_team_conceded)

        team_stats.append(
            {"team": team, "ddi": ddi, "late_conceded_pct": late_conceded_pct}
        )

    stats_df = pd.DataFrame(team_stats)

    if len(stats_df) < 2:
        return {"error": "Insufficient data"}

    correlation = stats_df["ddi"].corr(stats_df["late_conceded_pct"])

    return {
        "correlation_ddi_vs_late_concession": correlation,
        "team_samples": len(stats_df),
    }
