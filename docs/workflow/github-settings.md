# GitHub Settings That Enforce the Workflow

The workflow's merge gates live in docs and agent behavior. These repository settings make GitHub
itself enforce them, so a confused agent (or human) cannot bypass the rules. Apply them once per
repository (harness template and every downstream project repo).

## Branch protection for `main`

GitHub web → **Settings → Branches → Add branch ruleset** (or classic "Add rule") for `main`:

1. **Require a pull request before merging** — blocks direct pushes to `main`. This is the
   mechanical version of "all implementation and review work happens on the ticket branch".
2. **Require status checks to pass before merging**, and select:
   - `check-workflow-docs` (docs integrity)
   - `check-ticket-state` (ticket state machine validity)
   Status checks appear in the picker only after they have run at least once on a PR.
3. **Require conversation resolution before merging** — unresolved review threads block merge,
   matching the finalization gate's "no unresolved blocking findings" rule.
4. **Block force pushes** and **restrict deletions** — protects history the ticket ledgers point at.
5. Optional, recommended once the automated factory runs: **Require approvals: 1** so a human
   approval (from the GitHub Mobile app if you like) is always the last gate before merge. Note the
   single-account caveat below.

## Single-account caveat

When the implementer and reviewer run under the same GitHub account, GitHub blocks formal
self-approval. The workflow's documented fallback is the PR comment `LGTM — approved by reviewer`.
If you enable "Require approvals", merging then needs a second account (or a GitHub App) to
approve, or you approve from your own second account. Until then, leave "Require approvals" off and
rely on the required status checks plus the workflow's recorded review passes.

## Repository settings worth setting once

- **Settings → General → Pull Requests**: enable "Automatically delete head branches" (keeps the
  branch list clean after finalization merges).
- **Settings → Actions → General → Workflow permissions**: set the default `GITHUB_TOKEN` to
  "Read repository contents" and grant write permissions per-workflow in the workflow file instead
  ("least privilege"; the automation blueprint relies on per-workflow `permissions:` blocks).
- **Settings → Secrets and variables → Actions**: this is where automation credentials will live
  (see `automation-blueprint.md`). Never commit tokens to the repo.

## Why this matters

The stale-head gate, two-pass review, and finalization checklist are only promises until GitHub
refuses to merge without them. Required status checks turn `scripts/validate_ticket_state.py` and
`scripts/check_workflow_docs.py` into hard gates: if an agent writes an illegal state transition or
breaks a workflow doc, the PR physically cannot merge.
