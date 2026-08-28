"""Regression tests for the practical UPL analytical-case package."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "cases" / "_case_template"


def test_case_template_has_the_minimum_bounded_package() -> None:
    """Keep the active case template small, complete, and product-independent."""

    required_paths = {
        TEMPLATE / "README.md",
        TEMPLATE / "analysis.ipynb",
        TEMPLATE / "report.md",
        TEMPLATE / "checks" / "README.md",
        TEMPLATE / "outputs" / "README.md",
    }
    assert all(path.is_file() for path in required_paths)
    assert not (TEMPLATE / "product_plan.md").exists()


def test_case_contract_contains_scope_evidence_and_closure_guards() -> None:
    """Prevent drift back to topic-only analysis or automatic product promotion."""

    contract = (TEMPLATE / "README.md").read_text(encoding="utf-8").lower()
    required_terms = (
        "primary analytical question",
        "season or time frame",
        "unit of analysis",
        "metric definitions and denominators",
        "data-state",
        "quality and governance checks",
        "minimum valid completion",
        "stop and expansion rules",
        "no automatic api, react, dashboard",
    )
    assert all(term in contract for term in required_terms)


def test_case_contract_exposes_the_minimum_data_state_record() -> None:
    """Keep Issue #112 provenance fields visible to every case author."""

    contract = (TEMPLATE / "README.md").read_text(encoding="utf-8").lower()
    required_terms = (
        "analysis date",
        "maintained database or approved immutable extract",
        "data-state timestamp",
        "season or seasons",
        "row grain",
        "query filters, joins, exclusions, and missing-data treatment",
        "git commit and notebook/script/sql revision",
        "migration/schema state",
        "staging-validation run and issue counts",
        "case-specific coverage checks and results",
        "known corrections, source anomalies, limitations, and unresolved semantics",
        "extract version/checksum",
    )
    assert all(term in contract for term in required_terms)


def test_case_notebook_is_valid_notebook_json() -> None:
    """Ensure a copied template opens as a notebook without regeneration."""

    notebook = json.loads((TEMPLATE / "analysis.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert notebook["cells"]
    cell_ids = [cell["id"] for cell in notebook["cells"]]
    assert len(cell_ids) == len(set(cell_ids))
    headings = {
        line.strip()
        for cell in notebook["cells"]
        if cell["cell_type"] == "markdown"
        for line in cell["source"]
        if line.startswith("## ")
    }
    assert headings == {
        "## TL;DR",
        "## Context & Methods",
        "## Data & Checks",
        "## Results",
        "## Takeaways & Limitations",
    }


def test_case_report_stands_alone_and_closes_without_product_work() -> None:
    """Keep the analytical answer complete without an API or frontend step."""

    report = (TEMPLATE / "report.md").read_text(encoding="utf-8").lower()
    required_terms = (
        "short answer",
        "supporting evidence",
        "interpretation",
        "limitations and non-claims",
        "data state and reproduction",
        "follow-up questions",
        "closure",
    )
    assert all(term in report for term in required_terms)

    reproduction_terms = (
        "analysis date and evidence source",
        "row grain",
        "query filters, joins, exclusions, and missing-data treatment",
        "git commit and notebook/script/sql revision",
        "staging-validation run and issue counts",
        "known corrections, source anomalies, limitations, and unresolved semantics",
    )
    assert all(term in report for term in reproduction_terms)


def test_active_guidance_uses_the_case_template_not_feature_promotion() -> None:
    """Prevent agent guidance from restoring the historical package by default."""

    workflow = (ROOT / "docs" / "FEATURE_PROMOTION_WORKFLOW.md").read_text(
        encoding="utf-8"
    )
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "cases/_case_template/" in workflow
    assert "cases/_case_template/" in agents
    assert "There is no default `product_plan.md`" in workflow
    assert "There is no default `product_plan.md`" in agents
    assert "notebooks/features/_feature_template/" in workflow
    assert "historical" in workflow.lower()


def test_canonical_diagram_describes_the_case_workflow_as_active() -> None:
    """Prevent the completed Issue #113 workflow from becoming prospective again."""

    diagram = (ROOT / "docs" / "diagram_collection.md").read_text(encoding="utf-8")

    assert "Active practical case package" in diagram
    assert "Closed-case evidence" in diagram
    assert "Prospective #113" not in diagram
