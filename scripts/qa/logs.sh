#!/bin/sh
# qa:logs adapter
# Purpose: print a bounded, project-specific runtime log excerpt for agent and
# reviewer evidence without leaking secrets or dumping unbounded output.

QA_ADAPTER_NAME='qa:logs'
export QA_ADAPTER_NAME

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
# shellcheck source=scripts/qa/lib.sh
. "${SCRIPT_DIR}/lib.sh"

cat <<'MESSAGE'
qa:logs expected configured-command output:
- bounded log excerpt only; avoid full log dumps
- time range, request id, trace id, or other filter used
- artifact path if logs are stored outside terminal output
MESSAGE

qa_run_configured_command "${QA_LOGS_COMMAND:-}" 'QA_LOGS_COMMAND'
