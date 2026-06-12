# Architecture Map

This document is the top-level map of repository knowledge domains for progressive disclosure.

## Knowledge base layout
- `AGENTS.md`: short entry-point map + critical execution constraints.
- `workflow-reference.md`: canonical detailed ticket workflow behavior.
- `docs/design-docs/`: design beliefs, architecture-contract templates, domain maps, and verification status.
- `docs/product-specs/`: user-facing capability specs and acceptance intent.
- `docs/exec-plans/active/`: active execution plans with progress logs.
- `docs/exec-plans/completed/`: completed plans and decision summaries.
- `docs/exec-plans/tech-debt-tracker.md`: known debt and remediation backlog.
- `docs/exec-plans/ticket-change-log.md`: running implemented-ticket summary log.
- `docs/exec-plans/as-built.md`: actual built behavior and troubleshooting notes.
- `docs/exec-plans/build-cost.md`: ticket-level AI/tooling cost rollup.
- `docs/exec-plans/harness-template-todo.md`: template Harness improvement TODO list.
- `docs/exec-plans/review-feedback-tracker.md`: repeated review-feedback tracker for promotion into durable docs/tooling/TODOs.
- `docs/generated/`: generated references (schemas, inventories, snapshots).
- `docs/references/`: tool/framework references optimized for LLM consumption.

## Layering guidance
1. Read `AGENTS.md` first.
2. Open this map (`ARCHITECTURE.md`) to locate the right knowledge domain.
3. Open the domain index file (`docs/*/index.md`) before deep files.

## Verification metadata standard
Domain indexes should track:
- last reviewed date
- current owner
- verification status (`verified`, `stale`, `draft`)
