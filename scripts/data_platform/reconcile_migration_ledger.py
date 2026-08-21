"""Preflight or repair the legacy custom migration ledger.

The command is read-only unless both ``--repair`` and the exact confirmation
value are supplied. Repair mode never runs migration 012, a data refresh, or a
full rebuild.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.legacy_migration_repair import (
    MigrationLedgerAuthorizationError,
    MigrationLedgerReconciliationError,
    REPAIR_CONFIRMATION,
    ReconciliationReport,
    reconcile_legacy_migration_ledger,
)

DEFAULT_LOG_DIR = PROJECT_ROOT / "outputs" / "automation" / "migration-ledger"


def parse_args() -> argparse.Namespace:
    """Parse explicit operator controls."""

    parser = argparse.ArgumentParser(
        description="Inspect legacy migration drift or run the bounded 008/009 repair."
    )
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Run the transactional 008/009 repair and ledger reconciliation.",
    )
    parser.add_argument(
        "--confirm",
        help=f"Required with --repair. Exact value: {REPAIR_CONFIRMATION}",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help="Directory for the non-secret JSON operator report.",
    )
    return parser.parse_args()


def _write_report(report: ReconciliationReport, log_dir: Path) -> Path:
    """Write a non-secret JSON report for operator review."""

    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    mode = "repair" if report.repair_requested else "preflight"
    path = log_dir / f"{timestamp}_migration_ledger_{mode}.json"
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return path


def _print_report(report: ReconciliationReport) -> None:
    """Print a concise human-readable assessment."""

    print("UPL Lens - Legacy Migration Ledger Reconciliation")
    print(f"Mode: {'repair' if report.repair_requested else 'read-only preflight'}")
    print("Before:")
    for item in report.before:
        print(f"  [{item.status}] {item.filename}")
    if report.after != report.before:
        print("After:")
        for item in report.after:
            print(f"  [{item.status}] {item.filename}")
    print(f"Executed SQL: {list(report.executed_filenames)}")
    print(f"Inserted ledger rows: {list(report.inserted_filenames)}")
    print(f"Committed: {report.committed}")


def main() -> None:
    """Run read-only preflight or the separately approved repair path."""

    args = parse_args()
    try:
        report = reconcile_legacy_migration_ledger(
            repair=args.repair,
            confirmation=args.confirm,
        )
    except MigrationLedgerAuthorizationError as error:
        raise SystemExit(str(error)) from error
    except MigrationLedgerReconciliationError as error:
        if error.report is not None:
            _print_report(error.report)
            path = _write_report(error.report, args.log_dir)
            print(f"Report: {path}")
        raise SystemExit(str(error)) from error

    _print_report(report)
    path = _write_report(report, args.log_dir)
    print(f"Report: {path}")


if __name__ == "__main__":
    main()
