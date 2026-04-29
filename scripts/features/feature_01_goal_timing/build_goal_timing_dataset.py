#!/usr/bin/env python
"""
Clean and consolidate UPL goal data from all seasons.

Usage:
    python scripts/features/feature_01_goal_timing/build_goal_timing_dataset.py
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_SEASON_FILES, CLEANED_CSV
from src.dataset import consolidate_goal_seasons_from_raw, save_dataframe
from src.cleaning import clean_dataframe


def main():
    """Main entry point."""
    print(f"\n{'='*60}")
    print("UPL Goal Data - Cleaning & Consolidation Pipeline")
    print(f"{'='*60}\n")

    try:
        # Load and consolidate seasons
        print("Step 1: Loading raw season goal data from structured season folders or legacy files...")
        upl_goals = consolidate_goal_seasons_from_raw(list(RAW_SEASON_FILES.keys()), file_exists_check=True)
        print(f"  [ok] Consolidated {len(upl_goals)} rows from {len(RAW_SEASON_FILES)} seasons\n")

        # Apply comprehensive cleaning
        print("Step 2: Applying cleaning pipeline...")
        df_clean = clean_dataframe(upl_goals)

        # Save cleaned data
        print(f"\nStep 3: Saving cleaned data...")
        save_dataframe(df_clean, CLEANED_CSV)

        print(f"\n[ok] Cleaning complete!")
        print(f"  Input rows: {len(upl_goals)}")
        print(f"  Output rows: {len(df_clean)}")
        print(f"  Output file: {CLEANED_CSV}\n")

        return 0

    except Exception as e:
        print(f"\n[error] Cleaning failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
