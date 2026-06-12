#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_AGENTS_LINES = 100

required_files = [
    ROOT / 'AGENTS.md',
    ROOT / 'ARCHITECTURE.md',
    ROOT / 'README.md',
    ROOT / '.gitignore',
    ROOT / 'workflow-reference.md',
    ROOT / 'docs/workflow/index.md',
    ROOT / 'docs/workflow/roles.md',
    ROOT / 'docs/workflow/review-gates.md',
    ROOT / 'docs/workflow/prerequisites.md',
    ROOT / 'docs/workflow/validation-contracts.md',
    ROOT / 'docs/workflow/validation-evidence-matrix.md',
    ROOT / 'docs/workflow/agent-qa.md',
    ROOT / 'docs/workflow/qa-command-adapters.md',
    ROOT / 'docs/workflow/browser-critical-journeys.md',
    ROOT / 'docs/workflow/ephemeral-observability.md',
    ROOT / 'docs/workflow/structural-dependency-lint.md',
    ROOT / 'docs/workflow/boundary-validation-invariants.md',
    ROOT / 'docs/workflow/throughput-and-slicing.md',
    ROOT / 'docs/workflow/doc-hygiene.md',
    ROOT / 'docs/workflow/harness-template-setup.md',
    ROOT / 'docs/workflow/upgrading-existing-harness.md',
    ROOT / 'docs/workflow/security-review.md',
    ROOT / 'docs/workflow/review-tiers.md',
    ROOT / 'docs/workflow/github-settings.md',
    ROOT / 'docs/workflow/automation-blueprint.md',
    ROOT / 'docs/workflow/new-project-setup.md',
    ROOT / 'docs/agent-backlog.md',
    ROOT / '.ai/tickets/TEMPLATE/state.json',
    ROOT / 'docs/design-docs/index.md',
    ROOT / 'docs/design-docs/architecture-contract-template.md',
    ROOT / 'docs/design-docs/architecture-boundaries-template.json',
    ROOT / 'docs/design-docs/taste-invariants-template.md',
    ROOT / 'docs/exec-plans/index.md',
    ROOT / 'docs/exec-plans/tech-debt-tracker.md',
    ROOT / 'docs/exec-plans/ticket-change-log.md',
    ROOT / 'docs/exec-plans/harness-template-todo.md',
    ROOT / 'docs/exec-plans/review-feedback-tracker.md',
    ROOT / 'docs/exec-plans/build-cost.md',
    ROOT / 'docs/exec-plans/as-built.md',
    ROOT / 'docs/generated/index.md',
    ROOT / 'docs/product-specs/index.md',
    ROOT / 'docs/references/index.md',
    ROOT / 'docs/references/openai-harness-engineering.md',
    ROOT / 'scripts/qa/boot.sh',
    ROOT / 'scripts/qa/smoke.sh',
    ROOT / 'scripts/qa/logs.sh',
    ROOT / 'scripts/qa/stop.sh',
    ROOT / 'scripts/qa/lib.sh',
    ROOT / 'scripts/qa/qa.py',
    ROOT / 'scripts/claude_session_tokens.py',
    ROOT / 'scripts/codex_session_tokens.py',
    ROOT / 'scripts/architecture/check_dependencies.py',
    ROOT / 'scripts/architecture/fixtures/structural-dependencies/architecture-boundaries.fixture.json',
    ROOT / 'scripts/validate_ticket_state.py',
    ROOT / '.ai/schema/ticket-state.schema.json',
    ROOT / 'docs/workflow/automation.md',
    ROOT / 'scripts/factory/dispatch.py',
    ROOT / 'scripts/factory/notify.py',
    ROOT / 'scripts/factory/limits.py',
    ROOT / 'scripts/fixtures/factory/logs/expectations.json',
    ROOT / '.ai/factory.json',
    ROOT / '.github/workflows/factory-dispatch.yml',
    ROOT / '.github/workflows/factory-status.yml',
    ROOT / '.github/ISSUE_TEMPLATE/build-request.yml',
]

errors = []

for p in required_files:
    if not p.exists():
        errors.append(f"Missing required workflow doc: {p.relative_to(ROOT)}")


required_text = {
    ROOT / 'docs/design-docs/architecture-contract-template.md': [
        'Template-only warning',
        'Generation checklist',
        'Boundary validation invariant',
        'Explicit unknowns / TBDs',
        'architecture-boundaries-template.json',
        'taste-invariants-template.md',
    ],
    ROOT / 'docs/design-docs/taste-invariants-template.md': [
        'Template-only warning',
        'Rule promotion checklist',
        'Enforcement status labels',
        'Evidence expectations',
        'Examples only',
    ],
    ROOT / 'docs/workflow/harness-template-setup.md': [
        'Architecture contract bootstrap',
        'Do not commit a generic `architecture-contract.md` to this template repository',
        'architecture-boundaries-template.json',
        'boundary-validation-invariants.md',
        'taste-invariants-template.md',
        'review-feedback-tracker.md',
        'upgrading-existing-harness.md',
    ],
    ROOT / 'docs/workflow/upgrading-existing-harness.md': [
        'Upgrade safety rules',
        'Files to preserve',
        'Step-by-step upgrade',
        'Common upgrade mistakes',
    ],
    ROOT / 'docs/exec-plans/review-feedback-tracker.md': [
        'Template-only warning',
        'Do not promote one-off feedback',
        'Promotion destinations',
        'Finalization loop',
    ],
}

for p, markers in required_text.items():
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    for marker in markers:
        if marker not in text:
            errors.append(f"Missing required marker in {p.relative_to(ROOT)}: {marker}")

exec_index = ROOT / 'docs/exec-plans/index.md'
if exec_index.exists() and 'review-feedback-tracker.md' not in exec_index.read_text(encoding='utf-8'):
    errors.append('docs/exec-plans/index.md must link review-feedback-tracker.md')

if (ROOT / 'AGENTS.md').exists():
    lines = (ROOT / 'AGENTS.md').read_text(encoding='utf-8').splitlines()
    if len(lines) > MAX_AGENTS_LINES:
        errors.append(f"AGENTS.md exceeds {MAX_AGENTS_LINES} lines ({len(lines)} found)")

for role_path in sorted((ROOT / '.roles').glob('*.md')):
    text = role_path.read_text(encoding='utf-8')
    if 'codex resume --all' in text:
        errors.append(
            f"Active role file must not instruct agents to use `codex resume --all`: {role_path.relative_to(ROOT)}"
        )


def _contains_legacy_estimated_usd(value):
    if isinstance(value, dict):
        if 'estimated_usd' in value:
            return True
        return any(_contains_legacy_estimated_usd(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_legacy_estimated_usd(child) for child in value)
    return False


for state_path in sorted((ROOT / '.ai' / 'tickets').glob('*/state.json')):
    try:
        state = json.loads(state_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid ticket state JSON in {state_path.relative_to(ROOT)}: {exc}")
        continue
    if _contains_legacy_estimated_usd(state.get('ai_usage', {})):
        errors.append(
            f"Use ai_usage.entries[*].estimated_cost_usd, not legacy estimated_usd, in {state_path.relative_to(ROOT)}"
        )

link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
check_links_in = [
    ROOT / 'AGENTS.md',
    ROOT / 'ARCHITECTURE.md',
    ROOT / 'README.md',
    ROOT / 'workflow-reference.md',
    ROOT / 'docs/workflow/index.md',
]

for p in check_links_in:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    for target in link_pattern.findall(text):
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        rel = target.split('#', 1)[0].strip()
        if not rel:
            continue
        path = (p.parent / rel).resolve()
        if not path.exists():
            errors.append(f"Broken link in {p.relative_to(ROOT)} -> {target}")



# The repo-starter stamps these snapshots into new projects; if they drift from
# the root versions, downstream repos bootstrap with stale workflow policy.
starter_synced_files = [
    'AGENTS.md',
    'CLAUDE.md',
    'workflow-reference.md',
    '.Context/ExampleSpecification.md',
]
if (ROOT / '.ai/templates/repo-starter').is_dir():
    for name in starter_synced_files:
        root_copy = ROOT / name
        starter_copy = ROOT / '.ai/templates/repo-starter' / name
        if not starter_copy.exists():
            errors.append(
                f"Starter snapshot missing: .ai/templates/repo-starter/{name} "
                "(downstream bootstrap would lose this policy file)"
            )
            continue
        if not root_copy.exists():
            errors.append(f"Root file missing for starter snapshot pair: {name}")
            continue
        if root_copy.read_text(encoding='utf-8') != starter_copy.read_text(encoding='utf-8'):
            errors.append(
                f"Starter snapshot is stale: .ai/templates/repo-starter/{name} differs from {name}. "
                f"Re-sync it (copy the root file over the starter copy)."
            )

# Starter integrity checks apply only in the template repo. Downstream
# projects receive this checker but intentionally not the starter itself,
# so the absence of .ai/templates/repo-starter/ means: skip, not fail.
starter_root = ROOT / '.ai/templates/repo-starter'
manifest_path = starter_root / 'manifest.json'
if starter_root.is_dir() and not manifest_path.exists():
    errors.append('Starter folder exists but is missing manifest.json: .ai/templates/repo-starter/')
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    copied_destinations = {item.get('destination') for item in manifest.get('copy_items', [])}
    required_destinations = {
        'AGENTS.md',
        '.gitignore',
        'ARCHITECTURE.md',
        'workflow-reference.md',
        'docs/workflow',
        'docs/design-docs',
        'docs/exec-plans',
        'docs/generated',
        'docs/product-specs',
        'docs/references',
        'docs/agent-backlog.md',
        'scripts/check_workflow_docs.py',
        'scripts/claude_session_tokens.py',
        'scripts/codex_session_tokens.py',
        'scripts/validate_ticket_state.py',
        'scripts/fixtures',
        'scripts/qa',
        'scripts/architecture',
        '.ai/schema',
        '.github/workflows/workflow-docs-check.yml',
        '.github/pull_request_template.md',
        # Factory files are product, not template traces: every required file
        # above must reach stamped projects or their CI starts red.
        'scripts/factory',
        '.ai/factory.json',
        '.github/workflows/factory-dispatch.yml',
        '.github/workflows/factory-status.yml',
        '.github/ISSUE_TEMPLATE/build-request.yml',
    }
    for destination in sorted(required_destinations - copied_destinations):
        errors.append(f"Starter manifest does not copy required harness path: {destination}")



# The factory must ship inert: the template repo never runs itself, and every
# freshly stamped project starts disabled until its operator arms it
# (docs/workflow/automation.md). Template-repo-only check, following the
# starter-folder conditional pattern: downstream projects legitimately flip
# enabled=true, so the guard must not travel.
factory_path = ROOT / '.ai/factory.json'
if (ROOT / '.ai/templates/repo-starter').is_dir() and factory_path.exists():
    try:
        factory_config = json.loads(factory_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        factory_config = None
        errors.append(f"Invalid JSON in .ai/factory.json: {exc}")
    if isinstance(factory_config, dict) and factory_config.get('enabled') is not False:
        errors.append(
            'Template repo must ship the factory inert: .ai/factory.json "enabled" must be '
            'false (enabling is a per-project step; see docs/workflow/automation.md)'
        )


# Bootstrap engine self-test: dry-run a stamp so a broken engine or a manifest
# entry pointing at a missing source fails CI. Conditional on the starter
# folder because this checker also runs in downstream repos, which
# intentionally receive neither the starter nor the bootstrap engines —
# but in the template repo the engines are required, not optional.
bootstrap_script = ROOT / 'scripts/bootstrap_new_project.py'
if (ROOT / '.ai/templates/repo-starter').is_dir():
    if not bootstrap_script.exists():
        errors.append(
            'Template repo is missing the bootstrap engine: scripts/bootstrap_new_project.py '
            '(docs/workflow/new-project-setup.md depends on it)'
        )
    if not (ROOT / 'scripts/bootstrap_agent_system.ps1').exists():
        errors.append(
            'Template repo is missing the Windows bootstrap engine: scripts/bootstrap_agent_system.ps1'
        )
if bootstrap_script.exists() and not errors:
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as scratch:
        result = subprocess.run(
            [
                sys.executable, str(bootstrap_script),
                '--target', scratch,
                '--project-name', 'Selftest Project',
                '--project-type', 'Bootstrap dry-run self-test',
                '--spec-file', 'Selftest-Specification.md',
                '--roadmap-file', 'Selftest-Roadmap.md',
                '--dry-run',
            ],
            cwd=ROOT, text=True, capture_output=True,
        )
    if result.returncode != 0:
        errors.append(
            'Bootstrap dry-run self-test failed:\n' + result.stdout + result.stderr
        )


self_test_cmd = [
    sys.executable,
    str(ROOT / 'scripts/architecture/check_dependencies.py'),
    '--config',
    str(ROOT / 'scripts/architecture/fixtures/structural-dependencies/architecture-boundaries.fixture.json'),
    '--root',
    str(ROOT / 'scripts/architecture/fixtures/structural-dependencies'),
    '--expect-violation',
]
if not errors:
    import subprocess
    result = subprocess.run(self_test_cmd, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        errors.append(
            'Structural dependency fixture self-test failed:\n'
            + result.stdout
            + result.stderr
        )

if errors:
    print('\n'.join(errors))
    sys.exit(1)

print('Workflow docs check passed.')
