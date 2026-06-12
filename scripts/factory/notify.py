#!/usr/bin/env python3
"""Factory notifications: ntfy.sh pushes, "needs you" gate issues, dashboard.

The durable human surface is GitHub issues (resolvable from GitHub Mobile);
ntfy.sh pushes are best-effort pointers to them, so push failures warn and
never fail a workflow run. GitHub calls go through the `gh` CLI, which is
pre-authenticated in Actions via GH_TOKEN.

Subcommands:
  push       send an ntfy.sh notification (topic from the NTFY_TOPIC env var)
  needs-you  create or update the open "Factory needs you" gate issue
  close-gate close a gate issue with a resolution comment
  dashboard  regenerate the pinned factory dashboard issue
  self-test  offline regression test of the dashboard renderer

Exit codes: 0 = ok (including skipped/best-effort), 1 = hard failure or
self-test failure, 2 = bad arguments.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT / 'scripts' / 'fixtures' / 'factory'

NEEDS_YOU_LABEL = 'factory:needs-you'
DASHBOARD_LABEL = 'factory:dashboard'
BUILD_REQUEST_LABEL = 'factory:build-request'
DASHBOARD_TITLE = 'Factory dashboard'


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def gh(args, repo, input_text=None, check=True):
    command = ['gh'] + args + (['--repo', repo] if repo else [])
    result = subprocess.run(command, capture_output=True, text=True,
                            input=input_text, timeout=60)
    if check and result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def ensure_labels(repo):
    for name, color, description in (
        (NEEDS_YOU_LABEL, 'd93f0b', 'The factory is waiting on a human'),
        (DASHBOARD_LABEL, '0e8a16', 'Pinned factory status dashboard'),
        (BUILD_REQUEST_LABEL, '1d76db', 'Requirements intake for the factory'),
    ):
        try:
            gh(['label', 'create', name, '--color', color,
                '--description', description, '--force'], repo)
        except (RuntimeError, OSError, subprocess.SubprocessError):
            pass  # labels are cosmetic-critical, not run-critical


# --------------------------------------------------------------------------
# ntfy push
# --------------------------------------------------------------------------

def cmd_push(args):
    topic = os.environ.get('NTFY_TOPIC', '').strip()
    if not topic:
        print('NTFY_TOPIC not set; skipping push notification.')
        return 0
    url = topic if '://' in topic else f"https://ntfy.sh/{topic}"
    headers = {
        'Title': args.title.encode('utf-8', 'replace').decode('latin-1', 'replace')[:200],
        'Priority': args.priority,
    }
    if args.tags:
        headers['Tags'] = args.tags
    if args.click:
        headers['Click'] = args.click
    body = (args.message or args.title)[:2000].encode('utf-8')
    request = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read()
        print(f"ntfy push sent ({args.priority}): {args.title}")
    except OSError as exc:
        # Best-effort: the gate issue is the durable surface, so a failed
        # push must not fail the factory step.
        print(f"WARNING: ntfy push failed: {exc}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# Gate issues
# --------------------------------------------------------------------------

def find_open_issue(repo, label, title_prefix=''):
    try:
        raw = gh(['issue', 'list', '--state', 'open', '--label', label,
                  '--json', 'number,title', '--limit', '20'], repo)
        for item in json.loads(raw or '[]'):
            if title_prefix in item.get('title', ''):
                return item['number']
    except (RuntimeError, OSError, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return None


def record_gate_issue(args, number):
    """Persist the gate issue number into the runtime copy of factory.json."""
    if not args.record_runtime:
        return
    path = Path(args.record_runtime)
    try:
        factory = json.loads(path.read_text(encoding='utf-8'))
        factory.setdefault('runtime', {})['gate_issue'] = number
        path.write_text(json.dumps(factory, indent=2) + '\n', encoding='utf-8')
    except (OSError, json.JSONDecodeError) as exc:
        print(f"WARNING: could not record gate issue in {path}: {exc}", file=sys.stderr)


def cmd_needs_you(args):
    repo = args.repo
    if not repo:
        print('No --repo / GITHUB_REPOSITORY; cannot manage gate issues.', file=sys.stderr)
        return 2
    ensure_labels(repo)
    body = Path(args.body_file).read_text(encoding='utf-8') if args.body_file else args.message
    body += f"\n\n_Factory gate `{args.kind}` • updated {utc_now()}_\n"
    title = args.title

    number = args.issue or find_open_issue(repo, NEEDS_YOU_LABEL)
    if number:
        gh(['issue', 'edit', str(number), '--title', title, '--body', body], repo)
        gh(['issue', 'comment', str(number), '--body',
            f"**{title}**\n\n{args.message}"], repo)
        print(f"Updated gate issue #{number}")
    else:
        out = gh(['issue', 'create', '--title', title, '--body', body,
                  '--label', NEEDS_YOU_LABEL], repo)
        number = int(out.strip().rsplit('/', 1)[-1])
        print(f"Opened gate issue #{number}")
    record_gate_issue(args, number)
    output_path = os.environ.get('GITHUB_OUTPUT')
    if output_path:
        with open(output_path, 'a', encoding='utf-8') as handle:
            handle.write(f"gate_issue={number}\n")
    return 0


def cmd_close_gate(args):
    if not args.issue:
        print('No gate issue to close.')
        return 0
    try:
        gh(['issue', 'close', str(args.issue), '--comment',
            args.comment or 'Resolved; the factory is continuing.'], args.repo)
        print(f"Closed gate issue #{args.issue}")
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f"WARNING: could not close gate issue #{args.issue}: {exc}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------

def load_tickets(tickets_dir):
    tickets = []
    base = Path(tickets_dir)
    if not base.is_dir():
        return tickets
    for state_path in sorted(base.glob('*/state.json')):
        if state_path.parent.name == 'TEMPLATE':
            continue
        try:
            state = json.loads(state_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            state = {'ticket_id': state_path.parent.name, 'stage': 'UNREADABLE'}
        tickets.append(state if isinstance(state, dict) else
                       {'ticket_id': state_path.parent.name, 'stage': 'UNREADABLE'})
    return tickets


def render_dashboard(factory, tickets, prs, gates, now=None):
    runtime = factory.get('runtime', {}) if isinstance(factory, dict) else {}
    limits = factory.get('limits', {}) if isinstance(factory, dict) else {}
    lines = [f"# 🏭 {DASHBOARD_TITLE}", '', f"_Updated {now or utc_now()}_", '', '## Factory state', '']
    enabled = factory.get('enabled', False)
    state_label = 'enabled' if enabled else 'DISABLED (.ai/factory.json)'
    if runtime.get('pause_reason') or runtime.get('paused_until'):
        until = runtime.get('paused_until') or 'a human resumes it (`/factory resume`)'
        state_label += f" — **paused** ({runtime.get('pause_reason') or 'paused'}) until {until}"
    lines.append(f"- Status: {state_label}")
    lines.append(f"- Steps today: {runtime.get('steps_today', 0)}/{limits.get('max_steps_per_day', '?')}"
                 f" ({runtime.get('steps_date') or 'no steps yet'})")
    last = runtime.get('last_step') or {}
    if last:
        lines.append(f"- Last step: {last.get('reason', '?')} — {last.get('role', '?')}"
                     f" on {last.get('ticket') or 'n/a'} at {last.get('at', '?')}")
    lines.append(f"- Active ticket: {runtime.get('active_ticket') or 'none'}"
                 + (f" (branch `{runtime.get('active_ticket_branch')}`)"
                    if runtime.get('active_ticket_branch') else ''))

    lines += ['', '## Waiting on you', '']
    if gates:
        for gate in gates:
            lines.append(f"- [#{gate['number']}] {gate['title']} — {gate.get('url', '')}")
    else:
        lines.append('- Nothing — the loop is self-driving.')

    lines += ['', '## Tickets', '']
    if tickets:
        lines.append('| Ticket | Title | Stage | Next actor | Waiting on | PR |')
        lines.append('|---|---|---|---|---|---|')
        total_cost = 0.0
        any_cost = False
        for state in tickets:
            pr = state.get('pull_request') or {}
            pr_cell = f"[#{pr['number']}]({pr['url']})" if pr.get('number') and pr.get('url') else '—'
            title = str(state.get('title', ''))[:60]
            lines.append(
                f"| {state.get('ticket_id', '?')} | {title} | {state.get('stage', '?')} "
                f"| {state.get('next_actor', '—') or '—'} | {state.get('waiting_on', '—') or '—'} "
                f"| {pr_cell} |"
            )
            usage = state.get('ai_usage') or {}
            value = usage.get('ticket_total_estimated_usd')
            if isinstance(value, (int, float)) and value:
                total_cost += value
                any_cost = True
        if any_cost:
            lines += ['', f"Estimated AI cost across ticket ledgers: **${total_cost:.2f} USD** "
                          '(estimates; see `docs/exec-plans/build-cost.md`).']
    else:
        lines.append('No tickets yet — file a build-request issue to start.')

    lines += ['', '## Open PRs', '']
    if prs:
        for pr in prs:
            lines.append(f"- [#{pr.get('number')}]({pr.get('url', '')}) {pr.get('title', '')}")
    else:
        lines.append('- None.')

    lines += [
        '', '## What was done',
        '- Merged PRs: see the repository PR list.',
        '- Per-ticket outcomes: `docs/exec-plans/ticket-change-log.md`; backlog: `docs/agent-backlog.md`.',
        '',
        '_Commands (comment on the gate issue): `/factory resume`, `/factory pause`, `/factory status`._',
    ]
    return '\n'.join(lines) + '\n'


def cmd_dashboard(args):
    try:
        factory = json.loads(Path(args.factory_file).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        factory = {}
    tickets = load_tickets(args.tickets_dir)
    prs = []
    if args.pr_json and Path(args.pr_json).exists():
        try:
            prs = json.loads(Path(args.pr_json).read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            prs = []
    gates = []
    if args.repo:
        try:
            raw = gh(['issue', 'list', '--state', 'open', '--label', NEEDS_YOU_LABEL,
                      '--json', 'number,title,url', '--limit', '10'], args.repo)
            gates = json.loads(raw or '[]')
        except (RuntimeError, OSError, subprocess.SubprocessError, json.JSONDecodeError):
            gates = []

    body = render_dashboard(factory, tickets, prs, gates)
    if args.render_only:
        print(body)
        return 0
    if not args.repo:
        print('No --repo / GITHUB_REPOSITORY; cannot upsert the dashboard issue.', file=sys.stderr)
        return 2
    ensure_labels(args.repo)
    number = find_open_issue(args.repo, DASHBOARD_LABEL, DASHBOARD_TITLE)
    if number:
        gh(['issue', 'edit', str(number), '--body', body], args.repo)
        print(f"Dashboard issue #{number} updated.")
    else:
        out = gh(['issue', 'create', '--title', DASHBOARD_TITLE, '--body', body,
                  '--label', DASHBOARD_LABEL], args.repo)
        number = int(out.strip().rsplit('/', 1)[-1])
        print(f"Dashboard issue #{number} created.")
        try:  # pinning is cosmetic; GraphQL pin can fail without failing the run
            issue_id = gh(['issue', 'view', str(number), '--json', 'id', '-q', '.id'],
                          args.repo).strip()
            gh(['api', 'graphql', '-f',
                f'query=mutation {{ pinIssue(input: {{issueId: "{issue_id}"}}) '
                '{ issue { number } } }'], repo='')
        except (RuntimeError, OSError, subprocess.SubprocessError):
            pass
    return 0


# --------------------------------------------------------------------------

def run_self_test():
    """Offline check: the dashboard renders the fixture state coherently."""
    scenario = FIXTURES_DIR / 'scenarios' / 'review-accepted-needs-approval'
    if not scenario.is_dir():
        print(f"Missing fixtures under {FIXTURES_DIR.relative_to(ROOT)}")
        return 2
    factory = json.loads((scenario / 'factory.json').read_text(encoding='utf-8'))
    tickets = load_tickets(scenario / 'tickets')
    body = render_dashboard(
        factory, tickets,
        prs=[{'number': 7, 'url': 'https://example.test/pr/7', 'title': 'Example PR'}],
        gates=[{'number': 9, 'title': 'Factory needs you', 'url': 'https://example.test/issues/9'}],
        now='2026-06-12T00:00:00Z',
    )
    required = ['Factory dashboard', 'Steps today', '| Ticket |', 'Example PR',
                'Factory needs you', '/factory resume']
    missing = [marker for marker in required if marker not in body]
    if missing:
        print(f"Dashboard render is missing markers: {missing}")
        print('Factory notify self-test FAILED.')
        return 1
    print('Factory notify self-test passed (dashboard renderer).')
    return 0


def add_common(parser):
    parser.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY', ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    push = sub.add_parser('push', help='send an ntfy.sh notification')
    push.add_argument('--title', required=True)
    push.add_argument('--message', default='')
    push.add_argument('--priority', default='default',
                      choices=['min', 'low', 'default', 'high', 'urgent'])
    push.add_argument('--tags', default='factory')
    push.add_argument('--click', default='', help='URL opened when the notification is tapped')

    needs = sub.add_parser('needs-you', help='upsert the gate issue')
    add_common(needs)
    needs.add_argument('--title', required=True)
    needs.add_argument('--message', required=True)
    needs.add_argument('--kind', default='gate')
    needs.add_argument('--body-file', default='')
    needs.add_argument('--issue', type=int, default=0, help='known open gate issue number')
    needs.add_argument('--record-runtime', default='',
                       help='factory.json runtime copy to record the issue number in')

    close = sub.add_parser('close-gate', help='close a resolved gate issue')
    add_common(close)
    close.add_argument('--issue', required=True)
    close.add_argument('--comment', default='')

    dashboard = sub.add_parser('dashboard', help='regenerate the dashboard issue')
    add_common(dashboard)
    dashboard.add_argument('--factory-file', default='.ai/factory.json')
    dashboard.add_argument('--tickets-dir', default='.ai/tickets')
    dashboard.add_argument('--pr-json', default='', help='gh pr list --json number,title,url output')
    dashboard.add_argument('--render-only', action='store_true', help='print markdown, no GitHub calls')

    sub.add_parser('self-test', help='offline dashboard renderer test')

    args = parser.parse_args()
    try:
        if args.command == 'push':
            return cmd_push(args)
        if args.command == 'needs-you':
            return cmd_needs_you(args)
        if args.command == 'close-gate':
            return cmd_close_gate(args)
        if args.command == 'dashboard':
            return cmd_dashboard(args)
        return run_self_test()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
