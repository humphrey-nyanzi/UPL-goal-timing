"""Opt-in disposable-Postgres coverage for legacy migration repair."""

from __future__ import annotations

import os

import pytest

from src.db.connection import get_psycopg_connection
from src.db.legacy_migration_repair import (
    REPAIR_CONFIRMATION,
    TARGET_FILENAMES,
    reconcile_legacy_migration_ledger,
)
from src.db.migrations import MIGRATIONS_DIR
from src.db.settings import DatabaseSettings

MIGRATIONS = {path.name: path for path in sorted(MIGRATIONS_DIR.glob("*.sql"))}
BASE_LEDGER = (
    "001_create_raw_schema.sql",
    "002_create_staging_foundation.sql",
    "003_create_staging_validation_runs.sql",
    "005_add_staging_source_anomaly_flags.sql",
)


def _settings() -> DatabaseSettings:
    database = os.getenv("UPL_TEST_POSTGRES_DB")
    if not database:
        pytest.skip("UPL_TEST_POSTGRES_DB is required for disposable integration tests")
    if "test" not in database.lower():
        pytest.fail("UPL_TEST_POSTGRES_DB must name a disposable test database")
    return DatabaseSettings(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=database,
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        sslmode=os.getenv("POSTGRES_SSLMODE", "prefer"),
    )


def _prepare(
    settings: DatabaseSettings,
    filenames: tuple[str, ...],
    *,
    revert_refresh_function: bool = False,
) -> None:
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS app_meta CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS analytics CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS staging CASCADE")
        connection.execute("DROP SCHEMA IF EXISTS raw CASCADE")
        for filename in filenames:
            connection.execute(MIGRATIONS[filename].read_text(encoding="utf-8"))
        if revert_refresh_function:
            connection.execute(
                MIGRATIONS["007_repair_analytics_team_season_summary.sql"].read_text(
                    encoding="utf-8"
                )
            )
        connection.execute("CREATE SCHEMA app_meta")
        connection.execute("""CREATE TABLE app_meta.schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )""")
        for filename in BASE_LEDGER:
            connection.execute(
                "INSERT INTO app_meta.schema_migrations (filename) VALUES (%s)",
                (filename,),
            )


def _ledger(settings: DatabaseSettings) -> set[str]:
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        rows = connection.execute(
            "SELECT filename FROM app_meta.schema_migrations"
        ).fetchall()
    return {str(row[0]) for row in rows}


@pytest.mark.parametrize(
    ("filenames", "revert_refresh_function"),
    [
        (
            (
                "001_create_raw_schema.sql",
                "002_create_staging_foundation.sql",
                "003_create_staging_validation_runs.sql",
                "004_add_staging_match_flags.sql",
                "005_add_staging_source_anomaly_flags.sql",
                "006_create_analytics_team_season_summary.sql",
                "007_repair_analytics_team_season_summary.sql",
                "010_add_timeline_coverage_fields.sql",
                "011_add_io_mitigation_indexes.sql",
            ),
            False,
        ),
        (
            tuple(
                name
                for name in MIGRATIONS
                if name <= "011_add_io_mitigation_indexes.sql"
                and name != "009_backfill_team_summary_admin_fields.sql"
            ),
            True,
        ),
        (
            tuple(
                name
                for name in MIGRATIONS
                if name <= "011_add_io_mitigation_indexes.sql"
                and name != "009_backfill_team_summary_admin_fields.sql"
            ),
            False,
        ),
        (
            tuple(
                name
                for name in MIGRATIONS
                if name <= "011_add_io_mitigation_indexes.sql"
            ),
            False,
        ),
    ],
)
def test_disposable_repair_handles_absent_partial_ambiguous_and_complete_states(
    filenames: tuple[str, ...],
    revert_refresh_function: bool,
) -> None:
    """Every authorized 008/009 drift state converges and repeats safely."""

    settings = _settings()
    _prepare(
        settings,
        filenames,
        revert_refresh_function=revert_refresh_function,
    )

    report = reconcile_legacy_migration_ledger(
        settings=settings,
        repair=True,
        confirmation=REPAIR_CONFIRMATION,
    )
    assert report.committed is True
    assert report.final_contract_satisfied is True
    assert set(TARGET_FILENAMES).issubset(_ledger(settings))

    repeated = reconcile_legacy_migration_ledger(
        settings=settings,
        repair=True,
        confirmation=REPAIR_CONFIRMATION,
    )
    assert repeated.committed is True
    assert repeated.inserted_filenames == ()


def test_disposable_repair_rolls_back_when_proven_prerequisite_is_removed() -> None:
    """A missing migration-004 effect prevents all repair and ledger writes."""

    settings = _settings()
    filenames = tuple(
        name for name in MIGRATIONS if name <= "011_add_io_mitigation_indexes.sql"
    )
    _prepare(settings, filenames)
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        connection.execute("DROP INDEX staging.idx_staging_matches_is_forfeit")

    with pytest.raises(Exception, match="Non-replayable migration effects"):
        reconcile_legacy_migration_ledger(
            settings=settings,
            repair=True,
            confirmation=REPAIR_CONFIRMATION,
        )

    assert not set(TARGET_FILENAMES).intersection(_ledger(settings))
