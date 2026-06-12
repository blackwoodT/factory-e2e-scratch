# TEMPLATE Finalization

Use this file for both standard tickets and prerequisite child tickets.

If this is a prerequisite child ticket, also record:
- whether the prerequisite capability was verified
- whether the parent ticket was unblocked and returned to implementation
- any carry-forward setup notes the human will need later

## Finalization gate
- Current PR head SHA:
- Review pass 1 accepted current head: yes/no
- Review pass 2 accepted current head: yes/no
- Formal approval or fallback comment present: yes/no
- Unresolved REQUEST_CHANGES reviews: yes/no
- Unresolved P0/P1 automated findings: yes/no
- Required checks passing/complete: yes/no
- Validation contract evidence accepted: yes/no
- Required QA / observability artifact references accepted or explicitly skipped with reason: yes/no/not applicable
- Required taste-invariant evidence accepted or explicitly skipped with reason: yes/no/not applicable
- Notes:

## Final acceptance
- Accepted: yes/no
- Scope stayed within ticket: yes/no
- Reviewer outcome:
- Review pass records:
- Accepted validation evidence / artifact references:
- Accepted skipped-evidence rationale and residual risk:
- Final notes:

## Review feedback promotion check
- Review feedback inspected: yes/no
- Repeated feedback identified: yes/no/not applicable
- Tracker updated: yes/no/not applicable
- Promotion disposition: tracker-only / promote-to-taste-invariant / promote-to-architecture-contract / promote-to-structural-boundary-rule / promote-to-validation-guidance / future-lint-test-adapter-todo / deferred / do-not-promote / not applicable
- Evidence/source references:
- Why this matters beyond one-off preference:
- Scope / non-scope:
- Destination doc, config, TODO, or follow-up:
- Owner and follow-up trigger:
- If not promoted, rationale:

## Backlog write pre-check
- Current working directory:
- Git repo top-level:
- `docs/agent-backlog.md` exists relative to repo root: yes/no
- Backlog file inside writable workspace: yes/no
- Edit method used:
- Diff checked: yes/no
- `git diff --check` clean: yes/no

## Backlog updates made
- Status updated:
- Completion notes added:
- Carry-forward notes added:
- Deferred follow-up added:

## Completion notes
- Item
- Item

## Carry-forward notes
- Item
- Item

## Deferred follow-up
- Item
- Item

## Commit / PR / merge status
- Commit created on ticket branch: yes/no
- Branch pushed: yes/no
- PR opened against `main`: yes/no
- PR merged to `main`: yes/no
- Local checkout returned to `main`: yes/no
- Local `main` synced with remote: yes/no
- Ticket branch cleaned up: yes/no
- Notes:

## State transition checklist
- `state.json` read
- orchestrator-owned fields updated
- `stage` correct
- `next_actor` correct
- `handoff` correct
- history updated if stage changed
- both required review passes were current, blocking comments/checks were clear, PR merged, and local checkout returned to updated `main` before finalization is reported complete

## Recommended next ticket
- Next ticket:
- Why it is the next smallest useful slice:

## Optional Next Agent Prompt (Orchestrator for next ticket)
Use this when starting the next ticket in a fresh orchestrator chat.

### Prompt Packet (required if provided)
```yaml
ticket_id: <next-ticket-id>
stage: planned
next_actor: orchestrator
mode: planning
source_of_truth:
  - .ai/tickets/<next-ticket-id>/state.json
  - .ai/tickets/<next-ticket-id>/orchestrator.md
  - .Context/FactoryE2E-Specification.md
  - .Context/FactoryE2E-Roadmap.md
  - docs/agent-backlog.md
objective: Plan the next smallest useful slice.
scope_in:
  - Planning pass only for the next ticket.
scope_out:
  - No implementation in this pass.
state_updates_required:
  - Create or switch to the next ticket branch before handing off to the implementer later in the planning flow.
  - Ensure next ticket state reflects planned stage, review risk plan, validation contract, required review passes, and implementer handoff.
deliverables:
  - Refreshed .ai/tickets/<next-ticket-id>/orchestrator.md
  - Updated .ai/tickets/<next-ticket-id>/state.json
validation_required:
  - Repo or branch checks, ticket-branch creation or checkout, and backlog write pre-check.
acceptance_criteria_to_check:
  - Next ticket has clear done definition, acceptance criteria, review risk plan, validation contract, and required review passes.
blocker_protocol:
  - If ticket bootstrap or ticket-branch creation fails, document the exact mismatch and required fix.
output_contract:
  - Mode
  - Repo or branch check
  - Ticket state status
  - Slice plan summary
  - Review risk plan and validation contract status
  - Commit, PR, and merge status
  - Recommended next actor
```

```text
You are the orchestrator continuing from the previous finalized ticket.
Read the Prompt Packet above and execute it exactly.
If any required Prompt Packet field is missing, fall back to role rules and explicitly log the gap.
```
