#!/usr/bin/env python3
"""Validate every .ai/tickets/*/state.json against the ticket-state contract.

This is the mechanical safety net for the workflow state machine. Role docs
describe the rules in prose; this script enforces the subset that can be
checked deterministically:

- field presence, types, and enum values (loaded from .ai/schema/ticket-state.schema.json
  so the schema file stays the single source of truth for enums)
- stage <-> next_actor routing legality, including the security-review gate actor
- ticket_type coherence (specialist/prerequisite metadata, parent links, ID infixes)
- review pass list shape (non-empty, unique ids, current_pass known and actually
  pending/in-progress while reviewing)
- PR lifecycle coherence (implemented/reviewing imply a recorded PR, finalized
  implies merged, review_accepted implies every required pass accepted with a
  recorded head_sha and validation passed)

Usage:
  python scripts/validate_ticket_state.py             # validate all tickets
  python scripts/validate_ticket_state.py --strict    # warnings also fail
  python scripts/validate_ticket_state.py --self-test # run fixture regression tests

Exit codes: 0 = ok, 1 = validation errors (or warnings with --strict),
2 = could not run (missing schema, bad fixture layout).
"""
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / '.ai' / 'schema' / 'ticket-state.schema.json'
TICKETS_DIR = ROOT / '.ai' / 'tickets'
FIXTURES_DIR = ROOT / 'scripts' / 'fixtures' / 'ticket-state'

# Stages in which a pull request must already exist and be recorded. The
# implementer flips stage to 'implemented' in the same commit that records
# pull_request metadata (see .roles/implementer.md "Commit and PR creation"),
# so 'implemented' state without a PR is a contract violation, not a transient.
# 'finalized' keeps its PR metadata for the audit trail.
PR_REQUIRED_STAGES = {'implemented', 'reviewing', 'changes_requested', 'review_accepted', 'finalized'}

# Legal next_actor values per stage. "none" / null are normalized to "none".
STAGE_NEXT_ACTOR = {
    'planned': {'orchestrator', 'implementer'},
    'implementing': {'implementer'},
    'implemented': {'reviewer', 'sec-reviewer'},
    'reviewing': {'reviewer', 'sec-reviewer'},
    'changes_requested': {'implementer'},
    'review_accepted': {'orchestrator'},
    'finalized': {'orchestrator', 'none'},
    'blocked': {'orchestrator', 'none'},
}

# Ticket ID prefixes may be domain-grouped with hyphens (e.g. TKT-ARCH-006);
# sub-tickets always use the dot + infix form.
TICKET_ID_RE = re.compile(r'^[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d+$')
SUB_TICKET_ID_RE = re.compile(r'^[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d+\.(?P<infix>[A-Z0-9]+)-\d{2,}$')

REQUIRED_TOP_LEVEL = [
    'schema_version', 'ticket_id', 'ticket_type', 'title', 'branch', 'stage',
    'next_actor', 'status', 'execution_mode', 'waiting_on', 'summary',
    'validation', 'pull_request', 'review', 'handoff', 'history',
]


def load_enums():
    """Read enum lists out of the JSON schema so they are defined once."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    defs = schema['definitions']

    def enum(name):
        return set(defs[name]['enum'])

    return {
        'stage': enum('stage'),
        'next_actor': enum('next_actor'),
        'status': enum('ticket_status'),
        'execution_mode': enum('execution_mode'),
        'waiting_on': enum('waiting_on'),
        'ticket_type': enum('ticket_type'),
        'specialist_type': enum('specialist_type'),
        'specialist_agent': enum('specialist_agent'),
        'validation_status': enum('validation_status'),
        'pull_request_status': enum('pull_request_status'),
        'review_outcome': enum('review_outcome'),
        'pass_status': enum('pass_status'),
        'pass_outcome': enum('pass_outcome'),
        'handoff_role': enum('handoff_role'),
        'ai_usage_source': enum('ai_usage_source'),
        'ai_usage_confidence': enum('ai_usage_confidence'),
        'ai_usage_total_confidence': enum('ai_usage_total_confidence'),
    }


def normalize_actor(value):
    if value is None:
        return 'none'
    # Non-string values can never be valid actors; keep them out of set
    # membership tests so a malformed file reports errors instead of crashing.
    return value if isinstance(value, str) else '__invalid__'


def check_enum(errors, enums, enum_name, value, field_label):
    try:
        is_valid = value in enums[enum_name]
    except TypeError:
        # Unhashable values (lists/objects) can never be valid enum members.
        is_valid = False
    if not is_valid:
        allowed = sorted(str(v) for v in enums[enum_name])
        errors.append(f"{field_label}: {value!r} is not one of {allowed}")


def validate_state(state, enums, folder_name=None):
    """Return (errors, warnings) for one parsed state.json object."""
    errors = []
    warnings = []

    if not isinstance(state, dict):
        return ['state.json root must be a JSON object'], warnings

    for field in REQUIRED_TOP_LEVEL:
        if field not in state:
            errors.append(f"missing required field: {field}")
    if errors:
        # Without the basic shape, deeper checks would just cascade noise.
        return errors, warnings

    # Template leniency comes from WHERE the file lives, not what it claims:
    # a real ticket folder carrying ticket_id='TEMPLATE' is a copy-paste error,
    # not a template, and must fail the folder/id coherence checks below.
    if folder_name:
        is_template = folder_name == 'TEMPLATE'
    else:
        is_template = state.get('ticket_id') == 'TEMPLATE'

    stage = state['stage']
    next_actor = normalize_actor(state['next_actor'])
    ticket_type = state['ticket_type']
    ticket_id = state['ticket_id']

    check_enum(errors, enums, 'stage', stage, 'stage')
    check_enum(errors, enums, 'next_actor', state['next_actor'], 'next_actor')
    check_enum(errors, enums, 'status', state['status'], 'status')
    check_enum(errors, enums, 'execution_mode', state['execution_mode'], 'execution_mode')
    check_enum(errors, enums, 'waiting_on', state['waiting_on'], 'waiting_on')
    check_enum(errors, enums, 'ticket_type', ticket_type, 'ticket_type')

    # After the enum errors are recorded, coerce malformed values so the
    # semantic checks below stay crash-free (sets/dict lookups need strings).
    if not isinstance(stage, str):
        stage = '__invalid__'
    if not isinstance(ticket_id, str):
        errors.append('ticket_id must be a string')
        ticket_id = ''

    # --- Routing legality -------------------------------------------------
    allowed_actors = STAGE_NEXT_ACTOR.get(stage)
    if allowed_actors is not None and next_actor not in allowed_actors:
        # The architect only appears before normal ticket loops; allow it for
        # freshly bootstrapped planned tickets rather than hard-failing.
        if not (stage == 'planned' and next_actor == 'architect'):
            errors.append(
                f"stage={stage!r} cannot route to next_actor={state['next_actor']!r}; "
                f"allowed: {sorted(allowed_actors)}"
            )

    # --- Ticket id and type coherence ------------------------------------
    if not is_template:
        if folder_name and ticket_id != folder_name:
            errors.append(
                f"ticket_id {ticket_id!r} does not match its folder name {folder_name!r}"
            )
        sub_match = SUB_TICKET_ID_RE.match(ticket_id)
        if TICKET_ID_RE.match(ticket_id):
            if ticket_type != 'primary':
                errors.append(
                    f"ticket_id {ticket_id!r} has no sub-ticket infix but ticket_type is {ticket_type!r}"
                )
        elif sub_match:
            infix = sub_match.group('infix')
            # The child id encodes its parent; the recorded linkage must agree
            # because parent unblock/finalization logic relies on it.
            encoded_parent = ticket_id.split('.', 1)[0]
            recorded_parent = state.get('parent_ticket')
            if recorded_parent and recorded_parent != encoded_parent:
                errors.append(
                    f"parent_ticket {recorded_parent!r} does not match the parent encoded "
                    f"in ticket_id {ticket_id!r} (expected {encoded_parent!r})"
                )
            if infix == 'PREREQ' and ticket_type != 'prerequisite':
                errors.append(
                    f"ticket_id {ticket_id!r} uses the PREREQ infix but ticket_type is {ticket_type!r}"
                )
            if infix != 'PREREQ' and ticket_type != 'specialist':
                errors.append(
                    f"ticket_id {ticket_id!r} uses specialist infix {infix!r} but ticket_type is {ticket_type!r}"
                )
            # The infix exists so the sub-ticket type is self-describing at a
            # glance; routing resolves from specialist.type, so the two must
            # agree (standard infixes are the uppercase of the type).
            if (
                infix != 'PREREQ'
                and ticket_type == 'specialist'
                and isinstance(state.get('specialist'), dict)
                and isinstance(state['specialist'].get('type'), str)
                and infix.lower() != state['specialist']['type']
            ):
                errors.append(
                    f"ticket_id {ticket_id!r} uses infix {infix!r} but specialist.type is "
                    f"{state['specialist']['type']!r}; the ID would route differently than the metadata"
                )
        else:
            errors.append(
                f"ticket_id {ticket_id!r} does not match TKT-style id patterns "
                "(e.g. TKT-002, TKT-002.PREREQ-01, TKT-003.UI-01)"
            )

    specialist = state.get('specialist')
    if ticket_type == 'specialist':
        if not isinstance(specialist, dict):
            errors.append("ticket_type=specialist requires a populated specialist object")
        else:
            check_enum(errors, enums, 'specialist_type', specialist.get('type'), 'specialist.type')
            if specialist.get('agent') is not None:
                check_enum(errors, enums, 'specialist_agent', specialist.get('agent'), 'specialist.agent')
            if not specialist.get('skill'):
                warnings.append("specialist.skill is empty; 'Proceed' routing falls back to the type table")
        if not state.get('parent_ticket') and not is_template:
            errors.append("ticket_type=specialist requires parent_ticket")
    elif ticket_type == 'prerequisite':
        if state['execution_mode'] != 'human_assisted':
            errors.append("ticket_type=prerequisite requires execution_mode=human_assisted")
        if not state.get('parent_ticket') and not is_template:
            errors.append("ticket_type=prerequisite requires parent_ticket")
        if isinstance(specialist, dict) and specialist.get('type') not in (None, 'prereq'):
            warnings.append(
                f"prerequisite ticket carries specialist.type={specialist.get('type')!r}; expected 'prereq' or null"
            )
    else:  # primary
        if specialist not in (None, {}):
            errors.append("ticket_type=primary must keep specialist = null")

    # --- Validation block --------------------------------------------------
    validation = state['validation']
    if isinstance(validation, dict):
        check_enum(errors, enums, 'validation_status', validation.get('status'), 'validation.status')
    else:
        errors.append('validation must be an object')

    # --- Review passes ------------------------------------------------------
    review = state['review']
    passes = []
    if not isinstance(review, dict):
        errors.append('review must be an object')
    else:
        check_enum(errors, enums, 'review_outcome', review.get('outcome'), 'review.outcome')
        passes = review.get('required_passes')
        if not isinstance(passes, list) or not passes:
            errors.append('review.required_passes must be a non-empty list (review tier sets its content)')
            passes = []
        seen_ids = set()
        for index, item in enumerate(passes):
            label = f"review.required_passes[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            pass_id = item.get('id')
            if not pass_id or not isinstance(pass_id, str):
                errors.append(f"{label}.id is required")
            elif pass_id in seen_ids:
                errors.append(f"{label}.id {pass_id!r} is duplicated")
            else:
                seen_ids.add(pass_id)
            if not item.get('tool'):
                errors.append(f"{label}.tool is required (which tool/model runs this pass)")
            check_enum(errors, enums, 'pass_status', item.get('status'), f"{label}.status")
            if 'outcome' in item:
                check_enum(errors, enums, 'pass_outcome', item.get('outcome'), f"{label}.outcome")
        fix_loop_count = review.get('fix_loop_count')
        if fix_loop_count is not None:
            if not isinstance(fix_loop_count, int) or fix_loop_count < 0:
                errors.append('review.fix_loop_count must be a non-negative integer when present')
            elif fix_loop_count >= 3 and stage in ('changes_requested', 'implementing'):
                warnings.append(
                    f"review.fix_loop_count={fix_loop_count} has reached the loop guard threshold; "
                    "the orchestrator should triage findings instead of another silent fix loop "
                    "(docs/workflow/review-gates.md)"
                )
        current_pass = review.get('current_pass')
        if current_pass is not None and (
            not isinstance(current_pass, str) or current_pass not in seen_ids
        ):
            errors.append(
                f"review.current_pass {current_pass!r} is not an id in review.required_passes"
            )
        if stage == 'reviewing' and current_pass is None:
            errors.append(
                "stage='reviewing' requires review.current_pass so 'Proceed' routing "
                "knows which pass is in progress (state.json is authoritative, not the handoff prompt)"
            )
        if stage == 'implemented' and current_pass is None:
            warnings.append(
                "stage='implemented' normally records review.current_pass for the "
                "first review pass handoff"
            )
        if stage in ('implemented', 'reviewing') and isinstance(current_pass, str) and current_pass in seen_ids:
            current_record = next(
                (item for item in passes
                 if isinstance(item, dict) and item.get('id') == current_pass),
                None,
            )
            if current_record is not None and current_record.get('status') not in ('pending', 'in_progress'):
                errors.append(
                    f"stage={stage!r} but current_pass {current_pass!r} has status "
                    f"{current_record.get('status')!r}; the current pass must be the "
                    "pending/in-progress pass that still needs to run"
                )
        if (
            stage in ('implemented', 'reviewing')
            and isinstance(current_pass, str)
            and current_pass in seen_ids
        ):
            # Passes run in required_passes order; current_pass must not skip
            # an earlier pass that has not been accepted yet.
            for item in passes:
                if not isinstance(item, dict):
                    continue
                if item.get('id') == current_pass:
                    break
                if item.get('status') != 'accepted':
                    errors.append(
                        f"current_pass {current_pass!r} skips earlier required pass "
                        f"{item.get('id')!r} (status {item.get('status')!r}); "
                        "review passes run in required_passes order"
                    )
        if isinstance(current_pass, str):
            # The security gate must reach the independent security reviewer.
            # next_actor='reviewer' is tolerated because Universal "Proceed"
            # routing resolves that combination to $sec-reviewer, but the
            # explicit actor is safer for mechanical dispatch.
            if current_pass == 'security-review' and next_actor == 'reviewer':
                warnings.append(
                    "current_pass='security-review' with next_actor='reviewer': "
                    "'Proceed' routing resolves this to $sec-reviewer, but prefer "
                    "next_actor='sec-reviewer' so the gate cannot be missed"
                )
            if next_actor == 'sec-reviewer' and current_pass != 'security-review':
                errors.append(
                    f"next_actor='sec-reviewer' but current_pass is {current_pass!r}; "
                    "the security reviewer only owns the 'security-review' pass"
                )

    # --- Pull request lifecycle ---------------------------------------------
    pull_request = state['pull_request']
    pr_status = None
    if not isinstance(pull_request, dict):
        errors.append('pull_request must be an object')
    else:
        pr_status = pull_request.get('status')
        check_enum(errors, enums, 'pull_request_status', pr_status, 'pull_request.status')

        if stage in PR_REQUIRED_STAGES and pr_status == 'not_created':
            errors.append(f"stage={stage!r} requires an existing pull request (status is 'not_created')")
        pr_url = pull_request.get('url')
        if stage in PR_REQUIRED_STAGES and (not pr_url or not isinstance(pr_url, str)):
            errors.append(f"stage={stage!r} requires pull_request.url to be a usable URL string")
        if stage == 'finalized' and pr_status != 'merged':
            errors.append("stage='finalized' requires pull_request.status='merged'")

    if stage in ('review_accepted', 'finalized'):
        # The finalization contract requires accepted validation evidence
        # before merge; approval with failed or unrun validation is incoherent.
        validation_status = validation.get('status') if isinstance(validation, dict) else None
        if validation_status not in ('passed', 'passed_with_skips'):
            errors.append(
                f"stage={stage!r} requires validation.status 'passed' or "
                f"'passed_with_skips' (found {validation_status!r})"
            )
        # The canonical review summary must agree with the per-pass records.
        review_outcome = review.get('outcome') if isinstance(review, dict) else None
        if review_outcome not in ('accepted', 'accepted_with_follow_up'):
            errors.append(
                f"stage={stage!r} requires review.outcome 'accepted' or "
                f"'accepted_with_follow_up' (found {review_outcome!r})"
            )
        for item in passes:
            if not isinstance(item, dict):
                continue
            pass_id = item.get('id')
            # status is the state-machine record; an outcome-only record means
            # the pass has not actually completed in the workflow's eyes.
            if item.get('status') != 'accepted':
                errors.append(
                    f"stage={stage!r} requires pass {pass_id!r} to have status='accepted' "
                    f"(found {item.get('status')!r}; outcome alone is not acceptance)"
                )
            # The finalization gate also requires every pass to RECORD an
            # accepted outcome; a null outcome is an incomplete review record.
            # 'approved' is tolerated as a legacy synonym from the state.json
            # template comments.
            if item.get('outcome') not in ('accepted', 'accepted_with_follow_up', 'approved'):
                errors.append(
                    f"stage={stage!r} requires pass {pass_id!r} to record an accepted outcome "
                    f"(found {item.get('outcome')!r}; reviewers write 'accepted' or 'accepted_with_follow_up')"
                )
            # Without the accepted head SHA the stale-head gate and the
            # review-record exemption comparison cannot be evaluated.
            if not item.get('head_sha'):
                errors.append(
                    f"stage={stage!r} requires pass {pass_id!r} to record the accepted head_sha "
                    "(the stale-head gate cannot run without it)"
                )

    if stage == 'review_accepted' and pr_status not in ('approved', 'merged'):
        errors.append("stage='review_accepted' requires pull_request.status='approved'")

    if stage == 'changes_requested' and passes:
        flagged = any(
            isinstance(item, dict)
            and (item.get('status') == 'changes_requested' or item.get('outcome') == 'changes_requested')
            for item in passes
        )
        # A pass record is the normal signal; review.outcome covers
        # orchestrator-initiated returns (triage fix_now routing).
        outcome_flagged = isinstance(review, dict) and review.get('outcome') == 'changes_requested'
        if not flagged and not outcome_flagged:
            errors.append(
                "stage='changes_requested' but neither any review pass nor review.outcome "
                "records changes_requested; the implementer cannot route the fix loop from state.json"
            )

    if stage == 'finalized' and state['status'] != 'closed':
        errors.append("stage='finalized' requires status='closed' (finalization is the closeout state)")

    if stage in ('implemented', 'reviewing'):
        # The implementer contract hands to review only after validation passes;
        # routing reviewers a state that records unsatisfied validation is incoherent.
        validation_status = validation.get('status') if isinstance(validation, dict) else None
        if validation_status not in ('passed', 'passed_with_skips'):
            errors.append(
                f"stage={stage!r} requires validation.status 'passed' or 'passed_with_skips' "
                f"before reviewer handoff (found {validation_status!r})"
            )

    # --- Handoff and history --------------------------------------------------
    handoff = state['handoff']
    if isinstance(handoff, dict):
        for key in ('from', 'to'):
            # Absent or null endpoints must not be laundered into the legal
            # 'none' role by normalization; the audit trail needs both ends.
            if key not in handoff or handoff.get(key) is None:
                errors.append(
                    f"handoff.{key} is required and must name a role "
                    "(use the explicit string 'none' only when a ticket is finalized)"
                )
            else:
                check_enum(errors, enums, 'handoff_role', normalize_actor(handoff.get(key)), f"handoff.{key}")
    else:
        errors.append('handoff must be an object')

    history = state['history']
    if not isinstance(history, list) or not history:
        errors.append('history must be a non-empty list')
    else:
        for index, entry in enumerate(history):
            if not isinstance(entry, dict) or 'stage' not in entry or 'actor' not in entry:
                errors.append(f"history[{index}] must be an object with 'stage' and 'actor'")
            else:
                check_enum(errors, enums, 'stage', entry['stage'], f"history[{index}].stage")
                if not entry['actor'] or not isinstance(entry['actor'], str):
                    errors.append(f"history[{index}].actor must be a non-empty string (audit trail)")

    # --- AI usage ledger (shape only; numbers stay best-effort) ---------------
    ai_usage = state.get('ai_usage')
    if ai_usage is not None and not isinstance(ai_usage, dict):
        errors.append('ai_usage must be an object when present')
    if isinstance(ai_usage, dict):
        entries = ai_usage.get('entries')
        if entries is not None and not isinstance(entries, list):
            errors.append('ai_usage.entries must be a list when present')
            entries = []
        for index, entry in enumerate(entries or []):
            if not isinstance(entry, dict):
                errors.append(f"ai_usage.entries[{index}] must be an object")
                continue
            if 'source' in entry:
                check_enum(errors, enums, 'ai_usage_source', entry['source'], f"ai_usage.entries[{index}].source")
            if 'confidence' in entry:
                check_enum(
                    errors, enums, 'ai_usage_confidence', entry['confidence'],
                    f"ai_usage.entries[{index}].confidence"
                )
        # The ticket TOTAL uses its own value set (complete/partial/unknown),
        # distinct from per-entry confidence (exact/estimated/partial/unknown).
        if 'ticket_total_confidence' in ai_usage:
            check_enum(
                errors, enums, 'ai_usage_total_confidence',
                ai_usage['ticket_total_confidence'], 'ai_usage.ticket_total_confidence'
            )

    return errors, warnings


def validate_file(path, enums):
    try:
        state = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"], []
    return validate_state(state, enums, folder_name=path.parent.name)


def run_repo_validation(strict):
    enums = load_enums()
    state_files = sorted(TICKETS_DIR.glob('*/state.json'))
    total_errors = 0
    total_warnings = 0

    if not state_files:
        # At minimum the TEMPLATE scaffold must exist; an empty tickets tree
        # means the authoritative state machine has been deleted, not "clean".
        print(
            f"ERROR: no ticket state files found under {TICKETS_DIR.relative_to(ROOT)}; "
            "at least .ai/tickets/TEMPLATE/state.json must exist."
        )
        return 1

    for path in state_files:
        errors, warnings = validate_file(path, enums)
        rel = path.relative_to(ROOT)
        for message in errors:
            print(f"{rel}: ERROR: {message}")
        for message in warnings:
            print(f"{rel}: WARNING: {message}")
        total_errors += len(errors)
        total_warnings += len(warnings)

    print(
        f"Checked {len(state_files)} ticket state file(s): "
        f"{total_errors} error(s), {total_warnings} warning(s)."
    )
    if total_errors or (strict and total_warnings):
        return 1
    return 0


def run_self_test():
    """Fixture regression: valid/ must pass, invalid/ must each raise >=1 error."""
    enums = load_enums()
    valid_dir = FIXTURES_DIR / 'valid'
    invalid_dir = FIXTURES_DIR / 'invalid'
    if not valid_dir.is_dir() or not invalid_dir.is_dir():
        print(f"Fixture directories missing under {FIXTURES_DIR.relative_to(ROOT)}")
        return 2

    failures = []
    for path in sorted(valid_dir.glob('*.json')):
        state = json.loads(path.read_text(encoding='utf-8'))
        folder = state.get('_fixture_folder_name', state.get('ticket_id'))
        errors, _ = validate_state(state, enums, folder_name=folder)
        if errors:
            failures.append(f"valid fixture {path.name} unexpectedly failed: {errors}")
    for path in sorted(invalid_dir.glob('*.json')):
        state = json.loads(path.read_text(encoding='utf-8'))
        folder = state.get('_fixture_folder_name', state.get('ticket_id'))
        errors, _ = validate_state(state, enums, folder_name=folder)
        if not errors:
            failures.append(f"invalid fixture {path.name} unexpectedly passed")

    if failures:
        print('\n'.join(failures))
        print('Ticket state validator self-test FAILED.')
        return 1
    valid_count = len(list(valid_dir.glob('*.json')))
    invalid_count = len(list(invalid_dir.glob('*.json')))
    print(
        f"Ticket state validator self-test passed "
        f"({valid_count} valid, {invalid_count} invalid fixtures)."
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--strict', action='store_true', help='treat warnings as failures')
    parser.add_argument('--self-test', action='store_true', help='run fixture regression tests instead')
    args = parser.parse_args()

    if not SCHEMA_PATH.exists():
        print(f"Missing schema: {SCHEMA_PATH.relative_to(ROOT)}")
        return 2
    if args.self_test:
        return run_self_test()
    return run_repo_validation(strict=args.strict)


if __name__ == '__main__':
    sys.exit(main())
