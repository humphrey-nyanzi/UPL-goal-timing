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


def test_repair_requires_exact_sha_before_database_secrets() -> None:
    """A stale or mistyped ref must fail before secrets are exposed."""

    workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "migration-ledger-repair.yml"
    ).read_text(encoding="utf-8")
    sha_gate = workflow.index("Validate exact authorized commit SHA")
    first_secret = workflow.index("secrets.POSTGRES_HOST")
    assert "expected_sha:" in workflow
    assert (
        "required: true"
        in workflow[workflow.index("expected_sha:") : workflow.index("confirmation:")]
    )
    assert 'test "$EXPECTED_SHA" = "$GITHUB_SHA"' in workflow
    assert sha_gate < first_secret
    assert "POSTGRES_HOST:" not in workflow[workflow.index("env:") : sha_gate]


def test_all_hosted_database_mutations_share_one_concurrency_group() -> None:
    """Repair cannot overlap routine, admin, or rebuild hosted update modes."""

    repair_workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "migration-ledger-repair.yml"
    ).read_text(encoding="utf-8")
    update_workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "current-season-update.yml"
    ).read_text(encoding="utf-8")
    group = "group: upl-lens-hosted-db-mutation"
    assert group in repair_workflow
    assert group in update_workflow
    assert "cancel-in-progress: false" in repair_workflow
    assert "cancel-in-progress: false" in update_workflow
