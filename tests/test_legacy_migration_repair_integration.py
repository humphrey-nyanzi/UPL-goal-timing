"""Opt-in disposable-Postgres coverage for legacy migration repair."""

from __future__ import annotations

import os

import pytest

from src.db.connection import get_psycopg_connection
from src.db.legacy_migration_repair import (
    REPAIR_CONFIRMATION,
    TARGET_FILENAMES,
    inspect_legacy_migration_effects,
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

    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        connection.execute("""INSERT INTO analytics.team_season_summary
            (season, team_name, refreshed_at)
            VALUES ('no-op-test', 'No Op FC', '2026-01-01T00:00:00Z')
            ON CONFLICT (season, team_name) DO UPDATE
            SET refreshed_at = EXCLUDED.refreshed_at""")
        before_row = connection.execute("""SELECT TO_JSONB(summary)
            FROM analytics.team_season_summary AS summary
            WHERE season='no-op-test' AND team_name='No Op FC'""").fetchone()[0]

    repeated = reconcile_legacy_migration_ledger(
        settings=settings,
        repair=True,
        confirmation=REPAIR_CONFIRMATION,
    )
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        after_row = connection.execute("""SELECT TO_JSONB(summary)
            FROM analytics.team_season_summary AS summary
            WHERE season='no-op-test' AND team_name='No Op FC'""").fetchone()[0]
    assert repeated.committed is False
    assert repeated.executed_filenames == ()
    assert repeated.inserted_filenames == ()
    assert after_row == before_row


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


def _assessment_map(settings: DatabaseSettings):
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        return {
            item.filename: item for item in inspect_legacy_migration_effects(connection)
        }


def test_exact_catalog_contract_rejects_adversarial_near_misses() -> None:
    """Defaults, complete index definitions, and function bodies must match exactly."""

    settings = _settings()
    filenames = tuple(
        name for name in MIGRATIONS if name <= "011_add_io_mitigation_indexes.sql"
    )
    _prepare(settings, filenames)
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        connection.execute(
            "ALTER TABLE analytics.team_season_summary ALTER COLUMN official_points SET DEFAULT 10"
        )
    assert not _assessment_map(settings)[
        "008_add_admin_results_and_official_points.sql"
    ].effects_proven

    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        connection.execute(
            "ALTER TABLE analytics.team_season_summary ALTER COLUMN official_points SET DEFAULT 0"
        )
        connection.execute("DROP INDEX staging.idx_staging_events_season_match_type")
        connection.execute(
            "CREATE INDEX idx_staging_events_season_match_type ON staging.events (season, match_id, event_type, player_name)"
        )
    assert not _assessment_map(settings)[
        "011_add_io_mitigation_indexes.sql"
    ].effects_proven

    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        connection.execute("DROP INDEX staging.idx_staging_events_season_match_type")
        connection.execute(
            MIGRATIONS["011_add_io_mitigation_indexes.sql"].read_text(encoding="utf-8")
        )
        near_miss = (
            MIGRATIONS["008_add_admin_results_and_official_points.sql"]
            .read_text(encoding="utf-8")
            .replace(
                "team_summary.sporting_points + COALESCE(adjustments.points_adjustment, 0)",
                "team_summary.sporting_points + 0 + COALESCE(adjustments.points_adjustment, 0)",
            )
        )
        connection.execute(near_miss)
    states = _assessment_map(settings)
    assert not states["008_add_admin_results_and_official_points.sql"].effects_proven
    assert not states["009_backfill_team_summary_admin_fields.sql"].effects_proven


def test_disposable_fault_after_replay_rolls_back_schema_data_function_and_ledger(
    monkeypatch,
) -> None:
    """One transaction protects every replay effect until ledger insertion succeeds."""

    settings = _settings()
    filenames = (
        "001_create_raw_schema.sql",
        "002_create_staging_foundation.sql",
        "003_create_staging_validation_runs.sql",
        "004_add_staging_match_flags.sql",
        "005_add_staging_source_anomaly_flags.sql",
        "006_create_analytics_team_season_summary.sql",
        "007_repair_analytics_team_season_summary.sql",
        "010_add_timeline_coverage_fields.sql",
        "011_add_io_mitigation_indexes.sql",
    )
    _prepare(settings, filenames)
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        connection.execute(
            """INSERT INTO staging.matches
            (match_id, match_url, season, home_team, away_team, home_score, away_score, result)
            VALUES (999001, 'test://fault', 'fault-test', 'Home FC', 'Away FC', 1, 0, 'home_win')"""
        )
        before_function = connection.execute(
            "SELECT prosrc FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='analytics' AND p.proname='refresh_team_season_summary'"
        ).fetchone()[0]
        before_match = connection.execute(
            "SELECT home_awarded_points, away_awarded_points FROM staging.matches WHERE match_id=999001"
        ).fetchone()
        before_ledger = _ledger(settings)

    from src.db import legacy_migration_repair as repair_module

    def injected_failure(connection) -> None:
        assert connection.execute(
            "SELECT TO_REGCLASS('analytics.team_season_point_adjustments') IS NOT NULL"
        ).fetchone()[0]
        assert (
            connection.execute(
                "SELECT home_awarded_points FROM staging.matches WHERE match_id=999001"
            ).fetchone()[0]
            == 3
        )
        raise RuntimeError("injected pre-ledger failure")

    monkeypatch.setattr(repair_module, "_before_ledger_inserts", injected_failure)

    with pytest.raises(RuntimeError, match="injected pre-ledger failure"):
        reconcile_legacy_migration_ledger(
            settings=settings, repair=True, confirmation=REPAIR_CONFIRMATION
        )

    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        assert connection.execute(
            "SELECT TO_REGCLASS('analytics.team_season_point_adjustments') IS NULL"
        ).fetchone()[0]
        after_function = connection.execute(
            "SELECT prosrc FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='analytics' AND p.proname='refresh_team_season_summary'"
        ).fetchone()[0]
        after_match = connection.execute(
            "SELECT home_awarded_points, away_awarded_points FROM staging.matches WHERE match_id=999001"
        ).fetchone()
        summary_count = connection.execute(
            "SELECT COUNT(*) FROM analytics.team_season_summary WHERE season='fault-test'"
        ).fetchone()[0]
    assert after_function == before_function
    assert after_match == before_match
    assert summary_count == 0
    assert _ledger(settings) == before_ledger
