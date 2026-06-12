# Automation Blueprint ("Dark Factory")

Status: **implemented.** The operator guide is `docs/workflow/automation.md` — how to arm a
project, feed it work, resolve gates from your phone, and troubleshoot. This document remains the
design record for the loop. The state machine itself does not change — automation only replaces
the human typing "Proceed", and the factory ships inert (enabling it is a per-project step).

## Goals

- Requirements in → agents run the full ticket lifecycle unattended.
- Phone push (ntfy.sh) whenever a human is needed: blockers, PREREQ steps, visual reviews,
  failures, usage limits.
- Human resolves gates from the phone: replying to a GitHub issue, approving/merging a PR in
  GitHub Mobile.
- Subscription usage limits pause the factory; it resumes automatically when the window resets.
- On-demand status: where the project is, what remains, all PRs and what each did.

## Architecture

One dispatcher workflow is the loop; repo state stays the single source of truth.

```
"Build request" issue ─▶ architect run ─▶ spec + roadmap PR ─▶ human approves (phone)
                                                   │
        ┌──────────────  factory-dispatch.yml  ◀───┘
        ▼
 read .ai/factory.json + .ai/tickets/*/state.json
 pick active ticket → read next_actor (the existing "Proceed" routing, mechanized)
        │
        ├─ orchestrator / implementer / specialist / review-1
        │      → Claude Code action job (subscription OAuth token, bounded --max-turns,
        │        allow-listed tools) → commits + pushes → state validated → re-dispatch
        ├─ review-2 → Codex job (see decision point) → same loop
        ├─ finalization → orchestrator merges only after every gate passes
        │        (MVP keeps a human PR approval as the final gate)
        ├─ blocked / PREREQ step / visual review / invalid state
        │        → upsert "Factory needs you: <ticket> — <reason>" issue + ntfy push → pause
        └─ usage-limit error → write paused_until → ntfy push → cron resumes after reset
```

### Triggers on the dispatcher

| Trigger | Purpose |
|---|---|
| `workflow_dispatch` | Start/kick the factory manually (works from GitHub Mobile) |
| `repository_dispatch` | Self-chaining: one role pass ends → next begins (with loop budget) |
| `schedule` (cron ~30 min) | Auto-resume after `paused_until`, catch stalls |
| `issue_comment` | Your phone reply to a "needs you" issue feeds the next agent run (this is the human-assisted PREREQ loop, teleoperated) |
| `pull_request_review` | Your approval unblocks finalization |

### Agent jobs

- Claude roles run headless with the thin prompt: "You are <role>. Read `.roles/<role>.md` and the
  active ticket under `.ai/tickets/<id>/`. Execute exactly one pass, update ticket state per
  `workflow-reference.md`, commit and push." Tool allow-lists and `--max-turns` bound each pass.
- After every agent job: `python scripts/validate_ticket_state.py` runs. Invalid state pauses the
  factory and notifies the human (fail closed) instead of looping on garbage.
- Usage capture is automatic per the automation-first rule in `workflow-reference.md` § AI usage:
  the job writes the run's reported cost into `state.json.ai_usage.entries`.

### Planned files

- `.github/workflows/factory-dispatch.yml` — the loop described above
- `.github/workflows/factory-status.yml` — on-demand + per-cycle status digest
- `scripts/factory/dispatch.py` — routing, kill switch, budgets, paused_until
- `scripts/factory/notify.py` — ntfy push + "Factory needs you" issue upsert
- `scripts/factory/limits.py` — detect usage-limit errors, compute resume time
- `.ai/factory.json` — factory state: `enabled`, `paused_until`, loop counters, active ticket
- `.github/ISSUE_TEMPLATE/build-request.yml` — the "requirements in" entry point
- `docs/workflow/automation.md` — operator guide written at implementation time

### Secrets and variables (set once, never committed)

| Name | What it is |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | From `claude setup-token` on your machine (uses your Claude subscription) |
| `OPENAI_API_KEY` | Only if the review-2 decision lands on metered Codex (see below) |
| `NTFY_TOPIC` | Your private ntfy.sh topic name (subscribe to it in the ntfy phone app) |
| `FACTORY_ENABLED` (variable) | Kill switch checked at the start of every job |

## Status on demand

- **Dashboard issue**: a pinned issue regenerated each cycle and by `factory-status.yml` on
  demand — tickets by stage, the active ticket and `next_actor`, gates waiting on you, backlog
  remaining, cost rollup from the ledgers.
- **What was done**: the GitHub PR list plus `docs/exec-plans/ticket-change-log.md` (linked from
  the dashboard) — both already exist in the workflow.
- Optional: a `@claude` mention workflow for free-form questions ("what remains on this project?").

## Safety rails (MVP defaults)

- Concurrency group: one agent step at a time, one active ticket at a time.
- Per-day step budget; the loop refuses to re-dispatch past it (runaway protection).
- Fix-loop guard: the dispatcher refuses to start another fix loop once
  `state.json.review.fix_loop_count` reaches the threshold; the orchestrator's triage pass
  (`docs/workflow/review-gates.md` § "Automated finding triage and loop guard") decides
  merge/defer/dismiss for advisory findings, or escalates to your phone when genuinely blocked —
  the structural answer to "what if the bot reviewer never stops finding little things".
- The factory never merges without every required pass current **and** human PR approval (MVP);
  relax to auto-merge per-project later if desired.
- Minimal workflow permissions (`contents: write`, `issues: write`, `pull-requests: write` only
  where needed).
- Invalid ticket state = pause + notify, never continue.
- Kill switch: set `FACTORY_ENABLED=false` and every job exits at its first step.

## Decision point: review pass 2 in CI

`required_passes[*].tool` is configuration (see `review-tiers.md` and `workflow-reference.md`
§ Two-phase review). Cross-model review is the goal; options in preference order:
1. Codex CLI/action in CI authenticated with the ChatGPT subscription — verify at build time.
2. Codex with a metered `OPENAI_API_KEY` used only for review-2 (review passes are small).
3. Keep review-2 as a semi-manual phone/PC step while everything else automates.

## Usage limits and auto-resume

Subscription limit errors are text, not structured data: the job parses the failure message for the
reset time, writes `paused_until` into `.ai/factory.json`, pushes an ntfy notification ("factory
paused until ~HH:MM"), and stops re-dispatching. The scheduled trigger re-checks every cycle and
resumes automatically once past `paused_until` — no human action needed, matching the "picks back
up when limits reset" requirement.

## First end-to-end verification (human watching)

Run a dummy `TKT-000` light-tier ticket through the whole loop: build-request issue → planning →
implementation (trivial change) → review pass(es) → dashboard update → ntfy pushes received on the
phone → human PR approval from GitHub Mobile → finalization merge. Then simulate a usage-limit
failure to watch pause/auto-resume, and flip the kill switch to confirm everything stops.
