# Prerequisite Ticket Policy

## When to create prerequisite sub-tickets
Create `TKT-XXX.PREREQ-YY` when work depends on external/human setup (credentials, installs, access, infra, approvals).

## Parent ticket behavior
- Parent ticket remains blocked until prerequisite completion is verified.
- Prerequisite ticket follows full review cycle like any ticket.

## Implementer verification record
When prerequisite is complete, commit a clear verification record including:
- what was done
- commands/checks executed
- observed output
- human-reported evidence when relevant

See `workflow-reference.md` for full lifecycle and routing.
