# Product Strategy

This document now owns two related things:

1. the current UPL Lens identity as a maintained Uganda Premier League
   analytical data foundation and practical casework system;
2. the retained lessons from the completed public software-product phase.

Read this before changing project identity, public-facing language, research
case direction, API/frontend presentation, or documentation scope. The former
public-product strategy is preserved here because it explains many design,
trust, source-record, and engineering decisions, but it is no longer the active
north star for all new work.

## Current Project Definition

UPL Lens is a maintained UPL analytical data foundation and practical casework
system. It acquires official Uganda Premier League source data, preserves and
validates it in Postgres, keeps raw/staging/analytics contracts understandable,
provides reproducible read-only research access, and supports bounded football
questions as closed analytical cases.

The active project question is:

```text
What can trustworthy UPL source data answer when a real football question is
scoped, checked, reproduced, caveated, and closed deliberately?
```

The active flow is:

```text
Official UPL source record
  -> maintained Postgres foundation
  -> case-specific reproducibility record
  -> notebook/checks/findings/report/outputs/caveats
  -> hard endpoint for the case
```

A case-specific reproducibility record is not the same thing as a frozen central
snapshot. The Postgres foundation remains maintained; each case records the
source coverage, data state, checks, notebook evidence, caveats, and endpoint
that make that case reproducible.

## Component Status

- **Active**: source acquisition, raw/staging/analytics contracts, validation,
  operations, read-only notebooks, bounded UPL analytical cases, caveats,
  reproducibility records, and GitHub-native work discipline.
- **Retained/frozen**: FastAPI, React, Cloudflare Pages, Render deployment
  knowledge, frontend design rules, API contracts, and public-product QA
  lessons. These are assets and references, not mandatory destinations.
- **Historical**: UPL Goal Timing / UPL Match Intelligence naming, the v1 public
  product push, the June/July frontend build order, and Goal Timing as the
  first productized analysis.
- **Separately decision-gated**: public deployment disposition, project-board
  semantics, architecture-boundary rewrites, and any future case-to-software
  promotion.

## Product Dictionary

Use this compact dictionary to keep docs, Issues, PRs, UI copy, and agent
handoffs consistent during and after the transition.

| Term | Meaning | Use it when |
|---|---|---|
| UPL Lens | The unified repository/project name for the maintained UPL data foundation, casework system, and retained software assets. | Naming the repo, docs, Issues, PRs, cases, and retained public surfaces. |
| Official source | The official Uganda Premier League website and match pages this project reads from. | Explaining provenance, scraping, and source-data limitations. |
| Source record | The official archived match fact or page. | Distinguishing original records from UPL Lens analysis. |
| Maintained Postgres foundation | The active raw/staging/analytics database contracts that are refreshed, validated, and used for research access. | Describing the active technical foundation. |
| Case-specific reproducibility record | The coverage/snapshot/check/evidence/caveat record that makes one closed case reproducible. | Starting or closing a practical UPL analytical case. |
| Practical UPL case | A bounded football investigation with a question, data record, checks, notebook, findings/report, outputs, caveats, and hard endpoint. | Scoping future UPL analysis work. |
| Intelligence layer | The analytical meaning UPL Lens adds on top of official source records. | Explaining retained product decisions or current analytical interpretation. |
| Retained public app | The existing React/FastAPI product code and hosted knowledge from the completed software-product phase. | Maintaining or referencing frontend/API assets. |
| Featured insight | Historical/product-phase term for a notebook-backed analysis promoted into API/frontend presentation. | Discussing Goal Timing or retained public-product history. |
| Software promotion | Exceptional, owner-approved movement from a case into SQL/API/frontend presentation. | Deciding whether a case should become software rather than stop as a report/output. |
| Data-quality caveat | Visible context that prevents a number or finding from looking more certain than it is. | Writing case reports, notebooks, APIs, or retained UI copy. |
| Available data | A cautious phrase meaning the project is reporting from collected and validated records, not claiming official completeness. | Writing player, lineup, event, leaderboard, or case findings. |
| Staging data | Cleaned app/research-facing Postgres tables under `staging.*`. | Discussing trusted inputs for research, API, and casework. |
| Analytics data | Stable reusable summaries, facts, views, or tables under `analytics.*`. | Describing reusable metrics or derived contracts. |
| Browser-facing API proxy | Historical/retained Cloudflare Pages `/api/*` path from the product phase. Retirement is owner-approved under #108 and in execution until verified. | Understanding retained code or historical hosted behavior. |
| Backend origin API | Historical/retained Render-hosted FastAPI origin. Unrestricted public exposure is owner-approved for retirement under #108 and in execution until verified. | Understanding retained backend code or historical deployment behavior. |

## Strategic Change

The public software-product phase was useful. It proved that UPL Lens could move
from source pages to a scraper, Postgres, FastAPI, React, hosted operations,
QA, documentation, GitHub Issues/PRs, and public presentation. It also created
strong working habits: canonical doc ownership, source-record boundaries,
fail-closed operations, validation evidence, reproducible notebooks, and owner
review.

The direction changed because an open-ended public-product roadmap made every
useful football question feel like it needed release packaging, frontend polish,
API shape decisions, deployment checks, and long-lived product maintenance. That
cost can create drift away from the actual analytical value. The engineering
foundation should be maintained; the automatic product destination should not.

## Former Public-Product Strategy, Retained As Historical Context

The sections below preserve the product-phase lessons and decision rules. Use
them when maintaining retained frontend/API assets, reviewing the historical
Goal Timing product path, or considering an explicitly approved future
presentation surface. Do not treat them as a standing instruction to turn every
validated notebook into React/FastAPI work.

## Historical Product Definition

During the public-product phase, UPL Lens was defined as an independent
statistical observatory for the Uganda Premier League (the project previously
described public-facing work as "UPL Match Intelligence"). It turned official
match data into trustworthy football intelligence: curated statistical findings,
reusable analytical features, and deeper exploration for people who wanted to
understand the league beyond fixtures, results, and tables.

The historical product question was:

```text
What do the UPL numbers reveal that the official website does not explain?
```
## Source Record Vs Intelligence Layer

The retained source-record boundary is still active for both casework and retained product surfaces:

```text
Official UPL site = source record.
UPL Lens = analytical meaning.
```

Do not reproduce a raw official UPL page unless the app transforms that source
record into insight. The app should avoid becoming a cleaner clone of official
fixtures, results, match reports, lineups, officials, or timelines.

For every raw-data element, choose one of three treatments:

1. **Transform**
   - Show it because UPL Lens adds analytical value.
   - Examples: goal timing context, card timing, match rhythm, team trend
     impact, official card-rate context, late-drama tags, or season-relative
     comparisons.

2. **Summarize**
   - Show a compact version because it supports the analysis.
   - Examples: scoreline, key goals, decisive cards, a short match context
     strip, or a short event summary.

3. **Link Out**
   - Do not duplicate it. Link to the official source when the user wants the
     complete archive detail.
   - Examples: full raw timeline, full lineup list, plain officials list, full
     official match record, or other source details that UPL Lens has not yet
     contextualized.

Match pages should be treated as **Match Intelligence Briefs**, not official
match-page clones. A match page should answer why the match matters through
signals such as timing, momentum, cards, trend fit, anomalies, or team context.
If UPL Lens cannot add that layer yet, show only compact supporting facts and a
clear official-source link.

## Routine Intelligence Modules

Routine intelligence modules are reusable backend-supported features that can
appear on normal product pages without becoming promoted research insights.

Examples include:

- team profile labels
- match signal labels
- trends charts
- scoring and carding rates
- data coverage indicators
- form strips
- attack/defence comparisons
- player contribution categories

These modules should live on overview, match, team, player, and trends pages
when they help users interpret the league. They should be built as ordinary
page intelligence, not as featured research products.

## Featured Insights

Featured insights are promoted research products that move through the
notebook -> validation -> API -> frontend workflow when software promotion was approved.

Examples include:

- Goal Timing
- a future Discipline case or insight, if researched and separately approved for promotion
- a future Home Advantage case or insight, if researched and separately approved for promotion

Do not force routine page intelligence into `/insights`. Do not replace
featured insights with shallow dashboard widgets.

## Target Audiences

### Primary Audience

The primary audience is a UPL fan who cares about stats and wants a deeper
understanding of the league.

This user should be able to land on the app and quickly understand:

- this is an analytical product, not just a results page
- the numbers are meaningful and football-specific
- there are insights here they cannot easily get from generic sites
- the product is credible enough to revisit

### Secondary Audiences

Secondary audiences include:

- football analysts and researchers
- sports journalists and media people
- club staff or football professionals browsing for useful signals
- recruiters or technical reviewers who notice the quality of the system
- data people interested in the end-to-end workflow

These audiences matter, but the public interface should still lead with football
intelligence rather than technical self-promotion.

## Product Positioning

The best product model is:

```text
An analytical sports publication with dashboard-style drilldowns.
```

This means:

- Curated findings come first.
- Users can then dig deeper into filters, comparisons, team summaries, match
  events, and season trends.
- The interface should be understandable to a local football fan, while still
  serious enough for an analyst.

Avoid making the app only a dense analyst workspace. That can become
intimidating and reduce public usefulness.

Avoid making it only a simple dashboard. That can become a set of cards and
charts without a clear football story.

## First Ten Seconds

Within ten seconds of opening the app, a user should understand:

```text
This product helps me understand the Uganda Premier League through data and
analysis that I cannot easily get from ordinary fixture or results pages.
```

The first screen should make the analytical value obvious. It can include
ordinary league facts such as total goals or season coverage, but those should
support the bigger message rather than become the main product.

## Product Layers

The app should grow in layers.

### 1. League Intelligence Overview

Purpose: give a fast, useful view of the league through analytical summaries.

This should not be a plain fixtures page. It should show useful patterns such as
season totals, goal timing signals, recent analytical highlights, unusual team
trends, data freshness, and caveats that affect interpretation.

### 2. Featured Insights

Purpose: present validated analyses as readable football stories with charts and
supporting evidence.

Feature 1, Goal Timing, is the current flagship example. A good featured insight
should explain:

- the question being asked
- the data used
- the metric definition
- the finding
- why it matters in football or sports-science terms
- what caveats apply
- how the user can dig deeper

### 3. Explore The Numbers

Purpose: let users investigate the underlying data after the curated summary.

Likely surfaces include:

- team analytical summaries
- team comparisons
- match and event explorer
- goal timing explorer
- discipline dashboard
- player analytical summaries when the data is reliable enough
- season filters and trend views

These views should support exploration and comparison, not merely reproduce the
official website's profile pages.

### 4. Methodology And Data Quality

Purpose: build trust without making methodology the main feature.

The app should include a visible but quiet methodology/about/contact area that
explains:

- who maintains the project
- what the data source is
- how data moves through the system
- how often it is updated
- what the known limitations are
- how caveats are handled
- how to contact the maintainer

This section can also satisfy portfolio/recruiting curiosity without turning the
main product into a technical showcase.

## Content Priorities

Prioritize analysis that adds meaning beyond the official website:

- goal timing and period trends
- late goals and second-half patterns
- team scoring and conceding tendencies
- discipline and card trends
- cards and match outcomes
- home and away patterns
- player starts, substitutions, and impact indicators
- official/referee patterns
- season-over-season changes
- unusual or dramatic match timelines

Do not prioritize generic fixtures, results, and tables as the main feature.
They may exist as supporting context, but they should not define the product.
When a workflow risks copying the official website, prefer analytical
summaries, compact context, and official-source links over reproducing the whole
source page.

## Historical Feature Philosophy

Each important analytical feature should be reusable over time.

When a new analysis is promoted, it should not be a one-off static post. It
should become a continuing feature that can update as new seasons and matches
enter the database, when the underlying data supports that.

The historical product-phase flow was:

```text
notebook research -> research brief -> product plan -> Postgres/FastAPI ->
React feature
```

Use notebooks for discovery. Use the app for trusted, repeatable public
presentation.

## Voice And Tone

The product voice should be:

- neutral
- statistical
- sports-science informed
- clear enough for local fans
- serious enough for analysts and researchers
- honest about uncertainty

Avoid overconfident hot takes. Avoid tactical language that pretends to know
more than the data supports. Avoid jargon-heavy research language that makes the
product inaccessible to fans.

Good tone:

```text
This trend suggests...
This period accounts for...
The available match event data shows...
This should be read with caution because...
```

Avoid tone like:

```text
This proves...
This team always...
The data is perfect...
```

## Visual Direction

The visual identity should feel like a modern global sports analytics product.

Current preference:

- modern and polished
- analytical rather than decorative
- mobile-first
- clean and credible
- not heavily themed around Ugandan flag colors at this stage
- not a generic admin template
- not a marketing landing page

Local identity can be added later if it supports the product, but the first
priority is a professional sports analytics feel.

## Data Trust And Caveats

Credibility is central. The product runs on numbers, so wrong or misleading
numbers can damage trust quickly.

Every public number should fit one of these states:

1. **Publishable**
   - The data is complete enough and the metric is reliable enough to show
     normally.

2. **Publishable With Caveat**
   - The number can be shown, but nearby text should explain the limitation.
   - Examples: missing match event data, unusual season structure, known source
     limitations, incomplete player data.

3. **Blocked From Public Display**
   - The number should not be shown because it would likely mislead users.
   - Examples: broken source scrape, structural validation failure, row-count
     mismatch, missing data that changes the meaning of a ranking.

The app should never hide meaningful uncertainty. If there were 15 clubs in a
season, missing matches, unusual source behavior, or other anomalies, that
context is part of the analysis.

## Source Data Risk

The data source is the official UPL website, and the project currently depends
on scraping that source. This is useful but not guaranteed forever.

Product and technical decisions should acknowledge this:

- The app should show data freshness.
- The pipeline should log failures and validation issues.
- Broken or incomplete updates should not silently publish misleading values.
- Methodology should explain that the product is based on official source pages.
- If source structure changes, data reliability work takes priority over new
  product features.

This risk does not weaken the project. It is part of why transparent caveats,
validation, and methodology matter.

## Portfolio Role

This remains a strong portfolio project, but the portfolio value should be
secondary in the user interface.

The app should impress by being useful first. Recruiters and technical reviewers
can discover the engineering depth through:

- the repository
- documentation
- methodology/about notes
- visible data freshness and caveat handling
- the reliability of the public product

Do not make the main navigation or homepage revolve around the tech stack.

## Technical Implications

Product strategy should shape technical choices.

### Frontend

- Build analytical product surfaces, not decorative landing pages.
- Lead with curated insight and useful summaries.
- Keep drilldowns close to the story they support.
- Make mobile layouts first-class.
- Show loading, empty, error, and caveat states clearly.
- Use football language instead of raw database language.

### API

- Add endpoints when a real product surface needs them.
- Keep route functions thin.
- Put reusable query logic under `src/api/`.
- Do not make React duplicate durable SQL or backend logic.
- Prefer stable response shapes that match visible user workflows.

### Database And Analytics

- Keep raw, staging, and analytics concerns separate.
- Use `staging.*` for cleaned app-facing data.
- Use `analytics.*` views when a metric becomes stable, reusable, or complex.
- Use direct API queries for small first slices when that is simpler and clear.
- Do not serve production features from notebooks, CSVs, or exported images.

### Research

- Keep notebooks as the research lab.
- Promote only useful, validated findings.
- Record metric definitions and caveats in feature docs.
- Treat caveats as product content, not private notes.

### Operations

- Protect public credibility through validation, logs, and escalation.
- Prefer hands-off scheduled updates, but make failures visible.
- Do not let automation publish structurally broken or misleading data.

## Historical Minimum Serious Product

A minimum serious public version should include:

1. A polished mobile-friendly League Intelligence Overview.
2. Goal Timing as the first proper featured insight.
3. Team analytical summaries, not just standings.
4. Basic match or event exploration for evidence and drilldown.
5. Clear data freshness and caveat display.
6. A simple Methodology/About/Contact area.

This is not the final product. It is the minimum shape that communicates the
right identity.

## Historically Deferred Product Ideas

These ideas may become useful later, but should not drive the immediate
redesign:

- monetization
- paid club/scouting tools
- heavy player profile pages
- social share-card generation
- full fixture/result duplication
- strong local color branding
- advanced commercial dashboards
- login/accounts or private workspaces

## Decision Rules For Future Work

When deciding whether to pursue a case or build software, ask:

1. Does this reveal something meaningful about the UPL?
2. Is this different from what the official website already provides?
3. Can the number or claim be traced to trusted data, a query, or a notebook?
4. Does the UI make caveats visible when they matter?
5. Does this need maintained software, or can it close as a bounded reproducible case?
6. If software is proposed, will it keep working as new seasons are added?
7. Is this useful as football analysis before it is useful as portfolio evidence?
8. Are we transforming the official source record, summarizing it for context,
   or linking out instead of duplicating it?

If the answer to the first three questions is not clear, do more product or
research thinking before implementation.

## Agent Checklist

Before coding product-facing work or starting a practical UPL case, an AI agent should check:

- [START_HERE.md](START_HERE.md)
- this product strategy document
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
- the relevant work-area docs
- the current files for the specific feature or surface being changed

For retained or explicitly approved frontend work, also check:

- [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md)

For research, casework, or exceptional promotion work, also check:

- [FEATURE_PROMOTION_WORKFLOW.md](FEATURE_PROMOTION_WORKFLOW.md)
- the relevant feature folder under `notebooks/features/`

Do not implement a product feature only because it is technically possible.
Implement it because it advances the product promise:

```text
maintained UPL data, turned into reproducible football intelligence
```
