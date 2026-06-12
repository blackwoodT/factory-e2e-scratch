# Harness Template Setup

This repository is a reusable workflow template. Harness tickets should improve the template so every copied project can generate its own project-specific harness during the initial architect/orchestrator passes.

## Template-first rule
Do not hard-code one project's architecture, quality gates, or observability assumptions into this template. Instead, template tickets should add:
- scaffold files that new projects can fill in
- prompts and role rules that require project-specific generation
- validation scripts that check the generated structure exists
- examples that are clearly marked as examples, not universal policy

## Initial project bootstrap expectations
When a project is created from this template, the architect/orchestrator should generate or refresh. For repositories that already ran an older version of this harness, use `docs/workflow/upgrading-existing-harness.md` first so project-specific docs and active ticket history are preserved:
- `docs/design-docs/architecture-contract.md` from `docs/design-docs/architecture-contract-template.md`
- `docs/workflow/security-review.md` project-specific applicability notes
- `docs/exec-plans/as-built.md` with current implemented reality
- `docs/exec-plans/build-cost.md` with ticket cost rollups
- `docs/exec-plans/ticket-change-log.md` with finalized ticket summaries
- `docs/exec-plans/review-feedback-tracker.md` as the lightweight intake loop for repeated PR feedback, leaving it empty unless real project feedback exists
- project-specific validation evidence requirements in the active ticket's validation contract
- `docs/workflow/validation-evidence-matrix.md` customized with project-specific command names, artifact paths, thresholds, and non-applicable risk classes
- `docs/workflow/agent-qa.md` project-specific command names for app boot, UI journeys, logs, metrics, traces, artifacts, and teardown
- `docs/design-docs/taste-invariants.md` from `docs/design-docs/taste-invariants-template.md` when the project selects repeated human review preferences as durable invariants, replacing every example rule with project-specific scope, reason, enforcement status, evidence expectation, remediation, owner, and update path
- optional local/dev observability stack and query-pack choices from `docs/workflow/ephemeral-observability.md`, including safe environments, thresholds, retention, redaction, and skip rules
- optional project-specific structural dependency config from `docs/design-docs/architecture-boundaries-template.json` when the generated architecture contract has dependency-boundary rules ready for mechanical enforcement
- project-specific untrusted-boundary validation inventory in `docs/design-docs/architecture-contract.md`, with reviewer evidence expectations and enforcement status for applicable HTTP/RPC, CLI, queue, webhook, file, SDK, persistence, or other trust-zone crossings

### Architecture contract bootstrap
During initial downstream bootstrap, the architect should copy or derive `docs/design-docs/architecture-contract.md` from `docs/design-docs/architecture-contract-template.md` and replace template examples with project-specific facts. The generated contract should cover the downstream project's actual domains, code roots, layer/module/service boundaries, allowed and forbidden dependency edges, cross-cutting concerns, untrusted-boundary validation invariants, enforcement plan, verification status, and explicit unknowns.

Do not commit a generic `architecture-contract.md` to this template repository as if it applies to every future project. The template repository should keep the reusable template and role instructions; downstream projects should generate their own contract during bootstrap.

The orchestrator should consult the generated contract when a ticket touches architecture, dependency boundaries, untrusted input boundaries, cross-cutting concerns, or enforcement rules. For unrelated slices, the contract need not be added to every Prompt Packet; add it as source material when it materially reduces review risk.

When untrusted-boundary validation rules are identified, record each project-specific boundary, untrusted input, validation/parsing point, failure behavior, reviewer evidence expectation, and enforcement status in the generated architecture contract. If a ticket touches a boundary before validation enforcement is configured, record the selected evidence or skipped-check rationale with residual risk instead of treating missing enforcement as a pass. See `docs/workflow/boundary-validation-invariants.md`.

When dependency-boundary rules are ready for mechanical enforcement, the architect/orchestrator should generate `docs/design-docs/architecture-boundaries.json` from `docs/design-docs/architecture-boundaries-template.json`, replace all example values with project-specific boundaries, path globs, dependency patterns, allowed edges, forbidden edges, and remediation guidance, then set `template_only` to `false`. If structural linting is not configured yet, tickets that touch dependency boundaries should record the check as skipped with reason and residual risk rather than treating missing enforcement as a pass. See `docs/workflow/structural-dependency-lint.md`.

When taste invariants are selected, the architect/orchestrator should generate `docs/design-docs/taste-invariants.md` from `docs/design-docs/taste-invariants-template.md`, remove non-applicable examples, and record whether each rule is docs-only, manual-review-only, linted, tested, script-adapter-backed, structural-boundary-backed, or deferred. If a ticket touches a selected invariant before enforcement is configured, record the selected manual evidence or skipped-check rationale with residual risk instead of treating missing enforcement as a pass.

### Review feedback tracker bootstrap

Keep `docs/exec-plans/review-feedback-tracker.md` as the downstream project's repeated-feedback intake loop. Do not seed fake entries during bootstrap. If the project already has real historical review feedback, bugs, or refactor patterns, record only evidence-backed entries with project-specific sources, owners, disposition, follow-up trigger, and remediation path.

Tracker entries are candidates, not policy. Promote them into generated `docs/design-docs/taste-invariants.md`, generated `docs/design-docs/architecture-contract.md`, project-specific `docs/design-docs/architecture-boundaries.json`, validation guidance, tests, lints, scripts, or TODOs only after the rule is stable, scoped, and useful enough to justify durable enforcement.

## Harness ticket interpretation
- `TKT-ARCH-006` should build the template mechanism that causes each new project to create an architecture contract; it should not define a single architecture for all downstream projects.
- QA/observability tickets should add reusable scripts, prompts, and docs that adapt to the target project's app stack.
- Review and finalization tickets should update role rules and workflow docs so all downstream projects inherit the behavior.
