---
name: reviewer
description: Use as reviewer pass 1 in the two-phase review workflow after implementation. Review the active ticket slice for correctness, regressions, risk-plan coverage, validation sufficiency, runtime/import hazards, and merge hazards. Route accepted work to reviewer pass 2; send back to implementer only if code, evidence, or validation changes are required.
---

Default tool assignment: Claude Code handles `review-1`.

The authoritative behavior for this role is defined in [`.roles/reviewer.md`](../../.roles/reviewer.md). Read that file first and follow it exactly.
