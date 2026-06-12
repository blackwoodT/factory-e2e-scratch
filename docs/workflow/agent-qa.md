# Agent QA Enablement

Purpose: make application behavior directly legible to agents so they can reduce human QA load with repeatable evidence instead of only reading code.

## Plain-language model
Agent QA needs three layers:
1. **Command access**: the agent can run the app, tests, and smoke checks from the repo.
2. **Browser/app access**: the agent can inspect the running UI with screenshots, DOM snapshots, console logs, and navigation steps.
3. **Operational access**: the agent can query local logs, metrics, and traces for performance and reliability evidence.

VS Code can be part of this loop, but the key is not VS Code alone. The repo must expose predictable commands and evidence artifacts, and the agent runtime must be allowed to run those commands or connect to MCP/browser tooling.

## VS Code / ChatGPT / Codex guidance
- The ChatGPT VS Code extension used with ChatGPT Work with Apps can provide editor context, especially open files and selections, but it should not be treated as the whole QA harness.
- For autonomous test execution, prefer Codex in the IDE/CLI/app with permission to run workspace commands, because it can execute tests, inspect outputs, and attach evidence.
- For browser-driven validation, wire a browser automation path such as Playwright, Chrome DevTools Protocol, or an MCP browser server that can capture screenshots, console logs, DOM snapshots, and traces.
- For teams that stay in VS Code, define VS Code tasks that call the same repo scripts the agent uses. The editor becomes the operator surface; the repo scripts remain the source of truth.

## Template requirements for downstream projects
Each project bootstrapped from this template should define:
- app start command per worktree or branch
- smoke test command
- UI journey command(s) for critical flows
- screenshot/video artifact location
- console/log capture location
- safe authentication and test-data strategy for protected flows
- observability query commands when logs, metrics, or traces exist
- platform-appropriate wrappers, such as PowerShell/task-runner commands for Windows-first projects

A browser-tool failure in the agent runtime, IDE, or MCP server is separate from repo configuration. The repo should still provide deterministic browser commands where UI evidence matters, so agents can fall back to command-line screenshots/traces when a hosted browser plugin is unavailable. Record the hosted-tool failure as `failed_tooling`; do not treat it as satisfying required UI evidence unless an equivalent fallback passes or the validation contract explicitly accepts the skip.

The same rule applies outside browser apps. For Godot or other game engines, native desktop apps, CLIs, APIs, data jobs, or infrastructure projects, use the project-defined runtime command that best matches the risk: headless engine tests, scene-load smoke checks, export validation, screenshots/video from a deterministic test scene, bounded logs, database fixtures, API smoke checks, or observability queries. Missing engines, SDKs, export templates, credentials, fixtures, displays, sandboxes, or telemetry backends are `failed_tooling`/`skipped_with_reason` records, not passing product evidence.

## Recommended repo command shape
Projects should adapt these names to their stack while preserving the intent:

| Command | Purpose | Required output |
|---|---|---|
| `qa:boot` | Start the app in an isolated local environment | URL, PID/container id, log path |
| `qa:smoke` | Run a minimal health/user-flow check | pass/fail summary |
| `qa:ui` | Drive critical UI journey(s) | screenshots/video/trace path |
| `qa:logs` | Print relevant log excerpt | bounded text output |
| `qa:metrics` | Query performance/reliability budgets | pass/fail threshold summary |
| `qa:stop` | Tear down local app/observability resources | cleanup confirmation |


## Stack-neutral QA adapters

This template includes runnable placeholder adapters for the core command intents:

| Intent | Adapter | Default behavior |
|---|---|---|
| `qa:boot` | `scripts/qa/boot.sh` | Fails with exit `2` until `QA_BOOT_COMMAND` is configured or the adapter is replaced. |
| `qa:smoke` | `scripts/qa/smoke.sh` | Fails with exit `2` until `QA_SMOKE_COMMAND` is configured or the adapter is replaced. |
| `qa:logs` | `scripts/qa/logs.sh` | Fails with exit `2` until `QA_LOGS_COMMAND` is configured or the adapter is replaced. |
| `qa:stop` | `scripts/qa/stop.sh` | Fails with exit `2` until `QA_STOP_COMMAND` is configured or the adapter is replaced. |

The adapters are safe placeholders, not app-specific implementations. Downstream projects should wire them to their own task runner during bootstrap and keep this document updated with the actual commands and artifact locations. See `qa-command-adapters.md` for the adapter contract, environment variables, expected outputs, and safety behavior.

## Optional observability query packs

For projects with local/dev logs, metrics, traces, or operational signals, define the smallest useful observability query pack during bootstrap and record concrete command names, thresholds, artifact paths, retention, redaction rules, safe environments, and skip rules here or in a linked project observability doc.

Use `ephemeral-observability.md` for optional stack-neutral examples covering startup/shutdown, bounded log queries, metric threshold summaries, trace/span threshold summaries, artifact output, and required/optional/skip-with-reason evidence handling. Non-observability projects or projects without configured local/dev telemetry should explicitly mark observability evidence as skipped with reason and residual risk in the active validation contract.

Metric and trace commands are project-defined intents unless the downstream project adds adapters for them. The template-provided runnable adapters remain `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop`.

## Optional browser critical journeys

For projects with a runnable browser UI, define the smallest useful set of critical journeys during bootstrap and record concrete command names, artifact paths, console-error policy, and skip rules here. The recommended `qa:ui` name is an intent, not a mandatory template adapter; projects may map it to any safe local/dev browser tooling they choose.

Use `browser-critical-journeys.md` for optional Playwright-style, Chrome DevTools Protocol-style, and MCP browser-tooling example shapes. Non-UI projects or projects without configured browser tooling should explicitly mark browser journey evidence as skipped with reason and residual risk in the active validation contract.


## Recording evidence in ticket state

When QA evidence is selected by the active validation contract, record reviewable references in the implementer handoff and, when useful, in optional `state.json.validation.evidence`. Keep the state entry compact: evidence type, risk class, command intent or project-defined command, artifact path/reference, bounded result summary, safe environment, redaction/retention note, and skipped-evidence reason plus residual risk when applicable.

This state field is optional and additive. Older tickets may omit it, and non-runnable, non-UI, or non-observability projects should skip unavailable evidence with reason rather than fabricating artifacts.

## Evidence standard
Implementer handoff should include:
- exact command(s) run
- app URL or target environment
- before/after screenshot or video path when UI changed
- console errors and relevant runtime logs
- metric/trace threshold results when applicable
- skipped evidence with a reason and residual risk

## Safety boundaries
- Do not point agent QA at production systems unless explicitly approved.
- Use synthetic or sanitized data by default.
- Keep secrets out of screenshots, logs, videos, and PR artifacts.
- Prefer disposable local resources that can be torn down after the ticket.
