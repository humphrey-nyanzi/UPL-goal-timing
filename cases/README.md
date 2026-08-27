# Practical UPL Analytical Cases

This directory is the home for bounded investigations that answer genuine
Uganda Premier League football questions using the maintained data foundation.
It is separate from learning or assessment casework: choose the method because
it fits the football question, not because a technique needs practice.

## Start A Case

1. Confirm the question is specific enough to state the football problem,
   season or time frame, unit of analysis, important definitions, and intended
   answer.
2. Copy `cases/_case_template/` to a numbered, descriptive folder such as
   `cases/001-post-halftime-conceding/`.
3. Complete the case contract in the copied `README.md` before substantial
   analysis.
4. Query maintained Postgres read-only through `src.research.read_sql`. Use
   cleaned `staging.*` tables by default.
5. Keep only decision-relevant SQL, Python, and validation evidence in
   `checks/`.
6. Finish the reproducible path in `analysis.ipynb`, write the standalone
   answer in `report.md`, retain deliberate final artifacts in `outputs/`, and
   close the case when its stated done condition is met.

The full lifecycle, data-layer rules, expansion rules, and exceptional software
boundary are owned by
[`docs/FEATURE_PROMOTION_WORKFLOW.md`](../docs/FEATURE_PROMOTION_WORKFLOW.md).

## Naming

Use a stable numeric ID and a short football-question slug:

```text
cases/<three-digit-id>-<short-slug>/
```

Use the next available case ID. Record the owning GitHub Issue in the copied
case contract. Issue #116 owns Project-stage and Issue-template semantics; this
directory does not duplicate them.

## Hard Boundary

A case may finish as a notebook and report. Completion does not automatically
authorize an `analytics.*` object, FastAPI endpoint, React route, dashboard,
publication, or recurring maintenance obligation. Those require a separate
current Issue and explicit owner approval.
