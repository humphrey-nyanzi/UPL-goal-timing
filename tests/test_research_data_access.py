"""Regression coverage for read-only analytical case access."""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path

import pandas as pd
import pytest

from src.research import data_access


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM staging.matches",
        "WITH matches AS (SELECT 1) SELECT * FROM matches",
        "-- case coverage check\nEXPLAIN SELECT * FROM staging.events",
    ],
)
def test_read_only_validation_accepts_case_queries(query: str) -> None:
    """Normal case queries should pass the local SQL safety rail."""

    data_access._validate_read_only_query(query)


@pytest.mark.parametrize(
    "query",
    [
        "UPDATE staging.matches SET season = 'x'",
        "WITH removed AS (DELETE FROM staging.events RETURNING *) SELECT * FROM removed",
        "GRANT SELECT ON staging.matches TO analyst",
    ],
)
def test_read_only_validation_rejects_writes_and_permissions(query: str) -> None:
    """Write SQL must fail before a database connection is used."""

    with pytest.raises(ValueError, match="should not run write or permission SQL"):
        data_access._validate_read_only_query(query)


def test_read_sql_sets_transaction_read_only_before_case_query(monkeypatch) -> None:
    """The database transaction is a second safety rail behind SQL validation."""

    executed: list[str] = []
    expected = pd.DataFrame([{"match_count": 240}])

    class FakeConnection:
        def execute(self, statement) -> None:
            executed.append(str(statement))

    class FakeEngine:
        def connect(self):
            return nullcontext(FakeConnection())

    def fake_read_sql_query(statement, connection, params):
        executed.append(str(statement))
        assert isinstance(connection, FakeConnection)
        assert params == {"season": "2025_26"}
        return expected

    monkeypatch.setattr(
        data_access,
        "create_sqlalchemy_engine",
        lambda settings=None: FakeEngine(),
    )
    monkeypatch.setattr(data_access.pd, "read_sql_query", fake_read_sql_query)

    result = data_access.read_sql(
        "SELECT COUNT(*) AS match_count FROM staging.matches WHERE season = :season",
        {"season": "2025_26"},
    )

    assert result is expected
    assert executed == [
        "SET TRANSACTION READ ONLY;",
        "SELECT COUNT(*) AS match_count FROM staging.matches WHERE season = :season",
    ]


def test_research_reader_can_read_migration_provenance_without_write_grants() -> None:
    """The role template should expose provenance while remaining read-only."""

    permissions_path = (
        Path(__file__).resolve().parents[1]
        / "database"
        / "permissions"
        / "002_create_upl_research_reader.sql"
    )
    sql = permissions_path.read_text(encoding="utf-8")

    assert "GRANT USAGE ON SCHEMA app_meta TO upl_research_reader" in sql
    assert "ON app_meta.schema_migrations" in sql
    assert "ON ALL TABLES IN SCHEMA app_meta" not in sql
    assert "ALTER DEFAULT PRIVILEGES IN SCHEMA app_meta" not in sql
    assert "GRANT INSERT" not in sql
    assert "GRANT UPDATE" not in sql
    assert "GRANT DELETE" not in sql
