---
name: reviewer
description: Use as reviewer pass 2 in the two-phase review workflow after Claude Code reviewer pass 1 accepts the current PR head. Review the active ticket slice for correctness, regressions, risk-plan coverage, validation sufficiency, runtime/import hazards, and merge hazards. Route fully accepted work to orchestrator; send back to implementer only if code, evidence, or validation changes are required.
---

Default tool assignment: Codex IDE handles `review-2`.

The authoritative behavior for this role is defined in [`.roles/reviewer.md`](../../../.roles/reviewer.md). Read that file first and follow it exactly.
