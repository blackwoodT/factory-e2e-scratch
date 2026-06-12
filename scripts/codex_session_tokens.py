#!/usr/bin/env python3
"""Extract Codex token usage from local session JSONL.

Outputs a single JSON object suitable for adapting into a state.json
ai_usage.entries[*] record. The script is intentionally non-interactive and
avoids `codex resume --all`, which requires a real TTY.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# USD per 1M tokens. Source: OpenAI API pricing docs on 2026-06-10.
# Keep these fresh when the workflow pricing freshness rule says they are stale.
PRICES_AS_OF = "2026-06-10"
PRICING_SOURCE = "https://openai.com/api/pricing/"
LATEST_OPENAI_SCENARIO_MODEL = "gpt-5.5"
OPENAI_PRICES: dict[str, dict[str, float]] = {
    "gpt-5.5": {"input": 5.00, "cached_input": 0.50, "output": 30.00},
    "gpt-5.4": {"input": 2.50, "cached_input": 0.25, "output": 15.00},
    "gpt-5.4-mini": {"input": 0.75, "cached_input": 0.075, "output": 6.00},
    "gpt-5.2": {"input": 1.75, "cached_input": 0.175, "output": 14.00},
    "gpt-5.2-codex": {"input": 1.75, "cached_input": 0.175, "output": 14.00},
    "gpt-5.1": {"input": 1.25, "cached_input": 0.125, "output": 10.00},
    "gpt-5.1-codex": {"input": 1.25, "cached_input": 0.125, "output": 10.00},
    "gpt-5.1-codex-max": {"input": 1.25, "cached_input": 0.125, "output": 10.00},
    "gpt-5": {"input": 1.25, "cached_input": 0.125, "output": 10.00},
    "gpt-5-codex": {"input": 1.25, "cached_input": 0.125, "output": 10.00},
    "gpt-5-mini": {"input": 0.25, "cached_input": 0.025, "output": 2.00},
    "gpt-5-nano": {"input": 0.05, "cached_input": 0.005, "output": 0.40},
}
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


@dataclass
class SessionCandidate:
    path: Path
    meta: dict[str, Any]
    last_usage: dict[str, int]
    last_usage_at: str | None
    first_user_text: str
    mtime: float
    score: int
    reasons: list[str]


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _event_timestamp(obj: dict[str, Any], payload: dict[str, Any]) -> str | None:
    for value in (obj.get("timestamp"), payload.get("timestamp"), payload.get("time")):
        if isinstance(value, str) and value:
            return value
    return None


def _within_bounds(timestamp: str | None, since: datetime | None, until: datetime | None) -> bool:
    if since is None and until is None:
        return True
    event_dt = _parse_dt(timestamp)
    if event_dt is None:
        return False
    if since and event_dt < since:
        return False
    if until and event_dt > until:
        return False
    return True


def _default_sessions_root() -> Path:
    return Path.home() / ".codex" / "sessions"


def _default_session_index() -> Path:
    return Path.home() / ".codex" / "session_index.jsonl"


def _iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


def _payload_dict(obj: dict[str, Any]) -> dict[str, Any]:
    payload = obj.get("payload")
    return payload if isinstance(payload, dict) else {}


def _message_dict(payload: dict[str, Any]) -> dict[str, Any]:
    message = payload.get("message")
    return message if isinstance(message, dict) else {}


def _token_usage(usage: Any) -> dict[str, int] | None:
    if not isinstance(usage, dict):
        return None
    try:
        return {field: int(usage.get(field, 0) or 0) for field in TOKEN_FIELDS}
    except (TypeError, ValueError):
        return None


def _index_text(session_index: Path | None, session_id: str | None, session_path: Path) -> str:
    if not session_index or not session_index.exists():
        return ""
    chunks: list[str] = []
    session_name = session_path.name
    for obj in _iter_jsonl(session_index):
        encoded = json.dumps(obj, sort_keys=True)
        if (session_id and session_id in encoded) or session_name in encoded:
            chunks.append(encoded)
    return "\n".join(chunks)


def _extract_message_text(obj: dict[str, Any]) -> str:
    payload = _payload_dict(obj)
    for key in ("text", "message", "content", "thread_name", "title"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    message = _message_dict(payload)
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return "\n".join(parts)
    return ""


def _is_user_message(obj: dict[str, Any]) -> bool:
    payload = _payload_dict(obj)
    role = payload.get("role") or _message_dict(payload).get("role")
    kind = payload.get("type") or obj.get("type")
    return role == "user" or kind in {"user_message", "input_text"}


def _read_session(
    path: Path,
    since: datetime | None = None,
    until: datetime | None = None,
) -> tuple[dict[str, Any], dict[str, int], str | None, str]:
    meta: dict[str, Any] = {}
    last_usage: dict[str, int] = {}
    last_usage_at: str | None = None
    first_user_text = ""
    for obj in _iter_jsonl(path):
        if obj.get("type") == "session_meta" and isinstance(obj.get("payload"), dict):
            meta = obj["payload"]
            continue
        payload = _payload_dict(obj)
        if obj.get("type") == "event_msg" and payload.get("type") == "token_count":
            timestamp = _event_timestamp(obj, payload)
            if not _within_bounds(timestamp, since, until):
                continue
            info = payload.get("info")
            usage = info.get("total_token_usage") if isinstance(info, dict) else None
            tokens = _token_usage(usage)
            if tokens is not None:
                last_usage = tokens
                last_usage_at = timestamp
            continue
        if not first_user_text and _is_user_message(obj):
            first_user_text = _extract_message_text(obj)
    return meta, last_usage, last_usage_at, first_user_text


def _candidate_paths(sessions_root: Path) -> list[Path]:
    if sessions_root.is_file():
        return [sessions_root]
    return [p for p in sessions_root.glob("**/rollout-*.jsonl") if p.is_file()]


def _model_from_meta(meta: dict[str, Any]) -> str | None:
    for key in ("model", "model_slug", "model_provider"):
        value = meta.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _normal_model_key(model: str | None) -> str | None:
    if not model:
        return None
    lowered = model.lower()
    for key in sorted(OPENAI_PRICES, key=len, reverse=True):
        if key in lowered:
            return key
    return None


def _score_candidate(
    path: Path,
    meta: dict[str, Any],
    first_user_text: str,
    index_text: str,
    last_usage_at: str | None,
    args: argparse.Namespace,
) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    if args.session_id and meta.get("id") == args.session_id:
        score += 1000
        reasons.append("session_id")
    if args.cwd:
        meta_cwd = meta.get("cwd")
        try:
            if meta_cwd and Path(str(meta_cwd)).resolve() == Path(args.cwd).resolve():
                score += 100
                reasons.append("cwd")
        except OSError:
            if meta_cwd == args.cwd:
                score += 100
                reasons.append("cwd")
    if args.ticket_id:
        haystack = "\n".join([first_user_text, index_text, path.name]).lower()
        if args.ticket_id.lower() in haystack:
            score += 50
            reasons.append("ticket_id")
    since = _parse_dt(args.since)
    until = _parse_dt(args.until)
    usage_dt = _parse_dt(last_usage_at)
    mtime_dt = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    comparison_dt = usage_dt or mtime_dt
    if since and comparison_dt >= since:
        score += 10
        reasons.append("since")
    if until and comparison_dt <= until:
        score += 10
        reasons.append("until")
    return score, reasons


def find_candidates(args: argparse.Namespace) -> tuple[list[SessionCandidate], int]:
    paths = _candidate_paths(Path(args.sessions_root))
    candidates: list[SessionCandidate] = []
    excluded_subagents = 0
    since = _parse_dt(args.since)
    until = _parse_dt(args.until)
    for path in paths:
        meta, last_usage, last_usage_at, first_user_text = _read_session(path, since, until)
        thread_source = meta.get("thread_source")
        if thread_source == "subagent" and not args.include_subagents:
            excluded_subagents += 1
            continue
        if args.thread_source and thread_source != args.thread_source:
            continue
        if not last_usage:
            continue
        index = _index_text(Path(args.session_index) if args.session_index else None, meta.get("id"), path)
        score, reasons = _score_candidate(path, meta, first_user_text, index, last_usage_at, args)
        if args.session_id and meta.get("id") != args.session_id:
            continue
        if args.cwd and "cwd" not in reasons and not args.allow_cwd_mismatch:
            continue
        if args.ticket_id and "ticket_id" not in reasons and not args.allow_ticket_mismatch:
            continue
        candidates.append(
            SessionCandidate(
                path=path,
                meta=meta,
                last_usage=last_usage,
                last_usage_at=last_usage_at,
                first_user_text=first_user_text,
                mtime=path.stat().st_mtime,
                score=score,
                reasons=reasons,
            )
        )
    candidates.sort(key=lambda c: (c.score, c.mtime), reverse=True)
    return candidates, excluded_subagents


def _previous_checkpoint(path: str | None) -> dict[str, int] | None:
    if not path:
        return None
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "tokens" in data and isinstance(data["tokens"], dict):
        data = data["tokens"]
    return {field: int(data.get(field, 0) or 0) for field in TOKEN_FIELDS}


def _delta(current: dict[str, int], previous: dict[str, int] | None) -> tuple[dict[str, int], bool]:
    if previous is None:
        return dict(current), False
    return {field: max(0, current.get(field, 0) - previous.get(field, 0)) for field in TOKEN_FIELDS}, True


def _cost(tokens: dict[str, int], model: str | None) -> tuple[float | None, str | None, str, str]:
    key = _normal_model_key(model)
    if key:
        rates = OPENAI_PRICES[key]
        confidence = "exact" if model and model.lower() == key else "partial"
        scenario = None if confidence == "exact" else key
    else:
        rates = OPENAI_PRICES[LATEST_OPENAI_SCENARIO_MODEL]
        confidence = "partial"
        scenario = LATEST_OPENAI_SCENARIO_MODEL
    uncached_input = max(0, tokens.get("input_tokens", 0) - tokens.get("cached_input_tokens", 0))
    amount = (
        uncached_input * rates["input"]
        + tokens.get("cached_input_tokens", 0) * rates["cached_input"]
        + tokens.get("output_tokens", 0) * rates["output"]
    ) / 1_000_000
    return round(amount, 6), key, confidence, scenario


def build_output(args: argparse.Namespace) -> dict[str, Any]:
    candidates, excluded_subagents = find_candidates(args)
    if not candidates:
        return {
            "source": "not_available",
            "confidence": "unknown",
            "tool": "codex",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "notes": "No matching Codex session JSONL with token_count events found after attempting local JSONL parsing.",
            "excluded_subagent_sessions": excluded_subagents,
        }
    selected = candidates[0]
    previous = _previous_checkpoint(args.previous_checkpoint)
    tokens, has_delta = _delta(selected.last_usage, previous)
    model_observed = _model_from_meta(selected.meta)
    estimated_cost, price_model, cost_confidence, scenario = _cost(tokens, model_observed)
    confidence = "exact" if has_delta else "partial"
    notes = [
        "Parsed local Codex session JSONL non-interactively.",
        "Cost formula uses input minus cached input, cached input, and output tokens only; reasoning_output_tokens is reported as detail and is not added a second time.",
    ]
    if has_delta:
        notes.append("Token values are deltas from the supplied previous checkpoint.")
    else:
        notes.append("No previous checkpoint supplied; token values are a cumulative snapshot.")
    if scenario:
        notes.append(
            f"Observed exact model slug was missing or not recognized; estimated_cost_usd is a planning scenario using latest OpenAI model {scenario} rates, not an exact invoice."
        )
    notes.append("Codex subscription/seat-based usage may not be API-billed; treat estimated cost as planning-only.")
    return {
        "workflow_event": args.workflow_event,
        "actor": args.actor,
        "tool": "codex",
        "model": model_observed,
        "input_tokens": tokens["input_tokens"],
        "cached_input_tokens": tokens["cached_input_tokens"],
        "output_tokens": tokens["output_tokens"],
        "reasoning_output_tokens": tokens["reasoning_output_tokens"],
        "total_tokens": tokens["total_tokens"],
        "estimated_cost_usd": estimated_cost,
        "source": "session_jsonl",
        "confidence": confidence,
        "pricing_source": PRICING_SOURCE,
        "prices_as_of": PRICES_AS_OF,
        "price_model": price_model,
        "pricing_scenario_model": scenario,
        "cost_confidence": cost_confidence,
        "session_id": selected.meta.get("id"),
        "session_file": str(selected.path),
        "session_thread_source": selected.meta.get("thread_source"),
        "session_last_token_count_at": selected.last_usage_at,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint_type": "delta" if has_delta else "cumulative_snapshot",
        "matching_reasons": selected.reasons,
        "excluded_subagent_sessions": excluded_subagents,
        "notes": " ".join(notes),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-root", default=os.environ.get("CODEX_SESSIONS_ROOT", str(_default_sessions_root())))
    parser.add_argument("--session-index", default=os.environ.get("CODEX_SESSION_INDEX", str(_default_session_index())))
    parser.add_argument("--session-id")
    parser.add_argument("--cwd", default=str(Path.cwd()))
    parser.add_argument("--ticket-id")
    parser.add_argument("--since", help="ISO timestamp for handoff/baton matching lower bound")
    parser.add_argument("--until", help="ISO timestamp for handoff/baton matching upper bound")
    parser.add_argument("--previous-checkpoint", help="JSON file containing prior token counts or a prior helper output")
    parser.add_argument("--include-subagents", action="store_true")
    parser.add_argument("--thread-source")
    parser.add_argument("--allow-cwd-mismatch", action="store_true")
    parser.add_argument("--allow-ticket-mismatch", action="store_true")
    parser.add_argument("--workflow-event", default="codex_usage_capture")
    parser.add_argument("--actor", default="unknown")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(json.dumps(build_output(args), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
