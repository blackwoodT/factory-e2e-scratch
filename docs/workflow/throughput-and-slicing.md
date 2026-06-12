# Throughput and Slicing Policy

## Default slice targets
- Prefer tickets that can be completed in one implementation pass and one review cycle.
- Prefer narrow scope with low file count and focused outcome.

## Split trigger guidance
Orchestrator should split or stage work when:
- expected change set crosses many subsystems
- validation surface becomes broad/non-atomic
- ticket likely requires multiple independent stakeholder decisions

## Suggested metrics (record in ticket state/finalize output)
- planning-to-PR lead time
- review turnaround per pass
- changes-requested loops per ticket
- merge-ready rate on first pass

Use metrics as a feedback loop to improve ticket sizing and review load.
