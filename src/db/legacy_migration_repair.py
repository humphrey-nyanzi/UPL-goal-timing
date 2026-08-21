"""Fail-closed repair for legacy custom migration-ledger drift.

The hosted schema was advanced outside the repository migration runner. This
module keeps inspection read-only by default and limits the confirmed repair
to migrations 004 and 006 through 011. Migration 012 is never executed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.db.connection import get_psycopg_connection
from src.db.migrations import MIGRATIONS_DIR, MIGRATION_SCHEMA, MIGRATION_TABLE
from src.db.settings import DatabaseSettings

REPAIR_CONFIRMATION = "repair-legacy-008-009-and-ledger"
TARGET_FILENAMES = (
    "004_add_staging_match_flags.sql",
    "006_create_analytics_team_season_summary.sql",
    "007_repair_analytics_team_season_summary.sql",
    "008_add_admin_results_and_official_points.sql",
    "009_backfill_team_summary_admin_fields.sql",
    "010_add_timeline_coverage_fields.sql",
    "011_add_io_mitigation_indexes.sql",
)
PROVE_ONLY_FILENAMES = (
    "004_add_staging_match_flags.sql",
    "006_create_analytics_team_season_summary.sql",
    "007_repair_analytics_team_season_summary.sql",
    "010_add_timeline_coverage_fields.sql",
    "011_add_io_mitigation_indexes.sql",
)
REPLAY_FILENAMES = (
    "008_add_admin_results_and_official_points.sql",
    "009_backfill_team_summary_admin_fields.sql",
)


@dataclass(frozen=True)
class EffectCheck:
    """One read-only assertion for a durable migration effect."""

    name: str
    query: str


@dataclass(frozen=True)
class CheckResult:
    """Observed result for one migration-effect assertion."""

    name: str
    passed: bool


@dataclass(frozen=True)
class MigrationAssessment:
    """Ledger and effect state for one target migration."""

    filename: str
    ledger_recorded: bool
    checks: tuple[CheckResult, ...]

    @property
    def effects_proven(self) -> bool:
        """Return whether every required durable effect was observed."""

        return bool(self.checks) and all(check.passed for check in self.checks)

    @property
    def status(self) -> str:
        """Return an operator-facing state classification."""

        passed_count = sum(check.passed for check in self.checks)
        if not self.effects_proven:
            return "partial-or-ambiguous" if passed_count else "absent"
        if self.ledger_recorded:
            return "recorded-and-proven"
        return "present-unrecorded"


@dataclass(frozen=True)
class ReconciliationReport:
    """Read-only preflight or committed repair result."""

    repair_requested: bool
    authorization_satisfied: bool
    before: tuple[MigrationAssessment, ...]
    after: tuple[MigrationAssessment, ...]
    executed_filenames: tuple[str, ...] = ()
    inserted_filenames: tuple[str, ...] = ()
    committed: bool = False

    @property
    def prove_only_prerequisites_satisfied(self) -> bool:
        """Return whether migrations that cannot be replayed are proven."""

        states = {item.filename: item for item in self.before}
        return all(
            name in states and states[name].effects_proven
            for name in PROVE_ONLY_FILENAMES
        )

    @property
    def final_contract_satisfied(self) -> bool:
        """Return whether all effects and ledger rows are present."""

        states = {item.filename: item for item in self.after}
        return all(
            name in states
            and states[name].effects_proven
            and states[name].ledger_recorded
            for name in TARGET_FILENAMES
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable operator report."""

        return {
            "mode": "repair" if self.repair_requested else "read-only-preflight",
            "authorization_satisfied": self.authorization_satisfied,
            "prove_only_prerequisites_satisfied": (
                self.prove_only_prerequisites_satisfied
            ),
            "final_contract_satisfied": self.final_contract_satisfied,
            "executed_filenames": list(self.executed_filenames),
            "inserted_filenames": list(self.inserted_filenames),
            "committed": self.committed,
            "before": [_assessment_dict(item) for item in self.before],
            "after": [_assessment_dict(item) for item in self.after],
        }


class MigrationLedgerReconciliationError(RuntimeError):
    """Raised when repair cannot safely continue or commit."""

    def __init__(
        self, message: str, report: ReconciliationReport | None = None
    ) -> None:
        self.report = report
        super().__init__(message)


class MigrationLedgerAuthorizationError(MigrationLedgerReconciliationError):
    """Raised before connecting when the explicit repair gate is missing."""


def _assessment_dict(item: MigrationAssessment) -> dict[str, object]:
    return {
        "filename": item.filename,
        "ledger_recorded": item.ledger_recorded,
        "effects_proven": item.effects_proven,
        "status": item.status,
        "checks": [
            {"name": check.name, "passed": check.passed} for check in item.checks
        ],
    }


def _column_check(
    schema: str,
    table: str,
    column: str,
    data_type: str,
    *,
    nullable: str | None = None,
    default_contains: str | None = None,
) -> EffectCheck:
    predicates = [
        f"table_schema = '{schema}'",
        f"table_name = '{table}'",
        f"column_name = '{column}'",
        f"data_type = '{data_type}'",
    ]
    if nullable:
        predicates.append(f"is_nullable = '{nullable}'")
    if default_contains:
        predicates.append(
            f"POSITION('{default_contains.lower()}' "
            "IN LOWER(COALESCE(column_default, ''))) > 0"
        )
    return EffectCheck(
        f"column {schema}.{table}.{column}",
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE "
        + " AND ".join(predicates)
        + ")",
    )


def _columns_check(schema: str, table: str, columns: tuple[str, ...]) -> EffectCheck:
    quoted = ", ".join(f"'{name}'" for name in columns)
    return EffectCheck(
        f"required columns {schema}.{table}",
        f"SELECT COUNT(*) = {len(columns)} FROM information_schema.columns "
        f"WHERE table_schema = '{schema}' AND table_name = '{table}' "
        f"AND column_name IN ({quoted})",
    )


def _index_check(schema: str, table: str, name: str) -> EffectCheck:
    return EffectCheck(
        f"index {schema}.{name}",
        "SELECT EXISTS (SELECT 1 FROM pg_indexes "
        f"WHERE schemaname = '{schema}' AND tablename = '{table}' "
        f"AND indexname = '{name}')",
    )


def _function_check(*fragments: str) -> EffectCheck:
    definition = (
        "LOWER(COALESCE(pg_get_functiondef(TO_REGPROCEDURE("
        "'analytics.refresh_team_season_summary(text[])')), ''))"
    )
    predicates = " AND ".join(
        f"POSITION('{fragment.lower()}' IN {definition}) > 0" for fragment in fragments
    )
    return EffectCheck("analytics refresh function contract", "SELECT " + predicates)


def _primary_key_check(schema: str, table: str, columns: str) -> EffectCheck:
    return EffectCheck(
        f"primary key {schema}.{table}",
        f"""SELECT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON kcu.constraint_schema = tc.constraint_schema
             AND kcu.constraint_name = tc.constraint_name
            WHERE tc.table_schema = '{schema}'
              AND tc.table_name = '{table}'
              AND tc.constraint_type = 'PRIMARY KEY'
            GROUP BY tc.constraint_name
            HAVING STRING_AGG(kcu.column_name, ',' ORDER BY kcu.ordinal_position)
                = '{columns}'
        )""",
    )


def _rls_disabled_check(schema: str, table: str) -> EffectCheck:
    return EffectCheck(
        f"RLS disabled {schema}.{table}",
        f"""SELECT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = '{schema}'
              AND c.relname = '{table}'
              AND c.relrowsecurity IS FALSE
              AND c.relforcerowsecurity IS FALSE
        )""",
    )


def _migration_007_check() -> EffectCheck:
    definition = (
        "LOWER(COALESCE(pg_get_functiondef(TO_REGPROCEDURE("
        "'analytics.refresh_team_season_summary(text[])')), ''))"
    )
    return EffectCheck(
        "migration 007 function or proven admin-aware replacement",
        "SELECT POSITION('on conflict (season, team_name) do update' IN "
        + definition
        + ") > 0 OR (POSITION('administrative_matches' IN "
        + definition
        + ") > 0 AND POSITION('team_season_point_adjustments' IN "
        + definition
        + ") > 0)",
    )


ADMIN_MATCH_COLUMNS = (
    "is_administrative_result",
    "administrative_result_type",
    "administrative_note",
    "played_on_pitch",
    "home_awarded_points",
    "away_awarded_points",
)
ADMIN_SUMMARY_COLUMNS = (
    "played_matches",
    "administrative_matches",
    "expected_matches",
    "missing_matches",
    "sporting_points",
    "administrative_points",
    "points_adjustment",
    "official_points",
    "points_note",
)
TIMELINE_COLUMNS = (
    "timeline_status",
    "timeline_issue_count",
    "timeline_note",
    "scoreline_goal_count",
    "timeline_goal_count",
    "stats_assist_count",
    "timeline_assist_count",
    "stats_yellow_card_count",
    "timeline_yellow_card_count",
    "stats_red_card_count",
    "timeline_red_card_count",
)
IO_INDEXES = (
    ("raw", "matches", "idx_raw_matches_season_key_order"),
    ("raw", "events", "idx_raw_events_season_key_match"),
    ("raw", "lineups", "idx_raw_lineups_season_key_match"),
    ("raw", "staff", "idx_raw_staff_season_key_match"),
    ("raw", "officials", "idx_raw_officials_season_key_match"),
    ("raw", "stats", "idx_raw_stats_season_key_match"),
    ("raw", "failed_matches", "idx_raw_failed_matches_season_key_url"),
    ("staging", "matches", "idx_staging_matches_app_safe_season_date"),
    ("staging", "matches", "idx_staging_matches_app_safe_season_match_day"),
    ("staging", "events", "idx_staging_events_season_match_type"),
    ("staging", "lineups", "idx_staging_lineups_season_player_match"),
    ("staging", "events", "idx_staging_events_season_player_match"),
    ("staging", "events", "idx_staging_events_season_sub_in_match"),
    ("staging", "events", "idx_staging_events_season_sub_out_match"),
)


MIGRATION_CHECKS: dict[str, tuple[EffectCheck, ...]] = {
    TARGET_FILENAMES[0]: (
        _column_check(
            "staging",
            "matches",
            "is_forfeit",
            "boolean",
            nullable="NO",
            default_contains="false",
        ),
        _index_check("staging", "matches", "idx_staging_matches_is_forfeit"),
    ),
    TARGET_FILENAMES[1]: (
        _columns_check(
            "analytics",
            "team_season_summary",
            (
                "season",
                "team_name",
                "matches_played",
                "goals_for",
                "goals_against",
                "wins",
                "draws",
                "losses",
                "refreshed_at",
            ),
        ),
        _index_check(
            "analytics", "team_season_summary", "idx_team_season_summary_team_name"
        ),
        EffectCheck(
            "analytics refresh function exists",
            "SELECT TO_REGPROCEDURE("
            "'analytics.refresh_team_season_summary(text[])') IS NOT NULL",
        ),
        _primary_key_check("analytics", "team_season_summary", "season,team_name"),
        _rls_disabled_check("analytics", "team_season_summary"),
    ),
    TARGET_FILENAMES[2]: (_migration_007_check(),),
    TARGET_FILENAMES[3]: (
        _columns_check("staging", "matches", ADMIN_MATCH_COLUMNS),
        _index_check("staging", "matches", "idx_staging_matches_admin_result"),
        _columns_check("analytics", "team_season_summary", ADMIN_SUMMARY_COLUMNS),
        _columns_check(
            "analytics",
            "team_season_point_adjustments",
            ("season", "team_name", "points_adjustment", "note", "updated_at"),
        ),
        _primary_key_check(
            "analytics", "team_season_point_adjustments", "season,team_name"
        ),
        _rls_disabled_check("analytics", "team_season_point_adjustments"),
        _function_check(
            "administrative_matches",
            "home_awarded_points",
            "played_on_pitch",
            "team_season_point_adjustments",
        ),
    ),
    TARGET_FILENAMES[4]: (
        _function_check("administrative_matches", "team_season_point_adjustments"),
        EffectCheck(
            "team summary post-refresh invariants",
            """SELECT NOT EXISTS (
                SELECT 1 FROM analytics.team_season_summary AS summary
                WHERE COALESCE(
                        (TO_JSONB(summary)->>'played_matches')::integer, 0
                      ) < 0
                   OR COALESCE(
                        (TO_JSONB(summary)->>'played_matches')::integer, 0
                      ) > summary.matches_played
                   OR COALESCE(
                        (TO_JSONB(summary)->>'administrative_matches')::integer, 0
                      ) < 0
                   OR COALESCE(
                        (TO_JSONB(summary)->>'administrative_matches')::integer, 0
                      ) > summary.matches_played
                   OR (TO_JSONB(summary)->>'official_points')::integer
                      IS DISTINCT FROM
                      (TO_JSONB(summary)->>'sporting_points')::integer
                      + COALESCE((TO_JSONB(summary)->>'points_adjustment')::integer, 0)
            )""",
        ),
    ),
    TARGET_FILENAMES[5]: (
        _columns_check("staging", "matches", TIMELINE_COLUMNS),
        _column_check(
            "staging",
            "matches",
            "timeline_status",
            "text",
            nullable="NO",
            default_contains="unknown",
        ),
        _index_check("staging", "matches", "idx_staging_matches_timeline_status"),
    ),
    TARGET_FILENAMES[6]: tuple(_index_check(*item) for item in IO_INDEXES),
}


def _ledger_filenames(connection) -> set[str]:
    """Read the custom migration ledger without creating it."""

    exists = connection.execute(
        "SELECT TO_REGCLASS('app_meta.schema_migrations') IS NOT NULL"
    ).fetchone()[0]
    if not exists:
        raise MigrationLedgerReconciliationError(
            "app_meta.schema_migrations does not exist; repair cannot create it"
        )
    rows = connection.execute(
        f"SELECT filename FROM {MIGRATION_SCHEMA}.{MIGRATION_TABLE}"
    ).fetchall()
    return {str(row[0]) for row in rows}


def inspect_legacy_migration_effects(connection) -> tuple[MigrationAssessment, ...]:
    """Inspect ledger and durable effects using SELECT-only statements."""

    recorded = _ledger_filenames(connection)
    return tuple(
        MigrationAssessment(
            filename=filename,
            ledger_recorded=filename in recorded,
            checks=tuple(
                CheckResult(
                    check.name,
                    bool(connection.execute(check.query).fetchone()[0]),
                )
                for check in MIGRATION_CHECKS[filename]
            ),
        )
        for filename in TARGET_FILENAMES
    )


def _migration_sql(filename: str) -> str:
    """Read exact repository-tracked migration SQL."""

    path: Path = MIGRATIONS_DIR / filename
    if not path.is_file():
        raise MigrationLedgerReconciliationError(
            f"Required repository migration is missing: {path}"
        )
    return path.read_text(encoding="utf-8")


def reconcile_legacy_migration_ledger(
    *,
    settings: DatabaseSettings | None = None,
    repair: bool = False,
    confirmation: str | None = None,
) -> ReconciliationReport:
    """Run a read-only preflight or the exact owner-approved repair."""

    authorized = confirmation == REPAIR_CONFIRMATION
    if repair and not authorized:
        report = ReconciliationReport(True, False, (), ())
        raise MigrationLedgerAuthorizationError(
            "Repair mode requires --confirm " + REPAIR_CONFIRMATION,
            report,
        )

    with get_psycopg_connection(settings=settings) as connection:
        try:
            if repair:
                connection.execute(
                    f"LOCK TABLE {MIGRATION_SCHEMA}.{MIGRATION_TABLE} "
                    "IN SHARE ROW EXCLUSIVE MODE"
                )
            else:
                connection.execute("SET TRANSACTION READ ONLY")

            before = inspect_legacy_migration_effects(connection)
            preflight = ReconciliationReport(repair, authorized, before, before)
            if not repair:
                connection.rollback()
                return preflight

            if not preflight.prove_only_prerequisites_satisfied:
                blocked = [
                    item.filename
                    for item in before
                    if item.filename in PROVE_ONLY_FILENAMES and not item.effects_proven
                ]
                raise MigrationLedgerReconciliationError(
                    "Non-replayable migration effects are not proven: "
                    + ", ".join(blocked),
                    preflight,
                )

            executed: list[str] = []
            for filename in REPLAY_FILENAMES:
                connection.execute(_migration_sql(filename))
                executed.append(filename)

            after_effects = inspect_legacy_migration_effects(connection)
            failed = [
                item.filename for item in after_effects if not item.effects_proven
            ]
            if failed:
                report = ReconciliationReport(
                    True, True, before, after_effects, tuple(executed)
                )
                raise MigrationLedgerReconciliationError(
                    "Repair postconditions failed: " + ", ".join(failed), report
                )

            recorded = {item.filename for item in after_effects if item.ledger_recorded}
            inserted: list[str] = []
            for filename in TARGET_FILENAMES:
                if filename in recorded:
                    continue
                connection.execute(
                    f"INSERT INTO {MIGRATION_SCHEMA}.{MIGRATION_TABLE} "
                    "(filename) VALUES (%s)",
                    (filename,),
                )
                inserted.append(filename)

            final = inspect_legacy_migration_effects(connection)
            report = ReconciliationReport(
                True, True, before, final, tuple(executed), tuple(inserted)
            )
            if not report.final_contract_satisfied:
                raise MigrationLedgerReconciliationError(
                    "Final migration effects or ledger rows are incomplete", report
                )

            connection.commit()
            return ReconciliationReport(
                True,
                True,
                before,
                final,
                tuple(executed),
                tuple(inserted),
                committed=True,
            )
        except Exception:
            connection.rollback()
            raise
