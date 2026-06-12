# Boundary Validation Invariants

Purpose: make untrusted-input boundaries reviewable and, when a downstream project is ready, mechanically enforceable without prescribing one language, framework, transport, parser, schema system, or validation library.

This is template guidance, not a universal trust-boundary model. Downstream projects must identify their own boundaries during bootstrap and record project-specific validation/parsing points in `docs/design-docs/architecture-contract.md`.

## Relationship to the architecture contract

`docs/design-docs/architecture-contract.md` is the human-readable source of truth for boundary validation invariants. Generate it from `docs/design-docs/architecture-contract-template.md` during downstream bootstrap, then replace every example boundary, untrusted input, validation point, failure behavior, evidence expectation, and enforcement note with project-specific facts or explicit TBDs.

`docs/design-docs/architecture-boundaries.json` is currently the machine-readable scaffold for structural dependency rules only. Do not treat it as a universal validation-invariant config unless a downstream project intentionally extends its own architecture enforcement model. If boundary-validation enforcement later needs machine-readable policy, prefer a project-specific validation config or adapter that references the generated architecture contract.

## What counts as an untrusted boundary

An untrusted boundary is any place data crosses from a less-trusted source into project-controlled logic or from one trust zone into another. The exact list is project-specific.

Common examples only — remove non-applicable categories during bootstrap:

| Boundary category | Example untrusted input | Validation/parsing invariant | Example evidence |
|---|---|---|---|
| HTTP, RPC, or API request | Request path, query, headers, body, auth claims | Decode, authenticate/authorize when applicable, parse, validate, and normalize before invoking core business logic. | Positive request accepted; malformed, unauthorized, or unsafe request rejected before state mutation. |
| CLI or task runner | Arguments, flags, environment-derived inputs, stdin | Parse and validate before command execution changes state or calls domain logic. | Valid command succeeds; invalid argument or missing required value fails with bounded safe output. |
| Queue, event, or job message | Message body, metadata, retry/dead-letter attributes | Verify message shape and required metadata before processing side effects. | Fixture replay covers accepted message and rejected malformed/stale message. |
| Webhook or callback | Payload, signature headers, timestamp, delivery id | Verify authenticity/freshness when applicable, then parse and validate payload before domain handling. | Invalid signature or malformed payload is rejected without exposing secrets in logs. |
| File import or generated artifact | File contents, filenames, metadata, generated records | Decode using project-approved parser, validate shape/ranges, and reject unsafe paths or malformed content. | Representative fixture accepted; malformed, oversized, or unsafe-path fixture rejected safely. |
| SDK or external API response | Third-party response body, status, headers, pagination, error payload | Treat response as untrusted until decoded and validated against the project-owned internal representation. | Mock/fixture covers expected response and unexpected/missing-field response. |
| Database or persisted record | Legacy rows, migrated records, user-authored persisted data | Validate or hydrate into a safe internal representation at the boundary where data re-enters logic. | Fixture or migration check covers valid, legacy, and invalid persisted shapes where applicable. |

Validation may be implemented with a schema library, parser, decoder, type guard, framework model, manual validation function, generated contract, or another project-approved mechanism. The template does not prescribe which one.

## Bootstrap expectations

During initial downstream bootstrap, the architect/orchestrator should:

1. Generate `docs/design-docs/architecture-contract.md` from `docs/design-docs/architecture-contract-template.md`.
2. Inventory project-specific untrusted boundaries such as entrypoints, external connectors, files, queues, callbacks, generated clients, persistence hydration, or other trust-zone crossings.
3. For each material boundary, record the untrusted input, trust source, validation/parsing point, safe internal representation, failure behavior, enforcement status, reviewer evidence expectation, and owner.
4. Mark non-applicable example categories as removed rather than leaving template rows in the generated contract.
5. Mark unknown boundaries as explicit TBDs with owner, impact, and follow-up trigger.
6. Decide which invariants start as manual review, targeted tests, static lint, contract fixtures, generated-client checks, or intentionally deferred follow-up.
7. Keep `docs/workflow/validation-evidence-matrix.md`, `docs/workflow/validation-contracts.md`, and `docs/workflow/agent-qa.md` aligned with the project-specific command names and evidence locations.

## Orchestrator planning guidance

When a ticket touches an untrusted boundary, the orchestrator should include boundary validation in the review risk plan and validation contract.

Record:

- which boundary is touched,
- which input is untrusted,
- where parsing/validation should happen according to the generated architecture contract,
- whether the change affects positive, negative, authorization/authenticity, malformed-input, compatibility, or persistence cases,
- what evidence is required, optional, or skipped with reason under `validation-evidence-matrix.md`,
- whether any configured project-specific lint/test/check applies,
- residual risk if enforcement is not configured or is unsafe to run.

If a freshly bootstrapped downstream project lacks a generated architecture contract, record that as a bootstrap gap. Do not invent a universal boundary model for the ticket.

## Implementer evidence expectations

For boundary-touching slices, implementer evidence should be agent-legible and minimal. Prefer exact commands, targeted tests, fixtures, or bounded outputs selected by the validation contract.

Evidence should answer:

- What boundary was touched?
- What input is untrusted?
- Where does parsing, validation, authentication, authorization, decoding, normalization, or hydration happen?
- What positive case proves valid input still works?
- What negative case proves malformed, unauthorized, unsafe, stale, or incompatible input is rejected before core business logic or state mutation?
- What command, fixture, artifact, or project-specific check produced the pass/fail result?
- If evidence was skipped, why was it skipped, what residual risk remains, and what follow-up is needed?

Keep secrets, credentials, production data, unbounded logs, and unnecessary artifacts out of PR evidence.

## Reviewer checklist

When reviewing a boundary-touching ticket, check that:

- the generated architecture contract identifies the boundary or the implementer records a contract gap,
- untrusted input does not flow into core business logic without a project-approved parser/validator/decoder/check,
- validation failure behavior is safe, bounded, and does not expose secrets,
- positive and negative evidence matches the validation contract and risk matrix,
- skipped evidence includes a reason and residual risk,
- any project-specific lint/test/check was run or explicitly skipped,
- contract/config updates happen before enforcement changes when the intended boundary policy changes.

Request changes when boundary validation evidence is absent, too generic to review, stale relative to the current PR head, or inconsistent with the generated architecture contract.

## Optional enforcement patterns

Start with manual review and targeted tests. Promote to mechanical checks only when a project-specific rule is stable and useful.

Possible project-specific enforcement mechanisms include:

- targeted unit or integration tests for boundary adapters,
- fixture replay for accepted and rejected inputs,
- contract/schema compatibility checks when the project has chosen a contract format,
- static lint rules for approved boundary adapter usage,
- generated-client/server contract checks,
- smoke commands or QA adapters that exercise representative boundary flows,
- project-specific scripts that fail closed when their config is missing or still marked template-only.

A future validation-invariant adapter should emit agent-legible findings: boundary id, untrusted input, file or command under review, expected validation point, rule id, evidence command or fixture, reason for failure, and remediation path. If the rule is intentionally changed, update the generated architecture contract first, then update the project-specific enforcement config or tests.
