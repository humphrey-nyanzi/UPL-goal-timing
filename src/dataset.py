"""
Data loading and consolidation functions for UPL Goal Data project.

This module provides functions to load, consolidate, and save CSV datasets
from the raw and processed data directories.
"""

from pathlib import Path
from typing import Dict

import pandas as pd

from src import config


def load_season_csv(file_path: Path) -> pd.DataFrame:
    """
    Load a single season CSV file.

    Parameters
    ----------
    file_path : Path
        Path to the CSV file to load.

    Returns
    -------
    pd.DataFrame
        Loaded dataframe with error handling for missing files.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    return df


def consolidate_seasons(
    season_files: Dict[str, Path],
    file_exists_check: bool = True,
) -> pd.DataFrame:
    """
    Consolidate multiple season CSV files into a single dataframe.

    Parameters
    ----------
    season_files : Dict[str, Path]
        Dictionary mapping season names to file paths.
    file_exists_check : bool, optional
        If True, skip files that don't exist. If False, raise error.
        Default is True.

    Returns
    -------
    pd.DataFrame
        Consolidated dataframe from all seasons.

    Examples
    --------
    >>> from src.config import RAW_SEASON_FILES
    >>> df = consolidate_seasons(RAW_SEASON_FILES)
    """
    dataframes = []

    for season, file_path in season_files.items():
        try:
            df = load_season_csv(file_path)
            dataframes.append(df)
            print(f"[ok] Loaded {season}: {len(df)} rows")
        except FileNotFoundError as e:
            if file_exists_check:
                print(f"[skip] Skipped {season}: file not found")
                continue
            else:
                raise e

    if not dataframes:
        raise ValueError("No CSV files were successfully loaded.")

    consolidated = pd.concat(dataframes, ignore_index=True)
    return consolidated


def build_legacy_goal_dataframe_from_events(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the structured events table into the legacy goal-only schema.

    Parameters
    ----------
    events_df : pd.DataFrame
        Structured events dataframe produced by the scraper.

    Returns
    -------
    pd.DataFrame
        Goal-only dataframe matching the original raw cleaning input schema.
    """
    legacy_goal_columns = [
        "Date",
        "Time",
        "League",
        "Season",
        "Match Day",
        "home_team",
        "away_team",
        "goal_minute",
        "team_side",
        "player_name",
        "goal_type",
    ]

    if events_df.empty:
        return pd.DataFrame(columns=legacy_goal_columns)

    goal_events = events_df.loc[events_df["event_type"] == "goal"].copy()
    if goal_events.empty:
        return pd.DataFrame(columns=legacy_goal_columns)

    goal_events = goal_events.rename(
        columns={
            "date": "Date",
            "time": "Time",
            "league": "League",
            "season": "Season",
            "match_day": "Match Day",
            "event_minute": "goal_minute",
        }
    )

    for column in legacy_goal_columns:
        if column not in goal_events.columns:
            goal_events[column] = None

    return goal_events[legacy_goal_columns]


def load_goal_season_with_fallback(season: str) -> pd.DataFrame:
    """
    Load one season of goal data, preferring structured event tables.

    Parameters
    ----------
    season : str
        Season key such as ``2019_20`` or ``2025_26``.

    Returns
    -------
    pd.DataFrame
        Goal-only dataframe for the requested season.

    Raises
    ------
    FileNotFoundError
        If neither the structured events table nor the legacy goal CSV exists.
    """
    structured_events_path = config.raw_season_file(season, "events")
    if structured_events_path.exists():
        events_df = load_season_csv(structured_events_path)
        goal_df = build_legacy_goal_dataframe_from_events(events_df)
        print(f"[ok] Loaded {season} from structured events: {len(goal_df)} goal rows")
        return goal_df

    legacy_goal_path = config.RAW_SEASON_FILES.get(season)
    if legacy_goal_path and legacy_goal_path.exists():
        goal_df = load_season_csv(legacy_goal_path)
        print(f"[ok] Loaded {season} from legacy goals file: {len(goal_df)} rows")
        return goal_df

    archived_legacy_goal_path = config.LEGACY_RAW_ARCHIVE_DIR / f"upl_goals_{season}.csv"
    if archived_legacy_goal_path.exists():
        goal_df = load_season_csv(archived_legacy_goal_path)
        print(f"[ok] Loaded {season} from archived legacy goals file: {len(goal_df)} rows")
        return goal_df

    raise FileNotFoundError(
        f"No structured events or legacy goal file found for season {season}"
    )


def consolidate_goal_seasons_from_raw(
    seasons: list[str],
    file_exists_check: bool = True,
) -> pd.DataFrame:
    """
    Consolidate goal data across seasons, preferring structured raw tables.

    Parameters
    ----------
    seasons : list[str]
        Season keys such as ``['2019_20', '2020_21']``.
    file_exists_check : bool, optional
        If True, skip missing seasons. If False, raise on the first missing one.

    Returns
    -------
    pd.DataFrame
        Consolidated goal-only dataframe across all requested seasons.
    """
    dataframes = []

    for season in seasons:
        try:
            season_df = load_goal_season_with_fallback(season)
            dataframes.append(season_df)
        except FileNotFoundError as exc:
            if file_exists_check:
                print(f"[skip] Skipped {season}: {exc}")
                continue
            raise exc

    if not dataframes:
        raise ValueError("No season goal datasets were successfully loaded.")

    return pd.concat(dataframes, ignore_index=True)


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save a dataframe to CSV with parent directory creation.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to save.
    output_path : Path
        Path where the CSV should be saved.

    Examples
    --------
    >>> from src.config import CLEANED_CSV
    >>> df_cleaned = pd.DataFrame({...})
    >>> save_dataframe(df_cleaned, CLEANED_CSV)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[ok] Saved: {output_path} ({len(df)} rows)")
