# Research Brief: Feature 01 - Goal Timing

This file captures the football thinking behind Feature 1. The production
implementation details live in `product_plan.md`.

## Status

promoted

## Feature Question

When in a Uganda Premier League match are goals most likely to be scored?

## Why This Matters

The official UPL website stores individual match pages. This feature turns those
match timelines into a league-level pattern that is difficult to see by reading
match pages one by one.

## Data Used In Research

Research source:

- Older processed goal timing data under `data/processed/`.
- Structured scraper event data where available.
- Notebook research in `analysis.ipynb` and `analysis_v2.ipynb`.

Production feature source:

- Cleaned Postgres `staging.events`.

Seasons included:

- The original pilot covered completed seasons from `2019_20` through `2024_25`.
- The promoted API endpoint is season-filtered and can also serve current
  staging seasons such as `2025_26`.

Filters used in the promoted slice:

- `event_type` in `goal`, `own_goal`, `penalty_goal`
- `minute_total` between `1` and `90`
- `is_added_time IS NOT TRUE`

### 2025/26 Count Reconciliation

Issue #104 recorded 461 regular-time goals on 16 July 2026. The reconciled
release-candidate contract is 462. The one-row difference is match `31655`,
NEC FC 1-4 SC Villa, where Geofrey Gagganga's SC Villa goal belongs at minute
`34`.

The raw artifacts from hosted runs
[29240112495](https://github.com/humphrey-nyanzi/upl-lens/actions/runs/29240112495)
and
[29731677864](https://github.com/humphrey-nyanzi/upl-lens/actions/runs/29731677864)
stored that event as index `27`, minute `334`. The raw-artifact SHA-256 digests
are:

- run `29240112495`: `5c81dfebec4939be36e1bce3ba0f8c19c44d0712b424df0fc506e14706864ccb`
- run `29731677864`: `4a56200efab54c0895924f1aaebb70cf59be636ba06566f6ad2274c9b63f6fa1`

That malformed minute excludes the goal from the 1-90 regular-time subset and
produces 461. The local raw snapshot dated 23 May 2026 has SHA-256
`b39813c859381c6fcdb998e7aa9d6886305276c252368c6d129ece1989c30c10`. It stores
the event as index `7`, minute `34`; its paired
assist is also at minute `34`, and the complete five-goal timeline agrees with
the 1-4 scoreline. Hassan Mubiru's 87th-minute goal shifts from index `24` to
`25` between the two event sequences but does not change the count.

The 462 contract therefore treats `334` as a source-shaped minute typo and
uses the internally reconciled `34` value. The historical match URL was
`https://upl.co.ug/event/nec-fc-vs-sc-villa-3/`, but the UPL domain later
changed content and can no longer independently verify the event. The workflow
artifacts, local snapshot, paired assist, complete
timeline, and scoreline are the durable evidence; the unavailable original
page remains a provenance limitation.

## Final Finding

The original pilot found that the highest-volume regular-time goal window across
the historical study period was `46-60`, the first 15 minutes after halftime.
At finer resolution, the pilot also highlighted `51-60` and `56-60` as peak
windows.

## Metric Definitions

```text
regular_time_goal = goal event with minute_total between 1 and 90 and not added time
interval_goals = count of regular_time_goal rows in a 15-minute interval
interval_share = interval_goals / total_regular_time_goals
peak_interval = interval with the highest interval_goals
```

Intervals:

```text
0-15
16-30
31-45
46-60
61-75
76-90
```

## Caveats

- Added-time goals are excluded from the interval distribution.
- The product endpoint currently returns one season at a time.
- The first promoted slice is season-level only; team-level and home/away
  filters can be added later.
- Current-season results can change after each scheduled data refresh.
- The 2025/26 total depends on the documented minute-334 to minute-34
  reconciliation for match `31655`.

## Evidence

Notebook evidence:

```text
analysis.ipynb - Timing Patterns / Regular Time Goals
analysis.ipynb - 15-minute, 10-minute, and 5-minute interval sections
analysis_v2.ipynb - later exploratory match-state ideas
```

Reference outputs:

```text
outputs/features/feature_01_goal_timing/goal_timing_upl.png
outputs/features/feature_01_goal_timing/gqr_gtsi_trends.png
```
