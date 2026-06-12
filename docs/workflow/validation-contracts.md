# Validation Contract Expectations

Every planning pass defines a ticket-specific validation contract using the risk-based defaults in `validation-evidence-matrix.md` and these categories:
- static validation
- test validation
- build validation
- runtime smoke validation
- domain validation (security/data/infra/a11y/perf/obs/UI as relevant)

## Evidence expectations
Implementer handoff should include:
- exact command list when practical
- pass/fail outcome and notable output summary
- skipped checks with reason and residual risk note

## Validation attempt outcomes
Validation records must distinguish **product behavior** from **tooling or environment availability**. A failed or unavailable agent tool is evidence that the check was attempted; it is not evidence that the changed behavior passed.

Use these outcome labels when recording validation evidence in `implement.md` or optional `state.json.validation.evidence`:
- `passed`: the check ran and demonstrated the expected behavior.
- `failed_product`: the check ran and exposed an application, product, configuration, data, security, accessibility, performance, or reliability failure.
- `failed_tooling`: the check could not validate product behavior because the agent runtime, MCP server, browser, engine, SDK, dependency, credential, display, sandbox, fixture, export template, observability backend, or other tooling/environment capability failed.
- `skipped_with_reason`: the check did not run; record the reason, residual risk, and why remaining evidence is sufficient for this slice.
- `not_applicable`: the check does not apply to the project, runtime, or ticket risk.
- `blocked`: required evidence cannot be obtained yet and the ticket should route through the blocker/prerequisite path.

Required validation remains unsatisfied when the only record is `failed_tooling`, `skipped_with_reason`, or `blocked`, unless an equivalent fallback passes or the validation contract/reviewer explicitly accepts the skip with residual risk. For example, a failed Playwright MCP headed-browser session, missing Godot executable, unavailable database fixture, or unreachable metrics backend should be recorded honestly, but it does not prove the changed behavior works.

When required evidence is blocked by missing project QA capability, first try the configured fallback command or adapter intent from `agent-qa.md`/`qa-command-adapters.md`. If no equivalent fallback exists, create or route to a prerequisite, testing, infrastructure, or other appropriate follow-up ticket when the evidence is material to acceptance. Optional evidence failures may be accepted as non-blocking only when the handoff explains why the remaining evidence is sufficient.

## Boundary validation evidence
For slices that touch untrusted input boundaries, the validation contract should name the boundary, the untrusted input, the expected validation/parsing point from `docs/design-docs/architecture-contract.md`, and the smallest positive/negative evidence required by `validation-evidence-matrix.md`. If no project-specific boundary enforcement is configured, record the check as skipped with reason and residual risk rather than treating missing enforcement as a pass. See `boundary-validation-invariants.md`.

## Taste invariant evidence
For slices that touch selected project taste invariants, the validation contract should name the rule id, scope, enforcement status, and smallest evidence expected from `docs/design-docs/taste-invariants.md`. If the generated taste-invariants document or project-specific enforcement is not configured yet, record the check as skipped with reason and residual risk rather than treating example rules as active policy.

## Artifact matrix (recommended defaults)
- UI-touching slices: screenshot evidence when perceptible visual changes exist.
- Runtime-risky slices: short log excerpt or smoke output.
- Performance-sensitive slices: baseline vs new timing when feasible.

Use smallest sufficient evidence for the slice. The planning pass should mark selected evidence as required, optional, or skipped with reason based on the slice risk class. See `validation-evidence-matrix.md` for the template matrix that downstream projects customize during bootstrap.


## Optional ticket evidence references

Ticket state may include `validation.evidence` as an optional, additive list of reviewable evidence references. Older tickets may omit this field. When present, keep it aligned with `implement.md` and record only the smallest sufficient evidence selected by the validation evidence matrix.

Recommended evidence entries can reference:
- command transcripts or adapter intents such as `qa:boot`, `qa:smoke`, `qa:logs`, and `qa:stop`
- project-defined QA commands documented in `agent-qa.md`
- artifact paths for screenshots, browser journey output, bounded logs, metric summaries, trace summaries, or other project-defined evidence
- skipped evidence with reason, residual risk, and any human follow-up needed

When useful, evidence entries should also state the outcome label, whether the entry satisfies the validation contract, any fallback attempted, and the residual risk. Keep this shape advisory rather than mandatory so older tickets do not need a schema migration.

Do not treat `validation.evidence` as a mandatory schema migration. Use it to make evidence easier to review when a ticket's risk profile warrants artifacts.

Repeated reviewer feedback about missing, unclear, stale, or overly broad validation evidence should be recorded in `docs/exec-plans/review-feedback-tracker.md` during finalization. Promote evidence patterns into project-specific validation-contract guidance or the validation evidence matrix only when they are stable and useful beyond a one-off ticket.

## Agent QA evidence
For runnable applications, prefer validation evidence that an agent can reproduce: app boot output, smoke command output, screenshots or video for visual changes, console/runtime log excerpts, and metrics/trace threshold summaries when available. See `agent-qa.md`.
