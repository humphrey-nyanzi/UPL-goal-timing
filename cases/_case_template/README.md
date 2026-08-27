# Case Contract: [Bounded Football Question]

Status: `scoping`

Use one lifecycle state: `idea`, `scoping`, `ready`, `analysis`, `review`, or
`done`. Do not mark `ready` until another contributor could begin without
reconstructing chat history.

## Intended Use

Who needs to understand or decide what because of this case?

## Primary Analytical Question

State one answerable football question in plain language. Note whether the
answer will be descriptive, comparative, associational, predictive,
diagnostic, or exploratory when that distinction affects interpretation. Do
not make a causal claim unless the design supports it.

## Scope And Definitions

- Target population or entities:
- Season or time frame:
- Inclusion rules:
- Exclusion rules:
- Unit of analysis:
- Important metric definitions and denominators:

## Why It Matters

Explain the football value and the intended audience. Publication is optional
and is not required for completion.

## Evidence And Data State

- Case ID/title and analysis date:
- Evidence source: maintained database or approved immutable extract:
- Database environment and data-state timestamp/run reference:
- Season or seasons and coverage:
- Tables/views, material fields, and row grain:
- Query filters, joins, exclusions, and missing-data treatment:
- Git commit and notebook/script/SQL revision:
- Applied migration/schema state, when relevant:
- Latest relevant staging-validation run and issue counts:
- Case-specific coverage checks and results:
- Known corrections, source anomalies, limitations, and unresolved semantics:
- Extract version/checksum, only when an immutable extract is justified:

Default to maintained Postgres `staging.*` through the read-only research
access pattern. Use `raw.*` only for source investigation. Use an existing
`analytics.*` contract when it already expresses the needed metric. An
immutable extract is optional and must satisfy the criteria owned by Issue
#112; do not create one by habit.

## Case-Specific Quality And Governance Checks

List only checks that could change whether the question is answerable or the
finding is credible. Examples include relevant coverage, duplicate keys,
score/event reconciliation, exposure completeness, comparable definitions,
and privacy or attribution constraints.

- Required before analysis:
- Required before reporting:
- Evidence retained in `checks/`:

This is a proportionate case audit, not a full audit of every database domain.

## Method

Name the least complex defensible approach, its assumptions, and any required
sensitivity or validation checks. Do not select a technique merely to practise
it.

## Deliverables

- `analysis.ipynb`: reproducible analysis path.
- `report.md`: standalone answer, evidence, interpretation, and limitations.
- `checks/`: meaningful retained case checks only.
- `outputs/`: deliberate final figures, tables, or exports used by the report.

## Non-Goals

- No automatic API, React, dashboard, or public-product work.
- No unrelated follow-up question inside this case.
- [Add case-specific exclusions.]

## Minimum Valid Completion

Define observable criteria for a responsible answer. At minimum:

- the bounded question is answered as far as the evidence allows;
- scope, units, metrics, and data state are recorded;
- material coverage/quality checks pass or their failures are reflected in the
  claim;
- the notebook path to reported evidence is understandable;
- `report.md` contains the answer, evidence, limitations, and non-claims;
- deliberate outputs are retained and exploratory clutter is excluded.

## Stop And Expansion Rules

- Stop or rescope when:
- A follow-up question becomes a new backlog item or case when:
- A material change to population, source, metric, intended claim, or done
  condition requires explicit rescoping before analysis continues.

## Ownership

- GitHub Issue:
- Owner:
- Reviewer:
- Last scope decision/date:
