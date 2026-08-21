"""Regression coverage for the bounded legacy migration repair."""

from __future__ import annotations

from contextlib import contextmanager

import pytest

from src.db import legacy_migration_repair as repair


class FakeResult:
    """Minimal psycopg-like result used by the unit tests."""

    def fetchone(self):
        return (True,)

    def fetchall(self):
        return []


class FakeConnection:
    """Record transaction and SQL behavior without a database."""

    def __init__(self) -> None:
        self.statements: list[tuple[object, object]] = []
        self.commits = 0
        self.rollbacks = 0

    def execute(self, statement, parameters=None):
        self.statements.append((statement, parameters))
        return FakeResult()

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _assessment(
    filename: str, *, proven: bool = True, recorded: bool = False
) -> repair.MigrationAssessment:
    return repair.MigrationAssessment(
        filename=filename,
        ledger_recorded=recorded,
        checks=(repair.CheckResult("contract", proven),),
    )


def _states(
    *, failed: set[str] | None = None, recorded: bool = False
) -> tuple[repair.MigrationAssessment, ...]:
    failed = failed or set()
    return tuple(
        _assessment(name, proven=name not in failed, recorded=recorded)
        for name in repair.TARGET_FILENAMES
    )


def _use_connection(monkeypatch, connection: FakeConnection) -> None:
    @contextmanager
    def fake_connection(*, settings=None):
        yield connection

    monkeypatch.setattr(repair, "get_psycopg_connection", fake_connection)


def test_repair_requires_exact_confirmation_before_connecting(monkeypatch) -> None:
    """A repair typo must fail before a database connection is opened."""

    def unexpected_connection(*, settings=None):
        raise AssertionError("database connection must not be opened")

    monkeypatch.setattr(repair, "get_psycopg_connection", unexpected_connection)

    with pytest.raises(repair.MigrationLedgerAuthorizationError):
        repair.reconcile_legacy_migration_ledger(
            repair=True,
            confirmation="almost-right",
        )


def test_default_preflight_is_read_only(monkeypatch) -> None:
    """Default mode inspects inside a read-only transaction and rolls back."""

    connection = FakeConnection()
    _use_connection(monkeypatch, connection)
    monkeypatch.setattr(
        repair, "inspect_legacy_migration_effects", lambda connection: _states()
    )

    report = repair.reconcile_legacy_migration_ledger()

    assert report.repair_requested is False
    assert report.committed is False
    assert connection.statements == [("SET TRANSACTION READ ONLY", None)]
    assert connection.commits == 0
    assert connection.rollbacks == 1


@pytest.mark.parametrize(
    "initial_failures",
    [
        {
            "008_add_admin_results_and_official_points.sql",
            "009_backfill_team_summary_admin_fields.sql",
        },
        {"008_add_admin_results_and_official_points.sql"},
        {"009_backfill_team_summary_admin_fields.sql"},
    ],
)
def test_repair_establishes_absent_partial_or_ambiguous_008_009(
    monkeypatch, initial_failures: set[str]
) -> None:
    """Exact 008 then 009 SQL establishes every authorized drift state."""

    connection = FakeConnection()
    _use_connection(monkeypatch, connection)
    inspections = iter(
        (
            _states(failed=initial_failures),
            _states(),
            _states(recorded=True),
        )
    )
    monkeypatch.setattr(
        repair,
        "inspect_legacy_migration_effects",
        lambda connection: next(inspections),
    )
    monkeypatch.setattr(repair, "_migration_sql", lambda name: f"SQL::{name}")

    report = repair.reconcile_legacy_migration_ledger(
        repair=True,
        confirmation=repair.REPAIR_CONFIRMATION,
    )

    sql = [statement for statement, _ in connection.statements]
    assert sql[1:3] == [
        "SQL::008_add_admin_results_and_official_points.sql",
        "SQL::009_backfill_team_summary_admin_fields.sql",
    ]
    assert report.executed_filenames == repair.REPLAY_FILENAMES
    assert report.inserted_filenames == repair.TARGET_FILENAMES
    assert report.final_contract_satisfied is True
    assert report.committed is True
    assert connection.commits == 1


def test_repair_refuses_missing_non_replayable_prerequisite(monkeypatch) -> None:
    """The tool does not invent older schema effects or write the ledger."""

    connection = FakeConnection()
    _use_connection(monkeypatch, connection)
    monkeypatch.setattr(
        repair,
        "inspect_legacy_migration_effects",
        lambda connection: _states(failed={repair.PROVE_ONLY_FILENAMES[0]}),
    )

    with pytest.raises(repair.MigrationLedgerReconciliationError):
        repair.reconcile_legacy_migration_ledger(
            repair=True,
            confirmation=repair.REPAIR_CONFIRMATION,
        )

    assert not any(str(item[0]).startswith("SQL::") for item in connection.statements)
    assert not any("INSERT INTO" in str(item[0]) for item in connection.statements)
    assert connection.commits == 0
    assert connection.rollbacks == 1


def test_postcondition_failure_rolls_back_before_ledger_write(monkeypatch) -> None:
    """A failed 009 postcondition rolls back both replayed migrations."""

    connection = FakeConnection()
    _use_connection(monkeypatch, connection)
    inspections = iter(
        (
            _states(failed={repair.REPLAY_FILENAMES[1]}),
            _states(failed={repair.REPLAY_FILENAMES[1]}),
        )
    )
    monkeypatch.setattr(
        repair,
        "inspect_legacy_migration_effects",
        lambda connection: next(inspections),
    )
    monkeypatch.setattr(repair, "_migration_sql", lambda name: f"SQL::{name}")

    with pytest.raises(repair.MigrationLedgerReconciliationError):
        repair.reconcile_legacy_migration_ledger(
            repair=True,
            confirmation=repair.REPAIR_CONFIRMATION,
        )

    assert not any("INSERT INTO" in str(item[0]) for item in connection.statements)
    assert connection.commits == 0
    assert connection.rollbacks == 1


def test_repeat_repair_is_idempotent(monkeypatch) -> None:
    """A fully reconciled database receives no duplicate ledger rows."""

    connection = FakeConnection()
    _use_connection(monkeypatch, connection)
    inspections = iter(
        (_states(recorded=True), _states(recorded=True), _states(recorded=True))
    )
    monkeypatch.setattr(
        repair,
        "inspect_legacy_migration_effects",
        lambda connection: next(inspections),
    )
    monkeypatch.setattr(repair, "_migration_sql", lambda name: f"SQL::{name}")

    report = repair.reconcile_legacy_migration_ledger(
        repair=True,
        confirmation=repair.REPAIR_CONFIRMATION,
    )

    assert report.inserted_filenames == ()
    assert report.committed is True
    assert not any("INSERT INTO" in str(item[0]) for item in connection.statements)
