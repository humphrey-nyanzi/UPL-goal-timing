# UPL Lens - Mermaid Diagram Collection

Status: **canonical technical architecture and visual system reference**.

Use this file to determine which parts of UPL Lens are active analytical
infrastructure, which parts are retained from the public-product phase, and how
a practical case reaches trusted data. Detailed case packaging is owned by
[FEATURE_PROMOTION_WORKFLOW.md](FEATURE_PROMOTION_WORKFLOW.md) and Issue #113;
database trust and provenance are coordinated through Issue #112.

The active path is deliberately complete without FastAPI or React:

```text
official UPL source
  -> source checks and scraping
  -> raw.*
  -> cleaning and validation
  -> staging.*
  -> analytics.* only when reuse or semantic value justifies it
  -> read-only notebook and checks
  -> findings/report, caveats, outputs
  -> closed case
```

FastAPI and React remain useful retained assets, but they are an exceptional,
owner-approved presentation path rather than the default end of research.

Keep this file accurate when code changes affect architecture, major workflows,
service boundaries, database tables, or the active/retained classification.

Current planning home: use [START_HERE.md](START_HERE.md) for the four
continuous development areas and concise recent-history context.

---

## Architecture Classification

This classification follows the current code and service dependencies. A
classification describes the default maintenance obligation; it does not
delete code or prevent a separately approved change.

| Classification | Current areas and services | Why |
|---|---|---|
| **Active foundation** | `src/scraping/upl/`, `scripts/data_platform/`, `src/db/`, `src/validation/`, `database/migrations/`, raw/staging/analytics schemas, cache and raw artifacts, regression/contract tests | These acquire, preserve, clean, validate, and model the shared data used by every future case. |
| **Active operations** | `.github/workflows/current-season-update.yml`, `src/operations/`, source-health, routine-refresh, admin-migration, and full-rebuild/backfill modes | Scheduled acquisition and database maintenance run independently of the public app. Issue #84 owns acquisition reliability and season rollover. |
| **Active case access** | `src/research.read_sql`, read-only research credentials, notebooks, case checks, findings/reports, and case outputs | The default analytical consumer is a bounded case using maintained Postgres without write access. Issue #112 owns the detailed trust/provenance contract; Issue #113 owns the concrete case package and lifecycle. |
| **Optional shared analytics** | `analytics.*`, migrations that define reusable derived contracts, and supporting tests | Add a named contract only when logic has stable meaning, is reused across cases, or needs centralized validation/performance. A missing analytics object is not automatically a backlog gap. |
| **Retained/frozen software** | `api/`, `src/api/`, `frontend/`, `render.yaml`, Pages Functions/configuration, `docs/FRONTEND_DESIGN_SYSTEM.md`, and Goal Timing promotion history | These preserve the proven public-product implementation and may receive scoped correctness or maintenance work, but new cases do not flow here automatically. |
| **Separately governed live surfaces** | Cloudflare Pages sites/proxy and the Render FastAPI service | They remain live while Issue #108 evaluates a dormant/archive option. No provider retirement, archive conversion, or static archive is authorized by this architecture issue. |

Database migrations and tests can support both active and retained consumers.
Their classification follows the contract they protect: foundation correctness
is active; endpoint- or UI-only behavior is retained.

## Diagram 1 — Active Foundation And Casework Path

> Solid arrows are the default maintained path. The case ends without requiring
> an endpoint, route, or deployment.

```mermaid
flowchart LR
    SOURCE["Official UPL sources"] --> PREFLIGHT["Source preflight and cache"]
    PREFLIGHT --> SCRAPE["Scraper and refresh plan"]
    SCRAPE --> ARTIFACTS["data/raw/<season>/\nsource artifacts"]
    ARTIFACTS --> LOAD["Validated raw loader\nscoped upserts or explicit rebuild"]
    LOAD --> RAW["raw.*\nsource-shaped records"]
    RAW --> BUILD["Cleaning, reconciliation, validation"]
    BUILD --> STAGING["staging.*\ncleaned source facts"]
    STAGING --> ACCESS["Read-only research access\nsrc.research.read_sql"]
    STAGING --> DECISION{"Stable reusable\nsemantic contract?"}
    DECISION -->|"yes"| ANALYTICS["analytics.*\nshared derived contract"]
    DECISION -->|"no"| ACCESS
    ANALYTICS --> ACCESS
    ACCESS --> CASE["Bounded question\nnotebook and SQL checks"]
    CASE --> EVIDENCE["Findings/report\noutputs and caveats"]
    EVIDENCE --> CLOSED["Case closed"]

    ACTIONS["GitHub Actions\nroutine and explicit admin modes"] --> PREFLIGHT
    ACTIONS --> BUILD
    SUMMARY["Run summaries and validation evidence"]
    PREFLIGHT --> SUMMARY
    BUILD --> SUMMARY
```

The weekly workflow targets acquisition and Postgres maintenance directly. It
does not call FastAPI, React, Cloudflare, or Render, so freezing product work
does not freeze scheduled data maintenance.

### Default Case Access Rules

1. Query `staging.*` for cleaned source facts.
2. Query `raw.*` only to investigate capture or transformation problems.
3. Query an existing `analytics.*` object when it already expresses the needed
   shared metric.
4. Use `src.research.read_sql` and a database role that cannot write.
5. Keep case-specific SQL and checks with the case unless the logic has stable
   meaning beyond that case.
6. Introduce or change `analytics.*` through a migration and regression tests
   only when reuse, semantic consistency, centralized validation, or measured
   performance makes the shared contract worthwhile.
7. Do not create an analytics view merely to enable a future API or dashboard.

## Diagram 2 — Retained Public-Product Path

> This diagram records the live historical implementation. Dashed arrows mean
> retained/optional, not a required next step after case validation. Issue #108
> governs the live public surfaces.

```mermaid
flowchart LR
    POSTGRES["Supabase Postgres\nraw · staging · analytics"]
    QUERY["src/api/query_services/\nread queries"]
    API["FastAPI\napi/"]
    RENDER["Render service\npublic origin"]
    PROXY["Cloudflare Pages Function\n/api proxy and cache"]
    REACT["React application\nfrontend/"]
    SITES["Cloudflare Pages sites"]

    POSTGRES -.->|"retained read path"| QUERY
    QUERY -.-> API
    API -.-> RENDER
    RENDER -.-> PROXY
    PROXY -.-> REACT
    REACT -.-> SITES

    CASE["Closed analytical case"]
    CASE -.->|"only with a current Issue\nand owner approval"| QUERY
```

The source, tests, deployment configuration, and product lessons are retained.
This issue does not add routes, endpoints, UI work, provider changes, or a
static archive.

---

## Diagram 3 — Database Entity Relationship (ERD)
> Shows how staging tables relate to each other. All child tables share match_id with staging.matches.

```mermaid
erDiagram

    MATCHES {
        int     match_id        PK
        string  match_url
        string  season
        date    match_date
        string  home_team
        string  away_team
        int     home_score
        int     away_score
        int     total_goals
        string  result
        string  winner_team
        string  man_of_the_match
        string  ground_name
    }

    EVENTS {
        string  event_row_key   PK
        int     match_id        FK
        string  season
        int     event_index
        string  event_type
        int     minute_base
        int     minute_added
        int     minute_total
        string  minute_period
        bool    is_added_time
        string  team_side
        string  team_name
        string  player_name
        string  goal_type
        bool    is_goal
        bool    is_yellow_card
        bool    is_red_card
        bool    is_substitution
    }

    LINEUPS {
        string  lineup_row_key  PK
        int     match_id        FK
        string  season
        string  team_name
        string  team_side
        string  squad_role
        int     shirt_number
        string  player_name
        string  player_position
        bool    is_player_of_match
    }

    STAFF {
        string  staff_row_key   PK
        int     match_id        FK
        string  season
        string  team_name
        string  team_side
        string  role
        string  person_name
    }

    OFFICIALS {
        string  official_row_key PK
        int     match_id         FK
        string  season
        string  role
        string  official_name
    }

    STATS {
        string  stat_row_key    PK
        int     match_id        FK
        string  season
        string  statistic_name
        string  home_value
        string  away_value
    }

    VALIDATION_RUNS {
        string  run_id
        string  severity
        string  check_name
        string  table_name
        int     match_id        FK
        string  issue_message
        string  issue_value
    }

    MATCHES ||--o{ EVENTS          : "has timeline events"
    MATCHES ||--o{ LINEUPS         : "has squad"
    MATCHES ||--o{ STAFF           : "has coaching staff"
    MATCHES ||--o{ OFFICIALS       : "has officials"
    MATCHES ||--o{ STATS           : "has match stats"
    MATCHES ||--o{ VALIDATION_RUNS : "logged issues"
```

---

## Diagram 4 — Retained API Request Sequence

> Retained implementation reference. This sequence documents how the current
> browser product works; it is not part of the default casework path.
> What actually happens between the browser and the database when you open the dashboard.

```mermaid
sequenceDiagram
    actor User
    participant React as React App shell<br/>useDashboardData
    participant Client as api/client.ts<br/>fetch()
    participant Edge as Cloudflare Pages Function<br/>/api proxy + short cache
    participant FastAPI as FastAPI<br/>api/main.py
    participant Router as Router<br/>e.g. seasons.py
    participant Query as Query service<br/>src/api/query_services/*
    participant PG as Postgres<br/>staging + analytics

    User->>React: Opens dashboard in browser

    Note over React,PG: Phase 1 — Initial load (parallel, cacheable)
    React->>Client: loadInitialData()
    Client->>Edge: GET /health
    Client->>Edge: GET /seasons
    alt cached public response
        Edge-->>Client: cached JSON + x-upl-lens-cache=HIT
    else cache miss or bypass
        Edge->>FastAPI: forwards safe GET request
    end
    FastAPI->>Router: health + seasons routers
    Router->>Query: get_health_status() + list_seasons()
    Query->>PG: SELECT version(), current_database()
    Query->>PG: SELECT latest staging run FROM validation_runs
    PG-->>Query: db name + version + timestamp
    Query-->>Router: health row
    FastAPI-->>Edge: HealthResponse JSON
    Query->>PG: SELECT season, COUNT(match_id),<br/>COUNT(DISTINCT team), SUM(total_goals)<br/>FROM staging.matches GROUP BY season
    PG-->>Query: season rows
    Query-->>Router: typed rows
    Router-->>FastAPI: SeasonResponse[] rows
    FastAPI-->>Edge: SeasonResponse[] JSON
    Edge-->>Client: JSON responses with cache status
    Client-->>React: setData({ health, seasons })
    React->>User: shows season dropdown

    Note over React,PG: Phase 2 — Season selected (4 parallel calls)
    User->>React: selects season "2025_26"
    React->>Client: loadSeasonData("2025_26")

    par all 4 fetch in parallel
        Client->>Edge: GET /seasons/2025_26/overview
        and
        Client->>Edge: GET /insights/goal-timing?season=2025_26
        and
        Client->>Edge: GET /matches?season=2025_26&limit=200
        and
        Client->>Edge: GET /teams?season=2025_26
    end

    Edge->>FastAPI: forwards cache misses to API origin
    FastAPI->>Router: route handlers validate request
    Router->>Query: overview, insight, match, and team query functions
    Query->>PG: SQL against staging.matches,\nstaging.events, staging.lineups,\nand analytics.team_season_summary
    PG-->>Query: result sets
    Query-->>Router: typed rows
    FastAPI-->>Edge: 4 JSON responses
    Edge-->>Client: JSON responses with cache status

    Client-->>React: setData({ overview, goalTiming,\nmatches, teams })
    React->>User: renders selected page
```
---

## Diagram 5 — Active Scraper Package & State
> The internal structure of the scraper and what can happen to each match URL.

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Discovered : Calendar page fetched,\nmatch URLs extracted

    Discovered --> CacheHit : HTML file exists\nin data/cache/

    Discovered --> Requesting : No cache,\nrate limiter waits

    Requesting --> Fetched : HTTP 200 OK
    Requesting --> Retrying : HTTP 429/5xx\nor network error

    Retrying --> Fetched : Retry succeeded\n(up to 3 attempts)
    Retrying --> Failed : All retries exhausted

    CacheHit --> Parsing : Reads .html from disk
    Fetched --> Cached : Writes .html to disk
    Cached --> Parsing : Passes bytes to\nBeautifulSoup

    Parsing --> Extracted : All 6 table sections\nparsed successfully

    Parsing --> PartiallyExtracted : Some sections missing\n(e.g. no timeline,\nno lineups)

    Extracted --> CheckpointSaved : Every 25 matches\nCSVs flushed to disk
    PartiallyExtracted --> CheckpointSaved : Partial row still saved\nhas_timeline=False etc

    CheckpointSaved --> [*] : Match complete

    Failed --> FailedCSV : Written to\nupl_failed_matches\n_2025_26.csv

    FailedCSV --> [*]

    note right of Retrying
        Retry config:
        SCRAPE_RETRY_ATTEMPTS = 3
        RETRY_BACKOFF_SECONDS = 1.5
        forcelist: 429, 500, 502, 503, 504
    end note

    note right of Requesting
        Rate limiter:
        RATE_LIMIT_SECONDS = 0.75
        MAX_CONCURRENT = 4 threads
    end note
```
