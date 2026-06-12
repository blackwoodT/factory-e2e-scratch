# AGENTS.md

## Purpose
Short entry map for agent workflow. Use progressive disclosure: start here, then read only the relevant deeper docs.

## Execution-critical rules
- Keep scope tight; avoid unrelated refactors.
- One ticket per branch.
- Full flow: `orchestrator -> implementer -> reviewer pass 1 -> reviewer pass 2 -> orchestrator` (standard tier; `state.json.review.required_passes` is authoritative — see `docs/workflow/review-tiers.md`).
- `state.json` is authoritative for ticket state and routing.
- Main-ticket prerequisite dependencies must be split into explicit `TKT-XXX.PREREQ-YY` tickets.
- Do not merge/finalize until every required review pass is current for PR head or valid under the review-record/finalization-record exemptions (stale-head gate logic in `workflow-reference.md`).

## Start here (map)
- Top-level domain map: `ARCHITECTURE.md`
- Canonical workflow logic: `workflow-reference.md`
- Workflow policy index: `docs/workflow/index.md`
- Role behavior: `.roles/architect.md`, `.roles/orchestrator.md`, `.roles/implementer.md`, `.roles/reviewer.md`, `.roles/sec-reviewer.md`, and specialist role files

## Knowledge domains
- Design docs: `docs/design-docs/index.md`
- Product specs: `docs/product-specs/index.md`
- Execution plans: `docs/exec-plans/index.md`
- Generated references: `docs/generated/index.md`
- Technical/tool references: `docs/references/index.md`

## Ticket contract
Ticket folder: `.ai/tickets/<ticket-id>/`
Required files:
- `state.json`
- `orchestrator.md`
- `implement.md`
- `review.md`
- `finalize.md`

## Operator routing hints
- If the prompt is only “Proceed/Continue/Next action”, resolve active ticket from branch + `state.json.next_actor` and continue with the corresponding role skill.
- If prompt packet fields are missing, fallback to `state.json` + role rules and explicitly log missing fields.

## Documentation hygiene
- Doc integrity check: `python scripts/check_workflow_docs.py`
- CI job: `.github/workflows/workflow-docs-check.yml`
