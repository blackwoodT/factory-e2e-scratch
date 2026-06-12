# Architecture Contract Template

Status: `template`  
Owner: `architect`  
Last reviewed: `2026-06-03`

Use this template during the initial architect pass to create `docs/design-docs/architecture-contract.md` for the target project.

> **Template-only warning:** this file is not a universal architecture. All example domains, paths, layer names, dependency edges, invariants, and enforcement entries below are illustrative. Replace them during downstream bootstrap, or mark a project-specific unknown as `TBD` with an owner and follow-up.

## Generation checklist

When generating `docs/design-docs/architecture-contract.md`, the architect must:
- map the target project's actual business or technical domains and code roots
- define only the layers, modules, packages, services, or boundaries that apply to that project
- document allowed and forbidden dependency edges in terms the project can review and eventually enforce
- identify cross-cutting concerns and the interfaces that contain them
- record untrusted input boundaries and the validation invariant for each material boundary, including validation/parsing point, failure behavior, evidence expectation, and enforcement status
- list a small enforcement plan with current status, even when enforcement starts as manual review
- when dependency boundaries are ready for mechanical enforcement, generate a project-specific `docs/design-docs/architecture-boundaries.json` from `architecture-boundaries-template.json` and keep it aligned with this contract
- record explicit unknowns instead of leaving template examples in place
- reference the generated contract in the initial architect output and relevant orchestrator handoff

## Verification status

Use this section in the generated downstream contract to keep architecture guidance reviewable.

| Field | Value |
|---|---|
| Contract status | draft / verified / stale |
| Last reviewed | YYYY-MM-DD |
| Reviewed by | architect / orchestrator / human owner |
| Known gaps | Link or summarize unresolved TBDs |
| Enforcement readiness | docs-only / partially enforced / mechanically enforced |
| Structural dependency config | `docs/design-docs/architecture-boundaries.json` / not configured / TBD |
| Boundary validation inventory | complete / partial / not applicable / TBD |

## Project domains

List project-specific domains and the package, folder, service, or module roots that contain them.

| Domain | Code root(s) | Owner | Notes |
|---|---|---|---|
| Example only — replace | `path/to/project/domain/` | TBD | Replace during project setup |

## Layer or boundary model

Define the layer, module, service, package, or boundary model that applies to this project. If the project does not use layers, describe the actual dependency boundary model instead.

Example only — replace with project-specific terms:

`Types -> Config -> Repository -> Service -> Runtime -> Interface`

## Allowed dependency directions

Document allowed and forbidden dependency edges. Keep this project-specific and enforceable.

| From boundary | May depend on | Must not depend on | Reason / enforcement note |
|---|---|---|---|
| Example only — Interface | Runtime, Types | Repository internals, direct external IO | Replace during project setup |
| Example only — Runtime | Service, Config, Types | Interface | Replace during project setup |
| Example only — Service | Repository, Providers, Types | Interface | Replace during project setup |

## Cross-cutting boundaries

Define explicit interfaces for concerns that apply to the target project, such as:
- auth and authorization
- secrets/configuration
- telemetry/logging/tracing
- feature flags
- external connectors
- persistence and queues
- UI or API entry points
- background jobs, scheduled work, or CLI entry points

For each concern, record the project-specific owner, allowed call sites, data-safety constraints, and whether enforcement is manual, linted, tested, or pending.

## Boundary validation invariant

Every untrusted boundary should parse or validate incoming data before it enters core business logic. The project may choose the implementation library or technique, but the invariant should be mechanically checkable where practical. See `docs/workflow/boundary-validation-invariants.md` for bootstrap guidance, reviewer evidence expectations, and optional enforcement patterns.

Do not keep the example rows below in a generated downstream contract. Replace them with project-specific boundaries, or record explicit TBDs with owner and follow-up. Use only boundary categories that exist in the target project.

| Boundary | Trust source / untrusted input | Validation/parsing point | Safe internal representation | Failure behavior | Evidence expectation | Enforcement status | Notes |
|---|---|---|---|---|---|---|---|
| Example only — replace | External request / file / queue / CLI input | TBD project-specific parser/validator/decoder/check | TBD project-owned type/value/command/message | Reject before core business logic or state mutation | Positive and negative fixture/test/check selected by validation matrix | manual / tested / linted / deferred | Replace during project setup |

Common example categories to consider and then remove if non-applicable: HTTP/RPC requests, CLI inputs, queues/events/jobs, webhooks/callbacks, file imports, SDK or external API responses, generated clients, and database or persisted records. The generated contract should identify the actual project boundary, the exact untrusted input, where validation happens, and what reviewers should expect as evidence when a ticket changes that boundary.

## Taste invariants to enforce mechanically

Start with a small project-specific set and promote repeated review feedback into tooling. Generate `docs/design-docs/taste-invariants.md` from `docs/design-docs/taste-invariants-template.md` when the project selects durable taste rules, then summarize or link the architecture-relevant rules here.

Examples only — replace or remove if not applicable:
- structured logging at runtime/service boundaries
- schema/type naming conventions
- maximum file size or module complexity thresholds
- banned side-effect imports in pure layers
- timeout/retry requirements for external IO

Do not treat these examples as universal policy. Each selected invariant should name its scope, reason, enforcement status, verification evidence, remediation path, owner, and update path in the generated taste-invariants document.

## Enforcement plan

List the lint, structural test, CI check, reviewer checklist, or manual gate that will enforce each invariant. This section is the bridge to configurable structural dependency linting; do not invent tooling that the project has not chosen yet. When a project chooses structural dependency linting, create `docs/design-docs/architecture-boundaries.json` from `docs/design-docs/architecture-boundaries-template.json` and record which contract rules are mechanically enforced, manual-review-only, docs-only, or deferred.

| Invariant | Enforcement | Status | Follow-up |
|---|---|---|---|
| Example only — Boundary data validation | Manual review, targeted positive/negative tests, contract fixture replay, project-specific lint, or future validation adapter; see `docs/workflow/boundary-validation-invariants.md` | planned | Replace during project setup |
| Example only — Dependency direction | TBD; optionally `python scripts/architecture/check_dependencies.py --config docs/design-docs/architecture-boundaries.json` after project-specific config exists | planned | Replace during project setup |

## Explicit unknowns / TBDs

Use this section instead of leaving template examples in a generated downstream contract.

| Unknown | Owner | Impact | Follow-up trigger |
|---|---|---|---|
| TBD | TBD | TBD | Resolve during architect/orchestrator bootstrap |
