---
name: Data Foundation & Operations
about: Source acquisition, Postgres, staging, validation, automation, season rollover, migrations, or runbooks
title: "[Data/Ops] "
labels: "area: data-foundation, type: change"
assignees: ""
---

## Objective

What data-foundation or operations problem needs to be solved?

## Context

What failed, changed, needs maintenance, or needs to become more trustworthy?

## Scope

- Included:
- Excluded:

## Risk / Write Boundary

Describe the source, raw, staging, analytics, migration, automation, credential,
or hosted-write risk. State which actions are read-only and which require a
separate owner approval.

## Acceptance Criteria

- [ ] Relevant script, migration, validation, or workflow path is identified.
- [ ] Failure mode or data-quality risk is documented.
- [ ] Writes, migrations, provider actions, and rollback/stop rules are explicit.
- [ ] Fix or investigation is verified with the relevant command or evidence.
- [ ] Logs, run summaries, or validation issues are updated if applicable.
- [ ] Canonical operations and architecture documentation is updated when needed.

## Related Documents

- `docs/LOCAL_DEVELOPMENT.md`
- `docs/diagram_collection.md`

## Verification / Evidence

Paste commands, logs, workflow links, validation summaries, or read-only checks.
