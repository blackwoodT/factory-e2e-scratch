# Harness Template TODO

Purpose: lightweight working backlog for improving this template repository without creating project-shaped ticket folders that could be copied into downstream projects.

## Recommendation
Use this file as the active TODO list for template-harness improvements. Do **not** create `.ai/tickets/<ticket-id>/` folders for these roadmap items until the team intentionally starts a real implementation slice in this template repo. When a TODO is completed, move the outcome into `ticket-change-log.md` or remove the row if the change is fully captured elsewhere.

Why this approach:
- avoids making the template look like it already belongs to a specific downstream project
- keeps project-specific `.ai/tickets/` state out of copied scaffolding
- still lets the team work through the improvements one at a time
- keeps the roadmap visible without forcing premature ticket state-machine overhead

## Source context
Use `docs/references/openai-harness-engineering.md` as the local summary of the OpenAI Harness Engineering ideas behind this list. The reference links to the original OpenAI article and captures the specific patterns these TODOs are meant to preserve.

## Status legend
- `todo`: not started
- `next`: recommended next slice
- `in progress`: active work
- `blocked`: needs a decision or prerequisite
- `done`: implemented and recorded elsewhere

## Active TODOs

| ID | Status | Size | Goal | Recommended next action |
|---|---|---:|---|---|
| TKT-OBS-001 | done | M | Define validation evidence matrix by risk class. | Added stack-neutral `validation-evidence-matrix.md` with required, optional, and skip-with-reason evidence by risk class. |
| TKT-QA-002 | done | M | Add app boot + smoke + log capture script templates. | Added stack-neutral fail-closed adapters and docs for `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop`. |
| TKT-UI-003 | done | M/L | Add browser-driven critical-journey harness examples. | Added optional browser critical journey documentation with Playwright/CDP/MCP example shapes, required/optional/skip-with-reason evidence guidance, and no mandatory browser tooling. |
| TKT-OBS-004 | done | L | Add local ephemeral observability stack + query pack. | Added optional stack-neutral `ephemeral-observability.md` with local/dev observability profiles, query-pack templates, log/metric/trace example shapes, startup/shutdown evidence, artifact guidance, and safety boundaries. |
| TKT-WF-005 | done | S/M | Wire QA/observability artifacts into Prompt Packets/state. | Added optional `state.json.validation.evidence` guidance plus Prompt Packet, implementer handoff, reviewer checklist, and finalization gate references for QA/observability artifacts and skipped-evidence rationale. |
| TKT-ARCH-006 | done | M | Generate project-specific architecture contracts during bootstrap. | Added architect/orchestrator bootstrap guidance, clearer architecture-contract template generation rules, and docs-check markers without committing a universal downstream contract. |
| TKT-ARCH-007 | done | L | Add configurable structural dependency lint/test. | Added stack-neutral structural dependency checker scaffold, generated-config template, fixture self-test, docs, and role/bootstrap guidance. |
| TKT-ARCH-008 | done | M | Add boundary validation invariant checks/examples. | Added stack-neutral boundary-validation invariant guidance, architecture-contract prompts, evidence expectations, role/template hooks, and docs-check coverage without prescribing one validation library. |
| TKT-TASTE-009 | done | M | Encode top taste invariants. | Added template-first taste invariant rule pack guidance, promotion checklist, validation evidence hooks, role/bootstrap guidance, and docs-check coverage without prescribing universal style or tooling. |
| TKT-WF-010 | done | S | Add review-feedback-to-rule-promotion loop. | Added a lightweight repeated-feedback tracker, finalization promotion check, role/bootstrap guidance, README overview, and docs-check coverage without adding universal review taxonomy or tooling. |

## Ticket briefs

### TKT-OBS-001 — validation evidence matrix by risk class
- **Intent:** make the orchestrator choose validation evidence based on risk instead of ad hoc judgment.
- **Template deliverables:** add `docs/workflow/validation-evidence-matrix.md` with risk classes such as docs-only, UI, data, security, observability, infra, performance, and integration/API.
- **Bootstrap behavior:** downstream architect/orchestrator customizes the matrix to the project stack and writes project-specific command names.
- **Acceptance criteria:** matrix is linked from `validation-contracts.md`, required by `check_workflow_docs.py`, and has clear “required / optional / skip with reason” evidence rows.
- **Avoid:** hard-coding web-app-only or cloud-provider-specific requirements.

### TKT-QA-002 — app boot, smoke, and log capture templates
- **Intent:** give agents a predictable way to start the app, verify basic health, capture logs, and tear down resources.
- **Template deliverables:** add stack-neutral placeholder scripts/docs for `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop` plus instructions for adapting them in a downstream project.
- **Bootstrap behavior:** initial architect pass records actual commands and artifact locations in `docs/workflow/agent-qa.md`.
- **Acceptance criteria:** commands have expected inputs/outputs, produce bounded evidence, and never target production by default.
- **Avoid:** assuming Node, Python, Docker, or a browser exists unless the project opts in.

### TKT-UI-003 — browser-driven critical journey examples
- **Status:** done.
- **Intent:** let agents collect UI evidence such as screenshots, console logs, DOM snapshots, traces, or video.
- **Template deliverables:** added `docs/workflow/browser-critical-journeys.md` with optional Playwright-style, Chrome DevTools Protocol-style, and MCP browser-tooling example shapes plus clear adapter points.
- **Bootstrap behavior:** downstream project selects applicable journeys (for example login, onboarding, save flow), command names, artifact paths, console policy, thresholds, and skip rules in `agent-qa.md`.
- **Acceptance criteria:** examples demonstrate before/after capture, console-error capture, repeatable journey execution, and required/optional/skip-with-reason evidence handling.
- **Avoid:** requiring browser tooling for non-UI projects; no mandatory browser adapter or stack-specific executable was added.

### TKT-OBS-004 — ephemeral observability stack examples
- **Status:** done.
- **Intent:** make logs, metrics, and traces queryable by agents in isolated local/dev environments.
- **Template deliverables:** added `docs/workflow/ephemeral-observability.md` with optional local/dev observability profile guidance, query-pack templates, log query, metric threshold, trace/span threshold, startup/shutdown, artifact output, stack-pattern, safety, bootstrap, and reviewer examples.
- **Bootstrap behavior:** downstream project chooses a stack pattern and records query commands, budgets, thresholds, artifact paths, retention, redaction rules, safe environments, and skip rules in `agent-qa.md` or a project observability doc.
- **Acceptance criteria:** examples cover log query, metric threshold, trace/span threshold, startup/shutdown, artifact output, and required/optional/skip-with-reason evidence handling.
- **Avoid:** no mandatory Victoria, Prometheus, OpenTelemetry, Docker, Compose, browser, cloud, or vendor-specific implementation was added.

### TKT-WF-005 — QA/observability artifacts in workflow state
- **Status:** done.
- **Intent:** make QA artifacts first-class evidence in prompt packets and review/finalization gates.
- **Template deliverables:** added optional `state.json.validation.evidence` guidance and updated ticket templates, Prompt Packets, validation docs, implementer handoff, reviewer checklist, and finalization gate references for QA commands, artifact paths, bounded log excerpts, metrics, traces, screenshots/browser journey refs, and skipped-evidence rationale.
- **Bootstrap behavior:** downstream projects include only fields relevant to their stack and customize command names, artifact paths, thresholds, safe environments, redaction, retention, and skip rules.
- **Acceptance criteria:** implementer handoff and reviewer checklist clearly reference QA artifacts without breaking older tickets; older tickets may omit `validation.evidence`.
- **Avoid:** no ticket is required to produce every artifact type.

### TKT-ARCH-006 — project-specific architecture contract generation
- **Status:** done.
- **Intent:** ensure each downstream project generates its own architecture contract instead of inheriting a fake universal one.
- **Template deliverables:** updated architect and orchestrator role/bootstrap instructions to create and consult `docs/design-docs/architecture-contract.md` from `architecture-contract-template.md` during initial project setup.
- **Bootstrap behavior:** architect maps project domains, layers or boundaries, allowed edges, cross-cutting boundaries, enforcement plan, verification status, and explicit unknowns.
- **Acceptance criteria:** initial architect output references the generated contract, docs checker detects the template-generation markers, and downstream projects have clear instructions for replacing template examples.
- **Avoid:** committing project-specific layer rules into this template as if they apply everywhere.

### TKT-ARCH-007 — configurable structural dependency lint/test
- **Status:** done.
- **Intent:** mechanically enforce dependency boundaries once a downstream project has an architecture contract.
- **Template deliverables:** added a config-driven structural dependency checker scaffold, `architecture-boundaries-template.json`, stack-neutral fixture self-test, workflow docs, role/bootstrap guidance, and docs-check coverage.
- **Bootstrap behavior:** downstream projects generate `docs/design-docs/architecture-boundaries.json` from the template, choose boundary names, path globs, dependency patterns, allowed edges, forbidden edges, and remediation text, then set `template_only` to `false`.
- **Acceptance criteria:** checker fails closed on missing/template config, detects a forbidden edge in a sample fixture, and emits agent-legible remediation output.
- **Avoid:** no language-specific import parser, folder layout, framework, package manager, or app architecture was added as universal policy.

### TKT-ARCH-008 — boundary validation invariant examples
- **Status:** done.
- **Intent:** enforce the rule that untrusted inputs are parsed/validated at system boundaries.
- **Template deliverables:** added language/framework-neutral guidance, common boundary category examples, architecture-contract prompts, validation evidence expectations, and workflow/role hooks.
- **Bootstrap behavior:** downstream project identifies boundaries such as HTTP, CLI, queues, webhooks, files, SDK calls, and database records.
- **Acceptance criteria:** docs define what counts as a boundary, what evidence reviewers expect, and how projects can add lint/test enforcement. Completed with docs-check coverage and without adding a premature universal checker.
- **Avoid:** prescribing one validation library.

### TKT-TASTE-009 — taste invariant rule pack
- **Status:** done.
- **Intent:** capture repeated human preferences as enforceable rules or templates so agents stop relearning them.
- **Template deliverables:** added `docs/design-docs/taste-invariants-template.md`, a rule-promotion checklist, example-only starter invariant ideas, evidence expectations, and enforcement status guidance.
- **Bootstrap behavior:** downstream project generates `docs/design-docs/taste-invariants.md` from the template when selecting initial invariants such as structured logging, naming, file size, side-effect imports, retries/timeouts, and generated-code boundaries.
- **Acceptance criteria:** rules are small, reviewable, and indicate whether enforcement is docs-only, manual-review-only, linted, tested, script-adapter-backed, structural-boundary-backed, or deferred.
- **Avoid:** no universal code style, naming scheme, logging framework, threshold, retry policy, side-effect rule, generated-code convention, language, framework, linter, formatter, or app topology was added.

### TKT-WF-010 — review-feedback-to-rule-promotion loop
- **Status:** done.
- **Intent:** convert repeated PR comments, refactors, and bugs into durable docs, lints, tests, or TODOs.
- **Template deliverables:** add a lightweight repeated-feedback tracker and finalization prompt step.
- **Bootstrap behavior:** downstream finalization can add repeated feedback to the tracker or promote it into a rule.
- **Acceptance criteria:** finalization docs ask whether any review feedback should become documentation or tooling, and the tracker is linked from exec-plans.
- **Avoid:** turning every one-off preference into a rule.

## When to create real ticket folders
Create `.ai/tickets/<ticket-id>/` only when:
1. the TODO is selected for implementation now,
2. the branch is dedicated to that one template improvement,
3. the ticket state will not be copied into downstream projects as active project work, and
4. the work needs the full orchestrator/implementer/reviewer state-machine record.

For small documentation/template improvements, a PR plus this TODO file is usually enough.
