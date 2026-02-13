"""
Feature engineering and metric calculation modules for UPL Goal Analysis.

This module implements the core advanced metrics defined in the project structure:
1. GQR (Goal Quality Ratio)
2. GTSI (Goal Timing Shift Index)
3. DIS (Decisive Impact Score)
4. OVW (Opponent Vulnerability Window)
5. DDI (Discipline Degradation Index)
"""



import pandas as pd
import numpy as np
from typing import Dict, Optional, Union

from src import config


def calculate_gqr(df: pd.DataFrame) -> float:
    """
    Calculate Goal Quality Ratio (GQR).

    GQR = (Open Play Goals) / (Total Goals)

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing 'goal_type'.

    Returns
    -------
    float
        The GQR value. Returns 0.0 if no goals.
    """
    total_goals = len(df)
    if total_goals == 0:
        return 0.0

    # Define non-open play types
    non_open_play = [config.GOAL_TYPE_PENALTY, config.GOAL_TYPE_OWN_GOAL]
    
    # Count open play goals
    open_play_count = len(df[~df["goal_type"].isin(non_open_play)])
    
    return open_play_count / total_goals


def calculate_gtsi(df: pd.DataFrame) -> float:
    """
    Calculate Goal Timing Shift Index (GTSI).

    GTSI = ratio of goals in Decisive Window (76-90+) vs Peak Focus Window (16-30).

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing 'goal_minute_num'.

    Returns
    -------
    float
        The GTSI value. Returns NaN if zero goals in Peak Focus Window.
    """
    # Decisive Window: 76-90+ (>= 76)
    decisive_goals = len(df[df["goal_minute_num"] >= 76])
    
    # Peak Focus Window: 16-30 (inclusive)
    peak_focus_goals = len(df[(df["goal_minute_num"] >= 16) & (df["goal_minute_num"] <= 30)])
    
    if peak_focus_goals == 0:
        return np.nan
        
    return decisive_goals / peak_focus_goals


def calculate_match_evolution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reconstruct the scoreboard chronologically so we know the game state at the moment of every goal.

    Adds the following columns:
    - score_home_before: Home score before the goal
    - score_away_before: Away score before the goal
    - score_home_after: Home score after the goal
    - score_away_after: Away score after the goal
    - scoring_team_name: Name of the team that scored
    - is_home_goal: 1 if home team scored, 0 otherwise

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with 'match_id', 'goal_minute_num', 'team_side', 'home_team', 'away_team'.

    Returns
    -------
    pd.DataFrame
        Dataframe with added score context columns.
    """
    df = df.copy()
    
    # Ensure logical order
    df = df.sort_values(["match_id", "goal_minute_num"]) 
    
    # Identify scoring side
    is_og = df["goal_type"] == config.GOAL_TYPE_OWN_GOAL

    df["is_home_goal"] = np.where(is_og,
    (df["team_side"] == config.SIDE_AWAY).astype(int), # Flip: Away OG = Home Goal
    (df["team_side"] == config.SIDE_HOME).astype(int)  # Regular
    )
    
    df["is_away_goal"] = np.where(is_og,
    (df["team_side"] == config.SIDE_HOME).astype(int), # Flip: Home OG = Away Goal
    (df["team_side"] == config.SIDE_AWAY).astype(int)  # Regular
    )
    # Determine scoring team name
    df["scoring_team_name"] = np.where(
        df["is_home_goal"] == 1, 
        df["home_team"], 
        df["away_team"]
    )
    
    # Calculate running scores using cumulative sum within each match
    df["score_home_after"] = df.groupby("match_id")["is_home_goal"].cumsum()
    df["score_away_after"] = df.groupby("match_id")["is_away_goal"].cumsum()
    
    # Calculate previous scores (shift and fill with 0)
    df["score_home_before"] = df.groupby("match_id")["score_home_after"].shift(1).fillna(0).astype(int)
    df["score_away_before"] = df.groupby("match_id")["score_away_after"].shift(1).fillna(0).astype(int)
    
    return df


def calculate_dis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Decisive Impact Score (DIS) for each goal.

    DIS = Time Weight * Outcome Weight

    Time Weights:
    - 0-15: 0.5
    - 16-30: 0.6
    - 31-45: 0.7
    - 46-60: 0.8
    - 61-75: 0.9
    - 76+: 1.0

    Outcome Weights:
    - Winning/Lead-taking Goal (Break Tie): 2.0
    - Equalizer (Losing -> Draw): 1.5
    - Cushion Goal (Lead -> Lead+1): 1.0
    - Consolation (Losing -> Losing less): 0.5
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing match context (run calculate_match_evolution first).

    Returns
    -------
    pd.DataFrame
        Dataframe with 'dis_time_weight', 'dis_outcome_weight', and 'dis' columns.
    """
    df = df.copy()
    
    # 1. Calculate Time Weight
    def get_time_weight(minute):
        if pd.isna(minute): return 0
        if minute <= 15: return 0.5
        if minute <= 30: return 0.6
        if minute <= 45: return 0.7
        if minute <= 60: return 0.8
        if minute <= 75: return 0.9
        return 1.0
        
    df["dis_time_weight"] = df["goal_minute_num"].apply(get_time_weight)
    
    # 2. Calculate Outcome Weight
    # We need to know the state *before* the goal relative to the *scoring team*
    
    # Calculate score difference for the scoring team BEFORE the goal
    # If home scored: diff = home_before - away_before
    # If away scored: diff = away_before - home_before
    
    df["score_diff_before"] = np.where(
        df["is_home_goal"] == 1,
        df["score_home_before"] - df["score_away_before"],
        df["score_away_before"] - df["score_home_before"]
    )
    
    def get_outcome_weight(diff_before):
        if diff_before == 0:
            return 2.0  # Tie -> Lead (Potential Winner)
        elif diff_before == -1:
            return 1.5  # Losing by 1 -> Draw (Equalizer)
        elif diff_before > 0:
            return 1.0  # Winning -> Winning more (Cushion)
        else:
            return 0.5  # Losing by >1 -> Losing less (Consolation)
            
    df["dis_outcome_weight"] = df["score_diff_before"].apply(get_outcome_weight)
    
    # 3. Calculate Final DIS
    df["dis"] = df["dis_time_weight"] * df["dis_outcome_weight"]
    
    return df


def calculate_ovw(df: pd.DataFrame, team_name: str) -> str:
    """
    Calculate Opponent Vulnerability Window (OVW).
    
    Identifies the 15-minute segment where a specific team *concedes* the most goals.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of all goals.
    team_name : str
        Name of the team to analyze (e.g. "Vipers SC").

    Returns
    -------
    str
        The description of the window (e.g., "76-90").
    """
    # Filter for goals conceded by the team
    # A team concedes if they are Home and Away scores, or they are Away and Home scores.
    # Logic: If I am Home, I concede if is_away_goal == 1.
    
    # First, identify the opponent for every row
    # If home_team == team_name, opponent scored if is_away_goal.
    # If away_team == team_name, opponent scored if is_home_goal.
    
    # Easier way: Filter rows where the *defending team* is team_name.
    # Defending Home Team concedes Away Goals.
    conceded_home = df[(df["home_team"] == team_name) & (df["is_away_goal"] == 1)]
    
    # Defending Away Team concedes Home Goals.
    conceded_away = df[(df["away_team"] == team_name) & (df["is_home_goal"] == 1)]
    
    conceded = pd.concat([conceded_home, conceded_away])
    
    if len(conceded) == 0:
        return "N/A"
        
    # Bin into 15 min windows
    def get_window(minute):
        if pd.isna(minute): return "Unknown"
        if minute <= 15: return "0-15"
        if minute <= 30: return "16-30"
        if minute <= 45: return "31-45"
        if minute <= 60: return "46-60"
        if minute <= 75: return "61-75"
        return "76-90+"
        
    window_counts = conceded["goal_minute_num"].apply(get_window).value_counts()
    
    if window_counts.empty:
        return "N/A"
        
    return window_counts.idxmax()


def calculate_ddi(df: pd.DataFrame, team_name: str) -> float:
    """
    Calculate Discipline Degradation Index (DDI).

    Ratio of (Penalty + Own Goals) conceded in 2nd Half vs 1st Half.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of all goals.
    team_name : str
        Team to analyze.

    Returns
    -------
    float
        Ratio (2nd Half Bad Goals / 1st Half Bad Goals). 
        Returns infinity (or high number) if 0 in 1st half.
    """
    # Filter for bad goals conceded by team
    # Bad goals = Penalty or Own Goal
    bad_types = [config.GOAL_TYPE_PENALTY, config.GOAL_TYPE_OWN_GOAL]
    
    conceded_home = df[(df["home_team"] == team_name) & (df["is_away_goal"] == 1)]
    conceded_away = df[(df["away_team"] == team_name) & (df["is_home_goal"] == 1)]
    conceded = pd.concat([conceded_home, conceded_away])
    
    bad_goals = conceded[conceded["goal_type"].isin(bad_types)]
    
    bad_h1 = len(bad_goals[bad_goals["match_half"] == "First Half"])
    bad_h2 = len(bad_goals[bad_goals["match_half"] == "Second Half"])
    
    if bad_h1 == 0:
        if bad_h2 > 0:
            return float('inf') # Infinite degradation
        else:
            return 0.0 # No bad goals at all
            
    return bad_h2 / bad_h1
