# CLAUDE.md

## Purpose
Claude-specific entry point for this repo's agent workflow.

## Start here
Read `AGENTS.md` first. It is the single top-level workflow entry map and points to the canonical workflow reference, role files, and policy indexes.

## Canonical behavior
- Detailed workflow logic lives in `workflow-reference.md`.
- Role behavior lives in `.roles/<role>.md`.
- Claude agent wrappers live in `.claude/agents/` and should remain thin pointers to `.roles/<role>.md`.
- Codex skill wrappers live in `.agents/skills/` and should also remain thin pointers to `.roles/<role>.md`.

## Context discipline
- Keep replies beginner-friendly, practical, and concise.
- Prefer summaries over large dumps.
- Start a fresh chat after merge, branch change, or major scope change.
