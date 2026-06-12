# Workflow Documentation Hygiene

## Monthly doc-gardening checklist
- remove or archive stale workflow docs
- verify links and section anchors
- prune duplicated policy text
- mark superseded guidance explicitly

## Lightweight CI checks (recommended)
- local/manual run: `python scripts/check_workflow_docs.py`
- broken link detection for `AGENTS.md`, `README.md`, `workflow-reference.md`, and `docs/workflow/*.md`
- required-doc presence check for files listed in `docs/workflow/index.md`
- template manifest presence checks so copied projects inherit the docs harness
- optional AGENTS length threshold warning to keep it as an index + critical constraints

## Ownership
Orchestrator owns backlog-level follow-up tickets for hygiene work.
