# Review Gates

## Required pass model
All reviewer-routed tickets require:
1. every pass listed in `state.json.review.required_passes`, set by the ticket's review tier
   (`standard`: reviewer pass 1 + reviewer pass 2; `light`: reviewer pass 1 only; see
   `review-tiers.md`)
2. any risk-triggered security review gate recorded in `state.json.review.required_passes`
3. orchestrator finalization

## Stale-head rule
A prior pass is stale when its recorded head SHA differs from the current PR head, unless the changed paths since that SHA satisfy one of the explicit workflow exemptions below.

### Review-record exemption
Reviewer bookkeeping does not stale prior acceptance when the only changes since the recorded SHA are review-record-only updates to the current ticket's:
- `.ai/tickets/<ticket-id>/review.md`
- `.ai/tickets/<ticket-id>/state.json`

### Finalization-record exemption
After all required reviewer passes and required security/specialist review gates have accepted the implementation PR head, orchestrator closeout bookkeeping does not stale those approvals when every changed path since the accepted implementation head is limited to finalization records:
- `.ai/tickets/<ticket-id>/finalize.md`
- `.ai/tickets/<ticket-id>/state.json`
- `docs/agent-backlog.md`
- `docs/exec-plans/ticket-change-log.md`
- `docs/exec-plans/as-built.md`
- `docs/exec-plans/build-cost.md`
- `docs/exec-plans/review-feedback-tracker.md`

This exemption is only for closeout records. It never covers source code, tests, dependencies, migrations, runtime configuration, security-sensitive configuration, generated app artifacts, product behavior documentation, parent/other ticket state, or enforceable policy changes.

If closeout review becomes necessary because the closeout diff escaped the allowlist, the orchestrator must not create another non-exempt closeout commit after that review accepts.

## Automated finding triage and loop guard

Automated reviewers (Codex Code Review, bots, linters-as-comments) are advisors, not gatekeepers.
This section prevents two failure modes: endless trickles of minor findings re-blocking every
merge, and fix loops that burn tokens without converging — both fatal in unattended operation.

### What actually blocks finalization
1. A formal `REQUEST_CHANGES` review from a **required pass** that has not been superseded.
2. **High-severity (P0/P1)** automated findings that are unresolved.
3. Failed or pending **required status checks**.
4. Missing approval proof (formal approve or the documented fallback comment).

Everything else — P2/P3 badges, style nits, unlabeled bot comments — is **advisory**: input to the
reviewers and the orchestrator, never an automatic merge block.

### Orchestrator triage authority
During finalization the orchestrator must disposition every open advisory finding, one of:
- `fix_now` — genuinely worth a fix loop; route back to the implementer.
- `deferred` — real but not blocking; record it in `deferred_follow_up`/backlog and reply on the
  PR thread so the record shows it was seen, then proceed to merge.
- `dismissed_false_positive` — the finding misreads the code or contradicts canonical workflow
  docs; reply on the PR thread with the concrete reason, record it in `finalize.md`, and proceed.

Dispositions are recorded in `finalize.md` (finalization-record exemption applies). The
orchestrator judges advisory findings against the canonical docs and the ticket's acceptance
criteria — an automated reviewer that mis-identifies a problem does not get a veto. Dismissals
must always carry a written reason; silent dismissal is never allowed. When dismissals start
repeating, record the pattern in `docs/exec-plans/review-feedback-tracker.md` so the noisy rule
gets fixed at the source.

### Fix-loop guard
- `state.json.review.fix_loop_count` counts `changes_requested` → implementer returns; the
  implementer increments it on each return.
- Reviewers must batch all findings for the current PR head into one pass, not dribble them across
  rounds.
- When the count reaches **3** (default; a project may tune it), the next changes-requested
  decision escalates instead of looping: the orchestrator triages the remaining findings and
  either bulk-dispositions advisory items and proceeds to the gate, or — if genuinely blocking
  issues remain — sets the ticket `blocked`, `waiting_on = human`, with a concise summary of what
  is left and a recommendation. In automated operation this is a notify-the-human stop, not
  another silent loop.
- Diminishing-returns rule: if a new round contains only advisory findings and the count is
  already ≥ 2, the orchestrator may bulk-triage instead of dispatching another fix loop.
- A human decision on a finding ("defer it", "dismiss it", "fix it") recorded on the PR or ticket
  is authoritative and ends triage debate for that finding.

## Finalization gate checklist
Before merge:
- both required reviewer passes and any risk-triggered security review gate are current for PR head, review-record-exempt, or finalization-record-exempt
- validation evidence exists and is sufficient
- no unresolved blocking findings in PR reviews/checks
- approval proof present (formal approve or fallback text)
- closeout diff path check was recorded when the finalization-record exemption is used

See `workflow-reference.md` for canonical gate logic.
