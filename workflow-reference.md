# Workflow Reference (Detailed)

This file holds detailed workflow rules so `AGENTS.md` and `CLAUDE.md` can stay short.

## Workflow stages
0. architect: requirements + specification + initial ticket bootstrap
1. orchestrator: Planning Pass
1a. orchestrator: prerequisite assessment and prerequisite sub-ticket creation when needed
2. implementer: implementation pass + commit, push, and PR creation
3. reviewer pass 1: Claude Code PR review pass (approve the pass or request changes)
4. reviewer pass 2: Codex IDE PR review pass (approve the pass or request changes)
5. orchestrator: Finalization Pass (merge only after every required review pass approves the current PR head, then sync main)

## Ticket contract
Ticket folder: `.ai/tickets/<ticket-id>/`

Required files:
- `state.json`
- `orchestrator.md`
- `implement.md`
- `review.md`
- `finalize.md`

`state.json` is authoritative when there is a mismatch.

## AI usage and cost accounting
Each ticket should carry a lightweight AI usage ledger in `state.json.ai_usage`. The ledger is an estimate for project accounting, not an authoritative billing record.

**Automation-first capture rule:** when a pass runs through an automated or headless harness (CI job, `claude -p` / Agent SDK run, action output), record the run's tool-reported totals (`source = tool_reported`, e.g. the reported `total_cost_usd` or token counts) and move on. The manual capture workflows below (session JSONL helpers, dashboards) are fallbacks for interactive sessions. Do not spend implementation or review turns on usage archaeology: if usage is not cheaply available, record `source = not_available`, `confidence = unknown`, one short note, and continue. A thin or missing ledger entry is acceptable; a fabricated one is not.

Recommended shape:
```json
"ai_usage": {
  "currency": "USD",
  "entries": [
    {
      "role": "implementer",
      "workflow_event": "initial_implementation",
      "tool": "Claude Code",
      "model": "Claude Sonnet",
      "input_tokens": 0,
      "cached_input_tokens": 0,
      "output_tokens": 0,
      "credits_used": null,
      "estimated_cost_usd": 0.0,
      "source": "tool_reported",
      "confidence": "estimated",
      "recorded_at": "2026-05-18T10:30:00+10:00",
      "notes": "Recorded from Claude Code /usage before handoff."
    }
  ],
  "ticket_total_estimated_usd": 0.0,
  "ticket_total_confidence": "complete"
}
```

Field guidance:
- `workflow_event` names why this usage entry exists. Prefer short snake_case labels such as `planning`, `initial_implementation`, `implementer_pause`, `blocked_handoff`, `fix_loop_1`, `review_1_initial`, `review_1_rerun`, `review_2_initial`, `review_2_rerun`, or `finalization`.
- `source` should be one of `tool_reported`, `dashboard`, `manual`, `session_jsonl`, `estimated`, or `not_available`.
- `confidence` should be one of `exact`, `estimated`, `partial`, or `unknown`.
- Use `estimated_cost_usd` when a dollar estimate is available. Use `credits_used` when Codex reports credits instead of dollars.
- Do not fabricate token counts or cost. If the tool does not expose usage for the pass, add a short `notes` value and either omit the entry or record it with `source = not_available`, `confidence = unknown`, and no numeric cost. For Codex, `source = not_available` is allowed only after local session JSONL parsing has been attempted and failed or the environment explicitly prevents reading the session files.
- Claude Code users should capture usage from session JSONL logs in `~/.claude/projects/<repo-slug>/<session>.jsonl` because `/usage` and `/cost` may be unavailable in some environments.
- **Claude capture workflow:** run `python scripts/claude_session_tokens.py` at each baton point (planning handoff, implementation handoff, each review pass outcome, finalization), then paste the JSON payload into `state.json.ai_usage.entries[*]` with pass metadata (`workflow_event`, `actor`, `tool`, `recorded_at`).
- **Pricing freshness rule:** if the helper script's `PRICES_AS_OF` is older than ~6 months, omit `estimated_cost_usd`/`usd_estimate` and add a note that pricing is stale.
- Codex users should record the session/tool usage summary or Codex usage dashboard value when available. If only credits are available, record credits and leave `estimated_cost_usd` empty unless a known conversion is available.
- **Codex primary fallback for non-interactive agents:** parse local Codex session JSONL before giving up on usage capture. Codex stores sessions under `%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl` on Windows and `$HOME/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` on Unix-like systems. The session index is `%USERPROFILE%\.codex\session_index.jsonl` or `$HOME/.codex/session_index.jsonl`. Each relevant session JSONL should contain `type == "session_meta"` with fields such as `payload.id`, `payload.cwd`, `payload.source`, `payload.originator`, `payload.thread_source`, and `payload.model_provider`, plus `type == "event_msg"` where `payload.type == "token_count"` and `payload.info.total_token_usage` carries token counts.
- **Codex helper workflow:** run `python scripts/codex_session_tokens.py --ticket-id <ticket-id> --cwd <repo-root> --workflow-event <event> --actor <role>` at each baton point, then paste or adapt the JSON payload into `state.json.ai_usage.entries[*]`. Use `--session-id <id>` when the current Codex session id is known. Use `--since <iso-timestamp>` and/or `--until <iso-timestamp>` to filter `token_count` events to the baton/handoff window before selecting the last matching event. Use `--previous-checkpoint <json-file>` when the same thread continues after a prior checkpoint so the helper records deltas instead of another cumulative snapshot. If the helper cannot find a matching session, record its `not_available` output or a note showing JSONL parsing was attempted.
- **Codex session matching guidance:** prefer the current `session_meta.payload.id` when available. Otherwise match by `session_meta.cwd`, ticket id in the first user message or thread/index text, latest modified matching `rollout-*.jsonl`, and timestamps around the baton/handoff (`--since` / `--until` when useful). Exclude `thread_source == "subagent"` sessions from the parent pass by default, or record them as separate entries when subagent accounting is required.
- **Codex pass-boundary guidance:** capture the last `token_count` event present at the baton/handoff time. If the same Codex thread continues later, record deltas from the previous checkpoint. If no prior checkpoint exists, mark the entry as a cumulative snapshot and `confidence = partial` rather than pretending it is an exact pass delta.
- **Codex token accounting rule:** observed Codex token fields include `input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_output_tokens`, and `total_tokens`. Treat `reasoning_output_tokens` as a detail/subset of output accounting unless current OpenAI pricing documentation explicitly says otherwise; do not add reasoning tokens a second time. Use `total_tokens = input_tokens + output_tokens` as the sanity check when the event reports it that way.
- **Codex manual fallback for humans only:** `codex resume --all` may be used as a human/manual fallback when the plugin/dashboard and JSONL parsing are unavailable. Do not make this the primary agent fallback because `codex resume --all` requires a real TTY and can fail for API/tool-shell agents with `Error: stdin is not a terminal`.
- **Cost estimate guidance:** when exact model slug and current pricing are known, compute `estimated_cost_usd` as `((input_tokens - cached_input_tokens) * input_rate + cached_input_tokens * cached_input_rate + output_tokens * output_rate) / 1_000_000`. Record `pricing_source`, `prices_as_of`, and `cost_confidence`. If the model slug is missing but a model family is known, record a range or scenario estimate with `cost_confidence = partial` or `low`, not `exact`. If no model slug is available, prefer a planning scenario using the latest OpenAI model rates known to the helper at runtime (for example, latest frontier model `gpt-5.5` at $5.00 / 1M input tokens, $0.50 / 1M cached input tokens, and $30.00 / 1M output tokens as of 2026-06-10) and state that the model was not provided, so the estimate is not exact. If Codex is subscription/seat-based or otherwise not API-billed, mark the result as a planning estimate, not an invoice.
- **Per-pass boundary rule:** usage should be recorded as closely as possible to each baton handoff. If only cumulative session totals are available, record a cumulative snapshot and note that deltas for prior events are estimated or unavailable; do not fabricate per-pass token deltas.
- Subscription/seat plans may not map directly to incremental API billing; treat dollar fields as planning estimates, not invoices.
- Subscription-included usage should still be recorded as estimated token or credit consumption when visible; note that it may not equal incremental cash spend.

Role responsibilities:
- Architect may initialize the ledger when bootstrapping the project or first tickets, but this is not required.
- Orchestrator Planning Pass initializes `state.json.ai_usage` when missing.
- Implementer records its own pass usage before every handoff, pause, blocker, or fix-loop return.
- Each reviewer pass records its own pass usage before routing onward or back.
- Orchestrator Finalization Pass records its own finalization usage when available, recomputes `ticket_total_estimated_usd` from all numeric entry values, writes the rollup to `finalize.md`, and leaves the ticket ledger queryable.
- Orchestrator Finalization output must explicitly report AI usage/cost status for the pass: either numeric fields captured or a fallback note such as `Codex exact usage unavailable in this environment` with `source = not_available` and `confidence = unknown`.
- Every pass should append a new entry with an appropriate `workflow_event`; do not overwrite earlier entries from the same ticket, role, or review pass.
- Project cost can be estimated by summing `ticket_total_estimated_usd` across `.ai/tickets/*/state.json`. If child tickets should be included in a parent summary, use the ticket relationships already recorded in `state.json` rather than duplicating child entries into the parent ledger.

## User-facing final-answer requirements
Each role must include the relevant ticket-file fields in its user-facing final answer. Pull these values from the current ticket files under `.ai/tickets/<ticket-id>/`; if a field is missing, say it is missing instead of inventing it. After the listed fields, include a concise AI-written summary that explains what happened, the key risks/residual risks, mitigation status, and the recommended next actor.

### Orchestrator Planning Pass final answer
Source: `.ai/tickets/<ticket-id>/orchestrator.md` plus `state.json`.

Required fields:
- `Ticket ID:`
- `What This Ticket Comprises:`
- `Slice Plan:`
- `Done Definition:`
- `Acceptance Criteria:`
- `Foreseen Risks / Planned Mitigations / Human Intervention Points:`
- `Review Risk Plan:`
- `Validation Contract:`
- `AI Usage:`
- `Recommended Next Actor:`
- `[AI Summary of the above. What is proposed, what are the risks, what are the risk mitigations, and the next actor]`

### Implementer and specialist implementation final answer
Source: `.ai/tickets/<ticket-id>/implement.md` plus `state.json`.

Required fields:
- `Ticket ID:`
- `Summary of changes or prerequisite progress:`
- `Validation performed against contract:`
- `Skipped evidence / residual risk:`
- `Human action / blocker status:`
- `Review risk handoff:`
- `Remaining work or follow-up:`
- `Handoff decision:`
- `AI Usage:`
- `[AI Summary of the above. What was performed, what was changed / updated, any residual risks, any tests that couldn't be performed and why, and the next actor]`

### Standard reviewer final answer
Source: `.ai/tickets/<ticket-id>/review.md` plus `state.json`.

Required fields:
- `Ticket ID:`
- `Review pass:`
- `Review verdict:`
- `PR reviewed:`
- `Code inspection:`
- `Acceptance criteria check:`
- `Review risk plan check:`
- `Validation contract check:`
- `Findings:`
- `Non-blocking observations:`
- `AI Usage:`
- `Handoff decision:`
- `[AI Summary of the above. What was reviewed, what was found, any residual risks, and the next actor]`

### Security review gate final answer
Source: `.ai/tickets/<ticket-id>/review.md` plus `state.json`.

Required fields:
- `Ticket ID:`
- `Security Review Gate:`
- `Security Review Pass:`
- `PR reviewed:`
- `Code inspection:`
- `Findings:`
- `Non-blocking observations:`
- `AI Usage:`
- `Handoff decision:`
- `[AI Summary of the above. What was reviewed, what was found, any residual risks, and the next actor]`

### Orchestrator Finalization Pass final answer
Source: `.ai/tickets/<ticket-id>/finalize.md`, `state.json`, and `docs/exec-plans/build-cost.md`.

Required fields:
- `Ticket ID:`
- `Final acceptance:`
- `Deferred follow-up:`
- `Commit / PR / merge status:`
- `Carry-forward notes:`
- `Recommended Next Ticket:`
- `[AI Summary of the above. What was finalised, what was successfully implemented as part of this ticket, any residual risks, if mitigations are in place for the risks and what they are, any observations to carry forward, and the recommended next ticket]`
- `AI Usage Ledger Total:` summed from `docs/exec-plans/build-cost.md`, including confidence/completeness when available.

## Ticket ID convention
- Primary tickets use the normal form such as `TKT-002`.
- Prerequisite sub-tickets use the parent ticket ID plus the `PREREQ` infix and a zero-padded numeric suffix such as `TKT-002.PREREQ-01`, `TKT-002.PREREQ-02`.
- A prerequisite sub-ticket belongs to one parent ticket and represents external setup, approvals, credentials, infrastructure, or other human actions needed to unblock that parent ticket.
- Keep each prerequisite sub-ticket singular and verifiable. If two unrelated human actions are required, prefer two child tickets.

Allowed stages:
- `planned`
- `implementing`
- `implemented`
- `reviewing`
- `changes_requested`
- `review_accepted`
- `finalized`
- `blocked`

Use `blocked` for missing prerequisites, pending human action, missing credentials, unavailable external services, or other honest stop conditions. A blocked prerequisite ticket is not a failed ticket; it is waiting for its stated unblock condition.

## Ownership
Architect owns:
- requirement intake + clarification
- context review (`.Context/`)
- specification authoring
- initial ticket roadmap/bootstrap
- flagging likely external prerequisites at roadmap time when obvious
- handoff to orchestrator

Orchestrator owns:
- ticket bootstrap
- ticket-branch creation / checkout before implementation starts
- prerequisite assessment before main-ticket implementation
- creating and tracking prerequisite sub-tickets when human or external actions are required
- deciding whether the parent ticket can proceed, must stay blocked, or should route through a prerequisite loop
- done definition + acceptance criteria
- the ticket-specific review risk plan: risky files, runtime boundaries, import boundaries, selected taste invariants, data/security/infra/a11y/performance concerns, likely failure modes, and artifacts reviewers must inspect
- the validation contract: required static checks, tests, build checks, runtime smoke checks, domain-specific checks, selected taste-invariant evidence when applicable, and selected QA/observability evidence for the slice
- backlog write pre-check + backlog sync
- final acceptance
- finalization gate checks: every required review pass and any required security review gate is current for the PR head under the review-record or finalization-record exemption rules, required validation evidence and applicable QA/observability artifact references are accepted or explicitly skipped with reason, GitHub checks/comments contain no unresolved blocking findings, and approvals are not stale
- merging the fully approved PR to `main` and local `main` sync during finalization
- next-ticket recommendation

Implementer owns:
- code changes
- technical guidance for human-completed prerequisite work
- verification of prerequisite completion using the smallest practical commands or checks
- the human-assisted prerequisite loop until the prerequisite is verified complete or a true blocker is reached
- smallest relevant validation
- validation evidence against the orchestrator's validation contract, including optional `state.json.validation.evidence` references when useful, explicit skipped checks, and why they were accepted or unavoidable
- implementation risk handoff: changed files, import/runtime boundaries touched, module-load side effects, data/security/infra/a11y/performance concerns, and any areas reviewers should inspect closely
- committing, pushing, and creating the pull request to `main` after implementation is complete
- recording PR details in `state.json.pull_request`
- pushing fixup commits (artifact changes) when returning from `changes_requested`
- resetting review pass status after artifact fixup commits so both required reviewers re-approve the current PR head
- notes to preserve for orchestrator
- implementation state transitions

Reviewer owns:
- one assigned review pass in the two-phase review sequence
- PR review via GitHub (reading the PR diff, files changed, description, existing reviews/comments, and current head SHA)
- independent inspection of the PR diff, not just validation of the implementer's handoff
- submitting or documenting GitHub PR reviews: `REQUEST_CHANGES` when blocking issues are found; pass acceptance comments/reviews when accepted; final-pass formal `APPROVE` or fallback approval when applicable
- findings / observations (written to both `review.md` and the PR)
- checking the slice against the review risk plan, validation contract, known best practice for its domain, optional `state.json.validation.evidence` references when present, and missing artifacts the slice should have produced
- checking runtime/import boundaries, selected taste invariants, module-load side effects, server/client or Edge/Node compatibility, external side effects, secrets/PII exposure, migrations/schema effects, and dependency hazards when relevant
- preserving orchestrator notes through fix loops
- routing accepted work to the next required review pass, or to orchestrator only after all required review passes are current for the PR head under the review-record exemption rule
- review of every sub-ticket before orchestrator finalization, including prerequisite sub-tickets (the implementer's verification record is committed to the PR, so the reviewer always reviews a PR diff)

Security reviewer owns:
- independent security review gates for security-sensitive slices identified during Planning Pass
- reviewer-style inspection of the current PR head for authentication, authorization, secrets, privacy, dependency, infrastructure, and trust-boundary risks
- submitting or documenting GitHub PR security reviews: `REQUEST_CHANGES` with line-level comments for blocking security issues when possible; pass acceptance comments/reviews when accepted; final-pass formal `APPROVE` or fallback approval when applicable
- writing the security review gate record into `review.md` and `state.json.review.required_passes`, including the PR comment/review reference when available
- routing accepted gates onward only when the security review gate is current for the PR head under the review-record exemption rule
- routing changes back to `$sec-specialist` for security-specific implementation, `$implementer` for ordinary fixes, or another specialist when the finding belongs to that domain
- preserving security risk notes for orchestrator finalization and future workflow hardening

## Optional validation evidence references

Tickets may record reviewable QA and observability evidence in `state.json.validation.evidence`. This field is optional and additive; older tickets may omit it, and agents must fall back to `validation.performed`, `implement.md`, `review.md`, and the validation contract when it is absent.

Use the risk-based defaults in `docs/workflow/validation-evidence-matrix.md` to decide which evidence is required, optional, or skipped with reason. Evidence references should remain stack-neutral until a downstream project has configured concrete commands in `docs/workflow/agent-qa.md` or adapter intents in `docs/workflow/qa-command-adapters.md`. Browser evidence and observability evidence remain optional examples linked from `docs/workflow/browser-critical-journeys.md` and `docs/workflow/ephemeral-observability.md`; do not require screenshots, logs, metrics, traces, browser tooling, containers, cloud services, or vendor tooling for every ticket.

Evidence entries should be compact and reviewable: command intent or project-defined command, pass/fail or skipped status, artifact path/reference when produced, bounded summary, safe environment, redaction/retention note, and skip reason plus residual risk when expected evidence is not produced. Avoid secrets, credentials, production data, unbounded logs, unnecessary screenshots/videos/traces, and unnecessary retention. Do not point agent QA at production systems unless explicitly approved for that ticket.

Taste invariant evidence is optional and project-specific. When a downstream project has generated `docs/design-docs/taste-invariants.md` and a ticket touches a selected rule's declared scope, the orchestrator may add the rule id, enforcement status, and smallest evidence to the validation contract. Do not treat `docs/design-docs/taste-invariants-template.md` examples as active policy, and record missing or deferred enforcement as skipped with reason and residual risk.

## Routing rules
- Orchestrator should not normally hand directly to reviewer.
- Architect should not be used for normal ticket loops after orchestrator handoff.
- Planning Pass must not hand a main ticket to the implementer until hard prerequisites are either satisfied or split into explicit prerequisite sub-tickets.
- When a main ticket is blocked by an external dependency, the orchestrator keeps the parent ticket blocked and routes the prerequisite sub-ticket instead.
- **Every ticket and sub-ticket follows the full review cycle: `orchestrator -> implementer -> reviewer pass 1 -> reviewer pass 2 -> orchestrator`** (standard tier shown; the ticket's review tier in `docs/workflow/review-tiers.md` sets which passes `state.json.review.required_passes` requires). One state machine covers all tickets.
- Prerequisite sub-tickets stay with the implementer during the human-assisted setup loop. Do not bounce them back to orchestrator or onward to reviewer just because the human still needs to perform the next guided step; the implementer holds the ticket until the prerequisite is verified complete or a true blocker is reached.
- When the prerequisite is verified complete, the implementer commits the verification record (plus any setup scripts or docs), pushes the branch, opens a PR to `main`, and hands to reviewer pass 1. Each reviewer reviews the PR diff, which always contains at least the verification record, and approves the pass or requests changes.
- Normal ticket flow: implementer creates the PR, reviewer pass 1 reviews, reviewer pass 2 independently reviews, and orchestrator merges only after both required passes are current for the PR head under the review-record exemption rule.
- Either reviewer returns to implementer if code, validation, evidence, scope, or artifact changes are required. The reviewer adds comments to the PR so the implementer can reference them.
- After any fixup commit, prior review pass approvals are stale unless their recorded `head_sha` matches the current PR head OR the only commits since that recorded `head_sha` are review-record-only (see "Stale-head gate and review/finalization record exemptions" below). When a fixup commit changes any file outside the current ticket's `review.md` and `state.json`, the implementer restarts review at pass 1 unless the orchestrator explicitly documents a narrower re-review path.
- Accepted work with all required review passes approved returns to orchestrator for merge and finalization.

## Review risk plan
During Planning Pass, the orchestrator must write a ticket-specific review risk plan into `orchestrator.md` and `state.json.review.risk_plan` when practical.

The risk plan should be short and concrete:
- files or subsystems likely to change
- runtime boundaries: browser/server, Edge/Node, client/server components, build-time/runtime, local/cloud, sync/async worker boundaries
- import or dependency boundaries that must not be crossed
- module-load side effects to watch for
- data, migration, security, privacy, observability, accessibility, performance, or infrastructure concerns
- expected review artifacts, such as screenshots, logs, migration output, smoke-test output, or human verification evidence

The implementer must update the handoff if the actual implementation touches different or additional risk surfaces. Reviewers must use the risk plan, but they must still inspect independently for risks the plan missed.

## Human-facing planning summaries
During Planning Pass, the orchestrator must also write plain-language planning context for the human operator into `orchestrator.md` and include it in the response:

- `## What This Ticket Comprises`: the major capabilities, user-visible outcomes, important scope boundaries, and what is deliberately excluded from the slice.
- `## Foreseen Risks / Planned Mitigations / Human Intervention Points`: a concise summary derived from the review risk plan that explains each material risk, the planned mitigation agents must follow, what the human may need to prepare for, and where the human should intervene if the planned work looks too broad, too disruptive, or misaligned with intent.

These sections are for human situational awareness. Planned mitigations are also binding ticket guidance: implementers must preserve them in the handoff, and reviewers must verify they were followed or explicitly superseded with evidence. They do not replace the ticket-specific review risk plan, validation contract, acceptance criteria, or prompt handoff packet. Keep the language concrete and readable rather than reviewer-internal.

## Validation contract
During Planning Pass, the orchestrator must define a validation contract for the slice. Keep it ticket-appropriate and agnostic to implementation details.

Use these categories as a checklist:
- static validation: lint, typecheck, schema validation, dependency/import boundary checks when available
- test validation: unit, integration, end-to-end, fixture, or contract tests relevant to the slice
- build validation: production build, package build, migration validation, generated-client validation, or config validation
- runtime smoke validation: start the app/service, hit a route/API/CLI path, run a representative job, or verify a prerequisite capability
- domain validation: security, data, infrastructure, accessibility, performance, observability, or UI checks when the slice touches that domain

The implementer records what passed, exact commands where possible, observed output summaries, and skipped checks with reasons. Reviewers judge whether the evidence is sufficient. The orchestrator finalization gate verifies that required validation is present and accepted before merge.

## Two-phase review
Every reviewer-routed ticket requires two independent review passes by default (the `standard`
review tier):
- `review-1`: Claude Code by default
- `review-2`: Codex IDE by default

`required_passes[*].tool` is per-pass configuration recorded at planning time, not a fixed tool
identity. A project may run a pass with a different tool or model, and pass 2 SHOULD use a
different model than pass 1 when one is available, to reduce correlated review blind spots.

During Planning Pass the orchestrator may select a different review tier: `light` (a single
`review-1` pass, only for no-runtime-risk slices) or `high-risk` (adds the `security-review`
gate). Tier eligibility and upgrade rules live in `docs/workflow/review-tiers.md`. The tier only
changes what Planning Pass writes into `state.json.review.required_passes`; routing and gate logic
are unchanged.

Each pass is a code review first; checklists direct attention but do not substitute for reading the diff. Each pass must record:
- pass id and tool
- current PR head SHA reviewed
- code-inspection evidence: every file changed in the PR with a one-line note (`inspected — <concern or "no concerns">`, or `skipped — <reason>` for bulk/generated files); findings cite the file and line/hunk when applicable
- outcome: `accepted`, `accepted_with_follow_up`, or `changes_requested`
- blocking findings and non-blocking observations
- validation sufficiency assessment
- PR comment or review URL/reference when available

Reviewers must not spend the pass re-verifying state mechanics that `scripts/validate_ticket_state.py` already gates in CI; confirm the required checks are green and spend the review on the diff.

`state.json.review.required_passes` is the authoritative pass list. If it is missing on an older ticket, the first reviewer should initialize it with the default two-pass sequence and continue with `review-1`.

A reviewer pass that accepts while another required pass is still pending hands to the next
required pass, not orchestrator. The final required pass (`review-2` in the standard tier;
`review-1` in the light tier) hands accepted work to orchestrator only when every required pass
record is current for the PR head under the review-record exemption rule (see "Stale-head gate and
review/finalization record exemptions" below).

If either reviewer requests changes:
- set `stage = changes_requested`
- set `next_actor = implementer`
- keep `next_actor = implementer` even for specialist sub-tickets, because specialist roles run the implementer state machine
- resolve the human-visible implementation role from `state.json.specialist` when `ticket_type = specialist`; the reviewer handoff must name the concrete skill, for example `$sec-specialist`, and include it as `next_skill` in the Prompt Packet
- record which pass requested changes
- leave specific PR comments or a PR review
- require the implementer to push a fixup commit (an artifact change — code, tests, docs, or other content outside this ticket's `review.md`/`state.json`) and reset both required passes to pending for the new PR head unless the orchestrator explicitly documents a narrower re-review path

External GitHub automated review tools, including Codex Code Review, are optional safety nets. The workflow must not depend on them being available. If they do run, their unresolved high-severity (P0/P1) findings are blocking during finalization; lower-severity findings are advisory and are triaged by the orchestrator per `docs/workflow/review-gates.md` § "Automated finding triage and loop guard" (`fix_now`, `deferred`, or `dismissed_false_positive` with a written reason). The same section defines the fix-loop guard: `state.json.review.fix_loop_count` is incremented on each `changes_requested` return, and at the threshold (default 3) the orchestrator triages or escalates to the human instead of dispatching another loop.

## PR approval fallback
When the implementer and reviewer operate under the same GitHub account, GitHub blocks formal self-approval. This is a common case in single-human-operator projects and must not be treated as a failure.
- A reviewer pass that accepts while another required pass is still pending records pass acceptance in `review.md`, `state.json.review.required_passes`, and a PR comment/review. It does not route to orchestrator.
- The reviewer running the final required pass (`review-2` in the standard tier; `review-1` in the light tier) attempts final `APPROVE` after confirming all earlier required passes are current for the PR head under the review-record exemption rule. If GitHub rejects formal approval, that reviewer leaves a PR comment with the exact text `LGTM — approved by reviewer`.
- The orchestrator accepts either a GitHub approving review OR the fallback comment as proof of final-pass acceptance, provided every required pass record in `state.json.review.required_passes` is current for the PR head under the applicable review-record or finalization-record exemption rule.
- `state.json.pull_request.status = approved` remains the authoritative final acceptance signal after all required passes are accepted.
- Each reviewer always writes the full review into `review.md` as well, so the ticket record is complete either way.

## Stale-head gate and review/finalization record exemptions

**Default rule**: each required reviewer pass records the PR head SHA it accepted in `state.json.review.required_passes[*].head_sha`. A later gate (subsequent reviewer pass, orchestrator finalization) checks that every required pass's recorded `head_sha` matches the current PR head SHA. When they differ, the prior pass is **stale** and must be re-run before the gate can pass.

**Exemption — review-record-only commits**: commits whose tree changes are confined to the current ticket's `review.md` and `state.json` (both under `.ai/tickets/<ticket-id>/`) do **not** invalidate prior pass acceptance. These are workflow bookkeeping, not unreviewed content changes.

**How to evaluate the review-record exemption**:
1. Resolve the prior pass's recorded `head_sha` from `state.json.review.required_passes[*]`.
2. Run `git diff <prior_head_sha>..<current_pr_head> --name-only`.
3. If every path returned is exactly `.ai/tickets/<ticket-id>/review.md` or `.ai/tickets/<ticket-id>/state.json` for the current ticket, the prior pass is **current under the review-record exemption** — do not re-gate it.
4. If any other path appears, continue to the finalization-record exemption check before declaring the pass stale.

**Exemption — finalization-record-only commits**: after all required reviewer passes and required security/specialist review gates have accepted the implementation PR head, an orchestrator closeout commit does **not** invalidate those approvals when every changed path since the accepted head is limited to finalization records for the current ticket and project-level closeout ledgers.

Allowed finalization-record paths:
- `.ai/tickets/<ticket-id>/finalize.md`
- `.ai/tickets/<ticket-id>/state.json`
- `docs/agent-backlog.md`
- `docs/exec-plans/ticket-change-log.md`
- `docs/exec-plans/as-built.md`
- `docs/exec-plans/build-cost.md`
- `docs/exec-plans/review-feedback-tracker.md`

**How to evaluate the finalization-record exemption**:
1. Confirm every required review pass and required security/specialist gate accepted the implementation PR head before the orchestrator closeout commit was created.
2. Run `git diff <accepted_implementation_head>..<current_pr_head> --name-only`.
3. If every path is in the allowed finalization-record list for the current ticket, the prior approvals are **current under the finalization-record exemption**.
4. If any other path appears, the prior approvals are **stale** — request fresh review before continuing.

**Why these exemptions exist**: every reviewer's acceptance commit and every gate-check commit advances the PR HEAD. Without the review-record exemption, the strict "accept current head SHA" rule causes an infinite ping-pong loop on prerequisite-style PRs whose only content is ticket records — every reviewer's record commit invalidates every prior pass acceptance. Without the finalization-record exemption, required orchestrator closeout ledger commits can invalidate the already accepted implementation and create an endless closeout-review loop.

**Discipline required for reviewers**: keep your acceptance/finding record commits scoped strictly to the current ticket's `review.md` and `state.json`. If you need to update the backlog, a parent ticket's state, another ticket's state, or any other file, the review-record exemption does not apply. Plan your record commit so it does not bundle unrelated changes.

**Discipline required for orchestrator finalization**: keep closeout commits scoped strictly to the allowed finalization-record paths. After pushing a finalization-record-only closeout commit, re-fetch PR metadata, verify the path allowlist, rerun required workflow/document checks, and merge without creating another non-exempt commit. If the closeout must touch any non-allowed path, route back to review before merge.

**What the exemptions never relax**: any commit that touches application code, tests, dependencies, migrations, runtime configuration, security-sensitive configuration, generated app artifacts, product behavior documentation, parent-ticket state, other tickets' state, or any file outside the applicable exemption allowlist still triggers the stale-head gate. Both reviewer passes must independently accept the new content unless the orchestrator documents and enforces an intentionally narrower re-review path.

**Policy promotion boundary**: finalization may add or update `docs/exec-plans/review-feedback-tracker.md` under the finalization-record exemption. Promotion of feedback into active architecture contracts, taste invariants, validation policy, lint configuration, scripts, or other enforceable project policy is not finalization-record-only work; handle it as reviewed ticket scope or split it into a follow-up workflow/policy ticket.

**Implementer's own fixup commits**: when the implementer returns from `changes_requested` and pushes a fixup commit, those changes are by definition artifact changes (code, evidence, validation). Neither exemption applies; the implementer must reset both required passes to pending for the new PR head.

## Prerequisite assessment
During Planning Pass, the orchestrator must check whether the ticket depends on anything outside the current repo that Codex cannot complete alone. Common examples:
- software or CLIs installed on the machine
- local or remote services being reachable
- credentials, secrets, certificates, or approvals
- databases, storage accounts, Azure resources, or other infrastructure being provisioned
- manual configuration steps the human must perform

Decision rule:
- If the dependency is already available and easy to verify, record it and continue with the main ticket.
- If the dependency requires meaningful human or external work, create one or more prerequisite sub-tickets and keep the parent ticket blocked until they are complete.
- If the dependency can be handled inside the main ticket without human or external action, do not split it out.

## Prerequisite sub-ticket rules
Prerequisite sub-tickets are a kind of sub-ticket with a human-assisted implementation loop. They follow the same two-phase review routing as specialist sub-tickets: `orchestrator -> implementer -> reviewer pass 1 -> reviewer pass 2 -> orchestrator`. Their defining characteristic is the human-assisted loop inside the implementer pass, not a different routing.

- Use the parent ticket ID plus the `PREREQ` infix and a zero-padded numeric suffix, for example `TKT-002.PREREQ-01`.
- Set `ticket_type = prerequisite` and `execution_mode = human_assisted` in `state.json`.
- Give the sub-ticket a concrete capability outcome such as "Reachable development PostgreSQL database and verified DATABASE_URL", not just a guessed implementation method such as "Install PostgreSQL".
- Record:
  - the parent ticket it unblocks
  - the exact human action required
  - the exact verification step the implementer will run
  - the unblock condition for the parent ticket
- The implementer holds the ticket during the human-assisted loop (see next section). When the prerequisite is verified, the implementer commits the verification record (`implement.md` + updated `state.json`, alongside any setup scripts or docs), pushes the branch, opens a PR to `main`, and hands to reviewer pass 1.
- Both reviewer passes review the PR diff in every case. When the prerequisite produced only the verification record, that record is the reviewable artifact; reviewers approve if the recorded command(s), observed output, and human-reported evidence are sufficient to demonstrate the unblock condition, and request changes otherwise.
- There is no "no repo changes, skip PR" path for prerequisite tickets. The verification record is itself a committable artifact, so every reviewer-routed ticket produces a PR for the required review passes and the orchestrator to merge.

## Human-assisted prerequisite loop
Use this loop for environment-only prerequisite tickets that require collaboration with the human.

- The orchestrator creates the child ticket and hands it to the implementer with a capability-oriented objective, candidate paths when known, and the unblock condition.
- The implementer starts by asking the smallest useful set of short questions needed to choose a path, unless one path is already clearly the best low-risk option.
- The implementer recommends one concrete path, explains why it fits the current machine or access constraints, and guides the human one step at a time.
- After each human step, the implementer runs the smallest practical verification command(s), then either:
  - continues with the next guided step, or
  - declares the prerequisite verified complete.
- While the human still has an ordinary next step to perform, keep the ticket `stage=implementing`, `next_actor=implementer`, and treat it as an active human-assisted loop rather than a blocked ticket.
- If a prerequisite ticket returns to orchestrator too early under older wording, the orchestrator should reopen it to the implementer instead of leaving it parked in `blocked`.
- Only route back to orchestrator when the prerequisite is verified complete or when a true blocker is reached.

## True blocker definition for prerequisite tickets
Use `blocked` only when the implementer cannot reasonably continue the guided loop. Examples:
- the human lacks required permissions or approvals
- all viable setup paths are unavailable or rejected
- the environment still fails after guided attempts and the next step is no longer clear
- an external dependency is unavailable in a way the implementer cannot work around or help the human progress further

Waiting for the human to do the next clearly-described setup step is not, by itself, a blocker.

## Prompt packet guidance for prerequisite tickets
For prerequisite sub-tickets, add these extra fields when useful:
- `ticket_type`
- `execution_mode`
- `waiting_on`
- `completion_rule`
- `true_blocker_definition`
- `first_questions`

These fields do not need to be global requirements for every ticket, but they should be present when they materially improve prerequisite execution quality.

## Specialist sub-tickets

When a ticket includes work that benefits from a specific agent or skill set, the orchestrator spawns a specialist sub-ticket during Planning Pass. Specialist sub-tickets follow the full two-phase review cycle: `orchestrator -> implementer -> reviewer pass 1 -> reviewer pass 2 -> orchestrator`. Prerequisite sub-tickets follow the same routing (see Prerequisite sub-ticket rules above).

### When to spawn a specialist sub-ticket
- The orchestrator identifies during Planning Pass that part of the ticket's scope falls into a specialist domain (see Common specialists below).
- The work is separable; it can be built and reviewed independently from the rest of the ticket.
- A different agent or tool would produce meaningfully better results for that slice.

If the specialist work is trivial or tightly coupled to the rest of the ticket, keep it in the parent ticket and note the specialist recommendation in the acceptance criteria instead.

### Specialist sub-ticket ID convention
Use the parent ticket ID plus a role infix and zero-padded suffix:
- `TKT-003.UI-01` - first UI sub-ticket for TKT-003
- `TKT-003.SEC-01` - first security sub-ticket for TKT-003
- `TKT-003.UI-02` - second UI sub-ticket for TKT-003

The infix makes the sub-ticket type self-describing at a glance alongside prerequisite sub-tickets (`TKT-003.PREREQ-01`).

### Specialist sub-ticket state.json
Set the `specialist` field when creating the sub-ticket:
```json
"ticket_type": "specialist",
"parent_ticket": "TKT-003",
"specialist": {
  "type": "ui",
  "skill": "$ui-specialist",
  "agent": "claude",
  "reason": "Frontend page layout and interactive components"
}
```

### Routing
- Specialist sub-tickets follow the full review cycle: `orchestrator -> implementer -> reviewer pass 1 -> reviewer pass 2 -> orchestrator`.
- The `specialist.agent` field is a routing signal to the human; it tells you which tool or agent to run the implementer pass in. It is not automated dispatch.
- The specialist role itself is resolved from `specialist.type` using the Specialist invocation table. When a reviewer requests changes, the reviewer must hand back to that specialist role rather than a generic implementer prompt. Keep `next_actor = implementer`, but write the visible prompt target and Prompt Packet as the specialist skill, for example `next_skill: $sec-specialist`.
- `specialist.skill` is the durable skill invocation to use for handoffs. If it is missing on older tickets, derive it from `specialist.type` using the Specialist invocation table and include it in the next Prompt Packet.
- The parent ticket stays blocked until the specialist sub-ticket is complete.
- The orchestrator records the parent/specialist relationship in both tickets.

### Review expectations for specialist sub-tickets
- All specialist sub-tickets go through both required reviewer passes.
- For visual specialist types (UI, A11Y), the acceptance criteria should include a human visual review step; the human launches the UI and confirms the result before reviewers mark it accepted.
- Either reviewer can request changes like any normal ticket.

### Common specialists

| Type | ID Infix | Default Agent | Typical Scope | Extra Acceptance Criteria |
|------|----------|---------------|---------------|--------------------------|
| UI / Frontend | `UI` | Claude | Page layout, components, styling, responsive design, animations, theming | Human visual review in browser; responsive check on mobile/tablet breakpoints |
| Accessibility | `A11Y` | Claude | ARIA attributes, keyboard navigation, screen reader support, colour contrast, focus management | Human visual review; automated a11y audit (e.g. axe, Lighthouse) |
| Data / API | `DATA` | Any | Database models, migrations, API endpoints, query optimization, data validation | Schema validation; API contract tests |
| Performance | `PERF` | Any | Profiling, caching, bundle size, lazy loading, query optimization, memory leaks | Before/after benchmark or measurement |
| Security implementation | `SEC` | Any | Auth flows, input sanitization, secrets management, CSRF/XSS/SQLi prevention, dependency audit | Security-focused implementation validation; automated scan if available |
| Infrastructure | `INFRA` | Any | CI/CD pipelines, Docker, deployment configs, cloud resources, environment setup | Successful deployment or dry-run; config validation |
| Testing | `TEST` | Any | Test strategy, integration tests, E2E test suites, test fixtures, coverage gaps | Tests pass; coverage meets threshold if defined |
| Observability | `OBS` | Any | Structured logging, error reporting, metrics, tracing, log aggregation and retention | Representative logs emitted at each level; error path captured; no secrets/PII in output |

**Default Agent** is a recommendation, not a hard rule. Override it based on your own experience with each tool. "Any" means either agent handles this well — pick based on availability and preference.

### Specialist invocation

Each specialist role is defined once in `.roles/<role>.md` and registered with each tool via thin wrappers. The orchestrator writes the prompt baton addressed to the specialist, and the human invokes it in the appropriate tool.

| Type | Invoke as | Canonical role file |
|------|-----------|---------------------|
| UI / Frontend | `$ui-specialist` | `.roles/ui-specialist.md` |
| Accessibility | `$a11y-specialist` | `.roles/a11y-specialist.md` |
| Data / API | `$data-specialist` | `.roles/data-specialist.md` |
| Performance | `$perf-specialist` | `.roles/perf-specialist.md` |
| Security implementation | `$sec-specialist` | `.roles/sec-specialist.md` |
| Security review gate | `$sec-reviewer` | `.roles/sec-reviewer.md` |
| Infrastructure | `$infra-specialist` | `.roles/infra-specialist.md` |
| Testing | `$test-specialist` | `.roles/test-specialist.md` |
| Observability | `$obs-specialist` | `.roles/obs-specialist.md` |

The wrappers live at `.claude/agents/<role>.md` (Claude) and `.agents/skills/<role>/SKILL.md` (Codex). Each wrapper is a thin shell that registers the role with its tool and points back to the canonical file.

The orchestrator writes `## Next Agent Prompt (<Specialist Name>)` in `orchestrator.md`. The specialist looks for its named section, or falls back to `## Next Agent Prompt (Implementer)` if not found.

Reviewers use the same mapping when handing changes back on specialist sub-tickets:
- normal or prerequisite ticket: `## Next Agent Prompt (Implementer -- when CHANGES REQUESTED)`, `next_skill: $implementer`
- specialist ticket: `## Next Agent Prompt (<Specialist Name> -- when CHANGES REQUESTED)`, `next_skill: <specialist invocation from the table>`

### Adding new specialist types
To add a new specialist type:
1. Choose a short uppercase infix (2-5 characters).
2. Add a row to the Common specialists table and the Specialist invocation table in this file.
3. Write the canonical role content at `.roles/<name>-specialist.md`. Use an existing `.roles/<type>-specialist.md` as the template — follow `.roles/implementer.md` for the base workflow and add domain-specific guidance.
4. Create thin wrapper files at `.claude/agents/<name>-specialist.md` and `.agents/skills/<name>-specialist/SKILL.md` that register the role with each tool and point back to the canonical file. For reviewer-style gate roles, use a clear reviewer name such as `.roles/sec-reviewer.md` with matching Claude and Codex wrappers.
5. Add the prompt baton mapping to the orchestrator's Specialist prompt baton section (in `.roles/orchestrator.md`).

### Prompt packet guidance for specialist sub-tickets
For specialist sub-tickets, add these extra fields to the prompt packet when useful:
- `specialist.type`
- `specialist.skill`
- `specialist.agent`
- `specialist.reason`
- `visual_review_required` (boolean, for UI/A11Y types)
- `human_review_steps` (what the human should check visually)

## Branch lifecycle
- Every ticket must have a dedicated branch recorded in `state.json.branch`. If it is missing, the orchestrator derives one from the ticket id and title before handoff.
- Prerequisite sub-tickets also get their own dedicated branch under the same rule.
- Planning Pass must create or switch to the ticket branch before the implementer starts work. Prefer branching from updated `main` when the worktree is clean enough to do so safely.
- If local changes make branch checkout unsafe, stop and record the exact blocker instead of forcing a checkout or overwriting work.
- All implementation and review work happens on the ticket branch, not on `main`.
- The implementer creates the PR to `main` after implementation and validation are complete. The PR stays open through all required review passes and fix loops.
- Finalization Pass is not complete until the orchestrator has confirmed every required review pass is current for the PR head under the review-record exemption rule before closeout, committed any final closeout changes, re-validated that those pass approvals are still current after any new commits under either the review-record or finalization-record exemption, checked for unresolved blocking GitHub reviews/comments/checks, merged the fully approved PR, and returned the local checkout to updated `main`.
- If branch protection dismisses stale approvals after new commits, or if a required review pass's recorded `head_sha` differs from the current PR head AND the delta is neither review-record-only nor finalization-record-only, the orchestrator must request fresh review before merging.
- Closeout commits routinely touch `docs/agent-backlog.md`, `finalize.md`, and execution-plan ledgers. These are covered only by the finalization-record exemption after all required implementation/security review gates have accepted the implementation PR head. If closeout touches any path outside the finalization-record allowlist, request fresh review before merging.
- If merge, re-review, approval, or local `main` sync cannot complete, the orchestrator must report the exact blocker and treat finalization as incomplete.

## Prompt baton rule
- Read upstream handoff file and find `## Next Agent Prompt (...)`.
- That section must include `### Prompt Packet (required)` with all fields listed in `state.json.prompt_handoff.required_fields`.
- Implementer handoff packets should include the review risk plan, validation contract, implementation risk handoff, validation evidence, PR URL, and current PR head SHA when known.
- Reviewer handoff packets should include `review.current_pass`, required review pass status, current PR head SHA, and whether the next reviewer or orchestrator is the intended next actor.
- Reviewer handoff packets that request changes should also include `next_skill`. For specialist sub-tickets, include `specialist.type`, `specialist.skill`, `specialist.agent`, and `specialist.reason` so a human can type "Proceed" and the AI can resolve the concrete specialist from ticket state instead of using the generic implementer.
- If complete: execute it as the default brief.
- If missing/incomplete: use `state.json` + role rules, and explicitly log missing fields.
- At handoff: write/update the next role's prompt with a complete Prompt Packet.

## Universal "Proceed" routing
When the human types only a minimal continuation prompt, the agent must route from ticket state before doing role-specific work. Treat these prompts as equivalent, case-insensitively and with surrounding punctuation ignored: `Proceed`, `Continue`, `Progress`, `Next action`, `Go ahead`, `Carry on`, `Keep going`, `Resume`, `Next`, `Do it`, and close variants that contain no new substantive instruction. This applies at every workflow point, including planning, implementation, prerequisite loops, reviewer fix loops, review pass 2, finalization, and specialist sub-tickets.

1. Locate the active ticket:
   - Prefer the ticket whose `state.json.branch` matches the current git branch.
   - If no branch match is available, inspect non-final `.ai/tickets/*/state.json` files and prefer tickets with `next_actor` set and `stage` not in a completed/finalized state.
   - If exactly one plausible active ticket remains, report that ticket and continue. If multiple plausible active tickets remain, stop and ask the human which ticket to proceed with.
2. Read the ticket state and upstream prompt sources:
   - Always read `.ai/tickets/<ticket-id>/state.json`.
   - Read any existing `.ai/tickets/<ticket-id>/orchestrator.md`, `implement.md`, `review.md`, and `finalize.md`.
   - Prefer the newest relevant `## Next Agent Prompt (...)` section addressed to the resolved role. If several match, choose by state: `changes_requested` uses `review.md`; active human-assisted implementation uses `implement.md`; `implemented` or `reviewing` uses `implement.md` or `review.md` according to `review.current_pass`; `review_accepted` uses `review.md`; `blocked` uses `implement.md` unless the ticket is already handed to orchestrator; `planned` uses `orchestrator.md` or the upstream architect/orchestrator prompt.
3. Resolve the skill or role from the Prompt Packet first, then ticket state:
   - If the selected Prompt Packet has `next_skill`, use it.
   - If `next_actor = implementer` and `ticket_type = specialist`, use `state.json.specialist.skill` when present, otherwise map `state.json.specialist.type` through the Specialist invocation table.
   - If `next_actor = implementer` without specialist metadata, use `$implementer`.
   - If `next_actor = reviewer` and `state.json.review.current_pass` is `security-review` or the current required pass names `$sec-reviewer`, use `$sec-reviewer`; otherwise use `$reviewer` and `state.json.review.current_pass`.
   - If `next_actor = orchestrator`, use `$orchestrator`.
   - If `next_actor = architect`, use `$architect`.
4. Load and follow the resolved skill or role instructions before acting. If the current chat was opened under a different role, switch behavior to the resolved role for this turn and state the switch briefly.
5. If the required skill cannot be resolved, or the prompt and `state.json` disagree in a way that would change workflow routing, stop and report the missing or conflicting routing fields instead of guessing.

## Validation
- Run the smallest relevant validation required by the ticket's validation contract.
- For prerequisite tickets, validation may be environment verification rather than repo tests.
- If skipped, state exactly what was not run, why it was skipped, and why the remaining evidence is still sufficient.
- Distinguish product failures from tooling/environment failures. A failed agent tool, MCP server, browser, SDK/engine, fixture, credential, sandbox, display, observability backend, or comparable runtime capability is evidence of an attempted check, not evidence that changed behavior passed. Required validation remains unsatisfied until an equivalent fallback passes, the skip is explicitly accepted with residual risk, or a prerequisite/follow-up resolves the missing capability.
- Reviewers and orchestrator may reject a handoff when validation evidence is missing, too narrow for the risk plan, or stale relative to the current PR head under the review-record exemption rule.

## Tooling fallback
If `apply_patch` blocks progress:
1. use repo-relative forward-slash paths
2. retry path correction once
3. switch to direct editing (PowerShell/Python)
4. report tooling blocker vs implementation blocker clearly

## Throughput and slice-size guidance
To preserve quality under higher agent throughput:
- prefer the smallest independent slice that can complete in one implementation pass and one review cycle
- split tickets when validation scope becomes broad or changes span multiple independent subsystems
- prefer sequential sub-tickets when a single large change would blur risk ownership

Recommended ticket metrics (record when available in ticket state/finalization notes):
- planning-to-PR lead time
- review turnaround per required pass
- changes-requested loop count
- first-pass merge-ready rate

See `docs/workflow/throughput-and-slicing.md` for a concise operator checklist.


## Security review trigger policy
Security is risk-based by default. The standard review workflow remains two required passes, but the orchestrator must apply `docs/workflow/security-review.md` during Planning Pass and add a `$sec-specialist` implementation sub-ticket, a `$sec-reviewer` security review gate, or both for security-sensitive slices. Projects with high compliance or threat exposure may opt into a mandatory third security pass, but the template default is risk-based to avoid unnecessary latency for low-risk tickets.

## Template-first architecture contracts
Harness architecture tickets should improve the reusable template rather than defining one universal downstream architecture. During project setup, the architect should generate `docs/design-docs/architecture-contract.md` from `docs/design-docs/architecture-contract-template.md`, adapting layers, domains, allowed dependency edges, cross-cutting boundaries, and enforcement plans to the target project.

## Planned mitigations in risk planning
The orchestrator's human-facing risk section must pair each material foreseeable risk with planned mitigations. Implementers must treat those mitigations as part of the ticket scope, and reviewers must verify that the implementation and evidence respected them.

## Finalization knowledge-base updates
Finalization should update durable project knowledge, not only close the PR. In addition to backlog and ticket files, update `docs/exec-plans/ticket-change-log.md`, `docs/exec-plans/as-built.md` when actual built behavior or operational quirks changed, and `docs/exec-plans/build-cost.md` with the ticket cost rollup.

During finalization, inspect review findings, non-blocking observations, accepted-with-follow-up notes, repeated fix-loop causes, recurring validation gaps, and human comments for repeated-feedback candidates. If a pattern is evidence-backed and useful beyond a one-off PR, update `docs/exec-plans/review-feedback-tracker.md` under the finalization-record exemption. Do not promote one-off subjective preferences into durable rules. Promotion from tracker intake into generated downstream taste invariants, architecture contract guidance, structural dependency config, validation guidance, tests, lints, scripts, or scoped TODOs changes active project policy and must either be included in reviewed ticket scope before implementation review accepts or split into a follow-up workflow/policy ticket.


## Agent QA and application legibility
For runnable applications, validation contracts should prefer evidence that agents can collect and reviewers can inspect: app boot output, smoke checks, screenshots or videos for UI changes, console/log excerpts, and metrics/trace thresholds when available. Project-specific command names and artifact locations belong in `docs/workflow/agent-qa.md`; tickets should reference those commands rather than inventing one-off QA steps.
