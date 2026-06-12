#!/usr/bin/env python3
"""Summarize Claude Code session token usage from ~/.claude/projects/*/*.jsonl.

Outputs a single JSON object suitable for a state.json ai_usage entry.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import date, datetime, timezone

# Regenerate for another machine by taking absolute repo path and replacing ':' and '\\' with '-'.
WINDOWS_REPO_SLUG = "c--Users-blackwoodt-OneDrive---Fahan-School-Repositories-Incident-Reponse-Simulation"
PRICES_AS_OF = "2026-05-25"
MAX_PRICE_AGE_DAYS = 183

# USD per 1M tokens. Source: anthropic.com/pricing and docs.anthropic.com pricing table on 2026-05-25.
# Anthropic does not currently publish separate entries named "Opus 4.7" or "Haiku 4.5" in these tables;
# values below use nearest published families (Opus 4.1 and Sonnet 4; Haiku 4.5 is left unavailable).
PRICES = {
    "claude-opus-4-7": {"input": 15.0, "output": 75.0, "cache_write_5m": 18.75, "cache_write_1h": 30.0, "cache_read": 1.5},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0, "cache_write_5m": 3.75, "cache_write_1h": 6.0, "cache_read": 0.30},
    "claude-haiku-4-5": None,
}


def _possible_project_dirs() -> list[Path]:
    home = Path.home()
    base = home / ".claude" / "projects"
    candidates = []
    if WINDOWS_REPO_SLUG:
        candidates.append(base / WINDOWS_REPO_SLUG)
    # Portable fallback for current machine/repo.
    repo_slug = str(Path.cwd().resolve()).replace(":", "-").replace("\\", "-").replace("/", "-")
    candidates.append(base / repo_slug)
    return candidates


def _latest_jsonl(project_dir: Path) -> Path:
    files = [p for p in project_dir.glob("*.jsonl") if p.is_file()]
    if not files:
        raise FileNotFoundError(f"No .jsonl sessions found under {project_dir}")
    return max(files, key=lambda p: p.stat().st_mtime)


def _model_key(name: str) -> str:
    n = (name or "").lower()
    if "opus" in n:
        return "claude-opus-4-7"
    if "sonnet" in n:
        return "claude-sonnet-4-6"
    if "haiku" in n:
        return "claude-haiku-4-5"
    return "unknown"


def main() -> int:
    project_dir = None
    for c in _possible_project_dirs():
        if c.exists():
            project_dir = c
            break
    if project_dir is None:
        raise FileNotFoundError("Could not find ~/.claude/projects/<repo-slug> directory")

    session_file = _latest_jsonl(project_dir)
    # Caveat: if multiple Claude Code windows are active for this repo, "latest modified" can select a different session.

    totals = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0}
    per_model: dict[str, dict[str, float]] = {}

    with session_file.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            msg = obj.get("message") or {}
            usage = msg.get("usage") or {}
            if not usage:
                continue
            model = msg.get("model") or "unknown"
            mkey = _model_key(model)

            inp = int(usage.get("input_tokens", 0) or 0)
            out = int(usage.get("output_tokens", 0) or 0)
            cc = int(usage.get("cache_creation_input_tokens", 0) or 0)
            cr = int(usage.get("cache_read_input_tokens", 0) or 0)

            totals["input"] += inp
            totals["output"] += out
            totals["cache_creation"] += cc
            totals["cache_read"] += cr

            slot = per_model.setdefault(mkey, {
                "model_observed": model,
                "input": 0,
                "output": 0,
                "cache_creation": 0,
                "cache_creation_5m": 0,
                "cache_creation_1h": 0,
                "cache_read": 0,
                "usd_estimate": None,
            })
            slot["input"] += inp
            slot["output"] += out
            slot["cache_creation"] += cc
            slot["cache_read"] += cr

            breakdown = usage.get("cache_creation_input_tokens_breakdown") or {}
            c5 = int(breakdown.get("ephemeral_5m_input_tokens", 0) or 0)
            c1h = int(breakdown.get("ephemeral_1h_input_tokens", 0) or 0)
            if c5 or c1h:
                slot["cache_creation_5m"] += c5
                slot["cache_creation_1h"] += c1h
            else:
                slot["cache_creation_5m"] += cc

    total_usd = 0.0
    stale_prices = (date.today() - date.fromisoformat(PRICES_AS_OF)).days > MAX_PRICE_AGE_DAYS
    if not stale_prices:
        for key, bucket in per_model.items():
            pricing = PRICES.get(key)
            if not pricing:
                continue
            usd = (
                bucket["input"] / 1_000_000 * pricing["input"]
                + bucket["output"] / 1_000_000 * pricing["output"]
                + bucket["cache_creation_5m"] / 1_000_000 * pricing["cache_write_5m"]
                + bucket["cache_creation_1h"] / 1_000_000 * pricing["cache_write_1h"]
                + bucket["cache_read"] / 1_000_000 * pricing["cache_read"]
            )
            bucket["usd_estimate"] = round(usd, 6)
            total_usd += usd

    out = {
        "source": "session_jsonl",
        "session_file": session_file.name,
        "tokens": {
            **totals,
            "total": totals["input"] + totals["output"] + totals["cache_creation"] + totals["cache_read"],
        },
        "per_model": per_model,
        "usd_estimate": None if stale_prices else round(total_usd, 6),
        "prices_as_of": PRICES_AS_OF,
        "confidence": "high_for_tokens_medium_for_usd" if not stale_prices else "high_for_tokens_unknown_for_usd",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "notes": (
            f"USD estimate from Anthropic pricing as of {PRICES_AS_OF}; subscription usage is flat-billed, so this is planning-only."
            if not stale_prices
            else f"Pricing table is older than ~6 months (as-of {PRICES_AS_OF}); USD estimate omitted."
        ),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
