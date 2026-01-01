"""
Data cleaning and normalization functions for UPL Goal Data project.

This module provides functions to clean team names, standardize goal data,
and add derived features to the consolidated dataset.
"""

import pandas as pd
import numpy as np
import re
from typing import Callable, Optional

from src import config


def split_combined_teams(df: pd.DataFrame) -> pd.DataFrame:
    """
    Split combined team names (e.g., 'Team A Vs Team B') into home and away.

    This function handles multiple formats: 'Vs', 'VS', etc.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with potential combined team names.

    Returns
    -------
    pd.DataFrame
        Dataframe with separated home_team and away_team columns.

    Examples
    --------
    >>> df['home_team'] = 'Team A Vs Team B'
    >>> df = split_combined_teams(df)
    >>> df['home_team'].iloc[0]
    'Team A'
    >>> df['away_team'].iloc[0]
    'Team B'
    """
    df = df.copy()

    # Handle 'Vs' format
    df["home_team"] = df["home_team"].str.replace(r"\s+Vs\s+", "|", regex=True)
    split_teams = df["home_team"].str.split("|", expand=True)
    df["home_team"] = split_teams[0].str.strip()
    df.loc[split_teams[1].notna(), "away_team"] = split_teams[1].str.strip()

    # Handle 'VS' format
    df["home_team"] = df["home_team"].str.replace(r"\s+VS\s+", "|", regex=True)
    split_teams = df["home_team"].str.split("|", expand=True)
    df["home_team"] = split_teams[0].str.strip()
    df.loc[split_teams[1].notna(), "away_team"] = split_teams[1].str.strip()

    return df


def apply_team_name_corrections(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply standardized team name corrections.

    Uses the corrections mapping from config.CLUB_NAME_CORRECTIONS.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with team names to correct.

    Returns
    -------
    pd.DataFrame
        Dataframe with corrected team names.
    """
    df = df.copy()
    df["home_team"] = df["home_team"].replace(config.CLUB_NAME_CORRECTIONS)
    df["away_team"] = df["away_team"].replace(config.CLUB_NAME_CORRECTIONS)
    return df


def normalize_team_name(name: str) -> str:
    """
    Normalize a team name to Title Case with uppercase abbreviations.

    Converts team abbreviations (FC, SC, KCCA, etc.) to uppercase while
    keeping other parts as Title Case.

    Parameters
    ----------
    name : str or NaN
        Team name to normalize.

    Returns
    -------
    str or NaN
        Normalized team name.

    Examples
    --------
    >>> normalize_team_name('kcca fc')
    'KCCA FC'
    >>> normalize_team_name('vipers sc')
    'Vipers SC'
    """
    if pd.isna(name):
        return name

    parts = name.split()
    normalized = []

    for part in parts:
        # Strip non-alphanumeric for checking and output
        core = re.sub(r"[^A-Za-z0-9]", "", part)
        if not core:
            continue
        if core.lower() in config.UPPERCASE_TERMS:
            normalized.append(core.upper())
        else:
            normalized.append(core.title())

    return " ".join(normalized)


def normalize_team_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize all team names in home_team and away_team columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Dataframe with normalized team names.
    """
    df = df.copy()

    # Convert to lowercase first
    df["home_team"] = df["home_team"].str.lower().str.strip()
    df["away_team"] = df["away_team"].str.lower().str.strip()

    # Apply normalization
    df["home_team"] = df["home_team"].apply(normalize_team_name)
    df["away_team"] = df["away_team"].apply(normalize_team_name)

    return df


def fix_known_goal_minute_errors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix known erroneous goal minute values based on historical data issues.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Dataframe with corrected goal_minute values.
    """
    df = df.copy()

    # Known fixes with source data information
    df.loc[df["goal_minute"] == "247", "goal_minute"] = "90"
    # Note: Busoga United vs BUL FC MD24 2023/04/21

    df.loc[df["goal_minute"] == "90+", "goal_minute"] = "90+2"
    # Note: Kitara FC vs Busoga United FC MD22 2021/05/08

    df.loc[df["goal_minute"] == "757", "goal_minute"] = "80"
    # Note: Onduparaka vs Kyetume MD13 2019-11-08

    df.loc[df["goal_minute"] == "30 (p)", "goal_minute"] = "30"
    df.loc[df["goal_minute"] == "30 (p)", "goal_type"] = "Penalty"

    return df


def convert_minute_to_numeric(val: str) -> Optional[int]:
    """
    Convert goal minute string (including added time format) to numeric.

    Handles formats like '45', '90+2', etc.

    Parameters
    ----------
    val : str or NaN
        Goal minute string to convert.

    Returns
    -------
    int or NaN
        Numeric goal minute (base + added time) or NaN if input is NaN.

    Examples
    --------
    >>> convert_minute_to_numeric('45')
    45
    >>> convert_minute_to_numeric('90+2')
    92
    """
    if pd.isna(val):
        return np.nan

    val = str(val)
    if "+" in val:
        base, added = val.split("+")
        return int(base) + int(added)
    else:
        return int(val)


def add_goal_minute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add goal minute-derived features.

    Adds:
    - goal_minute_num: numeric goal minute (base + added time)
    - in_added_time: binary flag for added time goals
    - match_half: 'First Half', 'Second Half', or NaN

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with goal_minute column.

    Returns
    -------
    pd.DataFrame
        Dataframe with new goal minute features.
    """
    df = df.copy()

    # Convert to numeric
    df["goal_minute_num"] = df["goal_minute"].apply(convert_minute_to_numeric)

    # Flag added time goals
    df["in_added_time"] = df["goal_minute"].astype(str).str.contains("+", regex=False).astype(int)

    # Determine match half
    def match_half(minute):
        if pd.isna(minute):
            return np.nan
        elif minute <= 45:
            return "First Half"
        else:
            return "Second Half"

    df["match_half"] = df["goal_minute_num"].apply(match_half)

    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features for analysis.

    Adds:
    - has_goal: binary flag (1 if goal_minute is not NaN, 0 otherwise)
    - match_id: unique match identifier
    - round: 'Round 1' or 'Round 2' based on match day
    - match_half: match half designation

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with required columns (Date, Season, home_team, away_team, Match Day, goal_minute).

    Returns
    -------
    pd.DataFrame
        Dataframe with new features.
    """
    df = df.copy()

    # Add has_goal flag
    df["has_goal"] = df["goal_minute"].notna().astype(int)

    # Add match_id
    def team_code(name: str) -> str:
        """Extract 3-letter team code from team name."""
        return name.replace(" ", "")[:3].upper()

    df["match_id"] = (
        "UPL"
        + df["Season"].str[-2:]
        + "/"
        + df["home_team"].apply(team_code)
        + "/"
        + df["away_team"].apply(team_code)
        + "/"
        + pd.to_datetime(df["Date"]).dt.strftime("%d-%m")
    )

    # Add round designation
    df["round"] = np.where(df["Match Day"] <= 15, "Round 1", "Round 2")

    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply comprehensive cleaning pipeline to goal data.

    Pipeline steps:
    1. Split combined team names
    2. Apply team name corrections
    3. Normalize team names
    4. Fix known goal minute errors
    5. Add goal minute features
    6. Add derived features
    7. Standardize column names
    8. Remove unnecessary columns

    Parameters
    ----------
    df : pd.DataFrame
        Raw consolidated dataframe.

    Returns
    -------
    pd.DataFrame
        Cleaned and feature-rich dataframe.
    """
    df = df.copy()

    print("Starting cleaning pipeline...")

    # Step 1: Split combined teams
    df = split_combined_teams(df)
    print("✓ Split combined team names")

    # Step 2: Apply corrections
    df = apply_team_name_corrections(df)
    print("✓ Applied team name corrections")

    # Step 3: Normalize team names
    df = normalize_team_names(df)
    print("✓ Normalized team names")

    # Step 4: Fix goal minute errors
    df = fix_known_goal_minute_errors(df)
    print("✓ Fixed known goal minute errors")

    # Step 5: Add goal minute features
    df = add_goal_minute_features(df)
    print("✓ Added goal minute features")

    # Step 6: Add derived features
    df = add_derived_features(df)
    print("✓ Added derived features")

    # Step 7: Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    print("✓ Standardized column names")

    # Step 8: Convert date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    print("✓ Converted date column")

    # Remove League column if it exists
    if "league" in df.columns:
        df = df.drop(columns=["league"])
    print("✓ Removed unnecessary columns")

    print(f"\nCleaning complete! Final shape: {df.shape}")

    return df
