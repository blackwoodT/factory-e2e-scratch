#!/bin/sh
# qa:stop adapter
# Purpose: tear down local/dev runtime resources started for agent QA and report
# what was cleaned up.

QA_ADAPTER_NAME='qa:stop'
export QA_ADAPTER_NAME

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
# shellcheck source=scripts/qa/lib.sh
. "${SCRIPT_DIR}/lib.sh"

cat <<'MESSAGE'
qa:stop expected configured-command output:
- process/container/resource handles stopped
- remaining resources or cleanup warnings, if any
- confirmation that local/dev QA resources are no longer running
MESSAGE

qa_run_configured_command "${QA_STOP_COMMAND:-}" 'QA_STOP_COMMAND'
