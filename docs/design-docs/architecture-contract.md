# Architecture Contract

Status: `draft`
Owner: `architect`
Last reviewed: `2026-06-12`

Generated from `docs/design-docs/architecture-contract-template.md` during architect bootstrap for the Factory E2E project.

## Verification status

| Field | Value |
|---|---|
| Contract status | draft |
| Last reviewed | 2026-06-12 |
| Reviewed by | architect |
| Known gaps | None material for this scope; see Explicit unknowns section |
| Enforcement readiness | docs-only (no mechanical enforcement needed for a single-file script) |
| Structural dependency config | not configured — project is too small to warrant architecture-boundaries.json |
| Boundary validation inventory | not applicable — no untrusted input boundaries |

## Project domains

| Domain | Code root(s) | Owner | Notes |
|---|---|---|---|
| Application | `src/` | implementer | Single Python script `src/hello_factory.py` |
| Tests | `tests/` | implementer | pytest suite `tests/test_hello_factory.py` |

## Layer or boundary model

This project has two code locations only:

`src/` → Python stdlib → stdout

`tests/` → `src/` (via subprocess) → assert stdout

No layering is needed beyond this.

## Allowed dependency directions

| From boundary | May depend on | Must not depend on | Reason / enforcement note |
|---|---|---|---|
| `src/hello_factory.py` | Python stdlib (builtins only: `print`) | Third-party packages, network IO, filesystem IO, anything external | Build request constraint: standard library only |
| `tests/test_hello_factory.py` | pytest, subprocess (stdlib), `src/hello_factory.py` (via subprocess) | Third-party packages (beyond pytest) | Keep test dependencies minimal |

## Cross-cutting boundaries

| Concern | Owner | Allowed call sites | Data-safety constraint | Enforcement |
|---|---|---|---|---|
| stdout output | `src/hello_factory.py` main() | Single call site in main() | No PII, no secrets | Manual review |

## Boundary validation invariant

Not applicable. The script accepts no external inputs (no CLI args, no file reads, no network). There are no untrusted input boundaries to validate.

| Boundary | Trust source | Validation point | Safe representation | Failure behavior | Evidence | Enforcement | Notes |
|---|---|---|---|---|---|---|---|
| None | n/a | n/a | n/a | n/a | n/a | n/a | Script takes no external input |

## Taste invariants to enforce mechanically

None selected for this project. The script is too minimal for durable taste rules. See `docs/design-docs/taste-invariants.md`.

## Enforcement plan

| Invariant | Enforcement | Status | Follow-up |
|---|---|---|---|
| `src/` uses stdlib only | Manual review at PR time; reviewer confirms no import statements beyond stdlib | planned | Verify during review-1 |
| Script prints exact required string | pytest assertion in `tests/test_hello_factory.py` | planned | Part of the validation contract |
| Test uses subprocess, not inline import | Manual review: test runs script as a subprocess to test the CLI boundary honestly | planned | Verify during review-1 |

## Explicit unknowns / TBDs

| Unknown | Owner | Impact | Follow-up trigger |
|---|---|---|---|
| pytest installation path in CI | implementer | Low — install via pip if not present | Implementer records install step in implement.md |
| Whether `src/` directory exists in repo | implementer | Low — create it if absent | Implementer handles during implementation |
