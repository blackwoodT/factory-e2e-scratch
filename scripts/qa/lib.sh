#!/bin/sh
# Shared helpers for stack-neutral Agent QA adapter scripts.
# Keep this file POSIX-sh compatible so downstream projects can run it without
# assuming Bash, Node, Python, Docker, or a specific framework.

qa_adapter_name=${QA_ADAPTER_NAME:-qa}
qa_environment=${QA_ENVIRONMENT:-local}
qa_artifact_dir=${QA_ARTIFACT_DIR:-.ai/qa-artifacts}

qa_print_header() {
  printf '%s\n' "${qa_adapter_name}: adapter starting"
  printf '%s\n' "environment=${qa_environment}"
  printf '%s\n' "artifact_dir=${qa_artifact_dir}"
}

qa_refuse_production() {
  # Case-insensitive: Production / PROD / Live must also fail closed.
  qa_environment_lc=$(printf '%s' "${qa_environment}" | tr '[:upper:]' '[:lower:]')
  case "${qa_environment_lc}" in
    production|prod|live)
      if [ "${QA_ALLOW_PRODUCTION:-}" != "1" ]; then
        printf '%s\n' "${qa_adapter_name}: refusing to target ${qa_environment}." >&2
        printf '%s\n' "Set QA_ENVIRONMENT to a local/dev/staging target, or set QA_ALLOW_PRODUCTION=1 only with explicit human approval." >&2
        return 1
      fi
      ;;
  esac
  return 0
}

qa_require_command() {
  command_value=$1
  command_var=$2
  if [ -z "${command_value}" ]; then
    printf '%s\n' "${qa_adapter_name}: not configured." >&2
    printf '%s\n' "Set ${command_var}, or replace this adapter with the project-specific command." >&2
    printf '%s\n' "This placeholder exits 2 so agents do not mistake missing QA wiring for a passed check." >&2
    return 2
  fi
  return 0
}

qa_prepare_artifact_dir() {
  if ! mkdir -p "${qa_artifact_dir}"; then
    printf '%s\n' "${qa_adapter_name}: failed to create artifact directory: ${qa_artifact_dir}" >&2
    return 1
  fi
  return 0
}

qa_run_configured_command() {
  command_value=$1
  command_var=$2

  qa_print_header
  qa_refuse_production || return 1
  qa_require_command "${command_value}" "${command_var}" || return $?
  qa_prepare_artifact_dir || return 1

  printf '%s\n' "${qa_adapter_name}: running configured ${command_var}."
  # Use sh -c so the project can provide a command line without this template
  # knowing the target stack. Downstream projects may replace this file entirely
  # if they need stricter argument handling.
  sh -c "${command_value}"
}
