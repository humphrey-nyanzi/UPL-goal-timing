"""
Data loading and consolidation functions for UPL Goal Data project.

This module provides functions to load, consolidate, and save CSV datasets
from the raw and processed data directories.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

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

    return pd.read_csv(file_path)


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
            print(f"✓ Loaded {season}: {len(df)} rows")
        except FileNotFoundError as e:
            if file_exists_check:
                print(f"✗ Skipped {season}: file not found")
                continue
            else:
                raise e

    if not dataframes:
        raise ValueError("No CSV files were successfully loaded.")

    consolidated = pd.concat(dataframes, ignore_index=True)
    return consolidated


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
    print(f"✓ Saved: {output_path} ({len(df)} rows)")
