"""Opt-in Postgres integration coverage for Issue #104's migration contract."""

from __future__ import annotations

from contextlib import contextmanager
import os

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
    results = apply_pending_migrations(settings)
    migration = next(
        result
        for result in results
        if result.filename == "012_reconcile_scoreline_goal_contract.sql"
    )
    assert migration.applied is True

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
