# New Project Setup (Using the Repo Starter)

How a human takes this template repo and starts a real project from it. The starter is
**copied, never generated**: a deterministic script reads
`.ai/templates/repo-starter/manifest.json` (the single source of truth for what new projects
receive), copies those files, and replaces five documented placeholders. No agent invents or
rewrites workflow content during bootstrap — that rule is what prevents template mutation.
Project-specific content (architecture contract, taste invariants, backlog entries, README) is
generated later by the **architect inside the new repo**, from the templates, where it belongs.

## Prerequisites
- Python 3.10+ (`python --version`) — used by the bootstrap script and the harness checks.
- Git, and a GitHub account that can create repositories.
- This template repo cloned locally (the bootstrap script runs from here).

## Step 1 — Create the empty project repository
On GitHub: New repository → name it → **no** README/.gitignore/licence initialization (the
starter provides files; an empty repo avoids merge noise). Clone it next to this template repo.

## Step 2 — Stamp the starter into it
From the template repo root, either engine works (same manifest, same result):

Cross-platform (recommended):
```bash
python scripts/bootstrap_new_project.py \
  --target ../my-project \
  --project-name "My Project" \
  --project-type "Internal operations web application" \
  --spec-file MyProject-Specification.md \
  --roadmap-file MyProject-Roadmap.md
```

Windows PowerShell alternative:
```powershell
.\scripts\bootstrap_agent_system.ps1 `
  -TargetRepoRoot '..\my-project' `
  -ProjectName 'My Project' `
  -ProjectType 'Internal operations web application' `
  -SystemSpecificationFile 'MyProject-Specification.md' `
  -ImplementationRoadmapFile 'MyProject-Roadmap.md'
```

Use `--dry-run` / `-DryRun` first if you want to preview. Spec/roadmap filenames must be
project-specific (`ExampleSpecification.md` is reserved as copied reference material). The
stamp seeds three stubs for the architect to replace: the specification, the roadmap, and a
minimal `README.md`.

## Step 3 — Verify the stamp
Inside the new repo, run the harness's own integrity checks — a correct stamp passes both:
```bash
python scripts/check_workflow_docs.py
python scripts/validate_ticket_state.py
```

## Step 4 — First commit, push, and GitHub settings
```bash
git add -A && git commit -m "Bootstrap agent workflow harness" && git push -u origin main
```
Then apply the branch-protection and repository settings from
`docs/workflow/github-settings.md` (require PRs; require the `check-workflow-docs` and
`check-ticket-state` status checks once they have run at least once).

## Step 5 — Write down what you want
Replace the contents of `.Context/<YourProject>-Specification.md` stub with your real
requirements in plain language: what the app should do, who uses it, constraints, non-goals.
Rough notes are fine — the architect's job is to turn them into a proper specification by
asking you clarifying questions. Use `.Context/ExampleSpecification.md` as a reference for the
level of detail that helps.

## Step 6 — Architect bootstrap (in the new repo)
Open your agent tool in the **new** repo and invoke `$architect`. Per
`docs/workflow/harness-template-setup.md`, it will interview you about requirements, then
generate the project-specific documents from the shipped templates:
- the full system specification and implementation roadmap (replacing the stubs)
- `docs/design-docs/architecture-contract.md` (from the template)
- `docs/design-docs/taste-invariants.md` and `architecture-boundaries.json` when applicable
- the first planned tickets under `.ai/tickets/` and the initial `docs/agent-backlog.md` entries

## Step 7 — Run the loop
Invoke `$orchestrator` for the first ticket's Planning Pass, then follow the normal cycle
(`orchestrator → implementer → reviewer pass 1 → reviewer pass 2 → orchestrator`), typing
`Proceed` to advance — or, once the automation in `docs/workflow/automation-blueprint.md` is
implemented and enabled for the project, let the factory drive and respond to its
notifications.

## What keeps the template and projects from drifting
- The manifest is the only copy list, and both bootstrap engines read it.
- CI in the template repo guards the starter: snapshot files are byte-compared against the
  root versions, manifest destinations are checked against a required list, and the bootstrap
  engine is dry-run on every docs-check.
- Never edit `.roles/`, `workflow-reference.md`, or other workflow policy per-project on a
  whim; harness improvements belong in the template repo, and existing projects adopt them via
  `docs/workflow/upgrading-existing-harness.md`.
