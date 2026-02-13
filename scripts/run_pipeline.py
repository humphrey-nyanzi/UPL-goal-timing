#!/usr/bin/env python
"""
Orchestrate the complete UPL data pipeline.

Pipeline steps:
  1. Scrape - Fetch latest season data from UPL website
  2. Clean  - Consolidate and clean all season data
  3. Analyze - Generate analysis and visualizations

Usage:
    python scripts/run_pipeline.py                  # Run all steps
    python scripts/run_pipeline.py --skip scraping  # Skip scraping
    python scripts/run_pipeline.py --skip analysis  # Skip analysis
"""

import sys
import argparse
import subprocess
from pathlib import Path


SCRIPTS_DIR = Path(__file__).parent
SCRIPT_MAPPING = {
    "scraping": SCRIPTS_DIR / "01_scraping.py",
    "cleaning": SCRIPTS_DIR / "02_cleaning.py",
    "analysis": SCRIPTS_DIR / "03_analysis.py",
}


def run_script(script_path: Path, script_name: str) -> int:
    """
    Run a single script in subprocess.

    Parameters
    ----------
    script_path : Path
        Path to the script file
    script_name : str
        Friendly name for logging

    Returns
    -------
    int
        Return code (0 = success)
    """
    print(f"\n{'=' * 60}")
    print(f"Step: {script_name.upper()}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)], check=True, cwd=SCRIPTS_DIR.parent
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] {script_name} failed with code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"\n[ERROR] Error running {script_name}: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the UPL Goal Data Analysis pipeline"
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        choices=["scraping", "cleaning", "analysis"],
        default=[],
        help="Steps to skip (e.g., --skip scraping cleaning)",
    )
    parser.add_argument(
        "--season",
        type=str,
        default="2025-26",
        help="Season to scrape (passed to scraping step)",
    )
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print("UPL GOAL DATA ANALYSIS PIPELINE")
    print(f"{'=' * 60}")
    print(f"\nConfiguration:")
    print(f"  Season: {args.season}")
    print(f"  Skip steps: {args.skip if args.skip else 'None'}")

    steps = ["scraping", "cleaning", "analysis"]
    return_codes = []

    for step in steps:
        if step in args.skip:
            print(f"\n[SKIP] Skipping {step}...")
            continue

        script_path = SCRIPT_MAPPING[step]
        if not script_path.exists():
            print(f"\n[ERROR] Script not found: {script_path}")
            return_codes.append(1)
            continue

        # Pass season argument to scraping step
        if step == "scraping":
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), "--season", args.season],
                    check=True,
                    cwd=SCRIPTS_DIR.parent,
                )
                return_codes.append(result.returncode)
            except subprocess.CalledProcessError as e:
                print(f"\n[ERROR] {step} failed with code {e.returncode}")
                return_codes.append(e.returncode)
        else:
            return_code = run_script(script_path, step)
            return_codes.append(return_code)

    # Summary
    print(f"\n{'=' * 60}")
    print("PIPELINE SUMMARY")
    print(f"{'=' * 60}")

    total_steps = len(steps) - len(args.skip)
    successful_steps = sum(1 for code in return_codes if code == 0)

    print(f"\nCompleted: {successful_steps}/{total_steps} steps")

    if all(code == 0 for code in return_codes):
        print("\n[OK] Pipeline completed successfully!\n")
        return 0
    else:
        print("\n[ERROR] Pipeline completed with errors\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
