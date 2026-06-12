# Browser Critical Journey Examples

Purpose: provide optional, stack-neutral example shapes for browser-driven critical journeys so agents can collect practical UI evidence when a downstream project has a runnable UI.

This document is **not** universal policy. Non-UI projects, UI projects without configured browser tooling, and tickets with no material UI risk should skip this evidence with a reason and residual risk note in the active validation contract.

## Applicability

Use browser-driven critical journey evidence when all of these are true:
- the downstream project has a runnable browser UI or browser-like surface
- the project has selected safe local/dev browser tooling during bootstrap
- the ticket changes a material user-visible flow, visual state, or interaction
- the journey evidence is the smallest sufficient way to reduce review uncertainty

Treat browser evidence as:
- **Required** when the validation evidence matrix marks UI journey evidence required for the slice and the project has configured a safe runnable UI target.
- **Optional** when screenshots, console output, DOM snapshots, traces, or video would materially clarify a broad or risky UI change.
- **Skip with reason** when no runnable UI exists, browser tooling is not configured, the ticket has no perceptible UI behavior, the target is unsafe to run, or the evidence would be disproportionate for the slice.

If a required browser journey cannot run because the browser, Playwright, Chrome DevTools Protocol, MCP server, IDE integration, display, sandbox, credential, or fixture fails, record the attempt as `failed_tooling` or `blocked` rather than as passing UI evidence. Try a project-defined fallback such as `qa:ui` before accepting a skip. If no fallback can satisfy required evidence, route through the validation blocker or prerequisite/follow-up ticket path.

## Relationship to QA adapters

Browser journeys should compose with project-defined Agent QA commands instead of inventing one-off commands in ticket handoffs:

1. Start the safe local/dev target with the configured `qa:boot` intent when applicable.
2. Run the project-defined UI journey command, commonly documented as `qa:ui` or a journey-specific equivalent in `agent-qa.md`.
3. Capture bounded runtime evidence with `qa:logs` when logs are relevant.
4. Tear down local/dev resources with `qa:stop` when the journey started resources.

The template only provides fail-closed shell adapters for the core `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop` intents. Browser tooling, journey command names, artifact paths, thresholds, and applicability are selected by each downstream project during bootstrap and recorded in `agent-qa.md`.

## Critical journey definition template

Downstream projects can copy this shape into `agent-qa.md` for each applicable journey:

| Field | Project-specific value |
|---|---|
| Journey name | Human-readable flow name, such as login, onboarding, checkout, save flow, or settings update. |
| Applicability | Which ticket/risk classes should run it, and when to skip it with reason. |
| Safe target | Local/dev URL, browser surface, fixture, or mock target; never production by default. |
| Setup command | Project-defined boot/setup command or `qa:boot` intent. |
| Journey command | Project-defined repeatable command, such as a task-runner command mapped to the `qa:ui` intent. |
| Steps covered | Stable user actions and assertions in plain language. |
| Expected outcome | Visible state, persisted state, navigation result, or user-facing confirmation. |
| Required artifacts | Smallest sufficient artifacts for the risk class, such as after screenshot and console-error report. |
| Optional artifacts | Before screenshot, video, DOM snapshot, trace, accessibility notes, or human visual review. |
| Artifact paths | Project-specific directory or naming convention, commonly under the configured QA artifact directory. |
| Console policy | Whether any console error fails the journey, which warnings are allowed, and where output is stored. |
| Data safety | Synthetic users, sanitized fixtures, redaction rules, and secrets that must not appear in artifacts. |
| Teardown command | Project-defined cleanup command or `qa:stop` intent. |

## Evidence bundle template

A practical browser evidence bundle should be small, repeatable, and reviewable. Include only artifacts that match the validation evidence matrix for the slice.

| Evidence | Default label | Notes |
|---|---|---|
| Command transcript | Required when journey evidence is selected | Exact command, target, pass/fail result, and notable output. |
| After screenshot or equivalent visual artifact | Required for perceptible UI changes when a runnable UI exists | Use one representative artifact unless before/after comparison is needed. |
| Console-error capture | Required when the journey is used to validate runtime UI behavior | Include a bounded summary even when no errors were observed. |
| Before screenshot | Optional | Useful for visual diffs, regressions, or broad layout changes. |
| DOM snapshot | Optional | Useful when visual artifacts do not explain state, semantics, or accessibility-relevant structure. |
| Trace or video | Optional | Useful for flaky, timing-sensitive, multi-step, or difficult-to-review flows. |
| Runtime log excerpt | Optional or required by another risk class | Use `qa:logs` when changed behavior should emit bounded logs or when debugging a failure. |
| Skipped evidence note | Required when expected evidence is not produced | Include why it was skipped, residual risk, and whether human review is needed. |

## Optional Playwright-style example shape

This is a non-runnable adaptation sketch. It intentionally avoids package-manager, language, and framework assumptions.

1. Read the target URL and artifact directory from the project QA configuration.
2. Start console capture before navigation.
3. Capture a **before** screenshot if the ticket needs comparison evidence.
4. Execute stable journey steps using project-specific selectors or accessibility roles.
5. Assert the expected user-visible outcome.
6. Capture an **after** screenshot.
7. Write console errors to a bounded artifact, including an explicit `no console errors observed` result when clean.
8. Optionally retain a trace or video when the journey is flaky, timing-sensitive, or hard to review from screenshots alone.
9. Exit non-zero when required assertions fail or disallowed console errors appear.
10. Print artifact paths for the implementer handoff and reviewer prompt.

Adapter points for downstream projects:
- browser/tool selection
- selectors and test identities
- command name mapped to `qa:ui` or a project equivalent
- screenshot, video, trace, and console artifact paths
- console warning allowlist and failure threshold

## Optional Chrome DevTools Protocol-style example shape

This is a non-runnable adaptation sketch for projects that prefer direct browser instrumentation.

1. Connect to a safe local/dev browser target selected during bootstrap.
2. Enable page, runtime, network, and console-related event capture as needed.
3. Navigate to the project-defined target URL.
4. Capture a **before** screenshot or page snapshot when useful.
5. Drive the critical journey through the selected browser control mechanism.
6. Capture runtime console exceptions and console errors into a bounded artifact.
7. Capture an **after** screenshot or DOM snapshot for the expected state.
8. Optionally collect timing, network, or trace data when the validation evidence matrix selects performance, integration, or observability evidence too.
9. Print artifact paths and a pass/fail summary.
10. Disconnect and leave no browser process running unless the project intentionally manages it externally.

Adapter points for downstream projects:
- browser launch/connect command
- local/dev target URL
- event categories to capture
- artifact retention policy
- console error and network failure thresholds

## Optional MCP browser-tooling example shape

This is a non-runnable adaptation sketch for projects that expose browser automation through an MCP browser server or similar agent-accessible tool.

1. Document the MCP server name, safe target environment, and allowed browser actions in `agent-qa.md`.
2. Use the server to navigate to the local/dev target after `qa:boot` or equivalent setup.
3. Capture the initial visible state when before evidence is useful.
4. Execute the named journey steps with stable instructions and project-specific fixtures.
5. Capture the final visible state, console-error summary, and any configured DOM or trace artifact.
6. Save artifacts under the project-defined QA artifact path.
7. Summarize the journey command/tool calls and artifact paths in the implementer handoff.
8. Skip with reason if the MCP server is unavailable, unsafe for the target, or not configured for the project.

Adapter points for downstream projects:
- MCP server name and permissions
- allowed environments and data fixtures
- artifact export location
- whether tool output is sufficient evidence or must be mirrored to files

## Bootstrap checklist for downstream projects

During initial project setup, the architect/orchestrator should:

1. Decide whether browser-driven journeys apply to the project at all.
2. Select the smallest set of critical journeys that materially reduce review risk.
3. Choose browser tooling, command names, artifact paths, thresholds, and skip rules.
4. Record the concrete commands and artifact paths in `agent-qa.md`.
5. Define which artifacts are required, optional, or skip-with-reason for each relevant UI risk class in `validation-evidence-matrix.md`.
6. Confirm artifacts avoid production data, secrets, credentials, and unnecessary retention.
7. Run one safe local/dev dry run after configuration and record any residual gaps.

## Reviewer checklist

When browser journey evidence is included, reviewers should confirm:

- the journey is applicable to the ticket's UI risk
- commands and artifact paths are project-defined rather than invented for the ticket
- before/after evidence is present when comparison is needed
- console-error capture is present, even when the result is clean
- artifacts avoid secrets and production data
- skipped evidence includes reason, residual risk, and any needed human follow-up
- optional trace, video, DOM, or log artifacts are justified by risk rather than collected by default
