# Review Feedback Tracker

Status: `active`
Owner: `orchestrator`
Last reviewed: `2026-06-12`

## Purpose

Track repeated PR review feedback, recurring refactors, repeated validation gaps, and bugs that may deserve durable project guidance. See `docs/design-docs/taste-invariants-template.md` for the promotion checklist and `docs/design-docs/taste-invariants.md` for the current selected rule pack.

> **Template-only warning:** this file is not a universal review taxonomy, style guide, severity model, promotion threshold, lint config, naming scheme, logging model, package policy, or app architecture. Categories, owners, triggers, paths, commands, evidence expectations, remediation notes, and enforcement destinations must hold project-specific values, or remain explicit `TBD` entries with owner and follow-up trigger.

## Do not promote one-off feedback

Do not turn every PR comment into a rule. Track or promote feedback only when it:

- appears repeatedly across tickets, reviews, refactors, bugs, or human guidance; or
- prevents a serious reliability, maintainability, operability, security, accessibility, product-quality, or agent-legibility issue; and
- can be stated with clear scope, non-scope, rationale, evidence expectation, remediation path, owner, and update/retirement path.

One-off subjective preferences should normally remain PR-local unless they also identify correctness, safety, reliability, acceptance-criteria, or product-quality risk.

## Promotion destinations

Use the least durable or least mechanical destination that solves the repeated problem.

| Disposition | Use when | Update path |
|---|---|---|
| `tracker-only` | The pattern may repeat but is not stable enough for policy. | Keep evidence here and revisit during finalization or doc gardening. |
| `promote-to-taste-invariant` | Repeated human preference should become durable project taste policy. | Update `docs/design-docs/taste-invariants.md` using `docs/design-docs/taste-invariants-template.md` as the rule shape. |
| `promote-to-architecture-contract` | Feedback changes project domains, boundaries, cross-cutting concerns, trust boundaries, or enforcement plan. | Update `docs/design-docs/architecture-contract.md` first. |
| `promote-to-structural-boundary-rule` | Feedback is a dependency/import-boundary rule ready for mechanical enforcement. | Update the architecture contract first, then `docs/design-docs/architecture-boundaries.json` if configured. |
| `promote-to-validation-guidance` | Feedback repeatedly points to missing, unclear, or insufficient validation evidence. | Update validation contract guidance, evidence matrix, QA docs, or ticket templates. |
| `future-lint-test-adapter-todo` | Mechanical enforcement is desirable but the project has not selected safe tooling yet. | Add a scoped TODO or tech-debt item with owner, trigger, and residual risk. |
| `deferred` | The pattern is plausible but not ready, safe, or sufficiently evidenced. | Record what would make it promotable. |
| `do-not-promote` | Feedback is one-off, obsolete, subjective without durable value, or already covered. | Record rationale only when useful to prevent churn. |

## Tracker

No entries yet. This is a fresh project; no review feedback has been collected.

| ID | Feedback summary | Sources / evidence | Repetition signal | Why it matters | Scope / non-scope | Disposition | Destination / follow-up | Evidence expectation | Remediation | Owner | Status | Last reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Finalization loop

During ticket finalization, the orchestrator should inspect review findings, non-blocking observations, accepted-with-follow-up notes, repeated fix-loop causes, recurring validation gaps, and human comments. Then choose one of:

1. No tracker action — feedback was one-off, already covered, or not durable.
2. Add or update a tracker entry with sources and rationale.
3. Promote a tracker entry into generated `docs/design-docs/taste-invariants.md`.
4. Promote architecture-relevant feedback into `docs/design-docs/architecture-contract.md`.
5. Promote dependency-boundary feedback into project-specific structural dependency config after the contract is updated.
6. Promote repeated evidence gaps into validation-contract, evidence-matrix, QA, test, lint, script, or TODO guidance.
