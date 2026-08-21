"""Exact schema assertions for the legacy migration repair preflight."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractCheck:
    """One exact read-only schema assertion."""

    name: str
    query: str


def _column(
    schema: str,
    table: str,
    name: str,
    data_type: str,
    nullable: str,
    default_fragment: str | None,
) -> ContractCheck:
    if default_fragment is None:
        default_predicate = "column_default IS NULL"
    else:
        escaped = default_fragment.lower().replace("'", "''")
        default_predicate = (
            f"POSITION('{escaped}' IN LOWER(COALESCE(column_default, ''))) > 0"
        )
    return ContractCheck(
        f"exact column {schema}.{table}.{name}",
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        f"WHERE table_schema = '{schema}' AND table_name = '{table}' "
        f"AND column_name = '{name}' AND data_type = '{data_type}' "
        f"AND is_nullable = '{nullable}' AND {default_predicate})",
    )


def _index(
    schema: str,
    table: str,
    name: str,
    *definition_fragments: str,
) -> ContractCheck:
    fragments = " AND ".join(
        "POSITION('" + fragment.lower().replace("'", "''") + "' IN LOWER(indexdef)) > 0"
        for fragment in definition_fragments
    )
    return ContractCheck(
        f"exact index {schema}.{name}",
        "SELECT EXISTS (SELECT 1 FROM pg_indexes "
        f"WHERE schemaname = '{schema}' AND tablename = '{table}' "
        f"AND indexname = '{name}' AND {fragments})",
    )


def _columns(
    schema: str,
    table: str,
    specs: tuple[tuple[str, str, str, str | None], ...],
) -> tuple[ContractCheck, ...]:
    return tuple(_column(schema, table, *spec) for spec in specs)


BASE_SUMMARY_SPECS = (
    ("season", "text", "NO", None),
    ("team_name", "text", "NO", None),
    ("matches_played", "integer", "NO", "0"),
    ("goals_for", "integer", "NO", "0"),
    ("goals_against", "integer", "NO", "0"),
    ("wins", "integer", "NO", "0"),
    ("draws", "integer", "NO", "0"),
    ("losses", "integer", "NO", "0"),
    ("refreshed_at", "timestamp with time zone", "NO", "now()"),
)
ADMIN_MATCH_SPECS = (
    ("is_administrative_result", "boolean", "NO", "false"),
    ("administrative_result_type", "text", "YES", None),
    ("administrative_note", "text", "YES", None),
    ("played_on_pitch", "boolean", "NO", "true"),
    ("home_awarded_points", "integer", "YES", None),
    ("away_awarded_points", "integer", "YES", None),
)
ADMIN_SUMMARY_SPECS = (
    ("played_matches", "integer", "NO", "0"),
    ("administrative_matches", "integer", "NO", "0"),
    ("expected_matches", "integer", "YES", None),
    ("missing_matches", "integer", "NO", "0"),
    ("sporting_points", "integer", "NO", "0"),
    ("administrative_points", "integer", "NO", "0"),
    ("points_adjustment", "integer", "NO", "0"),
    ("official_points", "integer", "NO", "0"),
    ("points_note", "text", "YES", None),
)
ADJUSTMENT_SPECS = (
    ("season", "text", "NO", None),
    ("team_name", "text", "NO", None),
    ("points_adjustment", "integer", "NO", "0"),
    ("note", "text", "YES", None),
    ("updated_at", "timestamp with time zone", "NO", "now()"),
)
TIMELINE_SPECS = (
    ("timeline_status", "text", "NO", "unknown"),
    ("timeline_issue_count", "integer", "NO", "0"),
    ("timeline_note", "text", "YES", None),
    ("scoreline_goal_count", "integer", "YES", None),
    ("timeline_goal_count", "integer", "YES", None),
    ("stats_assist_count", "integer", "YES", None),
    ("timeline_assist_count", "integer", "YES", None),
    ("stats_yellow_card_count", "integer", "YES", None),
    ("timeline_yellow_card_count", "integer", "YES", None),
    ("stats_red_card_count", "integer", "YES", None),
    ("timeline_red_card_count", "integer", "YES", None),
)


FULL_CONTRACT_CHECKS: dict[str, tuple[ContractCheck, ...]] = {
    "004_add_staging_match_flags.sql": (
        _column("staging", "matches", "is_forfeit", "boolean", "NO", "false"),
        _index(
            "staging",
            "matches",
            "idx_staging_matches_is_forfeit",
            "using btree",
            "(is_forfeit)",
        ),
    ),
    "006_create_analytics_team_season_summary.sql": (
        *_columns("analytics", "team_season_summary", BASE_SUMMARY_SPECS),
        _index(
            "analytics",
            "team_season_summary",
            "idx_team_season_summary_team_name",
            "using btree",
            "(team_name)",
        ),
    ),
    "008_add_admin_results_and_official_points.sql": (
        *_columns("staging", "matches", ADMIN_MATCH_SPECS),
        *_columns("analytics", "team_season_summary", ADMIN_SUMMARY_SPECS),
        *_columns("analytics", "team_season_point_adjustments", ADJUSTMENT_SPECS),
        _index(
            "staging",
            "matches",
            "idx_staging_matches_admin_result",
            "using btree",
            "(is_administrative_result)",
        ),
    ),
    "010_add_timeline_coverage_fields.sql": (
        *_columns("staging", "matches", TIMELINE_SPECS),
        _index(
            "staging",
            "matches",
            "idx_staging_matches_timeline_status",
            "using btree",
            "(timeline_status)",
        ),
    ),
    "011_add_io_mitigation_indexes.sql": (
        _index(
            "raw",
            "matches",
            "idx_raw_matches_season_key_order",
            "replace(replace(season",
            "match_day",
            "date",
            "match_id",
        ),
        _index(
            "raw",
            "events",
            "idx_raw_events_season_key_match",
            "replace(replace(season",
            "match_id",
            "event_type",
        ),
        _index(
            "raw",
            "lineups",
            "idx_raw_lineups_season_key_match",
            "replace(replace(season",
            "match_id",
        ),
        _index(
            "raw",
            "staff",
            "idx_raw_staff_season_key_match",
            "replace(replace(season",
            "match_id",
        ),
        _index(
            "raw",
            "officials",
            "idx_raw_officials_season_key_match",
            "replace(replace(season",
            "match_id",
        ),
        _index(
            "raw",
            "stats",
            "idx_raw_stats_season_key_match",
            "replace(replace(season",
            "match_id",
        ),
        _index(
            "raw",
            "failed_matches",
            "idx_raw_failed_matches_season_key_url",
            "replace(replace(season",
            "match_url",
        ),
        _index(
            "staging",
            "matches",
            "idx_staging_matches_app_safe_season_date",
            "season",
            "match_date desc",
            "match_id desc",
            "is_source_anomaly",
        ),
        _index(
            "staging",
            "matches",
            "idx_staging_matches_app_safe_season_match_day",
            "season",
            "match_day",
            "match_id",
            "is_source_anomaly",
        ),
        _index(
            "staging",
            "events",
            "idx_staging_events_season_match_type",
            "season",
            "match_id",
            "event_type",
        ),
        _index(
            "staging",
            "lineups",
            "idx_staging_lineups_season_player_match",
            "season",
            "player_name",
            "match_id",
            "player_name is not null",
        ),
        _index(
            "staging",
            "events",
            "idx_staging_events_season_player_match",
            "season",
            "player_name",
            "match_id",
            "player_name is not null",
        ),
        _index(
            "staging",
            "events",
            "idx_staging_events_season_sub_in_match",
            "season",
            "sub_in_player_name",
            "match_id",
            "is not null",
        ),
        _index(
            "staging",
            "events",
            "idx_staging_events_season_sub_out_match",
            "season",
            "sub_out_player_name",
            "match_id",
            "is not null",
        ),
    ),
}
