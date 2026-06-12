# TEMPLATE Review

Use this file when a ticket is routed to reviewer. Every ticket and sub-ticket lands here after the implementer marks it `implemented`, and every reviewer-routed ticket has an open PR. Review pass 1 and review pass 2 both write to this file while preserving prior findings.

This is a code review first: read the PR diff in every case; the checklists below direct attention but do not substitute for it. For prerequisite tickets the diff will normally include at least the implementer's verification record (`implement.md` and `state.json` under `.ai/tickets/<ticket-id>/`); confirm the recorded command(s), observed output, and any human-reported evidence actually demonstrate the unblock condition. If the prerequisite produced repo artifacts (setup scripts, docs), review those in the same PR. Do not re-verify state mechanics CI already gates (`check-ticket-state`); confirm checks are green and spend the pass on the diff.

## Review verdict
- APPROVE PASS
- APPROVE WITH FOLLOW-UP
- CHANGES REQUESTED

## Review pass
- Pass ID: review-1 or review-2
- Tool: Claude Code or Codex IDE
- Current PR head SHA:
- Prior required pass status:

## PR reviewed
- PR number:
- PR URL:
- GitHub review action taken: APPROVE / REQUEST_CHANGES / pass acceptance comment

## Code inspection
List every file changed in the PR diff (proof the diff was read; a review without this list is incomplete):
- `path/to/file` — inspected: <one-line concern or "no concerns">
- `path/to/generated-file` — skipped: <reason, e.g. lockfile>

Findings below must cite the file, and the line or hunk when applicable.

## Acceptance criteria check
1. Criterion:
   - Status:
   - Notes:

2. Criterion:
   - Status:
   - Notes:

## Review risk plan check
- Runtime/import boundaries checked:
- Structural dependency lint evidence checked when applicable:
- Boundary-validation invariant evidence checked when applicable:
- Selected taste-invariant evidence checked when applicable:
- Module-load side effects checked:
- Domain concerns checked:
- Missing artifacts checked:
- QA / observability evidence references checked:
- Skipped evidence rationale and residual risk checked:
- Artifact safety checked (no secrets, production data, unbounded logs, or unnecessary retention):

## Validation contract check
- Required validation reviewed:
- Evidence sufficient: yes/no
- Required / optional / skipped evidence matched the validation evidence matrix: yes/no
- QA artifact paths or references are reviewable when produced: yes/no/not applicable
- Missing or stale validation:
- Structural dependency lint missing/skipped rationale acceptable: yes/no/not applicable
- Boundary-validation evidence or skipped-check rationale acceptable: yes/no/not applicable
- Taste-invariant evidence or skipped-check rationale acceptable: yes/no/not applicable

## Findings
- Blocking issue or `None`

## Non-blocking observations
- Item
- Item

## Notes to preserve for orchestrator
- Preserved implementer notes
- Reviewer follow-up notes worth carrying forward

## State transition checklist
- `state.json` read
- current PR head SHA checked
- reviewer-owned fields updated
- current review pass record updated
- stale prior approvals were not treated as current
- `stage` correct
- `next_actor` correct
- `handoff` correct
- history updated if stage changed

## Handoff decision
- To implementer only if code, evidence, or validation changes are required
- For specialist sub-tickets, keep `next_actor=implementer` but hand to the concrete specialist skill from `state.json.specialist` and include `next_skill` below
- To reviewer pass 2 if review pass 1 accepted and review pass 2 remains pending
- To orchestrator if all required review passes accepted the current PR head and only finalization remains
- Prerequisite tickets follow the same handoff rules as any other sub-ticket

## Next Agent Prompt (Implementer or Specialist -- when CHANGES REQUESTED)
Use this section when verdict is `CHANGES REQUESTED`.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: primary
execution_mode: standard
stage: changes_requested
next_actor: implementer
next_skill: $implementer
waiting_on: implementer
mode: implementing
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
  - .ai/tickets/TEMPLATE/implement.md
  - .ai/tickets/TEMPLATE/review.md
objective: Apply reviewer-requested fixes for this ticket slice, then restart required review passes on the new PR head.
scope_in:
  - Address only reviewer findings and required validation updates.
scope_out:
  - No unrelated refactors or new scope expansion.
state_updates_required:
  - On restart: stage=implementing, next_actor=implementer, waiting_on=implementer, add history.
  - On completion: stage=implemented, next_actor=reviewer, waiting_on=reviewer, review.current_pass=review-1, reset required review passes for the new PR head, update handoff implementer->reviewer pass 1, add history.
deliverables:
  - Updated code or files needed for findings
  - Updated .ai/tickets/TEMPLATE/implement.md
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Run or extend validation to cover the requested fixes and validation contract, including required evidence references or skipped-evidence rationale.
acceptance_criteria_to_check:
  - Re-check failed criteria and any impacted criteria.
review_risk_plan:
  - Preserve the orchestrator risk plan and add any new implementation risk surfaces.
validation_contract:
  - Preserve the validation contract and record new evidence in implement.md and optional state.json.validation.evidence when useful.
required_review_passes:
  - review-1: Claude Code
  - review-2: Codex IDE
specialist:
  type: null
  skill: null
  agent: null
  reason: null
blocker_protocol:
  - If blocked, log the blocker, missing dependency, and missing evidence in implement.md.
output_contract:
  - Summary of changes or prerequisite progress
  - Key files changed
  - Validation performed against contract
  - QA / observability evidence references, including skipped evidence with reason and residual risk
  - Human action / blocker status
  - Review risk handoff
  - Remaining work or follow-up
  - Notes to preserve for orchestrator
  - Handoff recommendation
```

```text
You are the implementer or resolved specialist for ticket TEMPLATE.
Read the Prompt Packet above and execute it exactly.
If `ticket_type: specialist`, use `next_skill`, then `specialist.skill`, otherwise map `specialist.type` through workflow-reference.md before acting.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```

## Next Agent Prompt (Reviewer Pass 2 -- when PASS 1 ACCEPTED)
Use this section when reviewer pass 1 accepted the current PR head and review pass 2 remains pending.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: primary
execution_mode: standard
stage: reviewing
next_actor: reviewer
waiting_on: reviewer
mode: review
review_current_pass: review-2
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
  - .ai/tickets/TEMPLATE/implement.md
  - .ai/tickets/TEMPLATE/review.md
objective: Complete reviewer pass 2 independently against the current PR head.
scope_in:
  - Review the PR diff, risk plan, validation evidence, prior review findings, and GitHub comments/checks.
scope_out:
  - Do not skip review because pass 1 accepted.
state_updates_required:
  - If changes needed: stage=changes_requested, next_actor=implementer, waiting_on=implementer, review.outcome=changes_requested, add history.
  - If accepted and both passes are current: stage=review_accepted, next_actor=orchestrator, waiting_on=orchestrator, review.outcome=accepted or accepted_with_follow_up, pull_request.status=approved, add history.
deliverables:
  - Updated .ai/tickets/TEMPLATE/review.md
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Confirm implementation validation is sufficient against the validation contract.
acceptance_criteria_to_check:
  - Evaluate each planned acceptance criterion with pass/fail notes.
review_risk_plan:
  - Use orchestrator.md, implement.md, and pass 1 notes.
validation_contract:
  - Use state.json.validation.contract and implement.md validation evidence.
required_review_passes:
  - review-1 must be accepted for the current PR head
  - review-2 is the current pass
blocker_protocol:
  - If review cannot be completed, record the exact blocker and missing evidence, including any required QA artifact or skipped-evidence rationale.
output_contract:
  - Review verdict
  - Review pass (id, tool, current PR head SHA)
  - PR reviewed (number, URL)
  - GitHub review action taken
  - Code inspection (files inspected with per-file notes)
  - Acceptance criteria check
  - Review risk plan check
  - Validation contract check
  - QA / observability evidence sufficiency and safety check
  - Findings
  - Non-blocking observations
  - Notes to preserve for orchestrator
  - Handoff decision
```

```text
You are reviewer pass 2 for ticket TEMPLATE.
Read the Prompt Packet above and execute it exactly.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```

## Next Agent Prompt (Orchestrator -- when BOTH REVIEW PASSES ACCEPTED)
Use this section when both required review passes accepted the current PR head.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: primary
execution_mode: standard
stage: review_accepted
next_actor: orchestrator
waiting_on: orchestrator
mode: finalization
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
  - .ai/tickets/TEMPLATE/implement.md
  - .ai/tickets/TEMPLATE/review.md
objective: Finalize an accepted ticket only after confirming both review passes, PR comments/reviews/checks, validation evidence, merge, and local main sync.
scope_in:
  - Final acceptance, finalization gate, backlog sync, finalize.md, and ticket state closeout
  - Commit creation on the ticket branch if closeout files changed
  - PR merge to `main`
  - Local checkout return to updated `main`
scope_out:
  - No new implementation unless reopening is explicitly required.
state_updates_required:
  - On finalization: stage=finalized, status=closed, set waiting_on=none or next ticket owner, set handoff orchestrator->none or next ticket, add history.
  - Do not treat finalization as complete until both review passes are current, blocking comments/checks are clear, PR merge completes, and local main sync is done.
deliverables:
  - .ai/tickets/TEMPLATE/finalize.md with required sections
  - Updated docs/agent-backlog.md when in scope
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Validate backlog edits with git diff and git diff --check where applicable.
  - Confirm both review passes accepted the current PR head and the branch was merged.
acceptance_criteria_to_check:
  - Confirm reviewer acceptance, validation sufficiency, and scope compliance before finalizing.
review_risk_plan:
  - Confirm no unresolved blocking findings remain from either review pass or optional automated review.
validation_contract:
  - Confirm required validation evidence and applicable QA/observability artifact references were accepted by reviewers or explicitly skipped with reason.
required_review_passes:
  - review-1 accepted for current PR head
  - review-2 accepted for current PR head
blocker_protocol:
  - If finalization is blocked, capture the exact blocker in finalize.md and state notes, and do not report the ticket as fully finalized.
output_contract:
  - Mode
  - Repo / branch check
  - Ticket state status
  - Slice plan or finalization summary
  - Review risk plan and validation contract status
  - Backlog write pre-check
  - Notes persisted or to persist
  - PR merge status
  - Recommended next actor
```

```text
You are the orchestrator for ticket TEMPLATE.
Read the Prompt Packet above and execute it exactly.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```
