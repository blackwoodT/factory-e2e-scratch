# Factory Operator Guide

How to run the automated ("Dark Factory") loop that
`docs/workflow/automation-blueprint.md` designed. The factory replaces the
human typing "Proceed" with an event-driven GitHub Actions loop; the state
machine itself is unchanged. Ticket state in `.ai/tickets/<id>/state.json`
stays authoritative, every gate from `workflow-reference.md` and
`docs/workflow/review-gates.md` still applies, and **nothing merges without
your PR approval** (the MVP human merge gate).

## Mental model

One workflow, `factory-dispatch.yml`, runs one step per cycle:

1. Read `.ai/factory.json` (config + runtime) and `.ai/tickets/*/state.json`
   (overlaying the active ticket branch, where in-flight state lives).
2. `scripts/factory/dispatch.py` decides exactly one next step from
   `next_actor`/`stage`/`review.current_pass` — the mechanized version of
   Universal "Proceed" routing.
3. Either run one agent pass (Claude or Codex, headless, bounded by
   `--max-turns` and a tool allow-list), or open a "Factory needs you" issue
   and push a phone notification, or do nothing (paused/disabled/idle).
4. After every agent pass: append the run's tool-reported cost to the ticket
   ledger, run `validate_ticket_state.py` + `check_workflow_docs.py`
   (fail closed: invalid state pauses the factory and notifies you), kick the
   required PR checks, refresh the dashboard, and chain the next cycle via
   `repository_dispatch`.

| Trigger | What it does |
|---|---|
| `workflow_dispatch` | Start/kick the loop manually (GitHub Mobile → Actions → Factory dispatch → Run workflow; tick `resume` to clear a pause) |
| `repository_dispatch` (`factory-step`) | Self-chaining: one pass ends, the next begins |
| `schedule` (every 30 min) | Auto-resume after `paused_until`, catch stalls |
| `issues` (opened/labeled) | A `Build request` issue dispatches the architect |
| `issue_comment` | Your reply on a gate issue feeds the next agent run (teleoperated PREREQ loop) and carries `/factory` commands |
| `pull_request_review` | Your PR approval unblocks finalization |

Only repository collaborators' issues/comments/approvals are acted on;
everything else is ignored.

## Arming a project (per-project, one-time)

The template ships the factory **inert**: `.ai/factory.json` has
`"enabled": false` and the `FACTORY_ENABLED` repository variable is unset, so
nothing runs until you finish all of these steps in the *project* repo
(never arm the template repo itself):

1. **Stamp + push the project** per `docs/workflow/new-project-setup.md`, and
   apply `docs/workflow/github-settings.md` (branch protection with the
   `check-workflow-docs` and `check-ticket-state` required checks — the
   factory relies on GitHub enforcing the merge gates).
2. **Claude auth**: on your machine run `claude setup-token`, then add the
   output as the `CLAUDE_CODE_OAUTH_TOKEN` Actions secret
   (Settings → Secrets and variables → Actions → New repository secret).
   This uses your Claude subscription.
3. **Notifications**: pick a private, hard-to-guess ntfy topic name (it acts
   as a password), subscribe to it in the ntfy phone app, and add it as the
   `NTFY_TOPIC` secret. A full self-hosted URL also works.
4. **Review pass 2 (Codex)** — runtime detection, in the locked preference
   order, recorded here as built:
   1. `CODEX_AUTH_JSON` secret = the contents of `~/.codex/auth.json` from a
      machine logged in with your ChatGPT subscription (`codex login`).
      Tokens rotate, so expect to refresh this secret occasionally.
   2. else `OPENAI_API_KEY` secret = metered API key used only for review-2.
   3. else **neither secret set**: review-2 becomes a documented manual gate —
      the factory opens a "needs you" issue telling you to run review pass 2
      from your IDE per `.roles/reviewer.md`, push the record, and comment
      `/factory resume`.
   Which option is actually in force is visible per-run in the Codex step log;
   confirm your choice during the first end-to-end test and tune
   `review_2.codex_args` in `.ai/factory.json` if your Codex CLI version needs
   different flags.
5. **Enable flag**: edit `.ai/factory.json` → `"enabled": true` on a normal PR
   (in the project repo this is allowed; the template repo's CI forbids it).
6. **Kill switch**: create the repository **variable** `FACTORY_ENABLED` =
   `true` (Settings → Secrets and variables → Actions → Variables).
7. **Kick it**: Actions → Factory dispatch → Run workflow. The first cycle
   creates labels and the pinned dashboard issue.

Both keys must be on for anything to run: the `FACTORY_ENABLED` variable
(checked at every job start, flip to `false` to stop everything instantly)
and `factory.json.enabled` (checked by the dispatcher).

## Feeding it work

- **New project**: open a **Build request** issue (template provided). The
  architect turns it into a specification + roadmap + initial tickets on
  branch `factory/build-request-<n>` and opens a PR. Review and merge that PR
  from your phone; the next scheduled tick starts the first ticket's Planning
  Pass (or kick the dispatch workflow manually for an instant start).
  Only newly *opened* issues dispatch automatically (the form applies the
  label at creation; adding the label to an existing issue does nothing by
  itself). To run the architect on an existing issue, or to re-run it after
  a failure or new comments, comment `/factory build` on that issue.
- **Existing backlog**: any `planned`, `status: active` ticket on main is
  picked up automatically (lowest id first; in-flight tickets and their
  prerequisite/specialist sub-tickets take priority).

## When the factory needs you

You get an ntfy push pointing at a **"Factory needs you"** issue (one open
gate at a time) for: human-assisted prerequisite steps, blockers, visual
reviews, the finalization approval gate, manual review-2 (option 3 above),
invalid state, or agent failures. Resolve gates from your phone:

- **Question / prerequisite step**: reply on the gate issue; your comment is
  fed into the next agent run verbatim (the teleoperated loop). The agent
  posts its next question back on the same issue.
- **Finalization approval**: approve the PR in GitHub Mobile. Because the
  factory's commits are authored by `github-actions[bot]`, your own formal
  approval works even in single-account projects — no `LGTM` fallback needed
  for factory PRs. The approval event triggers the finalization merge pass.
  The gate only accepts a collaborator's (non-bot) approval of the PR's
  **current head** — if commits land after you approve, it asks you to
  approve again rather than merging content you haven't seen.
- **Commands** (comment on the gate issue): `/factory resume` (clear a pause
  and continue), `/factory pause` (manual stop), `/factory status` (refresh
  the dashboard).

## Pauses, budgets, auto-resume

- **Usage limits**: when an agent run fails with a subscription limit,
  `scripts/factory/limits.py` parses the reset time from the error text,
  writes `paused_until`, and you get a push ("auto-resumes after …"). The
  30-minute schedule resumes it; no action needed. Unparseable reset times
  fall back to `limits.default_pause_minutes` and retry.
- **Daily step budget**: `limits.max_steps_per_day` (default 40) caps agent
  passes per UTC day; hitting it pauses until midnight UTC (runaway
  protection).
- **Fix-loop guard**: at `limits.fix_loop_threshold` (default 3, mirroring
  `docs/workflow/review-gates.md`) the dispatcher routes the orchestrator's
  triage pass instead of another silent fix loop.
- **Fail closed**: invalid post-step state, uncommitted or unpushed agent
  work (a clean tree with local-only commits would be silently lost on the
  next checkout), or a non-limit agent failure pauses the factory
  indefinitely and opens a gate issue; fix, then `/factory resume`. If a
  pause's gate issue ever goes missing (e.g. the notification call failed),
  the next scheduled tick recreates it.

## Status on demand

- The pinned **Factory dashboard** issue shows factory state, steps used,
  gates waiting on you, every ticket's stage/next actor/PR, open PRs, and the
  cost rollup. It refreshes each cycle, daily, and via Actions → Factory
  status → Run workflow (or `/factory status`).
- Durable history stays where the workflow already keeps it:
  `docs/exec-plans/ticket-change-log.md`, `docs/agent-backlog.md`, and the PR
  list.

## Where state lives (and why there is a `factory-state` branch)

`.ai/factory.json` on main is reviewed configuration. The mutable `runtime`
block (pauses, step counters, active ticket, gate bookkeeping) is persisted by
the workflows as a single-file commit on the unprotected **`factory-state`**
branch, because `docs/workflow/github-settings.md` (canonical) protects main
behind PRs and required checks — the factory cannot and must not push runtime
flips to main. Dispatch always reads main's config overlaid with that branch's
runtime. Delete the branch any time to reset runtime state; never merge it.

## GITHUB_TOKEN quirks the design works around

- Bot pushes don't trigger `pull_request` workflows, so required checks would
  sit "Expected" forever; the dispatcher re-dispatches
  `workflow-docs-check.yml` (which has `workflow_dispatch` for this) on the
  branch head after each agent push.
- Bot-created events don't re-trigger workflows (no accidental recursion);
  self-chaining uses `repository_dispatch`, the documented exception.
- GitHub disables cron schedules in repos with no activity for 60 days; any
  manual run re-arms them.

## Safety rails recap

Kill switch at every job start; one step at a time (`concurrency: factory`);
per-day step budget; validators after every agent step with pause+notify on
failure; finding-triage policy and fix-loop guard enforced at the dispatcher
and orchestrator levels; human PR approval before any merge; least-privilege
workflow permissions; only collaborator input is trusted, and human text is
delimited in prompts as content, not instructions. Agent passes never bypass
the two-pass review or the state validator — the same CI that gates you gates
them.

## First end-to-end verification

Follow the blueprint's checklist (`automation-blueprint.md` § "First
end-to-end verification") in a **throwaway stamped repo**, never the template:
build-request issue → spec PR → TKT-000 light-tier ticket through
planning → implementation → review → dashboard/ntfy pushes → phone PR approval
→ finalization merge; then simulate a usage-limit pause/auto-resume and flip
the kill switch. Delete the throwaway repo afterwards.

## Troubleshooting

- **Nothing runs**: check `FACTORY_ENABLED` variable = `true`, `enabled: true`
  in `.ai/factory.json`, and the Actions tab for skipped runs.
- **Paused and you don't know why**: dashboard issue → "Factory state", or
  read `.ai/factory.json` on the `factory-state` branch (`pause_reason`).
- **PR can't merge, checks "Expected"**: run `workflow-docs-check.yml`
  manually against the ticket branch (Actions → Workflow docs check → Run
  workflow → select the branch).
- **Gate issue answered but nothing happened**: replies only count from
  collaborators on the *open* gate issue; otherwise use `/factory resume`.
- **Wrong/stale runtime**: delete the `factory-state` branch and re-kick.
