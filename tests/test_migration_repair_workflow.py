"""Static safety checks for the manual migration-ledger repair workflow."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_repair_workflow_is_manual_and_exact_scope_only() -> None:
    """The one-time repair must never become scheduled or invoke normal updates."""

    workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "migration-ledger-repair.yml"
    ).read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "repair-legacy-008-009-and-ledger" in workflow
    assert "reconcile_migration_ledger.py" in workflow
    assert "update_hosted_data.py" not in workflow
    assert "apply_db_migrations.py" not in workflow
    assert "012_reconcile_scoreline_goal_contract.sql" not in workflow
    assert "cancel-in-progress: false" in workflow
