"""Exact catalog assertions for the bounded legacy migration repair."""

from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ContractCheck:
    """One exact read-only schema assertion."""

    name: str
    query: str


def _lit(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _column(
    schema: str,
    table: str,
    name: str,
    data_type: str,
    nullable: bool,
    default: str | None,
) -> ContractCheck:
    default_check = (
        "ad.adbin IS NULL"
        if default is None
        else (
            "LOWER(REGEXP_REPLACE(pg_get_expr(ad.adbin, ad.adrelid), '\\s+', '', 'g')) = "
            + _lit(default.lower())
        )
    )
    return ContractCheck(
        f"exact column {schema}.{table}.{name}",
        f"""SELECT EXISTS (
      SELECT 1 FROM pg_attribute a
      JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace
      LEFT JOIN pg_attrdef ad ON ad.adrelid=a.attrelid AND ad.adnum=a.attnum
      WHERE n.nspname={_lit(schema)} AND c.relname={_lit(table)} AND a.attname={_lit(name)}
        AND a.attnum>0 AND NOT a.attisdropped
        AND format_type(a.atttypid,a.atttypmod)={_lit(data_type)}
        AND a.attnotnull IS {str(not nullable).upper()} AND {default_check})""",
    )


def _index(schema: str, table: str, name: str, body: str) -> ContractCheck:
    definition = f"CREATE INDEX {name} ON {schema}.{table} USING btree ({body})"
    normalized = re.sub(r"\s+", "", definition.lower())
    return ContractCheck(
        f"exact index {schema}.{name}",
        f"""SELECT EXISTS (
      SELECT 1 FROM pg_class idx JOIN pg_namespace n ON n.oid=idx.relnamespace
      JOIN pg_index i ON i.indexrelid=idx.oid JOIN pg_class tbl ON tbl.oid=i.indrelid
      WHERE n.nspname={_lit(schema)} AND tbl.relname={_lit(table)} AND idx.relname={_lit(name)}
        AND i.indisvalid AND i.indisready
        AND LOWER(REGEXP_REPLACE(pg_get_indexdef(idx.oid), '\\s+', '', 'g'))={_lit(normalized)})""",
    )


def _function_digest(filename: str) -> str:
    path = Path(__file__).resolve().parents[2] / "database" / "migrations" / filename
    match = re.search(
        r"\bAS\s+\$\$(.*?)\$\$", path.read_text(encoding="utf-8"), re.I | re.S
    )
    if not match:
        raise RuntimeError(f"Function body missing from {path}")
    normalized = re.sub(r"\s+", "", match.group(1).lower())
    return hashlib.md5(normalized.encode(), usedforsecurity=False).hexdigest()


FUNCTION_007_DIGEST = _function_digest("007_repair_analytics_team_season_summary.sql")
FUNCTION_008_DIGEST = _function_digest("008_add_admin_results_and_official_points.sql")


def _function(*digests: str) -> ContractCheck:
    accepted = ",".join(_lit(value) for value in digests)
    return ContractCheck(
        "exact analytics refresh function contract",
        f"""SELECT EXISTS (
      SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
      JOIN pg_language l ON l.oid=p.prolang
      WHERE n.nspname='analytics' AND p.proname='refresh_team_season_summary'
        AND pg_get_function_identity_arguments(p.oid)='_target_seasons text[]'
        AND pg_get_function_result(p.oid)='void' AND l.lanname='plpgsql'
        AND p.provolatile='v' AND p.prosecdef IS FALSE
        AND MD5(REGEXP_REPLACE(LOWER(p.prosrc), '\\s+', '', 'g')) IN ({accepted}))""",
    )


def _columns(schema: str, table: str, specs):
    return tuple(_column(schema, table, *spec) for spec in specs)


BASE = (
    ("season", "text", False, None),
    ("team_name", "text", False, None),
    ("matches_played", "integer", False, "0"),
    ("goals_for", "integer", False, "0"),
    ("goals_against", "integer", False, "0"),
    ("wins", "integer", False, "0"),
    ("draws", "integer", False, "0"),
    ("losses", "integer", False, "0"),
    ("refreshed_at", "timestamp with time zone", False, "now()"),
)
ADMIN_MATCH = (
    ("is_administrative_result", "boolean", False, "false"),
    ("administrative_result_type", "text", True, None),
    ("administrative_note", "text", True, None),
    ("played_on_pitch", "boolean", False, "true"),
    ("home_awarded_points", "integer", True, None),
    ("away_awarded_points", "integer", True, None),
)
ADMIN_SUMMARY = (
    ("played_matches", "integer", False, "0"),
    ("administrative_matches", "integer", False, "0"),
    ("expected_matches", "integer", True, None),
    ("missing_matches", "integer", False, "0"),
    ("sporting_points", "integer", False, "0"),
    ("administrative_points", "integer", False, "0"),
    ("points_adjustment", "integer", False, "0"),
    ("official_points", "integer", False, "0"),
    ("points_note", "text", True, None),
)
ADJUSTMENT = (
    ("season", "text", False, None),
    ("team_name", "text", False, None),
    ("points_adjustment", "integer", False, "0"),
    ("note", "text", True, None),
    ("updated_at", "timestamp with time zone", False, "now()"),
)
TIMELINE = (
    ("timeline_status", "text", False, "'unknown'::text"),
    ("timeline_issue_count", "integer", False, "0"),
    ("timeline_note", "text", True, None),
    ("scoreline_goal_count", "integer", True, None),
    ("timeline_goal_count", "integer", True, None),
    ("stats_assist_count", "integer", True, None),
    ("timeline_assist_count", "integer", True, None),
    ("stats_yellow_card_count", "integer", True, None),
    ("timeline_yellow_card_count", "integer", True, None),
    ("stats_red_card_count", "integer", True, None),
    ("timeline_red_card_count", "integer", True, None),
)
IO = {
    (
        "raw",
        "matches",
        "idx_raw_matches_season_key_order",
    ): "replace(replace(season, '-'::text, '_'::text), '/'::text, '_'::text), match_day, date, match_id",
    (
        "raw",
        "events",
        "idx_raw_events_season_key_match",
    ): "replace(replace(season, '-'::text, '_'::text), '/'::text, '_'::text), match_id, event_type",
    (
        "raw",
        "lineups",
        "idx_raw_lineups_season_key_match",
    ): "replace(replace(season, '-'::text, '_'::text), '/'::text, '_'::text), match_id",
    (
        "raw",
        "staff",
        "idx_raw_staff_season_key_match",
    ): "replace(replace(season, '-'::text, '_'::text), '/'::text, '_'::text), match_id",
    (
        "raw",
        "officials",
        "idx_raw_officials_season_key_match",
    ): "replace(replace(season, '-'::text, '_'::text), '/'::text, '_'::text), match_id",
    (
        "raw",
        "stats",
        "idx_raw_stats_season_key_match",
    ): "replace(replace(season, '-'::text, '_'::text), '/'::text, '_'::text), match_id",
    (
        "raw",
        "failed_matches",
        "idx_raw_failed_matches_season_key_url",
    ): "replace(replace(season, '-'::text, '_'::text), '/'::text, '_'::text), match_url",
    (
        "staging",
        "matches",
        "idx_staging_matches_app_safe_season_date",
    ): "season, match_date DESC, match_id DESC) WHERE (is_source_anomaly IS NOT TRUE",
    (
        "staging",
        "matches",
        "idx_staging_matches_app_safe_season_match_day",
    ): "season, match_day, match_id) WHERE (is_source_anomaly IS NOT TRUE",
    (
        "staging",
        "events",
        "idx_staging_events_season_match_type",
    ): "season, match_id, event_type",
    (
        "staging",
        "lineups",
        "idx_staging_lineups_season_player_match",
    ): "season, player_name, match_id) WHERE (player_name IS NOT NULL",
    (
        "staging",
        "events",
        "idx_staging_events_season_player_match",
    ): "season, player_name, match_id) WHERE (player_name IS NOT NULL",
    (
        "staging",
        "events",
        "idx_staging_events_season_sub_in_match",
    ): "season, sub_in_player_name, match_id) WHERE (sub_in_player_name IS NOT NULL",
    (
        "staging",
        "events",
        "idx_staging_events_season_sub_out_match",
    ): "season, sub_out_player_name, match_id) WHERE (sub_out_player_name IS NOT NULL",
}
FULL_CONTRACT_CHECKS = {
    "004_add_staging_match_flags.sql": (
        _column("staging", "matches", "is_forfeit", "boolean", False, "false"),
        _index("staging", "matches", "idx_staging_matches_is_forfeit", "is_forfeit"),
    ),
    "006_create_analytics_team_season_summary.sql": (
        *_columns("analytics", "team_season_summary", BASE),
        _index(
            "analytics",
            "team_season_summary",
            "idx_team_season_summary_team_name",
            "team_name",
        ),
    ),
    "007_repair_analytics_team_season_summary.sql": (
        _function(FUNCTION_007_DIGEST, FUNCTION_008_DIGEST),
    ),
    "008_add_admin_results_and_official_points.sql": (
        *_columns("staging", "matches", ADMIN_MATCH),
        *_columns("analytics", "team_season_summary", ADMIN_SUMMARY),
        *_columns("analytics", "team_season_point_adjustments", ADJUSTMENT),
        _index(
            "staging",
            "matches",
            "idx_staging_matches_admin_result",
            "is_administrative_result",
        ),
        _function(FUNCTION_008_DIGEST),
    ),
    "009_backfill_team_summary_admin_fields.sql": (_function(FUNCTION_008_DIGEST),),
    "010_add_timeline_coverage_fields.sql": (
        *_columns("staging", "matches", TIMELINE),
        _index(
            "staging",
            "matches",
            "idx_staging_matches_timeline_status",
            "timeline_status",
        ),
    ),
    "011_add_io_mitigation_indexes.sql": tuple(
        _index(*key, body) for key, body in IO.items()
    ),
}
