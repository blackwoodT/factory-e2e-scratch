# Review Feedback Tracker

Status: `active`
Owner: `orchestrator`
Last reviewed: `2026-06-12`

## Purpose

Track repeated PR review feedback, recurring refactors, repeated validation gaps, and bugs that may deserve durable project guidance. See `docs/design-docs/taste-invariants-template.md` for the promotion checklist and `docs/design-docs/taste-invariants.md` for the current selected rule pack.

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
