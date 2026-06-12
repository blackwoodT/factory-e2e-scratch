#!/bin/sh
# qa:boot adapter
# Purpose: start the project-specific app or runnable target in a safe local/dev
# context and emit evidence such as URL, process/container id, and log path.

QA_ADAPTER_NAME='qa:boot'
export QA_ADAPTER_NAME

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
# shellcheck source=scripts/qa/lib.sh
. "${SCRIPT_DIR}/lib.sh"

cat <<'MESSAGE'
qa:boot expected configured-command output:
- target URL or endpoint, when applicable
- PID, process id, container id, or equivalent runtime handle
- log file or log query location
MESSAGE

qa_run_configured_command "${QA_BOOT_COMMAND:-}" 'QA_BOOT_COMMAND'
