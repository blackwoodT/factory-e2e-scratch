# Design Docs Index

Status: `draft`  
Owner: `orchestrator`  
Last reviewed: `2026-05-27`

## Purpose
Catalog design beliefs and architecture decisions used by agents during planning and review.

## Bootstrap expectation
Downstream projects should generate `architecture-contract.md` from `architecture-contract-template.md` during the initial architect pass. The generated file is project-specific and should replace template examples with actual domains, boundaries, allowed dependencies, enforcement status, and explicit TBDs. Downstream projects should also generate `taste-invariants.md` from `taste-invariants-template.md` when selecting repeated human review preferences as durable project policy. This template repository keeps only the reusable templates unless a downstream project has been bootstrapped.

## Files
- `core-beliefs.md`
- `verification-status.md`
- `architecture-contract-template.md`
- `architecture-boundaries-template.json`
- `taste-invariants-template.md`
- `architecture-contract.md` (generated downstream during bootstrap; not required in this template repository)
- `taste-invariants.md` (generated downstream during bootstrap when project-specific taste invariants are selected; not required in this template repository)
