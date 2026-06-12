# Review Tiers

One state machine covers all tickets. A tier never changes routing logic; it only changes what the
orchestrator writes into `state.json.review.required_passes` during Planning Pass. Gates downstream
(reviewer pass selection, stale-head checks, finalization) already read that list, so they work for
any tier without special cases.

## Tiers

| Tier | required_passes content | Use for |
|------|------------------------|---------|
| `light` | `review-1` only | Genuinely no-runtime-risk slices (see eligibility below) |
| `standard` (default) | `review-1` + `review-2` | Everything not explicitly light or high-risk |
| `high-risk` | `review-1` + `review-2` + `security-review` | Slices that trigger `docs/workflow/security-review.md` |

## Light tier eligibility

A ticket may be planned as `light` only when **every** expected changed path is:
- documentation or prose (`*.md` content that does not define agent workflow policy),
- code comments only, or
- non-executable content/config that cannot change runtime behavior, build output, dependencies,
  or security posture (for example copy text, README sections, changelog entries).

Never light, regardless of size:
- source code, tests, migrations, schema, scripts, CI/workflow files
- dependency manifests or lockfiles
- security-relevant configuration (auth, headers, CORS, secrets wiring, permissions)
- workflow policy files in a harness/template repo (`workflow-reference.md`, `.roles/`, `.claude/`,
  `.agents/`, `docs/workflow/`): these change agent behavior, which is runtime behavior here
- anything the orchestrator is unsure about — **when in doubt, use `standard`**

## Rules

- The orchestrator selects the tier during Planning Pass, records the tier and a one-line reason in
  `orchestrator.md`, and initializes `required_passes` to match. The default is `standard`.
- The default initialization rule elsewhere in the workflow ("initialize with `review-1` and
  `review-2` when missing") is the `standard` tier; `light` must be an explicit planning decision,
  never a fallback.
- On a `light` ticket the single reviewer pass is the final pass: on acceptance it follows the
  existing "all required passes current" path (formal `APPROVE` or the `LGTM — approved by
  reviewer` fallback, `stage = review_accepted`, hand to orchestrator).
- If implementation turns out to touch anything outside light eligibility, the implementer or
  reviewer must say so; the orchestrator upgrades the ticket to `standard` by appending `review-2`
  to `required_passes` (pending, current PR head) before finalization. Tier upgrades are always
  allowed; downgrades after planning are not.
- Finalization is pass-list-driven: the orchestrator gate verifies every pass recorded in
  `required_passes` — however many the tier selected — and accepts the final-pass `APPROVE` or
  `LGTM — approved by reviewer` fallback from whichever pass is last. It must never demand a
  `review-2` record on a ticket whose tier never required one.
- `scripts/validate_ticket_state.py` enforces that `required_passes` is non-empty and well-formed;
  tier content is a planning judgement reviewed like any other planning output.
