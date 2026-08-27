# Feature Promotion Workflow

This document is the research and practical-casework playbook for the
repository's Research & Football Intelligence lane.

It now owns:

- research idea capture
- practical UPL case lifecycle status
- historical feature lifecycle status
- notebook package workflow
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
  -> source coverage/snapshot record
  -> read-only notebook and SQL checks over maintained Postgres
  -> findings/report and outputs
  -> caveats
  -> hard endpoint
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

Active research or casework should be tracked as GitHub Issues when it moves
beyond a quick note. Use the Research / Football Intelligence Issue template
for notebook-first questions, including discipline questions such as
goal-scoring patterns after red cards. This document owns the durable research
and case lifecycle; Issues own active work, comments, handoffs, and owner
review.
## Reading Order

When working in Research & Football Intelligence, read in this order:

1. [START_HERE.md](START_HERE.md)
2. [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md)
3. this workflow doc
4. the feature folder under `notebooks/features/`
5. [START_HERE.md](START_HERE.md) if you need recent repo context

## Research And Case Lifecycle

Use these statuses consistently for research ideas and feature packages.
These statuses describe the research feature itself. GitHub Project columns
describe active workflow state across all work areas.

| Status | Meaning | What usually happens next |
|--------|---------|---------------------------|
| `idea` | Interesting question, but not ready to work on yet. | Capture notes and leave it parked. |
| `candidate` | Plausible next research topic. Needs prioritization. | Compare it against other football questions. |
| `selected` | Chosen as the next feature package, but not created yet. | Copy the template and start a notebook package. |
| `researching` | Notebook work has started. | Keep experimenting in `analysis.ipynb`. |
| `validated` | Research produced a useful finding, metric, chart, or case answer. | Write `research_brief.md` and record checks/caveats. |
| `promotion_ready` | Historical/exceptional status: ready for owner-approved software planning and implementation. | Ask an AI agent or engineer to promote it only when a current Issue explicitly approves software work. |
| `promoted` | Historical/exceptional status: the feature is available through FastAPI and React. | Track retained follow-up work in `product_plan.md`. |
| `needs_revision` | The feature exists, but the logic, caveats, data, or UI need review. | Add change requests before more implementation. |
| closed_case | The bounded case has ended with findings/report, outputs, caveats, and endpoint. | Reopen only through a new Issue. |
| parked | Keep the idea, but do not work on it soon. | Leave it documented but inactive. |
| `rejected` | Do not pursue unless revived later. | Keep only as historical context. |

## Standard Feature Package

Each real research feature lives under `notebooks/features/`:

```text
notebooks/features/
  feature_02_card_trends/
    README.md
    analysis.ipynb
    research_brief.md
    product_plan.md
    outputs/
```

Use the template folder when starting a new feature:

```text
notebooks/features/_feature_template/
```

Example:

```powershell
Copy-Item -Recurse notebooks\features\_feature_template notebooks\features\feature_02_card_trends
```

## What Each File Does

### `analysis.ipynb`

This is the research lab.

Use it to:

- load data
- test SQL
- use pandas
- make charts
- try multiple metric definitions
- keep notes on failed attempts

The notebook can be messy while exploring. Before promotion, the final sections
should clearly show the chosen metric, final chart or table, and caveats.

### `research_brief.md`

This is the football-thinking file.

It should answer:

- What question are we answering?
- Why does it matter?
- What data did we use?
- What is the final finding?
- What are the metric definitions?
- What caveats should users know?
- What notebook evidence supports the finding?

### `product_plan.md`

This is the retained product history, exceptional promotion, and implementation handoff.

It has three jobs:

- Case endpoint or exceptional promotion plan: what the case outputs or approved app version should do
- Change requests: what should change after the case or feature already exists
- Implementation history: what has already been built and verified

### `outputs/`

This folder can hold notebook exports or reference charts. These files are
evidence only. The product dashboard should not depend on them.

## Notebook Data Access Rules

Use this rule:

```text
Default notebook source: staging.*
Debug source-data issues: raw.*
Legacy comparison only: CSV files
Promoted reusable metrics: analytics.*
```

### Why `staging.*` Is The Default

Most feature research should start from cleaned Postgres tables:

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
- Source corrections preserve `raw.*` as acquired evidence and apply the
  justified change in `staging.*` through a migration. The minute-334 to
  minute-34 correction in migration 012 is the reference example; a notebook
  must not silently repeat or replace that correction.

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
    ORDER BY completed_at DESC
    LIMIT 1
    """
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
2. Inspect the latest `staging.validation_runs` summary and the relevant rows
   in `staging.validation_issues`.
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

## Analytics Promotion Decisions

Use this rule:

```text
raw.*       = source-shaped scraped data
staging.*   = cleaned source facts
analytics.* = reusable derived product metrics and summaries
```

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

### Promotion Decision Checklist

Before promoting notebook logic, decide:

- Can the result be reproduced from Postgres?
- Does it use cleaned `staging.*` data where possible?
- Is this a one-endpoint calculation or a reusable product metric?
- Would a named `analytics.*` view make the logic easier to maintain?
- Does the SQL avoid hardcoded seasons, team names, or notebook-only files?
- Does the frontend still receive JSON from FastAPI instead of reading CSVs?

## Research And Case Backlog

This section replaces the old separate research-backlog and feature-registry
docs.

### Priority Queue

```text
1. Card Trends And Discipline - case candidate
2. Match Explorer Data Questions - candidate
3. Team Profiles And Home/Away Strength - idea
```

### Current Feature Table

| Feature | Status | Feature Package | Research Source | Production Source | API Endpoint | Frontend Surface | Notes |
|---------|--------|-----------------|-----------------|-------------------|--------------|------------------|-------|
| Feature 1 - Goal Timing | `promoted` (historical/retained) | `notebooks/features/feature_01_goal_timing/` | `staging.events` via notebook and API query | direct query on `staging.events` joined to app-safe matches; no `analytics.*` view yet | `GET /insights/goal-timing?season=...` | Goal Timing Explorer | Historical first research-to-product slice and retained product example. Counts regular-time goal events by 15-minute interval, excludes added time, and exposes scoreline/timeline coverage context for the subset. |
| Card Trends And Discipline Case | `candidate` | none yet | likely `staging.events`, `staging.matches`, `staging.officials` | choose during promotion | none yet | case report/output first; software surface only if separately approved | Strong case candidate if card coverage is consistent enough across seasons; not an automatic Feature 2 product commitment. |
| Feature XX - Template | `idea` | `notebooks/features/_feature_template/` | `staging.*` by default | choose during promotion | none yet | none yet | Copy this package when starting a new experimental feature. |

### Active Research Ideas

#### Card Trends And Discipline

Status: `candidate`

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

Possible product surfaces:

```text
Discipline Dashboard
Team Profile discipline section
League Overview insight card
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

1. Start with a `selected` or explicitly approved idea in this document.
2. Copy the notebook template folder.
3. Rename it with the next feature number and short slug.
4. Change the feature table row to `researching`.
5. Work in `analysis.ipynb`.
6. Write `research_brief.md`.
7. Fill in the promotion plan and readiness notes in `product_plan.md`.
8. Close the case with findings/report, outputs, caveats, and hard endpoint, or mark it `promotion_ready` only when software promotion is explicitly approved.
9. Ask an AI agent to promote the feature only when the owner has approved software promotion.
10. After implementation or case closure, change the row to `closed_case`, `promoted`, or `needs_revision`.

## Historical/Exceptional Promotion Prompt

```text
Promote notebooks/features/feature_02_card_trends into a product feature only if a current Issue explicitly approves software promotion.

Read:
- docs/FEATURE_PROMOTION_WORKFLOW.md
- docs/PRODUCT_STRATEGY.md
- notebooks/features/feature_02_card_trends/README.md
- notebooks/features/feature_02_card_trends/research_brief.md
- notebooks/features/feature_02_card_trends/product_plan.md
- notebooks/features/feature_02_card_trends/analysis.ipynb

Use research_brief.md and product_plan.md as the source of truth.
Keep the frontend API-only.
Use Postgres/FastAPI/React.
Do not make React read CSV files or notebook outputs.
Keep route handlers thin and put query logic in src/api/query_services/ or an
appropriate query/service module.
Document how to run and verify the feature end to end.
After implementation, update product_plan.md implementation history and the
feature table in docs/FEATURE_PROMOTION_WORKFLOW.md.
```

## AI Agent Workflow

When asked to work on a research feature, practical case, or explicitly approved promotion, an AI agent should:

1. Read `AGENTS.md`, `.github/copilot-instructions.md`, and this workflow doc.
2. Read [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md).
3. Read the feature folder's `README.md`, `research_brief.md`, and
   `product_plan.md`.
4. Inspect the notebook only enough to understand the final metric and
   supporting evidence.
5. Confirm whether the notebook used `staging.*`, `raw.*`, CSVs, or
   `analytics.*`.
6. Identify the production-safe Postgres source.
7. Choose direct query, analytics view, or stored table deliberately.
8. For normal casework, document the final query/checks and endpoint. For approved software promotion, add query logic in the backend query/service layer.
9. Add or extend a thin FastAPI route only for approved software promotion.
10. Add typed response models and frontend response types only for approved software promotion.
11. Add a responsive dashboard component only for approved software promotion.
12. Update `product_plan.md`, this workflow doc's feature table, and any
    affected docs.
13. Run relevant verification commands.

The AI agent should not:

- make React read CSV files
- make React parse notebooks or exported chart images
- promote a CSV-only analysis without mapping it back to Postgres
- hide business logic inside route handlers
- add a database migration when a query over existing staging data is enough
- ignore caveats from `research_brief.md`

## Current Feature Packages

```text
notebooks/features/_feature_template/
notebooks/features/feature_01_goal_timing/
```

Ideas in notebooks are not considered product features until they are captured
in `research_brief.md`, described in `product_plan.md`, and served through
FastAPI to React.
