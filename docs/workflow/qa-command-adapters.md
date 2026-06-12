# QA Command Adapters

Purpose: provide stack-neutral command placeholders that downstream projects adapt so agents can boot a local target, run a smoke check, capture bounded logs, and stop the target without learning a new command shape for every ticket.

## Adapter command map

| Intent name | Template adapter (POSIX) | Cross-platform adapter | Downstream examples |
|---|---|---|---|
| `qa:boot` | `scripts/qa/boot.sh` | `python scripts/qa/qa.py boot` | VS Code task, `make qa-boot`, `just qa:boot`, package script, CI step |
| `qa:smoke` | `scripts/qa/smoke.sh` | `python scripts/qa/qa.py smoke` | smallest health check or critical-path smoke command |
| `qa:logs` | `scripts/qa/logs.sh` | `python scripts/qa/qa.py logs` | bounded local log query or artifact printer |
| `qa:stop` | `scripts/qa/stop.sh` | `python scripts/qa/qa.py stop` | local process/container/resource teardown |

The `qa:*` names describe the workflow intent. The shell adapters are the template's neutral runnable surface for POSIX shells; `scripts/qa/qa.py` provides the identical contract (same env vars, same exit codes) for native Windows or any environment with Python but no POSIX shell. Downstream projects may wrap or replace either with the project's preferred task runner.

## Default safety behavior

The adapters fail closed until configured:
- exit `0`: the configured project command ran successfully
- exit `1`: the adapter safety check or configured command failed
- exit `2`: the adapter is not configured yet

Exit `2` should be reported as skipped runtime QA with residual risk, not as a passed check. This prevents agents from mistaking an inert placeholder for real app evidence.

## Configuration contract

Projects can either replace the script bodies or set these environment variables in a local task runner, CI job, or shell profile:

| Variable | Used by | Purpose |
|---|---|---|
| `QA_BOOT_COMMAND` | `scripts/qa/boot.sh` | Starts the local/dev app or runnable target and prints URL/handle/log evidence. |
| `QA_SMOKE_COMMAND` | `scripts/qa/smoke.sh` | Runs a minimal runtime health or user-flow check and prints a pass/fail summary. |
| `QA_LOGS_COMMAND` | `scripts/qa/logs.sh` | Prints a bounded relevant log excerpt or log artifact path. |
| `QA_STOP_COMMAND` | `scripts/qa/stop.sh` | Tears down resources started for agent QA. |
| `QA_ARTIFACT_DIR` | all adapters | Directory for generated evidence; defaults to `.ai/qa-artifacts`. |
| `QA_ENVIRONMENT` | all adapters | Target environment label; defaults to `local`. |
| `QA_ALLOW_PRODUCTION` | all adapters | Must be `1` to allow `QA_ENVIRONMENT=production`, `prod`, or `live`. Use only with explicit human approval. |

Configured commands run through `sh -c` so the template does not need to know whether the project uses Node, Python, Docker, Make, Just, a compiled binary, or another stack. If that command-dispatch model is too loose for a project, replace the adapter body while preserving the inputs, outputs, and safety behavior.

## Evidence expectations

`qa:boot` evidence should include, when applicable:
- target URL, endpoint, socket, fixture, or equivalent runtime target
- PID, container id, service handle, or explanation when the runtime is externally managed
- log file path, log query, or artifact directory

`qa:smoke` evidence should include:
- exact target checked
- concise pass/fail summary
- artifact paths for screenshots, traces, or logs when produced

`qa:logs` evidence should include:
- bounded log excerpt only
- time range, request id, trace id, or other filter used
- note that secrets and production data were excluded

`qa:stop` evidence should include:
- resources stopped
- cleanup warnings or remaining resources
- confirmation that local/dev QA resources are no longer running

## Bootstrap checklist for downstream projects

During initial architect/orchestrator setup for a copied project:
1. Decide whether the project has a runnable local/dev target. If not, document why runtime QA is not applicable yet.
2. Replace the adapter bodies or set the `QA_*_COMMAND` variables in the project's chosen task runner.
3. Record the concrete commands and artifact locations in `docs/workflow/agent-qa.md`.
4. Run the four adapters once in a safe non-production environment (`scripts/qa/*.sh` on POSIX shells, or `python scripts/qa/qa.py boot|smoke|logs|stop` on native Windows).
5. Capture skipped checks with reasons and residual risk in the active ticket validation evidence.

## Relationship to optional observability examples

Optional local/dev observability stack and query-pack examples live in `ephemeral-observability.md`. Those examples may describe project-defined metric and trace query commands, but this adapter slice still provides fail-closed shell adapters only for `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop`.

Downstream projects may add `qa:metrics`, trace-query commands, compose-style startup, dashboard queries, or vendor-specific tooling during bootstrap when those choices fit the project. Keep those commands documented in `agent-qa.md` or a linked project observability doc, and preserve the safety behavior described here.

## Non-goals

This template intentionally does not provide mandatory browser automation, metrics adapters, trace adapters, Docker Compose, package-manager scripts, or framework-specific executable examples. Those can be added as optional project-specific adapters or later Harness improvements.
