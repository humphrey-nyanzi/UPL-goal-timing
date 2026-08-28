# Practical UPL Case Workflow And Exceptional Promotion

This document is the research and practical-casework playbook for the
repository's UPL Analytical Casework lane.

It now owns:

- practical-case selection and scope
- practical UPL case lifecycle status
- historical feature lifecycle status
- standard case package workflow
- notebook data-source rules
- case-specific reproducibility records
- decisions for `staging.*` versus `analytics.*`
- exceptional, owner-approved software promotion into FastAPI or React

Use this doc with [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md) and
[PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).

## Core Rule

Notebook research can be exploratory. Practical UPL cases must close with a
bounded evidence package:

```text
football question
  -> scope and explicit non-goals
  -> database state and proportionate checks
  -> read-only notebook and SQL checks over maintained Postgres
  -> findings, limitations, report, and deliberate outputs
  -> hard close
```

The active data foundation is maintained Postgres plus case-specific
reproducibility records. Do not replace that with a frozen central snapshot
model.

Software promotion is now exceptional. If a current Issue and owner instruction
explicitly approve presentation work, use the retained product path:

```text
Postgres staging/analytics
  -> FastAPI query or endpoint
  -> typed JSON
  -> React dashboard component
```

React must not read CSV files, notebook outputs, exported notebook images, or
local database files directly.

Active casework should be tracked as GitHub Issues when it moves beyond a quick
note. Use the Practical UPL Analytical Case Issue template for meaningful,
resumable questions. The `UPL Status` Project field maps `scoping`, `ready`,
active analysis, `review`, and `done` to the shared repository workflow. This
document owns the durable analytical lifecycle; Issues own active work,
comments, handoffs, and owner review.
## Reading Order

When working in UPL Analytical Casework, read in this order:

1. [START_HERE.md](START_HERE.md)
2. [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md)
3. this workflow doc
4. the case contract under `cases/<case-id>-<slug>/README.md`
5. the owning GitHub Issue

## Research And Case Lifecycle

Use these lifecycle states inside the case contract. Map them to the shared
Project stages without making publication or software promotion a workflow
requirement.

| Status | Meaning | What usually happens next |
|--------|---------|---------------------------|
| `idea` | A football question worth preserving but not yet committed. | Keep it in the neutral intake/backlog. |
| `scoping` | The question, intended use, data availability, non-goals, and done condition are being defined. | Complete the case contract or stop before analysis. |
| `ready` | Another contributor can start without reconstructing chat history. | Begin read-only queries and proportionate checks. |
| `analysis` | Checks, queries, interpretation, and iteration are active. | Produce a defensible answer or explicitly record why the evidence cannot answer it. |
| `review` | Findings, definitions, provenance, limitations, outputs, and reproducibility are being checked. | Correct the case package or approve closure. |
| `done` | The bounded case has a standalone answer, retained evidence, limitations, and a hard endpoint. | File it; route accepted follow-up questions into new work. |

Learning or assessment cases may share this analytical quality sequence, but
their curriculum, timed assessment, numeric rubric, evaluator-only material,
closed-book defence, and learning-method quotas do not belong in UPL Lens.

### Boundary With The Analytical Casework Lab

`Analytical Case Ideas` may act as a neutral pre-commitment intake hub using a
case-lane field. Once selected, a UPL practical case is governed and executed
inside this repository; a Learning Assessment case remains in its separate Lab
system. Both may share the quality kernel of question, scope, provenance,
proportionate checks, reproducible analysis, findings, limitations, and hard
closure. Do not share the Lab's assessment machinery or choose a UPL question
merely to practise a technique. Publication is optional downstream work and is
not required to close either the UPL case package or its owning Issue.
Ordinary UPL casework does not displace a live Learning assessment window;
only an explicit, time-sensitive UPL data/operations need may do so. Delay in
one lane creates no catch-up debt in the other.

## Standard Practical Case Package

New practical cases live under `cases/`:

```text
cases/
  001-example-question/
    README.md
    analysis.ipynb
    checks/
    report.md
    outputs/
```

Copy the template when a scoped question is ready to become committed work:

```text
cases/_case_template/
```

Example:

```powershell
Copy-Item -Recurse cases\_case_template cases\001-post-halftime-conceding
```

## What Each File Does

### `README.md`

This is the case contract. It records the football question, intended use,
scope, definitions, data state, proportionate checks, non-goals, deliverables,
done condition, and expansion boundary before substantial analysis begins.

### `analysis.ipynb`

This is the reproducible analysis path. Exploration may remain while the case
is active, but before closure its data, checks, final calculations, results,
interpretation, and limitations must be understandable from top to bottom.

### `checks/`

Keep only case-specific SQL, Python, or recorded evidence that could change
whether the question is answerable or the finding is credible. Link to shared
foundation validation instead of copying a full platform audit into every case.

### `report.md`

This is the standalone football answer. It owns the short answer, supporting
evidence, interpretation, limitations, non-claims, data-state reference,
follow-up questions, and closure record.

### `outputs/`

Keep only deliberate final charts, tables, figures, or exports cited by the
report. Do not use it as an exploratory dump.

There is no default `product_plan.md` in a practical case. Software promotion,
publication, or recurring monitoring requires separate approval and its own
scope after the analytical case can already close.

The old `notebooks/features/_feature_template/` and Goal Timing package remain
historical research-to-product evidence. Do not copy them for normal new cases.

## Notebook Data Access Rules

Use this rule:

```text
Default notebook source: staging.*
Debug source-data issues: raw.*
Legacy comparison only: CSV files
Promoted reusable metrics: analytics.*
```

### Why `staging.*` Is The Default

Most practical case analysis should start from cleaned Postgres tables:

```text
staging.matches
staging.events
staging.lineups
staging.staff
staging.officials
staging.stats
```

These tables match the production path and reduce the risk that a notebook
proves something the app cannot reproduce later.

### Does Reading `staging.*` Modify Data?

No. Normal notebook queries are read-only.

The risk is accidentally running write statements such as:

```text
UPDATE
DELETE
INSERT
DROP
TRUNCATE
CREATE
ALTER
GRANT
REVOKE
```

Prefer a read-only research role and the helper in `src.research`.

### Recommended Notebook Helper

```python
from src.research import read_sql

events = read_sql(
    """
    SELECT
        match_id,
        season,
        event_type,
        minute_total,
        team_name
    FROM staging.events
    WHERE season = :season
    """,
    {"season": "2025_26"},
)
```

The helper returns a pandas DataFrame, blocks obvious write statements, runs the
transaction as read-only, and reuses the project's `.env` database settings.

### Data Source Decision Guide

Use `staging.*` when:

- exploring team, match, event, discipline, official, lineup, or stats features
- building a metric that could become an API endpoint
- comparing seasons using cleaned fields
- making charts intended for the app

Use `raw.*` when:

- checking whether the scraper captured a field correctly
- debugging missing data
- investigating strange staging values
- planning a staging improvement

Use CSV files only when:

- reproducing the original legacy analysis
- comparing old notebook results to the new Postgres pipeline
- the data has not been loaded into Postgres yet

Use `analytics.*` when:

- a metric has become stable
- multiple endpoints or components need the same logic
- the query is complex enough to deserve a named database contract

## Maintained Database Trust And Case Reproducibility

The maintained Postgres database is the default analytical foundation for UPL
casework. A completed season does not require a permanent frozen export before
it can be analysed.

Use this path by default:

```text
maintained Postgres
  -> read-only case query
  -> case-specific coverage and quality checks
  -> analysis
```

### Trust Boundaries

Treat the schemas differently:

- `raw.*` preserves source-shaped evidence. Use it to diagnose acquisition or
  transformation problems, not as the normal analytical contract.
- `staging.*` contains cleaned and normalized source facts. Core match identity,
  season, teams, dates, scorelines, and results may be treated as generally
  reliable only after their owning migration, staging validation, and
  case-specific checks pass.
- Events, timelines, cards, lineups, staff, officials, and stats are
  coverage-dependent. Check relevant row counts, status fields, nulls,
  mismatches, exclusions, and `staging.validation_issues` before using them.
- `analytics.*` contains reusable derived contracts. Reuse one only when its
  grain, source tables, metric semantics, exclusions, correction rules, refresh
  behavior, and regression evidence are documented.
- Corrections and exceptions must remain queryable and sourced through database
  fields or tables, validation evidence, migrations, and their owning Issue or
  source record. Do not hide a manual correction inside notebook code.

Passing a general staging verification does not prove that every domain is
complete enough for every case. Each case still owns the checks material to its
question.

### Final Metric And Correction Semantics

Migration `012_reconcile_scoreline_goal_contract.sql` and Issue #104 establish
the current interpretation rules. New cases must preserve these distinctions:

- Final match scorelines in `staging.matches` are the source for goals for,
  goals against, goal difference, match results, standings, and general scoring
  rates. Do not reconstruct those metrics from event rows.
- `timeline_goal_count` describes goal events recovered from the source
  timeline. It is coverage-dependent evidence and must be paired with
  `timeline_status`, mismatch counts, and any relevant validation issues.
- Goal Timing is narrower again: it counts eligible goal events in regular time
  from minutes 1 through 90 and excludes added-time and out-of-window events.
  It is not interchangeable with either the final-score total or the complete
  recovered-timeline total.
- Team table points use `sporting_points` plus an explicit
  `points_adjustment` to produce `official_points`. Any deduction or award must
  remain in `analytics.team_season_point_adjustments` with its note, source,
  and owning migration or Issue evidence.
- Source corrections preserve `raw.*` as acquired evidence. Encode a justified
  correction in the raw-to-staging transformation or another rebuild-safe
  correction contract so every staging rebuild reapplies it. Use a migration
  when already-hosted staging or analytics rows also need reconciliation. The
  minute-334 to minute-34 transform and migration 012 are the reference
  example; a notebook must not silently repeat or replace that correction.

The verified 2025/26 post-migration baseline was 505 final-score goals, 496
recovered timeline goals, and 462 Goal Timing regular-time goals. These values
are verification evidence for that recorded data state, not constants to
hard-code into future cases. Recheck them after a source refresh, correction,
or migration.

### Minimum Case Data-State Record

Every practical case should record:

- case ID or title and analysis date
- season or seasons used
- tables, views, material fields, and row grain
- query filters, joins, exclusions, and missing-data treatment
- Git commit plus notebook, script, or SQL revision
- applied migration state when it affects interpretation
- latest relevant staging validation run and issue counts
- case-specific coverage checks and their results
- known corrections, source anomalies, limitations, and unresolved semantics
- whether the maintained database or an immutable extract was queried

The case package structure is owned separately by the practical-case workflow.
This section defines the data record that package must preserve.

The read-only research role may inspect `app_meta.schema_migrations` as well as
the three data schemas. The helper in `src.research` also rejects write SQL and
sets the transaction read-only. Record migration and validation state with
queries such as:

```python
from src.research import read_sql

migrations = read_sql(
    """
    SELECT filename, applied_at
    FROM app_meta.schema_migrations
    ORDER BY filename
    """
)

latest_validation = read_sql(
    """
    SELECT run_id, seasons, row_counts, issue_counts, completed_at
    FROM staging.validation_runs
    WHERE :season = ANY(
        string_to_array(replace(seasons, ' ', ''), ',')
    )
    ORDER BY completed_at DESC
    LIMIT 1
    """,
    {"season": "2025_26"},
)
```

After a migration, season rollover, or meaningful pipeline change, rerun the
relevant staging verification and case-specific coverage queries. A reusable
`analytics.*` object also needs focused regression evidence and a freshness
check appropriate to its refresh contract.

Use this lightweight post-change verification sequence before relying on an
existing case or beginning a new one:

1. Confirm the expected migration filenames and timestamps in
   `app_meta.schema_migrations`.
2. Inspect the latest relevant `staging.validation_runs` summary covering the
   case season or seasons, plus the relevant rows in
   `staging.validation_issues`.
3. Reconcile the case's core record counts and its coverage-dependent counts;
   for goal cases, keep final-score, recovered-timeline, and eligible-subset
   totals separate.
4. Re-run focused regression checks for any reused `analytics.*` object or
   correction rule.
5. Record the resulting commit, migration state, validation run, query scope,
   and material counts in the case package before interpreting the result.

A changed count is not automatically a failure. Stop and investigate when the
change cannot be explained by a documented source update, correction,
migration, or case-filter change.

### When An Immutable Extract Is Required

Keep querying maintained Postgres when the case can be responsibly revisited
from its recorded code, migration state, validation run, and query scope.

Create a case-specific immutable extract only when at least one of these is
material:

- publication, audit, assessment, or handoff requires the exact reviewed rows
- the source database may change before another reviewer can reproduce the work
- a third party cannot receive controlled read-only database access
- the result depends on an exceptional correction or exclusion that needs a
  preserved evidence package
- rerunning against corrected maintained data would answer a meaningfully
  different question

An extract must be limited to the required rows and fields, exclude credentials
and private operational material, and record its query, schema, creation time,
source commit/migration state, row count, and cryptographic checksum. Do not
commit raw working datasets or create a central frozen season snapshot by
default.

When maintained data changes, an older conclusion remains tied to its recorded
state. Re-running it creates a new case result or version; it does not silently
rewrite the historical conclusion.

## Reusable Analytics And Exceptional Software Decisions

Use this rule:

```text
raw.*       = source-shaped scraped data
staging.*   = cleaned source facts
analytics.* = reusable derived product metrics and summaries
```

The case package is complete without any of the options below. Use them only
for existing retained software or work separately approved after the case.

### Direct API Query

Use this when:

- the feature is small
- the logic is easy to understand
- one endpoint uses the logic
- the calculation is still narrow

Current example:

```text
Goal Timing Feature 1 uses a direct query on staging.events.
```

Goal Timing counts only non-added-time goal events from minutes 1 through 90.
Its API contract must also expose the surrounding scoreline total, timeline
total, and timeline coverage/mismatch counts. This keeps the research subset
distinct from both the official result record and the full event timeline.

### Analytics SQL View

Use this when:

- multiple endpoints or panels may reuse the same logic
- the query has meaningful business logic
- the metric should have a stable database name
- the result should always reflect the latest staging rebuild

Create or update views through migrations in `database/migrations/`.

### Stored Analytics Table Or Materialized View

Use this later, only when:

- a normal view is too slow
- snapshot history is needed
- the refresh must be part of the pipeline
- the calculation cannot stay a normal view

This repo should prefer direct queries and normal views while the research and
product layers are still small.

### Naming Conventions

Use clear names that describe what one row represents:

```text
analytics.season_<topic>_summary
analytics.team_season_<topic>_summary
analytics.team_match_<topic>_summary
analytics.player_season_<topic>_summary
analytics.official_season_<topic>_summary
analytics.match_<topic>_summary
```

Avoid naming data objects after charts.

### Reuse And Exceptional Promotion Decision

A case does not need a new `analytics.*` object or software surface to finish.
After the analytical answer is stable, make any reuse decision separately:

- Keep logic inside the case when it is question-specific or unlikely to recur.
- Use a documented `analytics.*` view or table only when the definition is
  stable, reusable across cases, or complex enough to need a named contract.
- Open a separate owner-approved Issue before adding or changing FastAPI,
  React, a dashboard, publication, or recurring monitoring.
- If software promotion is approved, reproduce the result from Postgres, keep
  query logic outside route handlers, and keep React dependent on typed API
  JSON rather than notebooks, CSVs, or exported images.

## Research And Case Backlog

This section replaces the old separate research-backlog and feature-registry
docs.

### Priority Queue

```text
1. Card Trends And Discipline - case candidate
2. Match Explorer Data Questions - candidate
3. Team Profiles And Home/Away Strength - idea
```

### Current Case And Historical Feature Register

| Item | Status | Package | Likely data | Default endpoint | Notes |
|------|--------|---------|-------------|------------------|-------|
| Goal Timing Feature 1 | historical `promoted` | `notebooks/features/feature_01_goal_timing/` | retained CSV/notebook evidence and `staging.events` API query | retained Goal Timing API/React surface | Historical first research-to-product slice. It is evidence, not the template for future case completion. |
| Card Trends And Discipline | `idea` / candidate question area | none | likely `staging.events`, `staging.matches`, and `staging.officials` | notebook/report and deliberate outputs only | Select one bounded football question before creating a case. It is not mandatory Feature 2 work. |
| New practical case | begins at `scoping` after selection | `cases/<case-id>-<slug>/` | maintained Postgres, usually `staging.*` | notebook/report and deliberate outputs only | Copy `cases/_case_template/`; any later software work needs a separate decision. |

### Active Research Ideas

#### Card Trends And Discipline

Status: `idea` / candidate question area

Football question:

```text
Which teams are most disciplined or most card-prone, and how does discipline
change by season?
```

Why it matters:

```text
Discipline is easy for football users to understand, and card patterns are not
well summarized by individual official match pages.
```

Likely data:

```text
staging.events
staging.matches
staging.officials
```

Possible bounded case questions:

```text
Which teams had the highest cards-per-match rate in a named season?
Did card rates change materially between two adequately covered seasons?
How often did red-card matches end differently from comparable no-red-card matches?
```

Key caveat:

```text
Confirm that card events are captured consistently enough across target seasons.
```

#### Dramatic Match Timelines

Status: `idea`

Football question:

```text
Which matches had the most dramatic timelines?
```

Why it matters:

```text
This could make Match Explorer more interesting than a fixture list.
```

Key caveat:

```text
Needs reliable goal ordering and match-state reconstruction.
```

#### Team Home And Away Strength

Status: `idea`

Football question:

```text
Which teams are strongest at home, and which are vulnerable away?
```

Why it matters:

```text
Home and away patterns fit naturally into team profiles and season comparison.
```

Key caveat:

```text
Check whether home and away fields are complete enough across target seasons.
```

#### Officials And Card Rates

Status: `idea`

Football question:

```text
Which officials are associated with the highest card rates?
```

Why it matters:

```text
Official patterns are rarely visible from basic match listings and could be a
useful intelligence layer.
```

Key caveat:

```text
Confirm which official role should count as the main referee and watch for
small-sample distortion.
```

## Human Case Workflow

1. Start with one genuine, bounded UPL football question.
2. During `scoping`, confirm intended use, available data, definitions,
   proportionate checks, non-goals, and observable done condition.
3. Create the owning GitHub Issue when the work is meaningful or resumable,
   then copy `cases/_case_template/` into the next case folder.
4. Record the #112 data-state/provenance fields before material analysis and
   move to `ready` only when another contributor could begin from the package.
5. During `analysis`, query maintained Postgres read-only, run only material
   case checks, and keep the final notebook path understandable.
6. During `review`, reconcile calculations, definitions, evidence, football
   interpretation, limitations, non-claims, and deliberate outputs.
7. Mark `done` when the report stands alone and the case's stated endpoint is
   met. An evidence-based non-answer may be a valid result.
8. Route follow-up questions into the backlog or new cases instead of silently
   expanding the completed case.
9. Open a separate Issue for publication, recurring monitoring, `analytics.*`
   reuse, FastAPI, React, or other software work when explicitly approved.

## Historical/Exceptional Promotion Prompt

```text
Evaluate a completed UPL practical case for software presentation only because a
current Issue and owner instruction explicitly approve that separate work.

Read:
- docs/FEATURE_PROMOTION_WORKFLOW.md
- docs/PRODUCT_STRATEGY.md
- cases/<case-id>-<slug>/README.md
- cases/<case-id>-<slug>/analysis.ipynb
- cases/<case-id>-<slug>/report.md
- cases/<case-id>-<slug>/checks/
- the separately approved software Issue

Use the case report for the analytical answer and the new Issue for software
scope. Do not reopen or redefine the completed case silently.
Keep the frontend API-only.
Use Postgres/FastAPI/React.
Do not make React read CSV files or notebook outputs.
Keep route handlers thin and put query logic in src/api/query_services/ or an
appropriate query/service module.
Document how to run and verify the feature end to end.
After implementation, update the owning software Issue and affected retained
software documentation.
```

## AI Agent Workflow

When asked to work on a practical case, historical feature, or explicitly
approved promotion, an AI agent should:

1. Read `AGENTS.md`, `.github/copilot-instructions.md`, and this workflow doc.
2. Read [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md).
3. Read the case `README.md`, owning Issue, and existing evidence before
   changing scope or analysis.
4. Confirm the question, intended use, data state, definitions, non-goals,
   material checks, and done condition.
5. Confirm whether the notebook uses `staging.*`, `raw.*`, CSVs,
   `analytics.*`, or an approved immutable extract, and preserve #112
   provenance.
6. Use the least complex defensible method and keep the final notebook path to
   reported evidence understandable.
7. Reconcile the report against notebook outputs, retained checks,
   limitations, and non-claims before closure.
8. Stop at the case endpoint. Create a separate backlog item or Issue for a
   materially different follow-up question.
9. Add `analytics.*`, FastAPI, React, publication, or monitoring work only when
   a separate owner-approved Issue explicitly scopes it.
10. Run relevant verification commands and update only the owning canonical
    docs.

The AI agent should not:

- make React read CSV files
- make React parse notebooks or exported chart images
- promote a CSV-only analysis without mapping it back to Postgres
- hide business logic inside route handlers
- add a database migration when a query over existing staging data is enough
- ignore caveats or non-claims from the case contract and report
- import the Analytical Casework Lab's curriculum, assessment clock, rubric,
  evaluator-only material, or learning-method quotas into UPL practical cases

## Historical Feature Packages

```text
notebooks/features/_feature_template/
notebooks/features/feature_01_goal_timing/
```

Ideas in notebooks are not considered product features until they are captured
in a completed case or historical research brief and separately approved for
software work. Goal Timing remains the retained example; it is not the default
future path.
