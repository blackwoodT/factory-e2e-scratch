#!/bin/sh
# qa:smoke adapter
# Purpose: run the smallest project-specific runtime health or user-flow check
# and emit a concise pass/fail summary suitable for PR evidence.

QA_ADAPTER_NAME='qa:smoke'
export QA_ADAPTER_NAME

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
# shellcheck source=scripts/qa/lib.sh
. "${SCRIPT_DIR}/lib.sh"

cat <<'MESSAGE'
qa:smoke expected configured-command output:
- target URL, endpoint, fixture, or environment checked
- concise pass/fail summary
- artifact paths for screenshots, traces, or logs when produced
MESSAGE

qa_run_configured_command "${QA_SMOKE_COMMAND:-}" 'QA_SMOKE_COMMAND'
