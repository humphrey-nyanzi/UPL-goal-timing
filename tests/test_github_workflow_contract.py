"""Regression checks for the repository's GitHub work-management contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITHUB = ROOT / ".github"


def _read(relative_path: str) -> str:
    """Return a repository text file using a stable UTF-8 read."""

    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_project_workflow_uses_the_casework_transition_pipeline() -> None:
    workflow = _read(".github/project-workflow.yml")

    expected_statuses = (
        '  - "Inbox"',
        '  - "Scoping"',
        '  - "Ready"',
        '  - "In Progress"',
        '  - "Review / QA"',
        '  - "Done"',
        '  - "Parked"',
    )
    assert all(status in workflow for status in expected_statuses)
    assert '  - "Research"' not in workflow
    assert '  - "Released"' not in workflow

    for lane in (
        "area: data-foundation",
        "area: analytical-casework",
        "area: project-system",
        "area: retained-product",
    ):
        assert lane in workflow

    assert 'name: "Active Work"' in workflow
    assert 'name: "Workflow"' in workflow
    assert 'name: "History"' in workflow
    assert "notion_boundary:" in workflow
    assert "GitHub owns execution details" in workflow


def test_labels_separate_work_type_from_project_status() -> None:
    labels = _read(".github/labels.yml")

    for label in (
        "area: data-foundation",
        "area: analytical-casework",
        "area: retained-product",
        "area: project-system",
        "type: change",
        "type: analytical-case",
        "status: blocked",
    ):
        assert f'- name: "{label}"' in labels

    for obsolete_label in (
        "area: data-reliability",
        "area: research-intelligence",
        "area: product-experience",
        "area: developer-experience",
        "type: feature",
        "type: research",
        "status: ready",
        "status: in-progress",
        "status: needs-review",
        "status: validated",
    ):
        assert f'- name: "{obsolete_label}"' not in labels

    assert '- name: "legacy-status: needs-review"' in labels
    assert "the UPL Status Project field" in labels


def test_issue_templates_match_the_four_active_lanes() -> None:
    template_dir = GITHUB / "ISSUE_TEMPLATE"
    template_names = {path.name for path in template_dir.glob("*.md")}

    assert {
        "01-practical-upl-case.md",
        "02-retained-product-maintenance.md",
        "03-data-foundation-operations.md",
    }.issubset(template_names)
    assert "01-research-football-intelligence.md" not in template_names
    assert "02-product-experience-frontend.md" not in template_names
    assert "03-data-reliability-operations.md" not in template_names

    practical_case = _read(".github/ISSUE_TEMPLATE/01-practical-upl-case.md")
    assert "## Football Question" in practical_case
    assert "## Close Condition" in practical_case
    assert "## Follow-Up Boundary" in practical_case
    assert "area: analytical-casework" in practical_case
    assert "type: analytical-case" in practical_case

    for template in template_dir.glob("*.md"):
        assert "status: needs-" not in template.read_text(encoding="utf-8")


def test_obsolete_issue_drafts_are_not_retained_as_a_parallel_backlog() -> None:
    drafts = GITHUB / "ISSUE_DRAFTS"

    assert not drafts.exists() or not list(drafts.glob("*.md"))


def test_milestones_are_finite_history_not_standing_work_lanes() -> None:
    milestones = _read(".github/milestones.yml")

    assert "active: []" in milestones
    assert "historical:" in milestones
    assert "Milestones represent finite owner-approved goals" in milestones
    assert "ordinary practical cases do not receive a release milestone" in milestones


def test_canonical_guidance_uses_the_same_project_system_contract() -> None:
    canonical_text = "\n".join(
        _read(path)
        for path in (
            "AGENTS.md",
            "docs/START_HERE.md",
            "docs/PROJECT_ROADMAP.md",
            "docs/FEATURE_PROMOTION_WORKFLOW.md",
        )
    )

    for lane in (
        "Data Foundation & Operations",
        "UPL Analytical Casework",
        "Retained Product",
        "Project System & Documentation",
    ):
        assert lane in canonical_text

    assert (
        "Inbox -> Scoping -> Ready -> In Progress -> Review / QA -> Done"
        in canonical_text
    )
    assert "GitHub still owns execution" in canonical_text
    assert "Notion" in canonical_text
