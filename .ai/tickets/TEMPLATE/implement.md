# TEMPLATE Implementation

## Summary of changes or prerequisite progress
Describe exactly what changed, or the current prerequisite progress.

## Key files changed
- path/to/file1
- path/to/file2

## Edit method used
- `apply_patch`
- PowerShell direct edit
- Python direct edit

Include why fallback was used if `apply_patch` failed.

## Validation performed against contract
- Command(s) run:
- Structural dependency lint command/result, if selected by the validation contract:
- Boundary-validation command/result or evidence, if selected by the validation contract:
- Taste-invariant rule/evidence, if selected by the validation contract:
- Result:
- If not run, explain why and why remaining evidence is sufficient:

## QA / observability evidence references
Record only evidence selected by the validation contract and `docs/workflow/validation-evidence-matrix.md`. Older tickets may omit `state.json.validation.evidence`; when present, keep it aligned with this section.

### Produced evidence
- Evidence item:
  - Risk class:
  - Required / optional:
  - Command intent or project-defined command:
  - Artifact path or reference:
  - Bounded summary:
  - Safe environment:
  - Redaction / retention note:

### Skipped evidence / residual risk
- Evidence item skipped:
  - Why skipped:
  - Residual risk:
  - Human follow-up needed, if any:

## Human action / blocker status
- Completed human action:
- Pending human action:
- Verification evidence:
- True blocker reached: yes/no
- If yes, explain:

## Questions for the human or exact next guided step when staying with implementer
- Question or next step:
- Verification command to rerun after that step:
- Success looks like:

## Review risk handoff
- Changed runtime/import boundaries:
- Changed untrusted input boundaries and validation/parsing points:
- Selected taste invariants touched:
- Module-load side effects:
- Data/security/infra/a11y/performance concerns:
- Areas reviewers should inspect closely:

## Remaining work or follow-up
- Item
- Item

## Notes to preserve for orchestrator
- Item
- Item

## State transition checklist
- `state.json` read
- implementer-owned fields updated
- `stage` correct
- `next_actor` correct
- `handoff` correct
- history updated if stage changed

## Handoff decision
- To reviewer pass 1 when the slice is review-ready (applies to main, specialist, and prerequisite tickets alike; prerequisite tickets also hand to reviewer pass 1 once the prerequisite is verified complete).
- Stay with implementer when this is a prerequisite ticket and the next ordinary human step is still pending. Pending ordinary human setup is not a blocker.
- To orchestrator only when a true blocker is reached.

## Next Agent Prompt (Implementer -- when continuing human-assisted prerequisite loop)
Use this section when the ticket should stay with the implementer for the next human-guided step.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: prerequisite
execution_mode: human_assisted
stage: implementing
next_actor: implementer
waiting_on: human_or_implementer
mode: implementing
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
  - .ai/tickets/TEMPLATE/implement.md
objective: Continue the human-assisted prerequisite loop without returning to orchestrator yet.
scope_in:
  - Ask the next smallest useful question or provide the next concrete setup step.
  - Rerun the planned verification command after the human completes that step.
scope_out:
  - Do not prematurely hand the ticket back to orchestrator.
  - No unrelated feature work.
state_updates_required:
  - Keep stage=implementing and next_actor=implementer while the next ordinary human step is pending.
  - Update waiting_on to reflect whether the immediate next move is with the human or the implementer.
deliverables:
  - Updated .ai/tickets/TEMPLATE/implement.md
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Run the smallest practical verification after the human completes the next guided step and record applicable evidence references or skipped-evidence rationale.
acceptance_criteria_to_check:
  - The prerequisite path remains concrete and feasible.
  - The next guided step is clear and verifiable.
completion_rule:
  - Keep the ticket with the implementer until the prerequisite is verified complete or a true blocker is reached.
true_blocker_definition:
  - The human lacks required permissions or approvals.
  - All viable setup paths are unavailable or rejected.
  - Guided attempts still fail and the next practical step is no longer clear.
blocker_protocol:
  - Pending ordinary human setup is not a blocker by itself.
output_contract:
  - Summary of changes or prerequisite progress
  - Validation performed
  - QA / observability evidence references, including skipped evidence with reason and residual risk
  - Human action / blocker status
  - Questions for the human or exact next guided step when staying with implementer
  - Handoff recommendation
```

```text
You are the implementer for ticket TEMPLATE.
Read the Prompt Packet above and continue the human-assisted prerequisite loop.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```

## Next Agent Prompt (Reviewer Pass 1 -- when review-ready)
Use this section when this is a normal implementation ticket and the slice is ready for the first required review pass.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: primary
execution_mode: standard
stage: implemented
next_actor: reviewer
waiting_on: reviewer
mode: review
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
  - .ai/tickets/TEMPLATE/implement.md
objective: Complete reviewer pass 1 for the implemented slice on the current PR head.
scope_in:
  - Validate only the planned slice and touched files.
scope_out:
  - Do not request unrelated changes.
state_updates_required:
  - If changes needed: stage=changes_requested, next_actor=implementer, waiting_on=implementer, review.outcome=changes_requested, add history.
  - If accepted: record review-1 accepted for the current PR head, set stage=reviewing, next_actor=reviewer, waiting_on=reviewer, review.current_pass=review-2, review.outcome=in_progress, add history.
deliverables:
  - .ai/tickets/TEMPLATE/review.md with required sections
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Confirm implementation validation satisfies the validation contract; request more only if required.
acceptance_criteria_to_check:
  - Evaluate each planned acceptance criterion with pass/fail notes.
review_risk_plan:
  - Use the risk plan from orchestrator.md and the implementation risk handoff in implement.md.
validation_contract:
  - Use state.json.validation.contract, implement.md validation evidence, and optional state.json.validation.evidence when present.
required_review_passes:
  - review-1: Claude Code
  - review-2: Codex IDE
blocker_protocol:
  - If review cannot be completed, record the exact blocker and missing evidence, including any required QA artifact or skipped-evidence rationale.
output_contract:
  - Review verdict
  - Review pass (id, tool, current PR head SHA)
  - Acceptance criteria check
  - Validation contract check
  - QA / observability evidence sufficiency and safety check
  - Findings
  - Non-blocking observations
  - Notes to preserve for orchestrator
  - Handoff decision
```

```text
You are reviewer pass 1 for ticket TEMPLATE.
Read the Prompt Packet above and execute it exactly.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```

## Next Agent Prompt (Orchestrator -- when truly blocked)
Use this section **only** when the prerequisite is truly blocked (the human lacks permissions, all viable paths are exhausted, etc.). A verified-complete prerequisite hands to reviewer pass 1 via the "Reviewer Pass 1 -- when review-ready" section above, not here.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: prerequisite
execution_mode: human_assisted
stage: blocked
next_actor: orchestrator
waiting_on: orchestrator
mode: blocked-triage
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
  - .ai/tickets/TEMPLATE/implement.md
objective: Triage a truly blocked prerequisite and decide whether to re-plan, wait, or escalate.
scope_in:
  - Record the exact blocker and missing condition.
  - Decide whether to wait, split, or escalate.
scope_out:
  - No unrelated feature work from the parent ticket.
state_updates_required:
  - Preserve the exact blocker and missing condition in state.json and implement.md.
deliverables:
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Confirm the recorded evidence honestly supports the "blocked" claim.
acceptance_criteria_to_check:
  - The blocker is concrete and the unblock condition is clearly stated.
blocker_protocol:
  - Do not mark the ticket blocked if an ordinary guided human step is still available; return to implementer instead.
output_contract:
  - Blocker summary
  - Unblock condition
  - State updates made
  - Recommended next actor
```

```text
You are the orchestrator for ticket TEMPLATE.
Read the Prompt Packet above and execute it exactly.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```
