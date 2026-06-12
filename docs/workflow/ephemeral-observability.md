# Ephemeral Observability Examples

Purpose: provide optional, stack-neutral example shapes for making local/dev logs, metrics, and traces queryable by agents without requiring any specific observability stack.

This document is **not** universal policy. It does not require Docker, Docker Compose, Kubernetes, OpenTelemetry, Prometheus, Grafana, Jaeger, Tempo, Loki, VictoriaMetrics, cloud telemetry, SaaS observability, a browser UI, or any vendor-specific tool. Downstream projects choose what applies during bootstrap and record concrete commands, thresholds, artifact paths, retention, redaction rules, safe environments, and skip rules in `agent-qa.md` or a linked project observability doc.

## Applicability

Use ephemeral observability evidence when all of these are true:
- the downstream project has configured a safe local/dev target or equivalent isolated test environment
- logs, metrics, traces, or operational signals materially reduce review uncertainty for the ticket slice
- the validation evidence matrix selects observability/reliability evidence for the slice
- the project has documented bounded query commands, thresholds, artifact paths, and teardown behavior

Treat observability evidence as:
- **Required** when the slice changes logging, error reporting, metrics, traces, alerts, operational dashboards, reliability behavior, or failure handling and the project has configured safe local/dev observability for that signal type.
- **Optional** when a bounded log excerpt, metric threshold, trace/span threshold, request correlation example, or operational artifact would materially clarify a risky or broad change.
- **Skip with reason** when the signal type is not configured, not applicable, unsafe to query, blocked by environment, disproportionate for the slice, or intentionally deferred. Record residual risk and what reviewers cannot observe.

Do not point agent QA at production systems unless explicitly approved by the human operator for that ticket.

## Relationship to QA adapters

Ephemeral observability should compose with project-defined Agent QA commands instead of inventing one-off commands in ticket handoffs:

1. Start the safe local/dev target with the configured `qa:boot` intent when applicable.
2. Run the project-defined smoke check with `qa:smoke` when runtime health is relevant.
3. Capture bounded runtime logs with `qa:logs` when log evidence applies.
4. Run project-defined metric or trace query commands when the project has configured them in `agent-qa.md` or a linked observability doc.
5. Write small evidence artifacts under the project-defined QA artifact directory.
6. Tear down app and observability resources with `qa:stop` or the project-defined cleanup command.

The template provides fail-closed shell adapters only for the core `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop` intents. Metric and trace commands are project-defined until a downstream project chooses to add adapters for them.

## Bootstrap observability profile

Downstream projects can copy this shape into `agent-qa.md` or a project observability doc during initial bootstrap.

| Field | Project-specific value |
|---|---|
| Applicability | Which risk classes, ticket types, or subsystems should produce observability evidence. |
| Safe environments | Local/dev targets allowed for agent queries; production is disabled unless explicitly approved. |
| Startup command | Project-defined command or `qa:boot` intent that starts the app and any local observability resources. |
| Shutdown command | Project-defined cleanup command or `qa:stop` intent that stops local observability resources. |
| Log query commands | Stable command names for bounded log excerpts, including filters such as time range, request id, trace id, component, or severity. |
| Metric query commands | Stable command names for budget checks, thresholds, units, windows, and pass/fail output. |
| Trace query commands | Stable command names for span count, error-span, latency, missing-span, or correlation checks. |
| Artifact paths | Directory and naming convention for query transcripts, excerpts, threshold summaries, and retained traces. |
| Retention | How long local artifacts are kept and when agents should delete or rotate them. |
| Redaction | Secrets, credentials, tokens, request bodies, production data, PII, hostnames, and other sensitive fields that must be excluded or masked. |
| Data fixtures | Synthetic or sanitized data used for observability evidence. |
| Skip rules | When logs, metrics, traces, or startup/shutdown evidence should be skipped with reason and residual risk. |
| Reviewer notes | What reviewers should inspect and which missing signal types matter for this project. |

## Query pack template

A query pack is a small, project-owned list of named checks that agents can run for observability evidence. The template does not prescribe a file format. Projects may use Markdown, JSON, YAML, task-runner commands, shell scripts, CI jobs, dashboard links for safe local/dev targets, or another format that is easy for agents and reviewers to read.

| Field | Meaning |
|---|---|
| Query name | Stable name used in validation contracts and reviewer handoffs. |
| Signal type | `log`, `metric`, `trace`, or project-defined operational signal. |
| Intent | What risk or behavior this query validates. |
| Applicability | Which tickets, risk classes, services, components, or flows should run it. |
| Safe target | Local/dev target, fixture, namespace, sandbox, file, or collector endpoint. |
| Command | Project-defined command or documented adapter intent; avoid one-off ticket-only commands. |
| Filters | Required time range, request id, trace id, component, severity, route, job id, or fixture identifier. |
| Threshold | Pass/fail rule, budget, unit, and allowed variance when applicable. |
| Expected artifact | Bounded transcript, excerpt, summary, trace reference, or artifact path. |
| Redaction rule | Sensitive fields that must be removed before artifacts are attached to a PR. |
| Retention rule | How long the artifact may remain in the workspace or PR evidence. |
| Skip rule | Acceptable skip conditions, residual risk statement, and human follow-up if needed. |

### Optional log query example shape

This is a non-runnable adaptation sketch. It intentionally avoids log backend, query language, and runtime assumptions.

1. Start from the project-defined safe local/dev target and artifact directory.
2. Select the smallest relevant time range for the ticket evidence.
3. Filter by request id, trace id, component, severity, fixture id, or another project-defined correlation key.
4. Return only a bounded excerpt or a path to a bounded artifact.
5. Include an explicit result when no matching errors or warnings were observed.
6. Exclude secrets, credentials, production data, unbounded logs, and unnecessary request bodies.
7. Print the query name, filters, artifact path, and pass/fail or informational result.

Adapter points for downstream projects:
- log source and query language
- command name mapped to `qa:logs` or a project equivalent
- maximum line count or byte count
- correlation identifiers and time-window defaults
- redaction and retention policy

### Optional metric threshold example shape

This is a non-runnable adaptation sketch for projects that expose local/dev metrics or derived runtime measurements.

1. Select a project-defined metric or derived measurement that maps to the ticket risk.
2. Query only a safe local/dev target and a bounded time window.
3. Compare the result with the project-defined threshold, budget, unit, and allowed variance.
4. Print a concise pass/fail summary with the observed value and threshold.
5. Save a small artifact containing the command transcript and threshold result.
6. Skip with reason when metrics are not configured, not affected, unsafe, or disproportionate for the slice.

Adapter points for downstream projects:
- metric source and query command
- threshold names, units, windows, and acceptable variance
- artifact path and retention policy
- failure behavior for missing, stale, or partial metrics

### Optional trace/span threshold example shape

This is a non-runnable adaptation sketch for projects that expose local/dev traces or span-like correlation data.

1. Trigger or identify a safe local/dev request, job, command, or workflow run.
2. Capture the project-defined correlation key, such as request id, job id, trace id, or fixture id.
3. Query for the relevant span, event, or correlation record within a bounded time window.
4. Check project-defined thresholds such as missing required span, error-span count, latency budget, retry count, or unexpected dependency edge.
5. Print a concise pass/fail summary and write a bounded artifact or trace reference.
6. Skip with reason when tracing is not configured, not applicable, unsafe, or disproportionate for the slice.

Adapter points for downstream projects:
- tracing source and query command
- correlation id capture method
- required spans/events for critical flows
- span/error/latency thresholds
- artifact path, redaction, and retention policy

## Optional stack patterns

Projects may choose any stack pattern that fits their environment. These patterns are examples, not policy.

| Pattern | When it fits | What to document |
|---|---|---|
| Local-process pattern | The app or test harness writes logs/metrics/traces to local files or stdout. | Startup command, file paths, query commands, bounds, cleanup, and redaction. |
| Compose-style pattern | The project has already selected a local container composition tool. | Services started, safe ports, volumes/artifact paths, startup readiness, shutdown, cleanup, and retained artifacts. |
| Existing-dev-service pattern | The team already runs a safe shared dev observability service. | Allowed target, credentials boundary, query commands, production guardrails, retention, and approval rules. |
| CI-ephemeral pattern | Observability resources are created only inside CI or a disposable preview job. | Job command, artifact export path, cleanup guarantee, and how agents retrieve evidence. |
| No-observability-yet pattern | Logs, metrics, or traces are not configured or not useful for this project yet. | Skip-with-reason wording, residual risk, and the future trigger for adding observability evidence. |

For compose-style or other infrastructure-backed patterns, keep reference material optional. Do not require downstream projects to adopt containers, cloud services, metrics, traces, or any vendor-specific collector.

## Evidence bundle template

A practical observability evidence bundle should be small, repeatable, and reviewable. Include only artifacts selected by the validation evidence matrix for the slice.

| Evidence | Default label | Notes |
|---|---|---|
| Command transcript | Required when observability evidence is selected | Exact command, safe target, time window, filters, pass/fail result, and notable output. |
| Startup evidence | Required when the observability stack is started for the slice | URL, endpoint, PID/container id/service handle, readiness result, or explanation when externally managed. |
| Bounded log excerpt | Required when log evidence is selected | Include filters and explicit redaction note; avoid unbounded logs. |
| Metric threshold summary | Required when metric evidence is selected | Include observed value, threshold, unit, window, and pass/fail result. |
| Trace/span threshold summary | Required when trace evidence is selected | Include correlation id, required span/event checks, observed values, and pass/fail result. |
| Artifact paths | Required when files are produced | Use project-defined QA artifact paths and retention rules. |
| Shutdown evidence | Required when resources are started for the slice | Confirm cleanup or list remaining resources and reason. |
| Skipped evidence note | Required when expected evidence is not produced | Include why it was skipped, residual risk, and whether human review or future setup is needed. |

## Safety boundaries

- Do not point agent QA at production systems unless explicitly approved for the ticket.
- Use synthetic or sanitized data by default.
- Keep secrets, credentials, tokens, production data, PII, and unnecessary request bodies out of logs, traces, screenshots, transcripts, and PR artifacts.
- Bound every query by time range, correlation key, component, severity, line count, byte count, or another project-defined limit.
- Prefer disposable local/dev resources that can be stopped after the ticket.
- Retain only the smallest useful evidence bundle for review.
- Document cleanup warnings and residual resources when teardown is partial.

## Bootstrap checklist for downstream projects

During initial project setup, the architect/orchestrator should:

1. Decide whether local/dev observability applies to the project at all.
2. Choose the stack pattern, signal types, safe environments, command names, thresholds, artifact paths, redaction rules, and retention policy.
3. Record concrete observability commands in `agent-qa.md` or a linked project observability doc.
4. Define which log, metric, and trace evidence is required, optional, or skip-with-reason in `validation-evidence-matrix.md`.
5. Confirm startup and shutdown commands avoid production targets and clean up local/dev resources.
6. Run one safe dry run when observability is configured and record any residual gaps.
7. Mark unavailable signal types as not configured, with residual risk and the trigger for revisiting them.

## Reviewer checklist

When observability evidence is included, reviewers should confirm:

- the evidence matches the ticket's observability/reliability risk
- commands and query names are project-defined rather than invented for one ticket
- logs, metrics, and traces are bounded to the smallest useful scope
- thresholds and budgets are documented and meaningful for the project
- artifacts avoid secrets, credentials, production data, and unnecessary retention
- startup/shutdown evidence is present when local observability resources were started
- skipped evidence includes reason, residual risk, and any needed human follow-up
- optional signal types are justified by risk rather than collected by default
