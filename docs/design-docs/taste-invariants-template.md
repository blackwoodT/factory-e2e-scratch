# Taste Invariants Template

Status: `template`  
Owner: `architect`  
Last reviewed: `2026-06-03`

Use this template during downstream bootstrap to create `docs/design-docs/taste-invariants.md` for the target project.

> **Template-only warning:** this file is not a universal style guide. All example rules, scopes, thresholds, commands, adapters, owners, naming schemes, logging expectations, retry policies, side-effect rules, generated-code boundaries, and enforcement entries below are illustrative. Replace them during downstream bootstrap, remove non-applicable examples, or mark a project-specific unknown as `TBD` with an owner and follow-up trigger.

## Purpose

Taste invariants capture repeated human review preferences that materially improve reliability, maintainability, operability, security, accessibility, product quality, or agent legibility. They help agents stop relearning the same preferences ticket by ticket.

Keep the rule pack small. Do not promote one-off subjective style comments unless they prevent meaningful churn or defects.

## Relationship to the architecture contract

`docs/design-docs/architecture-contract.md` remains the downstream project's human-readable architecture source of truth. Use the generated `docs/design-docs/taste-invariants.md` as the focused rule pack for selected project preferences.

During bootstrap:

1. Generate `docs/design-docs/architecture-contract.md` from `docs/design-docs/architecture-contract-template.md`.
2. Generate `docs/design-docs/taste-invariants.md` from this template.
3. Replace every example invariant with project-specific policy or remove it.
4. Link or summarize selected architecture-relevant taste invariants from the generated architecture contract.
5. Project individual rules into lint, tests, structural dependency checks, QA commands, or reviewer checklists only when the project has chosen those tools.

`docs/design-docs/architecture-boundaries.json` is for structural dependency-boundary rules. Use it for a taste invariant only when that invariant is intentionally expressed as a project-specific dependency/import-boundary rule. Do not turn it into a universal taste-rule config.

## Rule promotion checklist

Promote feedback into a taste invariant only when the proposed rule:

- has appeared repeatedly in human or reviewer feedback, or prevents a serious reliability, maintainability, operability, security, accessibility, or product-quality issue
- can be stated as a small, reviewable rule
- has a clear scope and explicit non-scope
- explains why it matters beyond personal preference
- identifies whether enforcement is docs-only, manual-review-only, linted, tested, script-adapter-backed, or deferred
- names the smallest useful evidence an implementer should provide when a ticket touches the rule
- has a remediation path agents can follow
- has an update or retirement path when project constraints change
- avoids assuming a language, framework, package manager, linter, formatter, logging library, import syntax, module system, transport, database, queue, cloud, or app topology unless the downstream project has selected it
- removes or narrows any example that does not fit the downstream project

Do not promote a rule when it only encodes subjective style with no reliability, maintainability, operability, or product-quality value.

Use `docs/exec-plans/review-feedback-tracker.md` as the intake record for repeated review feedback before promoting a candidate into this generated downstream rule pack. Tracker entries are candidates, not active taste policy.

## Invariant record format

Use one row per selected project rule. Remove example rows during downstream bootstrap.

| Rule id | Invariant | Why it matters | Scope | Applies when | Does not apply when | Enforcement status | Verification / evidence | Remediation | Owner | Last reviewed |
|---|---|---|---|---|---|---|---|---|---|---|
| Example only — replace | Runtime boundary logs include project-approved context fields. | Makes failures diagnosable by agents and humans. | Replace with project-specific runtime/service/command boundary. | A ticket adds or changes externally visible runtime behavior. | Docs-only changes or code paths without runtime behavior. | manual-review-only / linted / tested / deferred | Replace with project command, checklist, or artifact such as bounded log excerpt. | Add the approved fields, or update this rule if the policy changed. | TBD | YYYY-MM-DD |

## Enforcement status labels

Use one of these labels for each selected invariant:

- `docs-only`: the rule is documented for awareness; no per-ticket evidence is normally required.
- `manual-review-only`: reviewers check the rule when it is in scope.
- `linted`: a project-specific lint/static command enforces the rule.
- `tested`: targeted tests or fixtures verify the rule.
- `script-adapter-backed`: a project-specific command or adapter emits pass/fail evidence.
- `structural-boundary-backed`: the rule is projected into `docs/design-docs/architecture-boundaries.json` because it is a dependency-boundary rule.
- `deferred`: the rule is desired but not yet enforceable; record owner, follow-up trigger, and residual risk when relevant.

Mechanical enforcement must be project-specific and fail closed with clear messages when required configuration is missing or still template-only.

## Evidence expectations

When a ticket touches a selected taste invariant, the orchestrator should include the smallest relevant evidence in the validation contract. Evidence should be agent-legible and bounded:

- selected rule id and invariant name
- why the rule applies to this slice
- enforcement status
- exact command, checklist, artifact, or reviewer action used
- pass/fail or skipped status
- bounded output or artifact path when produced
- skipped-check reason, residual risk, and follow-up when enforcement is unavailable, unsafe, or intentionally deferred
- remediation or rule-update path if the invariant changed

Do not require every ticket to produce every artifact type. Do not include secrets, credentials, production data, unbounded logs, unnecessary screenshots/videos/traces, or artifacts unrelated to the selected invariant.

## Examples only — starter invariant ideas

The examples below are prompts for downstream selection, not universal policy. Remove non-applicable examples during bootstrap.

| Candidate invariant | Possible value | Possible enforcement | Bootstrap note |
|---|---|---|---|
| Structured logging | Runtime or service boundaries include project-approved context fields and avoid secrets. | Manual review, targeted log smoke output, project-specific lint/test, or `qa:logs` when configured. | Select only after the project defines logging fields, safe environments, redaction, and evidence expectations. |
| Naming conventions | Project-specific schemas, modules, commands, tests, or generated artifacts use agreed names. | Docs-only, manual review, formatter/linter rule, generator test, or repository-specific checker. | Do not invent a naming scheme in this template. |
| File size or module complexity | Large files/modules require split rationale or follow-up. | Manual review, project-specific static analysis, or language-specific lint when chosen. | Replace example thresholds with project-specific values, or leave as deferred/TBD. |
| Side-effect imports | Pure or core modules avoid import-time side effects. | Manual review, structural dependency lint, targeted module-load tests, or project-specific static check. | Applies only if the project defines pure/core/runtime boundaries. |
| Retries and timeouts | External IO has project-approved timeout, retry, and failure behavior. | Targeted tests, integration fixtures, manual review, or adapter checks. | Define transports/connectors and failure policy in project terms. |
| Generated-code boundaries | Generated files are not hand-edited, or custom edits live in approved extension points. | Generator check, diff check, manual review, or project-specific script. | Define generated paths, owners, regeneration command, and exceptions downstream. |

## Promotion to mechanical enforcement

Promote a docs/manual invariant to mechanical enforcement only when:

1. the project-specific rule is stable,
2. violations are common or costly enough to justify tooling,
3. the check can be scoped narrowly,
4. false positives have a clear escape/update path,
5. output explains the rule id, file or artifact, failure reason, and remediation,
6. the command is safe for local/dev or CI use,
7. missing config fails closed instead of silently passing.

Possible project-specific enforcement surfaces include existing linters, tests, formatter checks, repository scripts, QA adapters, generated-code checks, structural dependency lint, or future optional taste-rule adapters. Keep language/framework-specific adapters clearly marked as examples.

## Updating or retiring a rule

If an invariant is no longer useful:

1. update this generated project rule pack first,
2. update any architecture-contract summary or enforcement projection,
3. update lint/test/script configuration if applicable,
4. record why the change is safe,
5. remove stale reviewer expectations from active tickets.

Reviewers should not block on old taste preferences that are no longer selected project policy unless the issue is independently a correctness, safety, or reliability bug.

## Explicit unknowns / TBDs

Use this section instead of leaving template examples in a generated downstream rule pack.

| Unknown | Owner | Impact | Follow-up trigger |
|---|---|---|---|
| TBD | TBD | TBD | Resolve during architect/orchestrator bootstrap |
