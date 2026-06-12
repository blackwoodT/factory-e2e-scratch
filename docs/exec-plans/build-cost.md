# Build Cost

Purpose: roll up estimated AI/tooling cost by finalized ticket for project-level visibility.

## Update rule
The orchestrator finalization pass should append or update a row after recomputing `state.json.ai_usage.ticket_total_estimated_usd`.

## Cost entries

| Date | Ticket | Estimated cost (USD) | Confidence | Source notes |
|---|---|---:|---|---|

## Notes
- Costs are estimates, not billing records.
- Use `unknown` or `partial` confidence when tools do not expose complete usage.
