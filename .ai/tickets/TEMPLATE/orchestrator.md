# TEMPLATE Orchestrator Pass

## Mode
- Planning Pass
- Or Blocked Triage / Prerequisite Planning

## Ticket
- Ticket ID: TEMPLATE
- Title: Replace with ticket title
- Branch: replace-with-branch-name
- Ticket type: primary or prerequisite child ticket

## Repo / branch check
- Current working directory:
- Git repo top-level:
- Target ticket branch:
- Branch exists or will be created: yes/no
- Current branch after this pass:
- Ticket branch checked out before implementer handoff: yes/no
- Notes:

## Ticket state status
- Current state on entry:
- Current next actor on entry:
- Current status on entry:
- Notes:

## Prerequisite assessment / blocker summary
- Hard prerequisites already satisfied: yes/no
- If no, list the missing capability:
- Human/external action required:
- Exact verification step:
- Unblock condition:
- Child ticket created/refreshed if needed:
- Notes:

## Slice plan summary
- Describe the smallest useful slice to implement now.

## Done definition
- Add item
- Add item

## Acceptance criteria
- Add item
- Add item

## Review risk plan
- Files or subsystems likely to change:
- Runtime boundaries to protect:
- Import/dependency boundaries to inspect:
- Untrusted input boundaries and validation/parsing points to inspect:
- Configured structural dependency lint/check, if any:
- Configured boundary-validation checks or skipped-check rationale, if any:
- Selected taste invariants and evidence/skipped-check rationale, if any:
- Relevant `docs/design-docs/architecture-contract.md` constraints, if any:
- Module-load side effects to watch:
- Domain concerns:
- Review artifacts expected:
- Structural dependency lint evidence or skipped-check rationale expected:
- Boundary-validation evidence expected when untrusted input is touched (required / optional / skip with reason):
- QA / observability evidence expected (required / optional / skip with reason):

## Validation contract
- Static validation:
- Test validation:
- Build validation:
- Runtime smoke validation:
- Domain validation:
- Boundary-validation evidence selected from `docs/workflow/boundary-validation-invariants.md`, when applicable:
- Taste-invariant evidence selected from generated `docs/design-docs/taste-invariants.md`, when applicable:
- Evidence selected from `docs/workflow/validation-evidence-matrix.md`:
  - Required evidence:
  - Optional evidence:
  - Evidence to skip with reason and residual risk:
- QA adapter intents or project-defined commands to reference, when applicable:
- Artifact paths or reference conventions to use, when applicable:

## Required review passes
- review-1: Claude Code
- review-2: Codex IDE

## Files likely in scope
- path/to/file1
- path/to/file2

## Risks / assumptions
- Note assumptions, scope limits, and things intentionally deferred.

## Backlog write pre-check
- Current working directory:
- Git repo top-level:
- `docs/agent-backlog.md` exists relative to repo root: yes/no
- Backlog file inside writable workspace: yes/no
- Notes:

## State transition checklist
- `state.json` read
- orchestrator-owned fields updated
- `stage` correct
- `next_actor` correct
- `handoff` correct
- history updated if stage changed
- ticket branch created or checked out before implementer handoff
- prerequisite child ticket created if hard prerequisites are missing
- review risk plan recorded
- validation contract recorded
- required review passes initialized

## Handoff decision
- If hard prerequisites are missing, keep the parent ticket with orchestrator, create or refresh the prerequisite child ticket, and use the prerequisite implementer prompt below.
- If prerequisites are satisfied, use the standard implementer prompt below.

## Next Agent Prompt (Implementer -- Standard Ticket)
Use this section when this ticket is a normal implementation slice and hard prerequisites are already satisfied.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: primary
execution_mode: standard
stage: planned
next_actor: implementer
waiting_on: implementer
mode: implementing
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
objective: Execute the planned slice only.
scope_in:
  - Implement only files and behaviors listed in this orchestrator brief.
scope_out:
  - No unrelated refactors.
  - No changes outside this ticket slice.
state_updates_required:
  - Confirm the ticket branch from state.json.branch is already checked out before implementation begins; if not, stop and route back to orchestrator.
  - On start: set stage=implementing, next_actor=implementer, waiting_on=implementer, add history entry.
  - On completion: set stage=implemented, next_actor=reviewer, waiting_on=reviewer, review.current_pass=review-1, reset required review passes for the PR head, set handoff implementer->reviewer pass 1, add history entry.
deliverables:
  - .ai/tickets/TEMPLATE/implement.md with required sections
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Run the smallest relevant validation for this slice according to the validation contract and record the exact command and result.
  - Record applicable QA/observability evidence references in implement.md and, when useful, state.json.validation.evidence. Include command intents, artifact paths, bounded log excerpts, screenshots/browser journey refs, metric/trace summaries, or skipped-evidence rationale only when selected by the risk matrix.
  - Keep all work on the active ticket branch.
acceptance_criteria_to_check:
  - Copy criteria from this orchestrator brief and verify each during implementation.
review_risk_plan:
  - Copy the Review risk plan from this orchestrator brief.
validation_contract:
  - Copy the Validation contract from this orchestrator brief.
required_review_passes:
  - review-1: Claude Code
  - review-2: Codex IDE
blocker_protocol:
  - If blocked, document the blocker, partial progress, and exact next step in implement.md.
  - If the branch is wrong or checkout was not completed safely, stop and hand back to orchestrator instead of continuing on the wrong branch.
output_contract:
  - Summary of changes or prerequisite progress
  - Key files changed
  - Edit method used
  - Validation performed against contract
  - QA / observability evidence references, including skipped evidence with reason and residual risk
  - Human action / blocker status
  - Questions for the human or exact next guided step when staying with implementer
  - Review risk handoff
  - Remaining work or follow-up
  - Notes to preserve for orchestrator
  - Handoff recommendation
```

```text
You are the implementer for ticket TEMPLATE.
Read the Prompt Packet above and execute it exactly.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```

## Next Agent Prompt (Implementer -- Prerequisite Child Ticket)
Use this section when the orchestrator creates a prerequisite child ticket such as `TKT-002.PREREQ-01`.

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: prerequisite
execution_mode: human_assisted
stage: implementing
next_actor: implementer
waiting_on: implementer
mode: implementing
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
objective: Work with the human to satisfy the prerequisite capability and verify it honestly.
scope_in:
  - Ask the smallest useful set of short questions needed to choose the right path when the path is not already clear.
  - Recommend one concrete path that fits the current machine and access constraints.
  - Guide the human one step at a time.
  - Verify the prerequisite after each meaningful human step.
scope_out:
  - No unrelated feature work from the parent ticket.
state_updates_required:
  - On start or reopen: set stage=implementing, next_actor=implementer, waiting_on=implementer, and add history entry if the stage changed.
  - While ordinary guided human setup is still pending, keep stage=implementing, next_actor=implementer, waiting_on=human or implementer as appropriate, and record the exact next question or step plus the verification command to rerun.
  - When the prerequisite is verified, set stage=implemented, next_actor=reviewer, waiting_on=reviewer, review.current_pass=review-1, reset required review passes for the PR head, update handoff implementer->reviewer pass 1, and add a history entry.
  - Only if a true blocker is reached, set stage=blocked, next_actor=orchestrator, waiting_on=orchestrator, update handoff implementer->orchestrator, and add a history entry.
deliverables:
  - Updated .ai/tickets/TEMPLATE/implement.md
  - Updated .ai/tickets/TEMPLATE/state.json
validation_required:
  - Record the exact commands used to prove the prerequisite capability is now available.
  - Prefer the smallest practical verification that honestly proves the parent ticket can resume.
acceptance_criteria_to_check:
  - The chosen path is concrete and feasible for the human to complete.
  - The prerequisite capability is verified from the current environment.
  - The orchestrator has enough evidence to resume the parent ticket honestly.
review_risk_plan:
  - Verification record and any setup artifacts are the reviewable risk surfaces.
validation_contract:
  - The verification commands must prove the prerequisite capability and record any reviewable evidence references or skipped-evidence rationale.
required_review_passes:
  - review-1: Claude Code
  - review-2: Codex IDE
completion_rule:
  - Do not advance this ticket merely because the human still needs to do the next setup step.
  - Keep the ticket with the implementer until the prerequisite is verified complete or a true blocker is reached.
  - Once verified, commit the verification record (`implement.md` with what was done, the verification command(s) run, observed output, and any human-reported evidence, plus the updated `state.json`) to the ticket branch, push, open a PR to `main`, and hand to reviewer pass 1 (not orchestrator). Every reviewer-routed ticket produces a PR.
true_blocker_definition:
  - The human lacks required permissions or approvals.
  - All viable setup paths are unavailable or rejected.
  - Guided attempts still fail and the next practical step is no longer clear.
  - An external dependency remains unavailable in a way that prevents further practical progress.
first_questions:
  - What access, permissions, or installation rights does the human have on this machine?
  - Is there already an approved external service or instance that can satisfy the prerequisite?
  - If multiple setup paths are possible, which low-risk path fits this environment best?
blocker_protocol:
  - Pending ordinary human setup is not a blocker by itself.
  - Ask only the smallest useful set of questions needed to choose a path, recommend one path, guide one step at a time, and rerun verification after each step.
  - If the human still needs to complete setup, keep the ticket with the implementer and record the exact next action and the verification step to rerun.
output_contract:
  - Summary of changes or prerequisite progress
  - Key files changed
  - Edit method used
  - Validation performed against contract
  - QA / observability evidence references, including skipped evidence with reason and residual risk
  - Human action / blocker status
  - Questions for the human or exact next guided step when staying with implementer
  - Review risk handoff
  - Remaining work or follow-up
  - Notes to preserve for orchestrator
  - Handoff recommendation
```

```text
You are the implementer for ticket TEMPLATE.
Read the Prompt Packet above and execute the human-assisted prerequisite implementation pass only.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```

## Next Agent Prompt (Specialist Sub-Ticket — Example: UI Specialist)
Use this section as the pattern for any specialist sub-ticket (UI, A11Y, Data, Performance, Security, Infrastructure, Testing, Observability). Replace the specialist name and fields to match the chosen type. Invoke the matching specialist via the name in the "Specialist invocation" table in `workflow-reference.md` (e.g. `$ui-specialist`, `$sec-specialist`, `$obs-specialist`).

### Prompt Packet (required)
```yaml
ticket_id: TEMPLATE
ticket_type: specialist
parent_ticket: <parent-ticket-id>
specialist:
  type: ui
  skill: $ui-specialist
  agent: claude
  reason: Frontend page layout and interactive components
execution_mode: standard
stage: planned
next_actor: implementer
waiting_on: implementer
mode: implementing
source_of_truth:
  - .ai/tickets/TEMPLATE/state.json
  - .ai/tickets/TEMPLATE/orchestrator.md
  - .Context/<ProjectName>-Specification.md
objective: Execute the specialist slice only, using the specialist's domain guidance.
scope_in:
  - Implement only the files and behaviors listed in this orchestrator brief.
  - Apply the specialist-specific implementation guidance from the specialist's agent/skill file.
scope_out:
  - No unrelated refactors.
  - No changes outside this specialist slice.
state_updates_required:
  - Confirm the ticket branch from state.json.branch is checked out before implementation begins.
  - On start: set stage=implementing, next_actor=implementer, waiting_on=implementer, add history entry.
  - On completion: set stage=implemented, next_actor=reviewer, waiting_on=reviewer, review.current_pass=review-1, reset required review passes for the PR head, set handoff implementer->reviewer pass 1, add history entry.
deliverables:
  - .ai/tickets/TEMPLATE/implement.md with required sections
  - Updated .ai/tickets/TEMPLATE/state.json
  - PR opened against main with the specialist slice
validation_required:
  - Run the smallest relevant validation for this specialist domain (see the specialist's agent/skill file for specifics) and record applicable evidence references or skips.
  - Keep all work on the active ticket branch.
visual_review_required: true  # Set true for UI and A11Y types; remove for other specialists.
human_review_steps:
  - Launch the dev server and confirm the component renders correctly at mobile, tablet, and desktop breakpoints.
  - Confirm interactive elements (focus states, keyboard navigation) behave as expected.
acceptance_criteria_to_check:
  - Copy criteria from the orchestrator brief and verify each during implementation.
  - For visual specialist types, human visual review must be completed before the reviewer marks it accepted.
review_risk_plan:
  - Copy the Review risk plan from this orchestrator brief and add specialist-specific risks.
validation_contract:
  - Copy the Validation contract from this orchestrator brief and add specialist-specific validation.
required_review_passes:
  - review-1: Claude Code
  - review-2: Codex IDE
blocker_protocol:
  - If blocked, document the blocker, partial progress, and exact next step in implement.md.
output_contract:
  - Summary of specialist changes
  - Components / code paths touched
  - Domain-specific validation performed
  - Items requiring human review (if applicable)
  - PR created or updated (number, URL)
  - Notes to preserve for orchestrator
  - Handoff recommendation
```

```text
You are the UI specialist for ticket TEMPLATE.
Read the Prompt Packet above and execute it exactly, applying the UI specialist's domain guidance from .roles/ui-specialist.md.
If any required Prompt Packet field is missing, fall back to state.json + role rules and explicitly log the gap.
```
