# Roles and Ownership (Summary)

## Core sequence
`architect -> orchestrator -> implementer -> reviewer pass 1 -> reviewer pass 2 -> orchestrator`

## Role intent
- **Architect**: project-start context synthesis and initial ticket roadmap.
- **Orchestrator**: planning pass, prerequisite triage, risk plan + validation contract, finalization gates.
- **Implementer**: artifact delivery, smallest relevant validation, PR creation, reviewer handoff evidence.
- **Reviewer pass 1 and pass 2**: independent PR review against risk plan + validation contract.
- **Security reviewer**: independent risk-triggered security review gate for security-sensitive slices; separate from the security implementation specialist.

## Detailed authority
The authoritative detailed ownership and routing behavior remains in `workflow-reference.md` and `.roles/*.md`.
