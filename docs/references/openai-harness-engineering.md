# OpenAI Harness Engineering Reference

Source: <https://openai.com/index/harness-engineering/>  
Published: 2026-02-11  
Purpose: local, short reference notes for template TODOs. Do not copy the article into this repo; use this as a navigational summary and follow the source link for full context.

## Key ideas to preserve
- **Map, not manual:** keep `AGENTS.md` short and use structured repo-local docs as the system of record.
- **Application legibility:** expose UI, logs, metrics, and traces so agents can validate behavior directly.
- **Agent QA loop:** agents should be able to boot the app, reproduce failures, capture before/after evidence, implement fixes, restart, and re-run validation.
- **Architecture constraints:** enforce boundaries mechanically with linters/structural tests rather than relying only on documentation.
- **Taste invariants:** promote repeated human review preferences into docs, lints, or tests.
- **Continuous cleanup:** treat entropy as expected and run recurring small cleanup/refactor/doc-gardening passes.

## How this applies to this template repo
This repository should encode reusable harness mechanisms, not one project's assumptions. Template work should produce:
- prompts that generate downstream project docs during bootstrap
- configurable scripts and examples instead of hard-coded stacks
- CI checks that verify structure and links
- optional QA/observability examples that projects can adopt when applicable

## Use this reference when working on
- `TKT-OBS-001` validation evidence matrix
- `TKT-QA-002` app boot/smoke/log capture templates
- `TKT-UI-003` browser-driven QA examples
- `TKT-OBS-004` local observability stack examples
- `TKT-WF-005` QA/observability artifacts in workflow state
- `TKT-ARCH-006` architecture contract generation
- `TKT-ARCH-007` structural dependency linting
- `TKT-ARCH-008` boundary validation invariant checks
- `TKT-TASTE-009` taste invariant rules
- `TKT-WF-010` review-feedback-to-rule-promotion loop
