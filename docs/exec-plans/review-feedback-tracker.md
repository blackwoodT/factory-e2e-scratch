# Review Feedback Tracker

Status: `template`  
Owner: `orchestrator`  
Last reviewed: `2026-06-03`

## Purpose

Track repeated PR review feedback, recurring refactors, repeated validation gaps, and bugs that may deserve durable project guidance. Use this tracker as an intake loop before promoting feedback into documentation, validation guidance, lint, tests, scripts, or future TODOs.

This tracker helps agents stop relearning the same feedback ticket by ticket while avoiding broad rules for one-off preferences.

> **Template-only warning:** this file is not a universal review taxonomy, style guide, severity model, promotion threshold, lint config, naming scheme, logging model, package policy, or app architecture. Downstream projects must replace example categories, owners, triggers, paths, commands, evidence expectations, remediation notes, and enforcement destinations with project-specific values, or leave them as explicit `TBD` entries with owner and follow-up trigger.

## Do not promote one-off feedback

Do not turn every PR comment into a rule. Track or promote feedback only when it:

- appears repeatedly across tickets, reviews, refactors, bugs, or human guidance; or
- prevents a serious reliability, maintainability, operability, security, accessibility, product-quality, or agent-legibility issue; and
- can be stated with clear scope, non-scope, rationale, evidence expectation, remediation path, owner, and update/retirement path.

One-off subjective preferences should normally remain PR-local unless they also identify correctness, safety, reliability, acceptance-criteria, or product-quality risk.

## Promotion destinations

Use the least durable or least mechanical destination that solves the repeated problem. Suggested dispositions below are examples; downstream projects may rename or replace them.

| Disposition | Use when | Update path |
|---|---|---|
| `tracker-only` | The pattern may repeat but is not stable enough for policy. | Keep evidence here and revisit during finalization or doc gardening. |
| `promote-to-taste-invariant` | Repeated human preference should become durable project taste policy. | Update generated `docs/design-docs/taste-invariants.md` using `docs/design-docs/taste-invariants-template.md` as the rule shape. |
| `promote-to-architecture-contract` | Feedback changes project domains, boundaries, cross-cutting concerns, trust boundaries, or enforcement plan. | Update generated `docs/design-docs/architecture-contract.md` first. |
| `promote-to-structural-boundary-rule` | Feedback is a dependency/import-boundary rule ready for mechanical enforcement. | Update generated architecture contract first, then project-specific `docs/design-docs/architecture-boundaries.json` if configured. |
| `promote-to-validation-guidance` | Feedback repeatedly points to missing, unclear, or insufficient validation evidence. | Update project-specific validation contract guidance, evidence matrix, QA docs, or ticket templates. |
| `future-lint-test-adapter-todo` | Mechanical enforcement is desirable but the project has not selected safe tooling yet. | Add a scoped TODO or tech-debt item with owner, trigger, and residual risk. |
| `deferred` | The pattern is plausible but not ready, safe, or sufficiently evidenced. | Record what would make it promotable. |
| `do-not-promote` | Feedback is one-off, obsolete, subjective without durable value, or already covered. | Record rationale only when useful to prevent churn. |

## Entry format

Keep entries compact and agent-legible. Record enough evidence that a future agent can understand what repeated, why it matters, and what to do next.

| Field | Guidance |
|---|---|
| Feedback summary | Short description of the repeated comment, bug, refactor, or evidence gap. |
| Sources / evidence | PRs, tickets, review notes, bug reports, or bounded excerpts showing repetition. Avoid secrets, production data, and unbounded logs. |
| Repetition signal | Why this is more than a one-off, or why one severe issue justifies tracking. Do not use a universal numeric threshold unless the downstream project explicitly defines one. |
| Why it matters | Reliability, maintainability, operability, security, accessibility, product quality, or agent legibility impact. |
| Scope / non-scope | Where the rule or guidance applies and where it does not apply. |
| Disposition | One suggested destination from the table above, or a project-specific value. |
| Destination / follow-up | Target doc, config, test, lint, TODO, or reason no promotion is planned. |
| Evidence expectation | Smallest useful evidence future tickets should provide if the candidate is promoted. |
| Remediation | What an agent should change when the issue appears again. |
| Owner / status / last reviewed | Project-specific owner, current state, and review date. |

## Tracker

Remove example rows during downstream bootstrap or replace them with real project feedback.

| ID | Feedback summary | Sources / evidence | Repetition signal | Why it matters | Scope / non-scope | Disposition | Destination / follow-up | Evidence expectation | Remediation | Owner | Status | Last reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Example only — replace/remove | Reviewers repeatedly ask for project-approved runtime diagnostic context in logs. | Replace with PRs/tickets/review notes. | Replace with project evidence; do not invent history. | Improves agent and human diagnosis of production-like failures. | Replace with project runtime boundary; not applicable to docs-only tickets. | `tracker-only` / `promote-to-taste-invariant` / `deferred` | Replace with target doc or TODO. | Replace with project command, bounded log excerpt, or manual checklist. | Add approved context fields or update selected rule if policy changed. | TBD | example | YYYY-MM-DD |

## Finalization loop

During ticket finalization, the orchestrator should inspect review findings, non-blocking observations, accepted-with-follow-up notes, repeated fix-loop causes, recurring validation gaps, and human comments. Then choose one of these outcomes:

1. No tracker action because feedback was one-off, already covered, or not durable.
2. Add or update a tracker entry with sources and rationale.
3. Promote a tracker entry into generated downstream `docs/design-docs/taste-invariants.md`.
4. Promote architecture-relevant feedback into generated downstream `docs/design-docs/architecture-contract.md`.
5. Promote dependency-boundary feedback into project-specific structural dependency config only after the architecture contract is updated.
6. Promote repeated evidence gaps into validation-contract, evidence-matrix, QA, test, lint, script, or TODO guidance.

If promotion changes active project policy, update the source-of-truth document before expecting implementers or reviewers to enforce the new rule.

## Relationship to taste invariants

Use this tracker as intake. Use generated downstream `docs/design-docs/taste-invariants.md` as selected durable taste policy. A tracker entry becomes a taste invariant only after it passes the promotion checklist in `docs/design-docs/taste-invariants-template.md` and has project-specific scope, evidence, remediation, owner, and update path.

## Relationship to architecture and validation

Architecture-relevant feedback should update generated downstream `docs/design-docs/architecture-contract.md`. Dependency-boundary feedback may later be projected into project-specific `docs/design-docs/architecture-boundaries.json` when configured. Repeated validation-evidence feedback should update project-specific validation-contract guidance or evidence-matrix expectations instead of creating ad hoc ticket instructions.
