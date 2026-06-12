# TKT-000 Orchestrator Pass

## Mode
- Planning Pass

## Ticket
- Ticket ID: TKT-000
- Title: Hello Factory CLI
- Branch: tkt-000/hello-factory-cli
- Ticket type: primary

## Repo / branch check
- Target ticket branch: tkt-000/hello-factory-cli
- Branch exists or will be created: will be created by orchestrator during Planning Pass
- Notes: Architect bootstrap was done on `factory/build-request-4`. Orchestrator must create/checkout `tkt-000/hello-factory-cli` before handing to the implementer.

## Ticket state status
- Current state on entry: planned
- Current next actor on entry: orchestrator
- Current status on entry: active
- Notes: TKT-000 bootstrapped by architect on 2026-06-12.

## Prerequisite assessment / blocker summary
- Hard prerequisites already satisfied: yes (Python 3.11+ and pip are assumed available; pytest install is implementer-handled)
- Human/external action required: none
- Notes: pytest availability is a low-risk dependency the implementer handles in-pass. No infrastructure, credentials, or external services are required.

## What This Ticket Comprises

TKT-000 delivers the smallest possible factory E2E verification artifact:

1. `src/hello_factory.py` — a Python script that prints exactly `Hello from the Factory E2E project` and exits 0. No external imports beyond builtins.
2. `tests/test_hello_factory.py` — a pytest test that runs the script via subprocess and asserts the exact expected output.
3. `README.md` — a one-line usage note appended at the bottom: `python src/hello_factory.py`.

**Deliberately excluded:** no web app, no database, no CI changes, no workflow/factory file edits, no `.roles/` edits, no external dependencies beyond stdlib + pytest.

## Foreseen Risks / Planned Mitigations / Human Intervention Points

1. **pytest not installed** — Mitigation: implementer runs `pytest --version` first; installs via `pip install pytest` if absent; records the install step in `implement.md`.
2. **`src/` directory absent** — Mitigation: implementer creates it before writing the script.
3. **Exact string assertion fragility** — Mitigation: implementer uses `.strip()` on captured output, or ensures the script prints exactly the required string with no trailing whitespace beyond the newline. Reviewer verifies the assertion approach.
4. **Review tier confusion** — The build request says "light tier" but lists two review passes. Per `docs/workflow/review-tiers.md`, source code and tests cannot be `light`. **Planned mitigation: use `standard` tier (review-1 + review-2).** If the human disagrees, they should comment on the PR before merging.
5. **Human intervention point:** Human PR approval is required before finalization merge. No other human intervention is expected.

## Slice plan summary

Single slice: implement all three deliverables (script, test, README note) in one implementation pass. The slice is small enough to fit comfortably in one pass and one review cycle.

## Done definition

- `src/hello_factory.py` exists and prints exactly `Hello from the Factory E2E project` and exits 0
- `pytest tests/test_hello_factory.py` passes with the correct assertion
- `README.md` has a one-line usage note appended
- No external dependencies beyond Python stdlib and pytest

## Acceptance criteria

1. Running `python src/hello_factory.py` prints exactly `Hello from the Factory E2E project` (newline-terminated) and exits 0.
2. Running `pytest tests/test_hello_factory.py` passes with at least one test asserting the exact expected string.
3. `README.md` contains a one-line usage note for the script.
4. `src/hello_factory.py` imports nothing beyond Python builtins (no import statements, or stdlib only if needed for sys.exit).
5. The test uses subprocess to invoke the script (not a direct module import) to test the CLI boundary honestly.

## Review risk plan

- **Files likely to change:** `src/hello_factory.py` (new), `tests/test_hello_factory.py` (new), `README.md` (append)
- **Runtime boundaries:** stdout is the only output channel. The script has no runtime state, no filesystem side effects, no network IO.
- **Import/dependency boundaries:** `src/hello_factory.py` must not import third-party packages. Reviewers confirm no unexpected imports.
- **Untrusted input boundaries:** None — the script takes no external input.
- **Configured structural dependency lint:** none configured (not warranted for a single-file project).
- **Selected taste invariants:** none selected (see `docs/design-docs/taste-invariants.md`).
- **Architecture contract constraints:** see `docs/design-docs/architecture-contract.md` — stdlib-only constraint for `src/`.
- **Module-load side effects:** none expected for a minimal print-and-exit script.
- **Domain concerns:** none (no security, data, infra, a11y, performance, or observability concerns for this scope).
- **Review artifacts expected:** pytest output showing test pass; `python src/hello_factory.py` output.

## Validation contract

- **Static validation:** confirm no third-party imports in `src/hello_factory.py` (manual review).
- **Test validation:** `pytest tests/test_hello_factory.py` — passes.
- **Build validation:** not applicable (no build step).
- **Runtime smoke validation:** `python src/hello_factory.py` — prints `Hello from the Factory E2E project`, exits 0.
- **Domain validation:** not applicable.
- **Evidence required:**
  - Command + output for `pytest tests/test_hello_factory.py` (bounded, shows pass).
  - Command + output for `python src/hello_factory.py` (shows exact printed string and exit code 0).
- **Evidence optional:** none additional.
- **Evidence to skip with reason:** structural dependency lint (not configured; manual review covers the single-file constraint).

## Required review passes

- review-1: Claude Code
- review-2: Codex IDE
- Tier: standard (source code + tests; light tier not eligible per `docs/workflow/review-tiers.md`)

## Files likely in scope

- `src/hello_factory.py` (new)
- `tests/test_hello_factory.py` (new)
- `README.md` (append one line)

## Risks / assumptions

1. Review tier: standard, not light (see Specification §11, Assumption 1).
2. pytest install: low-risk; implementer handles in-pass.
3. `src/` directory: implementer creates if absent.
4. Non-functional requirements: not applicable for this scope (Specification §5).
5. All changes are purely additive; no existing code is modified.

## Backlog write pre-check

- `docs/agent-backlog.md` exists relative to repo root: yes (confirmed during architect bootstrap)
- Backlog file inside writable workspace: yes
- Notes: Architect updates backlog in this pass; orchestrator should also update it during Planning Pass.

## State transition checklist (architect bootstrap)

- [x] `state.json` created
- [x] architect-owned fields populated
- [x] `stage = planned`
- [x] `next_actor = orchestrator`
- [x] `handoff` set (architect → orchestrator)
- [x] history entry added
- [x] ticket branch recorded (`tkt-000/hello-factory-cli`)
- [x] review risk plan recorded (in this file)
- [x] validation contract recorded (in this file)
- [x] required review passes initialized (standard: review-1, review-2)

## Handoff decision

Hand to orchestrator for Planning Pass. Orchestrator should create/checkout `tkt-000/hello-factory-cli` before handing to the implementer.

---

## Next Agent Prompt (Orchestrator)

### Prompt Packet (required)

```yaml
ticket_id: TKT-000
ticket_type: primary
execution_mode: standard
stage: planned
next_actor: orchestrator
waiting_on: orchestrator
mode: planning
source_of_truth:
  - .ai/tickets/TKT-000/state.json
  - .ai/tickets/TKT-000/orchestrator.md
  - .Context/FactoryE2E-Specification.md
  - .Context/FactoryE2E-Roadmap.md
  - docs/design-docs/architecture-contract.md
  - docs/agent-backlog.md
objective: >
  Complete the Planning Pass for TKT-000 (Hello Factory CLI).
  Finalize the done definition, acceptance criteria, review risk plan, and validation contract.
  Create or switch to ticket branch tkt-000/hello-factory-cli.
  Write the implementer handoff prompt packet and hand off to the implementer.
scope_in:
  - Planning Pass only: done definition, acceptance criteria, review risk plan, validation contract, branch creation/checkout, backlog entry, implementer handoff.
scope_out:
  - No implementation in this pass.
  - No changes to workflow policy, factory files, or .roles/.
state_updates_required:
  - Create or checkout branch tkt-000/hello-factory-cli before implementer handoff.
  - Update state.json: stage=planned (or update to reflect planning complete), next_actor=implementer, waiting_on=implementer, handoff orchestrator->implementer, add history entry.
  - Record risk plan in state.json.review.risk_plan.
  - Record validation contract in state.json.validation.contract.
  - Update docs/agent-backlog.md: add TKT-000 to Active section.
deliverables:
  - Refreshed .ai/tickets/TKT-000/orchestrator.md with complete Planning Pass output
  - Updated .ai/tickets/TKT-000/state.json
  - Updated docs/agent-backlog.md (TKT-000 in Active)
validation_required:
  - Backlog write pre-check (confirm docs/agent-backlog.md exists and is writable).
  - Confirm branch tkt-000/hello-factory-cli is checked out before handing to implementer.
acceptance_criteria_to_check:
  - Done definition is clear and verifiable.
  - Acceptance criteria are testable.
  - Review risk plan covers src/hello_factory.py, tests/test_hello_factory.py, and README.md.
  - Validation contract includes pytest run and smoke test commands.
  - required_passes set to standard tier (review-1, review-2).
review_risk_plan:
  - Files: src/hello_factory.py (new), tests/test_hello_factory.py (new), README.md (append).
  - stdlib-only constraint for src/.
  - subprocess-based test boundary.
  - No untrusted input, no external services.
validation_contract:
  - pytest tests/test_hello_factory.py
  - python src/hello_factory.py (smoke)
required_review_passes:
  - review-1: Claude Code
  - review-2: Codex IDE
blocker_protocol:
  - If branch creation fails, record the exact blocker and do not hand to implementer.
  - If backlog write fails, record the exact error.
output_contract:
  - Ticket ID
  - What This Ticket Comprises
  - Slice Plan
  - Done Definition
  - Acceptance Criteria
  - Foreseen Risks / Planned Mitigations / Human Intervention Points
  - Review Risk Plan
  - Validation Contract
  - AI Usage
  - Recommended Next Actor
```

```text
You are the orchestrator for TKT-000 (Hello Factory CLI).
Read the Prompt Packet above and execute the Planning Pass.
Key references:
  - .Context/FactoryE2E-Specification.md (requirements and assumptions)
  - .Context/FactoryE2E-Roadmap.md (phase plan)
  - docs/design-docs/architecture-contract.md (stdlib constraint for src/)
  - docs/workflow/review-tiers.md (standard tier required; source code not light)
If any required Prompt Packet field is missing, fall back to state.json + role rules and log the gap.
```
