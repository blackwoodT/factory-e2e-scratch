#!/usr/bin/env python3
"""Detect subscription usage-limit errors in agent output and compute resume time.

Subscription limit errors are text, not structured data (see
docs/workflow/automation-blueprint.md § "Usage limits and auto-resume"). This
script scans a failed agent run's captured output for known limit/rate-limit
shapes and derives the `paused_until` timestamp the dispatcher writes into
.ai/factory.json. When a limit is detected but no reset time can be parsed, it
falls back to --default-pause-minutes; the scheduled dispatcher tick re-checks
after the pause and simply pauses again if the limit still holds.

Usage:
  python scripts/factory/limits.py --log-file out.log [--now ISO] \
      [--default-pause-minutes 90]
  python scripts/factory/limits.py --self-test

Output: JSON on stdout {limit_detected, paused_until, matched, detail} and the
same fields appended to $GITHUB_OUTPUT when set. Exit codes: 0 = ran (whether
or not a limit was detected), 1 = self-test failure, 2 = could not run.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT / 'scripts' / 'fixtures' / 'factory' / 'logs'

# Signals that the failure is a usage/rate limit rather than a product error.
# Deliberately NO bare "429": agent logs can mention the status incidentally
# (e.g. a failing test asserting an HTTP 429), and provider limit errors carry
# these words anyway. A missed limit degrades to the durable agent_failure
# gate — surfaced to the human — which is the safe direction.
LIMIT_SIGNALS = re.compile(
    r'usage limit|rate limit|rate_limit|too many requests|quota exceeded'
    r'|hit your .{0,20}limit|limit reached',
    re.IGNORECASE,
)

# "Claude AI usage limit reached|1750118400" — epoch seconds (or ms) after a pipe.
EPOCH_AFTER_PIPE = re.compile(r'limit reached\|(\d{10,13})', re.IGNORECASE)
# Any explicit reset epoch, e.g. "resets at 1750118400" / "retry after 1750118400".
EPOCH_INLINE = re.compile(r'(?:reset[s]?(?: at)?|retry(?: |-)?after)[ :]+(\d{10,13})', re.IGNORECASE)
# "resets at 7pm (UTC)" / "resets 3am" / "try again at 19:30".
CLOCK_TIME = re.compile(
    r'(?:reset[s]?(?: at)?|try again at|available again at)\s+'
    r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
    re.IGNORECASE,
)
# "try again in 2 hours 30 minutes" / "retry in 45 minutes" / "in 90 seconds".
RELATIVE_TIME = re.compile(
    r'(?:try again|retry|available)(?: again)? in\s+'
    r'(?:(\d+)\s*h(?:ours?|rs?)?)?\s*(?:(\d+)\s*m(?:in(?:utes?)?)?)?\s*(?:(\d+)\s*s(?:ec(?:onds?)?)?)?',
    re.IGNORECASE,
)
# HTTP header style: "retry-after: 3600" (seconds).
RETRY_AFTER_SECONDS = re.compile(r'retry-after[: ]+(\d{1,6})(?!\d)', re.IGNORECASE)


def utc_now(now_arg=None):
    if now_arg:
        return datetime.fromisoformat(now_arg.replace('Z', '+00:00')).astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def parse_reset_time(text, now):
    """Return (datetime|None, matched_pattern_name)."""
    for pattern, name in ((EPOCH_AFTER_PIPE, 'epoch_after_pipe'), (EPOCH_INLINE, 'epoch_inline')):
        match = pattern.search(text)
        if match:
            value = int(match.group(1))
            if value > 10**12:  # milliseconds
                value //= 1000
            resume = datetime.fromtimestamp(value, tz=timezone.utc)
            # An epoch in the past or absurdly far out means we misparsed;
            # let the caller fall back to the default pause instead.
            if now < resume <= now + timedelta(days=8):
                return resume, name

    match = RETRY_AFTER_SECONDS.search(text)
    if match:
        return now + timedelta(seconds=int(match.group(1))), 'retry_after_seconds'

    match = RELATIVE_TIME.search(text)
    if match and any(match.groups()):
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if delta.total_seconds() > 0:
            return now + delta, 'relative_time'

    match = CLOCK_TIME.search(text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        meridiem = (match.group(3) or '').lower()
        if meridiem == 'pm' and hour < 12:
            hour += 12
        if meridiem == 'am' and hour == 12:
            hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            # Timezone is rarely stated reliably; assume UTC and take the next
            # occurrence. Worst case the factory resumes early, hits the limit
            # again, and re-pauses — self-healing.
            resume = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if resume <= now:
                resume += timedelta(days=1)
            return resume, 'clock_time'

    return None, ''


def analyze(text, now, default_pause_minutes):
    if not LIMIT_SIGNALS.search(text):
        return {'limit_detected': False, 'paused_until': '', 'matched': '', 'detail': ''}
    resume, matched = parse_reset_time(text, now)
    if resume is None:
        resume = now + timedelta(minutes=default_pause_minutes)
        matched = 'default_pause'
    signal = LIMIT_SIGNALS.search(text)
    line_start = text.rfind('\n', 0, signal.start()) + 1
    line_end = text.find('\n', signal.end())
    detail = text[line_start:line_end if line_end != -1 else None].strip()[:300]
    return {
        'limit_detected': True,
        'paused_until': iso(resume),
        'matched': matched,
        'detail': detail,
    }


def emit(result):
    print(json.dumps(result, indent=2))
    output_path = os.environ.get('GITHUB_OUTPUT')
    if output_path:
        with open(output_path, 'a', encoding='utf-8') as handle:
            for key, value in result.items():
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                handle.write(f"{key}={str(value).splitlines()[0] if value else ''}\n")


def run_self_test():
    expectations_path = FIXTURES_DIR / 'expectations.json'
    if not expectations_path.exists():
        print(f"Missing fixtures: {expectations_path.relative_to(ROOT)}")
        return 2
    expectations = json.loads(expectations_path.read_text(encoding='utf-8'))
    now = utc_now(expectations.get('_now', '2026-06-12T00:00:00Z'))
    default_minutes = expectations.get('_default_pause_minutes', 90)
    failures = []
    count = 0
    for log_name, expected in expectations.items():
        if log_name.startswith('_'):
            continue
        count += 1
        log_path = FIXTURES_DIR / log_name
        if not log_path.exists():
            failures.append(f"{log_name}: fixture log missing")
            continue
        result = analyze(log_path.read_text(encoding='utf-8'), now, default_minutes)
        for key, want in expected.items():
            if result.get(key) != want:
                failures.append(f"{log_name}: {key} = {result.get(key)!r}, expected {want!r}")
    if failures:
        print('\n'.join(failures))
        print('Factory limits self-test FAILED.')
        return 1
    print(f"Factory limits self-test passed ({count} fixture logs).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--log-file', action='append', default=[],
                        help='agent output/error log to scan (repeatable)')
    parser.add_argument('--now', default='', help='ISO timestamp override (tests)')
    parser.add_argument('--default-pause-minutes', type=int, default=90)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.log_file:
        print('Provide at least one --log-file (or --self-test).', file=sys.stderr)
        return 2
    chunks = []
    for log in args.log_file:
        path = Path(log)
        if path.exists():
            chunks.append(path.read_text(encoding='utf-8', errors='replace'))
    emit(analyze('\n'.join(chunks), utc_now(args.now), args.default_pause_minutes))
    return 0


if __name__ == '__main__':
    sys.exit(main())
