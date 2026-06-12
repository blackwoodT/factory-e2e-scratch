# Validation Evidence Matrix

Purpose: help orchestrators choose validation evidence from the slice's risk profile instead of ad hoc judgment.

This is a template default. Downstream projects should customize command names, artifact paths, thresholds, and applicability during architect/orchestrator bootstrap. Keep the matrix stack-neutral until the project has selected concrete tools.

## How to use this matrix

1. Identify every risk class touched by the ticket slice.
2. Select the smallest sufficient **required** evidence for each material risk.
3. Add **optional** evidence only when it materially reduces review uncertainty.
4. Record every skipped required or expected check as **skip with reason**, including residual risk and why the skip is acceptable for this slice.
5. Reference project-specific command names from `agent-qa.md` or adapter intents from `qa-command-adapters.md`; do not invent one-off commands in ticket handoffs.
6. When useful for review, record produced or skipped evidence references in optional `state.json.validation.evidence`; older tickets may omit this field.

Evidence labels mean:
- **Required**: expected for this risk class when the risk applies and the project has the relevant capability.
- **Optional**: useful when the slice is broad, risky, user-visible, or difficult to reason about from static review alone.
- **Skip with reason**: acceptable only when the check is not applicable, not configured, blocked by environment, unsafe to run, or intentionally deferred with residual risk recorded.

Attempt outcome labels mean:
- `passed`: the command/tool ran and validated the expected behavior.
- `failed_product`: the command/tool ran and found a product, app, configuration, data, security, accessibility, performance, or reliability problem.
- `failed_tooling`: the command/tool could not validate behavior because a runtime, agent tool, browser/MCP server, game engine, SDK, dependency, fixture, credential, display, sandbox, observability backend, export template, or comparable environment capability failed.
- `skipped_with_reason`: the check did not run and must include reason, residual risk, and sufficiency rationale.
- `not_applicable`: the check does not apply to the slice.
- `blocked`: required evidence cannot be obtained yet.

A `failed_tooling`, `skipped_with_reason`, or `blocked` record is reviewable evidence about the validation attempt, but it does not satisfy required validation by itself. Required evidence is satisfied only by a passing equivalent check, an explicitly accepted skip with residual risk, or completion of the prerequisite/follow-up that restores the missing capability. This applies to browser apps, Godot or other game engines, APIs, CLIs, infrastructure, observability, and any other runtime.

## Template matrix by risk class

| Risk class | Typical triggers | Required evidence | Optional evidence | Skip with reason | Bootstrap customization |
|---|---|---|---|---|---|
| Docs-only / workflow | Policy docs, templates, role guidance, README/index updates, documentation checks. | Doc integrity check; link/path validation when available; concise summary of changed policy surface. | Reviewer checklist dry-run; sample prompt or handoff excerpt when the doc changes agent behavior. | Explain why no runtime/build/test evidence applies and note any unchecked links or generated references. | Define the doc checker command and which indexes must link new policy docs. |
| Taste / maintainability invariant | A ticket touches a selected project taste invariant's declared scope, such as logging, naming, module complexity, side-effect imports, retries/timeouts, or generated-code boundaries. | Evidence named by the selected rule in `docs/design-docs/taste-invariants.md`: manual checklist, lint/test command, bounded artifact, structural check, or skipped-with-reason note. | Before/after example, narrow diff walkthrough, reviewer checklist dry-run, or project-specific adapter output when it materially reduces uncertainty. | Explain why the invariant is not applicable, not configured, unsafe to check, or intentionally deferred; record residual risk and follow-up. Do not treat template examples as active policy. | Generate project-specific taste invariants from `docs/design-docs/taste-invariants-template.md`; replace example rules with selected scopes, enforcement status, commands, evidence, owners, and remediation paths. |
| UI / user experience | Perceptible layout, copy, navigation, accessibility, visual state, or interaction changes. | Static/build checks relevant to the UI surface; screenshot or equivalent visual artifact when a visual change is perceptible; smoke or journey evidence when a runnable UI exists. | Before/after screenshots, video, DOM snapshot, console-error excerpt, keyboard/screen-reader notes, human visual review. | State why no UI is runnable or no perceptible change exists; record residual risk for unobserved visual behavior. | Define UI journey commands, artifact paths, accessibility checks, and when human visual review is required. |
| Data / persistence | Schema, migration, model, validation, query, fixture, import/export, or persistence logic changes. | Schema/config validation when available; targeted tests for changed data behavior; evidence that migrations or data transforms were validated safely. | Seed/fixture replay, rollback/dry-run, representative query output, contract fixture update evidence. | Explain missing database/storage access, unsafe migration conditions, or why the change is data-shape only; note rollback risk. | Define safe data environments, migration validation commands, fixture locations, and data-sanitization rules. |
| Security / trust boundary | Auth, authorization, secrets, input validation, permissions, crypto, dependency trust, untrusted boundary parsing/validation, or production-safety changes. | Targeted security/domain tests or checks; evidence for changed trust-boundary behavior; boundary id, untrusted input, validation/parsing point, positive/negative case result, and confirmation secrets are not exposed in logs/artifacts. | Threat-model note, dependency advisory scan, malformed/unauthorized/abuse-case tests, manual review by security specialist. | Explain why a security or boundary-validation check is not applicable, not configured, unavailable, or unsafe; record residual exposure and any human approval needed. | Define security scan commands, sensitive artifact rules, approved test identities, boundary-validation evidence commands, and specialist-trigger thresholds. |
| Observability / reliability | Logging, error reporting, metrics, traces, alerts, operational dashboards, or failure visibility changes. | Evidence that new/changed behavior emits expected bounded logs or operational signals when applicable; error-path evidence for changed failure handling. | Metric/trace threshold summary, alert/dash query result, correlation/request-id example, before/after log excerpt. | Explain why logs/metrics/traces are not configured or not affected; record what reviewers cannot observe. | Define log/metric/trace query commands, artifact redaction rules, thresholds, and local/dev observability availability. |
| Infrastructure / environment | CI, deployment config, runtime config, secrets wiring, local tooling, environment bootstrap, or resource definitions. | Config validation, dry-run, plan, or syntax check when available; evidence that changed environment assumptions are documented. | Isolated deploy preview, rollback note, dependency/tool version inventory, cleanup verification. | Explain unavailable credentials/services, unsafe deployment target, or why only documentation changed; note operational residual risk. | Define safe dry-run commands, allowed environments, credential boundaries, and cleanup commands. |
| Performance / capacity | Latency, throughput, memory, bundle size, query cost, startup time, caching, or resource-use changes. | Baseline vs changed measurement when the slice intentionally affects performance; targeted test/check for the changed hot path when available. | Profiling excerpt, resource budget comparison, bundle/artifact size delta, stress/sampling run. | Explain why measurement is unavailable or disproportionate; record whether performance risk is accepted or deferred. | Define budgets, benchmark commands, acceptable variance, artifact locations, and when performance specialist review is required. |
| Integration / API / boundary | API contracts, CLI behavior, webhooks, queues, SDK calls, file formats, generated clients, persistence hydration, or external system boundaries. | Contract/schema/parser validation or targeted integration test for the changed boundary; smoke evidence for representative request/command/job when safe; positive and negative boundary-validation evidence when untrusted input handling changes. | Mock/fixture replay, backward-compatibility check, generated-client diff, bounded log excerpt for request correlation. | Explain missing external dependency, unsafe live target, unconfigured validation enforcement, or why the boundary is not executable; record compatibility and trust-boundary risk. | Define safe integration targets, fixture contracts, command names, boundary inventory, parser/validator evidence expectations, and production-protection rules. |

## Relationship to boundary validation invariants

For security, trust-boundary, integration, API, CLI, webhook, queue, file, SDK, or persistence risk, use `boundary-validation-invariants.md` to decide which boundary-validation evidence is required, optional, or skipped with reason. Boundary evidence should remain project-specific and should reference the generated architecture contract rather than a universal validation library or transport model.

## Relationship to QA adapters

For runnable targets, prefer evidence that agents can reproduce through project-defined commands. The template provides stack-neutral adapter intents for `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop`; they fail closed until a downstream project configures them. See `qa-command-adapters.md` for adapter behavior and `agent-qa.md` for project-specific command and artifact documentation.

For observability/reliability risk, optional local/dev observability stack and query-pack examples are documented in `ephemeral-observability.md`. Use those examples only when a downstream project has configured safe queryable logs, metrics, traces, or operational signals, and keep artifacts bounded to the smallest sufficient evidence for the slice.

For UI risk, optional browser-driven journey examples are documented in `browser-critical-journeys.md`. Use those examples only when a downstream project has configured a safe runnable UI target, and keep browser screenshots, console logs, DOM snapshots, traces, or video scoped to the smallest sufficient evidence for the slice.

The matrix does not require every ticket to run every adapter or produce every signal type. Use adapter evidence only when it is applicable to the risk class and the project has configured a safe non-production target. Record missing selected evidence as skipped with reason and residual risk rather than treating unavailable tooling as a pass.

## Bootstrap checklist for downstream projects

During initial project setup, the architect/orchestrator should:

1. Keep or remove risk classes based on the project's actual surfaces.
2. Replace generic evidence descriptions with project-specific command names and artifact paths.
3. Define thresholds, budgets, and safe environments where applicable.
4. Mark unavailable evidence types as not configured yet, with the residual risk this creates.
5. Keep `validation-contracts.md`, `agent-qa.md`, and this matrix aligned so ticket handoffs reference stable commands instead of one-off instructions.
