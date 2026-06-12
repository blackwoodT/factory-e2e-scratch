# Factory E2E System Specification

## 1) Project Overview

- **Project name:** Factory E2E Smoke Test (`hello_factory`)
- **Problem statement:** Verify that the automated factory loop (docs/workflow/automation.md) works end-to-end by building a minimal Python CLI deliverable through the complete ticket lifecycle: planning → implementation → review pass 1 → review pass 2 → human PR approval → finalization merge.
- **Target users:** The factory loop itself; developers verifying the workflow harness.
- **Success criteria:** `src/hello_factory.py` prints exactly `Hello from the Factory E2E project` and exits 0; the pytest test passes; the full standard ticket lifecycle completes without human edits to the code.

## 2) Goals and Non-Goals

### Goals
- Deliver `src/hello_factory.py` as a minimal Python CLI script printing the required string.
- Deliver `tests/test_hello_factory.py` asserting that output using pytest.
- Append a one-line usage note to `README.md`.
- Complete the full ticket lifecycle end-to-end via TKT-000 (standard review tier).

### Non-Goals
- No web app, no database, no complex architecture.
- No external dependencies beyond Python 3.11+ stdlib and pytest.
- No CI pipeline changes.
- No edits to factory/workflow files or `.roles/`.

## 3) Constraints

- **Platform/runtime constraints:** Python 3.11+, standard library only (production code). pytest for tests.
- **Performance constraints:** None; the script runs in milliseconds.
- **Team/process constraints:** Full factory loop must succeed with no human edits to the code. Exactly one ticket (TKT-000).
- **Tooling constraints:** Bash, Edit, Write, Read tools available. pytest must be installable or already present.

## 4) Functional Requirements

- **FR-1:** `src/hello_factory.py` prints exactly `Hello from the Factory E2E project` (followed by a trailing newline) and exits with code 0.
- **FR-2:** `tests/test_hello_factory.py` uses pytest to capture stdout from `src/hello_factory.py` and asserts the exact expected string.
- **FR-3:** `README.md` has a one-line usage note appended: `python src/hello_factory.py`.

## 5) Non-Functional Requirements

### Observability plan

- **Logging framework:** Not applicable. The script's only output is the required string to stdout. No structured logging is needed for a throwaway CLI proof-of-concept.
- **Log levels:** stdout is the single output channel.
- **Correlation identifiers:** Not applicable.
- **Error reporting sink:** Not applicable; the script exits 0 by design and has no error paths.
- **Metrics:** Not applicable.
- **Retention:** Not applicable.

**Gap note:** Non-functional items (logging, error reporting, monitoring) are intentionally not applicable for this minimal throwaway CLI script per the build request. This is the architect's recommendation and the orchestrator should accept it for TKT-000.

### Quality
- **Reliability:** The script is deterministic; it always prints the same string.
- **Performance:** No targets; sub-millisecond execution.
- **Security/privacy:** No PII, no secrets, no network I/O, no external dependencies.
- **Accessibility:** Not applicable (CLI script, no UI).

## 6) System Scope and Boundaries

- **In scope:** `src/hello_factory.py`, `tests/test_hello_factory.py`, `README.md` usage note.
- **Out of scope:** All other project files, CI configuration, workflow infrastructure, factory/workflow policy files.

## 7) Architecture and Design Notes

- **High-level design:** Single Python module in `src/`. No imports beyond stdlib. A `main()` function prints the string and an `if __name__ == "__main__"` guard calls it.
- **Key modules/components:**
  - `src/hello_factory.py` — CLI entry point. No external state, no imports beyond optional stdlib (print is a builtin).
  - `tests/test_hello_factory.py` — pytest test that runs the script via `subprocess` and asserts stdout content.
- **Data model notes:** Not applicable.
- **External dependencies:** None (stdlib only for production code; pytest for tests).

## 8) Milestones / Ticket Phases

- **Phase 1 — TKT-000 (Hello Factory CLI):** Implement `src/hello_factory.py`, `tests/test_hello_factory.py`, and `README.md` usage note. Traverse full standard ticket lifecycle.

## 9) Validation and Testing Strategy

- **Baseline validation command(s):**
  - `python src/hello_factory.py` — manual smoke: prints exact string and exits 0.
  - `pytest tests/test_hello_factory.py -v` — automated: asserts expected output.
- **Ticket-level validation expectations:** pytest suite passes; script exits 0 and prints the exact string.
- **Acceptance test approach:** pytest assertion on captured stdout from the script.

## 10) Risks and Mitigations

- **Risk:** pytest not available in the execution environment.
  - **Mitigation:** The implementer should verify pytest availability and install with `pip install pytest` if needed. Record any install step in `implement.md`.
- **Risk:** The test captures stdout via subprocess and the exact string assertion is fragile to trailing whitespace or platform line endings.
  - **Mitigation:** Use `.strip()` in the assertion, or ensure the script outputs exactly the expected string. Record the assertion approach in `implement.md`.

## 11) Open Questions and Explicit Assumptions

The following are assumptions recorded because this run is unattended and clarifying questions cannot be asked.

1. **Review tier:** The build request says "light tier" but then describes "review pass 1 → review pass 2", which matches the `standard` tier. Per `docs/workflow/review-tiers.md`, source code and tests are explicitly excluded from the `light` tier. **This ticket is planned as `standard` tier** (two required review passes). The word "light" in the build request is interpreted as describing scope/complexity, not the workflow review tier.
2. **pytest availability:** pytest is assumed installable via pip if not already present. The implementer will verify.
3. **`src/` directory:** The build request targets `src/hello_factory.py`, implying a `src/` directory. The implementer creates it if absent.
4. **README.md location:** The one-line usage note appends to the bottom of the existing root `README.md`.
5. **Non-functional requirements:** Logging, observability, error reporting, and monitoring are not applicable for this minimal throwaway script, as documented in Section 5.

## 12) Initial Ticket Bootstrap Notes

- **Suggested first ticket id:** TKT-000
- **First ticket objective:** Implement `src/hello_factory.py`, `tests/test_hello_factory.py`, and `README.md` usage note in a single standard-tier ticket.
- **First ticket acceptance criteria:**
  - `src/hello_factory.py` exists and prints exactly `Hello from the Factory E2E project` when run.
  - `pytest tests/test_hello_factory.py` passes.
  - `README.md` contains a one-line usage note.
  - Script exits 0.
