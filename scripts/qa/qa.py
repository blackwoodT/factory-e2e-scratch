#!/usr/bin/env python3
"""Cross-platform Agent QA adapter entrypoint (Windows/macOS/Linux).

Same contract as the POSIX adapters in this folder, for environments without a
POSIX shell (native Windows). One entrypoint covers all four adapter intents:

  python scripts/qa/qa.py boot
  python scripts/qa/qa.py smoke
  python scripts/qa/qa.py logs
  python scripts/qa/qa.py stop

Behavior contract (kept in sync with scripts/qa/lib.sh):
- reads the project-configured command from QA_BOOT_COMMAND / QA_SMOKE_COMMAND /
  QA_LOGS_COMMAND / QA_STOP_COMMAND
- refuses production targets unless QA_ALLOW_PRODUCTION=1 (exit 1)
- exits 2 when the adapter is not configured, so agents never mistake missing
  QA wiring for a passed check
- creates QA_ARTIFACT_DIR (default .ai/qa-artifacts) before running
- otherwise propagates the configured command's exit code
"""
import os
import subprocess
import sys

EXPECTED_OUTPUT = {
    'boot': (
        'qa:boot expected configured-command output:\n'
        '- target URL or endpoint, when applicable\n'
        '- PID, process id, container id, or equivalent runtime handle\n'
        '- log file or log query location'
    ),
    'smoke': (
        'qa:smoke expected configured-command output:\n'
        '- the representative route/API/CLI/job actually exercised\n'
        '- pass/fail signal with a bounded output summary'
    ),
    'logs': (
        'qa:logs expected configured-command output:\n'
        '- bounded recent log excerpt or query result (no unbounded dumps)\n'
        '- source location so reviewers can re-run the query'
    ),
    'stop': (
        'qa:stop expected configured-command output:\n'
        '- confirmation the booted target was stopped/cleaned up'
    ),
}


def main(argv):
    if len(argv) != 2 or argv[1] not in EXPECTED_OUTPUT:
        print(f"usage: python {argv[0]} {{boot|smoke|logs|stop}}", file=sys.stderr)
        return 2

    intent = argv[1]
    adapter_name = f"qa:{intent}"
    command_var = f"QA_{intent.upper()}_COMMAND"
    command_value = os.environ.get(command_var, '')
    environment = os.environ.get('QA_ENVIRONMENT', 'local')
    artifact_dir = os.environ.get('QA_ARTIFACT_DIR', '.ai/qa-artifacts')

    print(f"{adapter_name}: adapter starting")
    print(f"environment={environment}")
    print(f"artifact_dir={artifact_dir}")

    # Case-insensitive: QA_ENVIRONMENT=Production / PROD must also fail closed.
    if environment.lower() in ('production', 'prod', 'live') and os.environ.get('QA_ALLOW_PRODUCTION') != '1':
        print(f"{adapter_name}: refusing to target {environment}.", file=sys.stderr)
        print(
            'Set QA_ENVIRONMENT to a local/dev/staging target, or set '
            'QA_ALLOW_PRODUCTION=1 only with explicit human approval.',
            file=sys.stderr,
        )
        return 1

    if not command_value:
        print(f"{adapter_name}: not configured.", file=sys.stderr)
        print(f"Set {command_var}, or replace this adapter with the project-specific command.", file=sys.stderr)
        print(
            'This placeholder exits 2 so agents do not mistake missing QA wiring for a passed check.',
            file=sys.stderr,
        )
        return 2

    try:
        os.makedirs(artifact_dir, exist_ok=True)
    except OSError as exc:
        print(f"{adapter_name}: failed to create artifact directory: {artifact_dir} ({exc})", file=sys.stderr)
        return 1

    print(EXPECTED_OUTPUT[intent])
    print(f"{adapter_name}: running configured {command_var}.")
    # shell=True so projects can configure a full command line without this
    # template knowing the target stack; mirrors `sh -c` in lib.sh.
    result = subprocess.run(command_value, shell=True)
    return result.returncode


if __name__ == '__main__':
    sys.exit(main(sys.argv))
