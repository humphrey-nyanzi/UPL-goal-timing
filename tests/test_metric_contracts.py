"""Regression tests for Issue #104 metric-source contracts."""

from __future__ import annotations

from contextlib import nullcontext

from src.api.query_services import insights, seasons
from src.api.query_services.overview import _overview_notices
from src.api.query_services.trends import _shape_season_trend_row


def test_season_overview_uses_scoreline_goals_for_general_total(monkeypatch) -> None:
    """Overview's general goal count should not silently mean timeline goals."""

    monkeypatch.setattr(seasons, "get_api_psycopg_connection", lambda: nullcontext(object()))
    monkeypatch.setattr(
        seasons,
        "_fetch_one",
        lambda *args, **kwargs: {
            "season": "2025_26",
            "scope_key": "2025_26",
            "season_count": 1,
            "match_count": 240,
            "team_count": 16,
            "scoreline_goal_count": 505,
            "first_match_date": None,
            "latest_match_date": None,
        },
    )
    monkeypatch.setattr(
        seasons,
        "_fetch_all",
        lambda *args, **kwargs: [{"event_type": "goal", "count": 496}],
    )

    result = seasons.get_season_overview("2025_26")

    assert result is not None
    assert result["goal_count"] == 505
    assert result["scoreline_goal_count"] == 505
    assert result["timeline_goal_count"] == 496


def test_season_trend_keeps_scoreline_and_timeline_rates_distinct() -> None:
    """General scoring rates use scorelines while event rates stay named."""

    result = _shape_season_trend_row(
        {
            "season": "2025_26",
            "match_count": 240,
            "scoreline_goal_count": 505,
            "timeline_goal_count": 496,
            "yellow_card_count": 729,
            "red_card_count": 21,
            "home_wins": 106,
            "away_wins": 63,
            "draws": 71,
            "high_scoring_match_count": 87,
            "goal_heavy_match_count": 16,
            "timeline_complete_match_count": 232,
            "timeline_partial_match_count": 7,
            "timeline_unavailable_match_count": 0,
            "administrative_result_count": 1,
            "source_anomaly_count": 0,
        }
    )

    assert result["goals_per_match"] == 2.1042
    assert result["timeline_goals_per_match"] == 2.0667


def test_overview_scoring_notice_names_scoreline_source() -> None:
    """Viewer-facing Overview copy should agree with the metric source."""

    notices = _overview_notices(
        {
            "goals_per_match": 2.1042,
            "high_scoring_match_share": 0.3,
            "timeline_coverage_share": 1.0,
        }
    )

    assert notices[0]["text"] == "Recorded scorelines show 2.1042 goals per match."


def test_goal_timing_exposes_subset_and_timeline_coverage(monkeypatch) -> None:
    """Goal Timing should disclose how its subset relates to source totals."""

    interval_rows = [
        {
            "interval": "0-15",
            "start_minute": 1,
            "end_minute": 15,
            "goals": 10,
            "share": 1.0,
            "rank": 1,
        }
    ]
    monkeypatch.setattr(insights, "_fetch_all", lambda *args, **kwargs: interval_rows)
    monkeypatch.setattr(
        insights,
        "_fetch_one",
        lambda *args, **kwargs: {
            "season_count": 1,
            "match_count": 240,
            "scoreline_goal_count": 505,
            "timeline_goal_count": 496,
            "timeline_complete_match_count": 232,
            "timeline_partial_match_count": 7,
            "timeline_unavailable_match_count": 0,
            "timeline_administrative_result_count": 1,
            "timeline_mismatch_match_count": 4,
            "first_match_date": None,
            "last_match_date": None,
        },
    )

    result = insights.get_goal_timing_insight("2025_26")

    assert result["total_regular_time_goals"] == 10
    assert result["timeline_goal_count"] == 496
    assert result["scoreline_goal_count"] == 505
    assert result["timeline_partial_match_count"] == 7
    assert result["timeline_administrative_result_count"] == 1
    assert result["timeline_mismatch_match_count"] == 4
