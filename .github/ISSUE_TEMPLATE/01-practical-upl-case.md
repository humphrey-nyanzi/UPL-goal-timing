---
name: Practical UPL Analytical Case
about: A bounded Uganda Premier League question that should end with evidence, findings, limitations, and a hard close
title: "[Case] "
labels: "area: analytical-casework, type: analytical-case"
assignees: ""
---

## Football Question

What exact Uganda Premier League question should this case answer?

## Why It Matters

Who would use the answer, what could they understand or decide, and why is the
question worth execution capacity?

## Scope And Definitions

- Season or time frame:
- Unit of analysis:
- Metric definitions and denominators:
- Included:
- Excluded:

## Data Requirements And Known Limits

- Expected `staging.*` or existing `analytics.*` inputs:
- Material fields and coverage needed:
- Known corrections, anomalies, missingness, or unresolved semantics:
- Immutable extract needed? If yes, which Issue #112 criterion justifies it?

## Proportionate Checks

List only checks that could change whether the question is answerable or the
finding is credible.

- Required before analysis:
- Required before reporting:
- Evidence to retain in `checks/`:

## Deliverables

- [ ] Case contract under `cases/<case-id>-<slug>/README.md`.
- [ ] Reproducible `analysis.ipynb` or an explicitly justified equivalent.
- [ ] Standalone `report.md` with evidence, limitations, and non-claims.
- [ ] Deliberate final artifacts in `outputs/`, if needed.

## Non-Goals

- No automatic analytics object, publication, API endpoint, React route, or
  continuing maintenance obligation.
- Additional non-goals:

## Close Condition

What minimum valid answer and retained evidence allow this case to close?

## Follow-Up Boundary

Accepted follow-up questions become separate ideas or Issues by default; they do
not silently extend this case.

## Case Folder

Add the repository path after the case is committed and created.

## Related Guidance

- `cases/README.md`
- `docs/FEATURE_PROMOTION_WORKFLOW.md`
- `docs/PRODUCT_STRATEGY.md`
