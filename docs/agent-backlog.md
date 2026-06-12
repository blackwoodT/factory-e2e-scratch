# Agent Backlog

Template-only warning: in the harness template repository this file is an empty scaffold. A
downstream project's architect/orchestrator maintains the real backlog here during bootstrap,
Planning Passes, and Finalization Passes. Do not record harness-template work as if it were a
downstream product backlog.

## How this file is used
- The orchestrator performs the backlog write pre-check before editing this file.
- Planning Pass adds or updates the active ticket's entry.
- Finalization Pass records completion notes, carry-forward notes, and deferred follow-ups, then
  marks the entry done.
- Keep one short entry per ticket; durable detail belongs in `docs/exec-plans/`.

## Active

| Ticket | Title | Stage | Next actor | Notes |
|---|---|---|---|---|
| TKT-000 | Hello Factory CLI | planned | orchestrator | Architect bootstrap complete 2026-06-12. Implement src/hello_factory.py, tests/test_hello_factory.py, README note. Standard tier. Branch: tkt-000/hello-factory-cli. |

## Done

| Ticket | Title | Outcome | Follow-ups |
|---|---|---|---|
| _none yet_ | | | |
