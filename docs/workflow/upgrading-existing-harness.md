# Upgrading an Existing Harness Repo

Purpose: help an existing downstream repository adopt the completed Harness workflow after it was already running an older version of this template.

This is a stack-neutral upgrade path. It does not assume an application language, framework, package manager, CI system, QA tool, browser, container runtime, database, API shape, import system, validation library, or observability vendor.

## Plain-language answer

To get the completed workflow running in an existing repo, do not blindly overwrite the repo with this template. Create an upgrade branch, copy or merge the harness scaffold, preserve project-specific generated docs and active ticket state, run the workflow docs check, then ask the architect/orchestrator to refresh the project-specific contracts and current ticket handoff.

Use the latest template as a source of workflow files, not as proof that every downstream project must adopt every optional artifact.

## What changed across the Harness TODOs

The ten Harness improvements added these capabilities:

1. risk-based validation evidence matrix,
2. fail-closed QA command adapters for boot, smoke, bounded logs, and teardown,
3. optional browser critical-journey evidence examples,
4. optional ephemeral observability examples,
5. optional `state.json.validation.evidence` guidance,
6. generated downstream architecture contracts,
7. configurable structural dependency lint scaffold,
8. boundary validation invariant guidance,
9. downstream taste invariant rule-pack template,
10. repeated review-feedback tracker and promotion loop.

Most of these are scaffolds or prompts. They become active downstream policy only after the project generates or configures project-specific docs, commands, contracts, or checks.

## Upgrade safety rules

- Work on a dedicated branch, for example `harness-upgrade`.
- Preserve existing app code, generated project docs, active tickets, backlog, and project context.
- Do not overwrite generated downstream policy files with template examples.
- Do not mark optional checks as passing just because the new scaffold exists.
- Leave unavailable QA, structural lint, observability, browser, taste, or boundary-validation checks as skipped with reason and residual risk until the project configures them.
- Do not create fake review-feedback tracker entries during upgrade.

## Files to preserve in the downstream repo

Preserve these if they already contain project-specific content:

| Path | Why preserve it |
|---|---|
| `.Context/` | Project specifications, roadmaps, and human-provided context. |
| `docs/agent-backlog.md` | Project backlog and ticket progress. |
| `.ai/tickets/<ticket-id>/` except `TEMPLATE/` | Historical and active ticket state. |
| `docs/design-docs/architecture-contract.md` | Generated project-specific architecture contract. |
| `docs/design-docs/taste-invariants.md` | Generated project-specific taste policy, if selected. |
| `docs/design-docs/architecture-boundaries.json` | Project-specific structural dependency config, if configured. |
| `docs/exec-plans/as-built.md` | Implemented-reality notes. |
| `docs/exec-plans/build-cost.md` | Project cost rollups. |
| `docs/exec-plans/ticket-change-log.md` | Project ticket history. |
| `docs/exec-plans/tech-debt-tracker.md` | Project debt backlog. |
| `docs/exec-plans/review-feedback-tracker.md` | Project feedback history, if it already exists. |

If any of these files are still template stubs, refresh them during architect/orchestrator bootstrap rather than copying fake universal content.

## Files usually safe to update from this template

These are harness scaffold files. Existing downstream repos should usually update or merge them from the latest template:

| Path | Notes |
|---|---|
| `AGENTS.md` | Keep short; preserve project-specific map entries only if still useful. |
| `CLAUDE.md` | Keep as a thin pointer to `AGENTS.md` so top-level workflow routing is maintained in one place. |
| `ARCHITECTURE.md` | Keep as a top-level map, not a project-specific contract. |
| `workflow-reference.md` | Canonical workflow state-machine behavior. |
| `README.md` | Operator overview; merge with project README if the repo also has app README content. |
| `.roles/` | Role behavior for architect, orchestrator, implementer, reviewer, security reviewer, and specialists. |
| `.agents/skills/` | Skill wrappers and specialist workflows. |
| `.claude/agents/` | Claude agent definitions when used. |
| `.ai/tickets/TEMPLATE/` | Ticket scaffold for future tickets; do not overwrite active ticket folders. |
| `docs/workflow/` | Workflow policy docs; merge project-specific command notes carefully. |
| `docs/design-docs/*-template.md` and `architecture-boundaries-template.json` | Templates only; do not replace generated downstream files. |
| `docs/exec-plans/review-feedback-tracker.md` | Add if missing; leave empty unless real repeated feedback exists. |
| `scripts/check_workflow_docs.py` | Documentation integrity check. |
| `scripts/qa/` | Fail-closed QA adapters; downstream projects wire them to real commands. |
| `scripts/architecture/` | Structural dependency checker and fixtures. |
| `.github/workflows/workflow-docs-check.yml` | Optional CI doc integrity check. |

## Step-by-step upgrade

### 1. Start clean and create an upgrade branch

```bash
git status --short
git checkout -b harness-upgrade
```

If the repo has active uncommitted app changes, commit or stash them first. Do not mix a harness upgrade with feature work.

### 2. Bring in the latest template as a comparison source

Use whichever source path your team has for this template: a clone, a release branch, or a downloaded copy. The examples below use `../AI_Repository` as the template source.

```bash
TEMPLATE_ROOT=../AI_Repository
```

On Windows PowerShell:

```powershell
$TemplateRoot = '..\AI_Repository'
```

### 3. Review what the bootstrap manifest would copy

The starter manifest is the canonical list of scaffold paths copied into a new repo:

```text
.ai/templates/repo-starter/manifest.json
```

For an existing repo, use it as a checklist, not as permission to overwrite everything. The bootstrap script supports `-DryRun`, which is useful for seeing the intended scaffold paths:

```powershell
pwsh "$TemplateRoot/scripts/bootstrap_agent_system.ps1" `
  -TargetRepoRoot . `
  -ProjectName "Factory E2E" `
  -ProjectType "Throwaway factory verification" `
  -SystemSpecificationFile "<ProjectName>-Specification.md" `
  -ImplementationRoadmapFile "<ProjectName>-Roadmap.md" `
  -DryRun
```

Do not run the bootstrap script with `-Force` against an existing repo unless you intentionally want to overwrite scaffold files and have reviewed the diff first.

### 4. Stage the latest scaffold, then merge intentionally

Prefer a manual merge or a temporary staging directory. The goal is to compare the latest harness scaffold against the existing repo before overwriting anything.

Create a local staging copy of the template scaffold:

```bash
rm -rf .harness-template-update
mkdir -p .harness-template-update
cp -R "$TEMPLATE_ROOT/AGENTS.md" .harness-template-update/
cp -R "$TEMPLATE_ROOT/ARCHITECTURE.md" .harness-template-update/
cp -R "$TEMPLATE_ROOT/workflow-reference.md" .harness-template-update/
cp -R "$TEMPLATE_ROOT/README.md" .harness-template-update/
cp -R "$TEMPLATE_ROOT/.roles" .harness-template-update/
cp -R "$TEMPLATE_ROOT/.agents" .harness-template-update/
cp -R "$TEMPLATE_ROOT/.claude" .harness-template-update/
cp -R "$TEMPLATE_ROOT/.ai/tickets/TEMPLATE" .harness-template-update/TICKET_TEMPLATE
cp -R "$TEMPLATE_ROOT/docs/workflow" .harness-template-update/docs-workflow
cp -R "$TEMPLATE_ROOT/docs/design-docs" .harness-template-update/docs-design-docs
cp -R "$TEMPLATE_ROOT/docs/exec-plans" .harness-template-update/docs-exec-plans
cp -R "$TEMPLATE_ROOT/scripts/qa" .harness-template-update/scripts-qa
cp -R "$TEMPLATE_ROOT/scripts/architecture" .harness-template-update/scripts-architecture
cp "$TEMPLATE_ROOT/scripts/check_workflow_docs.py" .harness-template-update/check_workflow_docs.py
```

Then compare and copy only the reviewed scaffold files into the repo. Example comparisons:

```bash
diff -ru .roles .harness-template-update/.roles || true
diff -ru docs/workflow .harness-template-update/docs-workflow || true
diff -ru .ai/tickets/TEMPLATE .harness-template-update/TICKET_TEMPLATE || true
```

When applying updates, merge carefully instead of overwriting project-specific generated files. In particular, preserve generated downstream docs such as `docs/design-docs/architecture-contract.md`, `docs/design-docs/taste-invariants.md`, `docs/design-docs/architecture-boundaries.json`, project-specific notes in `docs/workflow/agent-qa.md`, active ticket folders, and exec-plan history.

Typical scaffold files to copy after review include:

```bash
mkdir -p .roles .agents .claude scripts docs/workflow docs/design-docs docs/exec-plans
cp -R .harness-template-update/.roles/. .roles/
cp -R .harness-template-update/.agents/. .agents/
cp -R .harness-template-update/.claude/. .claude/
cp -R .harness-template-update/scripts-qa scripts/qa
cp -R .harness-template-update/scripts-architecture scripts/architecture
cp .harness-template-update/check_workflow_docs.py scripts/check_workflow_docs.py
cp .harness-template-update/docs-design-docs/architecture-contract-template.md docs/design-docs/
cp .harness-template-update/docs-design-docs/architecture-boundaries-template.json docs/design-docs/
cp .harness-template-update/docs-design-docs/taste-invariants-template.md docs/design-docs/
cp .harness-template-update/docs-exec-plans/review-feedback-tracker.md docs/exec-plans/review-feedback-tracker.md
```

For `AGENTS.md`, `ARCHITECTURE.md`, `workflow-reference.md`, `README.md`, `docs/workflow/`, and `.ai/tickets/TEMPLATE/`, prefer a reviewed merge because existing downstream repos may have local routing notes, command names, or active workflow assumptions.

### 5. Update the ticket template, not active ticket folders

Refresh future-ticket scaffolding:

```bash
mkdir -p .ai/tickets
rm -rf .ai/tickets/TEMPLATE.new
cp -R "$TEMPLATE_ROOT/.ai/tickets/TEMPLATE" .ai/tickets/TEMPLATE.new
```

Compare `.ai/tickets/TEMPLATE.new` with the existing `.ai/tickets/TEMPLATE`, then replace or merge the template after reviewing changes:

```bash
diff -ru .ai/tickets/TEMPLATE .ai/tickets/TEMPLATE.new || true
```

Do not overwrite active historical ticket folders. For active tickets created before the upgrade, migrate only what the current ticket needs, such as missing review pass records, validation contract fields, or finalization prompts.

### 6. Generate or refresh project-specific contracts

After copying template files, run an architect or orchestrator bootstrap pass to generate or refresh project-specific docs. The top-level `README.md` bootstrap checklist is the operator-facing list of surfaces that must be filled during new-project setup or harness upgrade.

At minimum, verify:

- `docs/design-docs/architecture-contract.md` from `architecture-contract-template.md`,
- `docs/design-docs/taste-invariants.md` only if the project selects durable taste rules,
- `docs/design-docs/architecture-boundaries.json` only if dependency-boundary rules are ready for mechanical enforcement,
- `docs/exec-plans/review-feedback-tracker.md` only with real prior repeated feedback, otherwise leave it as an empty scaffold,
- project-specific command names, artifact paths, safe environments, auth/test-data strategy, and browser/UI journey commands in `docs/workflow/agent-qa.md`,
- project-specific required/optional/skipped validation evidence in `docs/workflow/validation-evidence-matrix.md` and active ticket validation contracts.

Do not leave example rows as if they are active project policy.

### 7. Wire QA adapters or leave them fail-closed

The template provides fail-closed adapters for:

- `qa:boot`,
- `qa:smoke`,
- `qa:logs`,
- `qa:stop`.

If the project already has safe local/dev commands, wire the adapters to those commands or replace the adapters. For browser-capable apps, also add a project command such as `qa:ui` using Playwright, Chrome DevTools Protocol, an MCP browser server, or equivalent tooling so agents can capture screenshots/traces even when an IDE browser plugin is unavailable. If the primary operator environment is Windows, add PowerShell or task-runner wrappers rather than relying only on POSIX shell scripts.

If commands are not ready, leave adapters fail-closed and record QA/browser evidence as skipped with reason and residual risk when a ticket selects it.

### 8. Upgrade active tickets conservatively

For an active pre-upgrade ticket:

1. Keep its existing `state.json` as authoritative.
2. Add missing `review.required_passes` only if the ticket is entering review and the field is absent.
3. Add optional `validation.evidence` only when useful; older tickets may omit it.
4. Add the new finalization feedback-promotion check to `finalize.md` if the ticket is close to finalization.
5. Do not rewrite old ticket history just to match the newest template.

### 9. Validate the upgraded harness

Run:

```bash
python scripts/check_workflow_docs.py
git diff --check
```

If structural dependency lint is configured for the project, also run the project-specific command, for example:

```bash
python scripts/architecture/check_dependencies.py --config docs/design-docs/architecture-boundaries.json --root .
```

If `architecture-boundaries.json` is missing or still template-only, do not treat that as a project failure unless the active ticket selected dependency-boundary enforcement. Record a skip with reason instead.

### 10. Commit the harness upgrade separately

```bash
git status --short
git add <reviewed harness files>
git commit -m "Upgrade agent workflow harness"
```

Keep this PR separate from application feature work so reviewers can focus on workflow behavior and avoid mixing harness changes with product changes.

## Starter prompt for upgrading an existing repo

Use this prompt after copying or merging the scaffold:

```text
You are the orchestrator for an existing repo that has just upgraded its agent workflow harness.

Do an upgrade bootstrap pass only:
- read AGENTS.md, ARCHITECTURE.md, workflow-reference.md, docs/workflow/index.md, and docs/workflow/upgrading-existing-harness.md
- inspect whether docs/design-docs/architecture-contract.md exists and is project-specific
- inspect whether docs/design-docs/taste-invariants.md exists and is selected project policy or should remain absent
- inspect whether docs/design-docs/architecture-boundaries.json exists and is configured or should remain absent
- inspect whether docs/exec-plans/review-feedback-tracker.md exists and contains only real evidence-backed entries
- inspect current active ticket state, if any, without rewriting historical ticket records
- update only the smallest necessary project-specific docs and current ticket handoff
- run python scripts/check_workflow_docs.py
- report skipped optional checks with reason and residual risk
```

## Common upgrade mistakes

| Mistake | Why it is risky | Safer alternative |
|---|---|---|
| Running bootstrap with `-Force` and no diff review | Can overwrite generated project contracts, ticket history, or backlog. | Use `-DryRun`, copy scaffold paths intentionally, and review diffs. |
| Copying template examples into active policy | Makes the downstream repo look like a fake generic app. | Generate project-specific docs or mark unknowns as TBD. |
| Rewriting all old tickets | Destroys useful history and creates noise. | Update only active tickets that need new fields for the current workflow stage. |
| Enabling structural lint with template config | The checker should fail closed because template config is not project policy. | Generate `architecture-boundaries.json` only after project-specific boundaries are ready. |
| Treating QA adapters as proof of runnable QA | The adapters are placeholders until wired downstream. | Configure safe local/dev commands or record skip-with-reason. |
| Promoting every review comment into taste policy | Creates brittle and noisy rules. | Use the review-feedback tracker as candidate intake and promote only repeated or high-impact patterns. |
