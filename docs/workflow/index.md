# Workflow System of Record

This folder is the indexed, maintainable source for workflow policy and operational guidance.

## Documents
Canonical end-to-end state machine and procedures live at the repo root in
[`workflow-reference.md`](../../workflow-reference.md); the topic files below refine it.

- `roles.md`: responsibility boundaries and handoff expectations.
- `review-gates.md`: two-pass review, stale-head handling, and merge gates.
- `review-tiers.md`: light/standard/high-risk review tiers and what each writes into `required_passes`.
- `prerequisites.md`: prerequisite assessment, child ticket policy, and verification loop.
- `validation-contracts.md`: required validation categories and evidence expectations.
- `validation-evidence-matrix.md`: risk-class matrix for required, optional, and skip-with-reason validation evidence.
- `agent-qa.md`: guidance for browser/app/observability evidence that agents can collect.
- `qa-command-adapters.md`: stack-neutral placeholders and contracts for `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop`.
- `browser-critical-journeys.md`: optional browser-driven critical-journey examples for UI evidence when a downstream project has a runnable UI.
- `ephemeral-observability.md`: optional local/dev observability stack and query-pack examples for logs, metrics, traces, startup/shutdown, and artifacts.
- `structural-dependency-lint.md`: config-driven scaffold for mechanically enforcing project-specific architecture dependency boundaries.
- `boundary-validation-invariants.md`: stack-neutral guidance for making untrusted-input boundary validation reviewable and optionally enforceable.
- `security-review.md`: risk-based security review trigger policy.
- `new-project-setup.md`: human runbook for stamping the repo starter into a new project and bootstrapping it.
- `harness-template-setup.md`: template-first rules for reusable Harness tickets.
- `upgrading-existing-harness.md`: safe upgrade path for existing downstream repos that predate the completed Harness workflow.
- `throughput-and-slicing.md`: recommended ticket slice size, split rules, and cycle metrics.
- `doc-hygiene.md`: documentation maintenance checks and monthly gardening cadence.
- `github-settings.md`: branch protection and repository settings that mechanically enforce the merge gates.
- `automation-blueprint.md`: design record for the automated GitHub Actions factory loop.
- `automation.md`: factory operator guide — arming a project, gates, commands, pauses, troubleshooting.

## Operator quick path
1. Start with `AGENTS.md` for high-priority constraints and routing.
2. Use `workflow-reference.md` for end-to-end procedural detail.
3. Use this `docs/workflow/` index for maintainable policy-by-topic.

## Maintenance standard
- Keep each topic file short and concrete.
- Prefer links over repeating policy text.
- Add/update links here when adding a new workflow policy doc.
