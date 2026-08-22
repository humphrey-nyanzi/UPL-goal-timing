"""Opt-in Postgres integration coverage for Issue #104's migration contract."""

from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path

import pytest

from src.api.query_services import common, insights, seasons
from src.api.query_services.overview import _team_signals
from src.api.query_services.teams import list_teams
from src.db.connection import get_psycopg_connection
from src.db.migrations import apply_pending_migrations
from src.db.settings import DatabaseSettings


def _test_settings() -> DatabaseSettings:
    database = os.getenv("UPL_TEST_POSTGRES_DB")
    if not database:
        pytest.skip(
            "UPL_TEST_POSTGRES_DB is required for the migration integration test."
        )
    if "test" not in database.lower():
        pytest.fail("UPL_TEST_POSTGRES_DB must name a disposable test database.")
    return DatabaseSettings(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=database,
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        sslmode=os.getenv("POSTGRES_SSLMODE", "prefer"),
    )


def test_migration_012_and_query_services_on_disposable_database(monkeypatch) -> None:
    """Execute migration 012 and read its public contracts from an isolated clone."""

    settings = _test_settings()
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        target = connection.execute("""
            SELECT event_row_key
            FROM staging.events
            WHERE season = '2025_26'
                AND match_id = 31655
                AND match_url = 'https://upl.co.ug/event/nec-fc-vs-sc-villa-3/'
                AND event_type = 'goal'
                AND team_name = 'SC Villa'
                AND player_name = 'Geofrey Gagganga'
            """).fetchall()
        assert len(target) == 1
        target_key = target[0][0]

        unrelated = connection.execute("""
            SELECT event_row_key
            FROM staging.events
            WHERE match_id = 31655
                AND event_type = 'yellow_card'
                AND player_name = 'Geofrey Gagganga'
            """).fetchall()
        assert len(unrelated) == 1
        unrelated_key = unrelated[0][0]

        hosted_like_minute = (
            "334",
            334,
            0,
            334,
            False,
            "90+",
        )
        connection.execute(
            """
            UPDATE staging.events
            SET event_minute_text = %s,
                minute_base = %s,
                minute_added = %s,
                minute_total = %s,
                is_added_time = %s,
                minute_period = %s
            WHERE event_row_key = %s
            """,
            (*hosted_like_minute, target_key),
        )
        connection.execute(
            """
            UPDATE staging.events
            SET event_minute_text = %s,
                minute_base = %s,
                minute_added = %s,
                minute_total = %s,
                is_added_time = %s,
                minute_period = %s
            WHERE event_row_key = %s
            """,
            (*hosted_like_minute, unrelated_key),
        )
        connection.execute(
            "UPDATE raw.events SET event_minute = '334' WHERE event_row_key = %s",
            (target_key,),
        )

    results = apply_pending_migrations(settings)
    migration = next(
        result
        for result in results
        if result.filename == "012_reconcile_scoreline_goal_contract.sql"
    )
    assert migration.applied is True

    migration_sql = (
        Path(__file__).resolve().parents[1]
        / "database"
        / "migrations"
        / "012_reconcile_scoreline_goal_contract.sql"
    ).read_text(encoding="utf-8")
    with get_psycopg_connection(settings=settings, autocommit=True) as connection:
        corrected = connection.execute(
            """
            SELECT event_minute_text, minute_base, minute_added, minute_total,
                   is_added_time, minute_period
            FROM staging.events
            WHERE event_row_key = %s
            """,
            (target_key,),
        ).fetchone()
        assert corrected == ("34", 34, 0, 34, False, "31-45")
        assert connection.execute(
            "SELECT event_minute FROM raw.events WHERE event_row_key = %s",
            (target_key,),
        ).fetchone() == ("334",)
        assert connection.execute(
            "SELECT minute_total, minute_period FROM staging.events WHERE event_row_key = %s",
            (unrelated_key,),
        ).fetchone() == (334, "90+")

        # Execute the SQL again directly to prove its cardinality guard accepts
        # the one already-corrected row and remains idempotent.
        connection.execute(migration_sql)
        assert (
            connection.execute(
                """
            SELECT event_minute_text, minute_base, minute_added, minute_total,
                   is_added_time, minute_period
            FROM staging.events
            WHERE event_row_key = %s
            """,
                (target_key,),
            ).fetchone()
            == ("34", 34, 0, 34, False, "31-45")
        )
        assert connection.execute(
            "SELECT minute_total, minute_period FROM staging.events WHERE event_row_key = %s",
            (unrelated_key,),
        ).fetchone() == (334, "90+")

    @contextmanager
    def test_api_connection():
        with get_psycopg_connection(settings=settings, autocommit=True) as connection:
            yield connection

    monkeypatch.setattr(common, "get_api_psycopg_connection", test_api_connection)

    teams = list_teams(season="2025_26", limit=500)
    by_name = {team["team_name"]: team for team in teams}
    buhimba = by_name["Buhimba United Saints FC"]
    assert (
        buhimba["sporting_points"],
        buhimba["points_adjustment"],
        buhimba["official_points"],
    ) == (
        15,
        -3,
        12,
    )
    assert "three-point deduction" in buhimba["points_note"]

    assert (by_name["SC Villa"]["goals_for"], by_name["SC Villa"]["goals_against"]) == (
        47,
        17,
    )
    assert (
        by_name["Vipers SC"]["goals_for"],
        by_name["Vipers SC"]["goals_against"],
    ) == (
        55,
        17,
    )
    defence_signals = [
        signal
        for signal in _team_signals(teams)
        if signal["signal"] == "Tightest defence (tie)"
    ]
    assert {signal["team_name"] for signal in defence_signals} == {
        "SC Villa",
        "Vipers SC",
    }

    overview = seasons.get_season_overview("2025_26")
    assert overview["goal_count"] == overview["scoreline_goal_count"] == 505
    assert overview["timeline_goal_count"] == 496

    goal_timing = insights.get_goal_timing_insight("2025_26")
    assert goal_timing["total_regular_time_goals"] == 462
    assert goal_timing["timeline_partial_match_count"] == 7
    assert goal_timing["timeline_administrative_result_count"] == 1
    assert goal_timing["timeline_mismatch_match_count"] == 4
