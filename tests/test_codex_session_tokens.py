import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts import codex_session_tokens as codex


class CodexSessionTokensTests(unittest.TestCase):
    def _write_session(self, root: Path, day: str, name: str, *, sid: str, cwd: str, ticket: str, usage: dict, thread_source: str = "user", mtime: int = 1, model: str | None = "gpt-5.5") -> Path:
        session_dir = root / day
        session_dir.mkdir(parents=True, exist_ok=True)
        path = session_dir / name
        meta = {"type": "session_meta", "payload": {"id": sid, "cwd": cwd, "thread_source": thread_source, "model_provider": model}}
        user = {"type": "event_msg", "payload": {"type": "user_message", "role": "user", "text": f"Work on {ticket}"}}
        token = {"type": "event_msg", "timestamp": "2026-06-10T00:00:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": usage}}}
        path.write_text("\n".join(json.dumps(x) for x in [meta, user, token]) + "\n", encoding="utf-8")
        os.utime(path, (mtime, mtime))
        return path

    def _args(self, root: Path, cwd: str, **kwargs):
        argv = ["--sessions-root", str(root), "--session-index", str(root / "missing-index.jsonl"), "--cwd", cwd, "--ticket-id", kwargs.pop("ticket_id", "TKT-1")]
        for key, value in kwargs.items():
            flag = "--" + key.replace("_", "-")
            if value is True:
                argv.append(flag)
            elif value is not False and value is not None:
                argv.extend([flag, str(value)])
        return codex.parse_args(argv)

    def test_finds_newest_matching_codex_jsonl_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            usage = {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": 3}
            self._write_session(root, "2026/06/09", "rollout-old.jsonl", sid="old", cwd=cwd, ticket="TKT-1", usage=usage, mtime=10)
            self._write_session(root, "2026/06/10", "rollout-new.jsonl", sid="new", cwd=cwd, ticket="TKT-1", usage=usage, mtime=20)
            out = codex.build_output(self._args(root, cwd))
            self.assertEqual(out["session_id"], "new")
            self.assertEqual(out["source"], "session_jsonl")

    def test_extracts_last_token_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            path = self._write_session(root, "2026/06/10", "rollout-one.jsonl", sid="one", cwd=cwd, ticket="TKT-1", usage={"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": 3}, mtime=20)
            later = {"type": "event_msg", "timestamp": "2026-06-10T00:01:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 7, "reasoning_output_tokens": 4, "total_tokens": 17}}}}
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(later) + "\n")
            out = codex.build_output(self._args(root, cwd))
            self.assertEqual(out["input_tokens"], 10)
            self.assertEqual(out["output_tokens"], 7)
            self.assertEqual(out["reasoning_output_tokens"], 4)
            self.assertEqual(out["total_tokens"], 17)

    def test_since_until_filter_token_count_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            path = self._write_session(root, "2026/06/10", "rollout-windowed.jsonl", sid="windowed", cwd=cwd, ticket="TKT-1", usage={"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": 3}, mtime=20)
            records = [
                {"type": "event_msg", "timestamp": "2026-06-10T00:05:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 5, "cached_input_tokens": 1, "output_tokens": 4, "reasoning_output_tokens": 2, "total_tokens": 9}}}},
                {"type": "event_msg", "timestamp": "2026-06-10T00:10:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 7, "reasoning_output_tokens": 4, "total_tokens": 17}}}},
            ]
            with path.open("a", encoding="utf-8") as handle:
                for record in records:
                    handle.write(json.dumps(record) + "\n")

            out = codex.build_output(self._args(root, cwd, since="2026-06-10T00:02:00Z", until="2026-06-10T00:06:00Z"))

            self.assertEqual(out["session_id"], "windowed")
            self.assertEqual(out["input_tokens"], 5)
            self.assertEqual(out["output_tokens"], 4)
            self.assertEqual(out["session_last_token_count_at"], "2026-06-10T00:05:00Z")
            self.assertIn("since", out["matching_reasons"])
            self.assertIn("until", out["matching_reasons"])

    def test_since_until_exclude_sessions_without_windowed_token_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            self._write_session(root, "2026/06/10", "rollout-outside.jsonl", sid="outside", cwd=cwd, ticket="TKT-1", usage={"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": 3}, mtime=20)

            out = codex.build_output(self._args(root, cwd, since="2026-06-10T00:02:00Z", until="2026-06-10T00:06:00Z"))

            self.assertEqual(out["source"], "not_available")

    def test_payload_message_string_is_parsed_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            session_dir = root / "2026/06/10"
            session_dir.mkdir(parents=True, exist_ok=True)
            path = session_dir / "rollout-string-message.jsonl"
            records = [
                {"type": "session_meta", "payload": {"id": "string-message", "cwd": cwd, "thread_source": "user", "model_provider": "gpt-5.5"}},
                {"type": "event_msg", "payload": {"type": "user_message", "message": "Work on TKT-1"}},
                {"type": "event_msg", "timestamp": "2026-06-10T00:00:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 4, "cached_input_tokens": 1, "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": 6}}}},
            ]
            path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            out = codex.build_output(self._args(root, cwd))
            self.assertEqual(out["source"], "session_jsonl")
            self.assertEqual(out["session_id"], "string-message")
            self.assertEqual(out["total_tokens"], 6)

    def test_payload_message_dict_with_role_and_content_matches_ticket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            session_dir = root / "2026/06/10"
            session_dir.mkdir(parents=True, exist_ok=True)
            path = session_dir / "rollout-dict-message.jsonl"
            records = [
                {"type": "session_meta", "payload": {"id": "dict-message", "cwd": cwd, "thread_source": "user", "model_provider": "gpt-5.5"}},
                {"type": "event_msg", "payload": {"message": {"role": "user", "content": "Please work on TKT-1"}}},
                {"type": "event_msg", "timestamp": "2026-06-10T00:00:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 5, "cached_input_tokens": 0, "output_tokens": 3, "reasoning_output_tokens": 1, "total_tokens": 8}}}},
            ]
            path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            out = codex.build_output(self._args(root, cwd))
            self.assertEqual(out["source"], "session_jsonl")
            self.assertEqual(out["session_id"], "dict-message")
            self.assertEqual(out["input_tokens"], 5)
            self.assertIn("ticket_id", out["matching_reasons"])

    def test_malformed_payload_shapes_are_skipped_safely(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            session_dir = root / "2026/06/10"
            session_dir.mkdir(parents=True, exist_ok=True)
            path = session_dir / "rollout-malformed.jsonl"
            records = [
                ["not", "a", "dict"],
                {"type": "session_meta", "payload": {"id": "malformed", "cwd": cwd, "thread_source": "user", "model_provider": "gpt-5.5"}},
                {"type": "event_msg", "payload": "string payload"},
                {"type": "event_msg", "payload": {"type": "token_count", "info": "not a dict"}},
                {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": "not a dict"}}},
                {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": "not an int"}}}},
            ]
            path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            out = codex.build_output(self._args(root, cwd, allow_ticket_mismatch=True))
            self.assertEqual(out["source"], "not_available")
            self.assertEqual(out["excluded_subagent_sessions"], 0)

    def test_computes_deltas_from_previous_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            checkpoint = root / "checkpoint.json"
            checkpoint.write_text(json.dumps({"tokens": {"input_tokens": 4, "cached_input_tokens": 1, "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": 6}}), encoding="utf-8")
            self._write_session(root, "2026/06/10", "rollout-one.jsonl", sid="one", cwd=cwd, ticket="TKT-1", usage={"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 7, "reasoning_output_tokens": 4, "total_tokens": 17}, mtime=20)
            out = codex.build_output(self._args(root, cwd, previous_checkpoint=checkpoint))
            self.assertEqual(out["checkpoint_type"], "delta")
            self.assertEqual(out["input_tokens"], 6)
            self.assertEqual(out["cached_input_tokens"], 2)
            self.assertEqual(out["output_tokens"], 5)
            self.assertEqual(out["total_tokens"], 11)

    def test_excludes_subagent_sessions_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            usage = {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 2, "reasoning_output_tokens": 1, "total_tokens": 3}
            self._write_session(root, "2026/06/10", "rollout-main.jsonl", sid="main", cwd=cwd, ticket="TKT-1", usage=usage, thread_source="user", mtime=10)
            self._write_session(root, "2026/06/10", "rollout-sub.jsonl", sid="sub", cwd=cwd, ticket="TKT-1", usage={**usage, "input_tokens": 99, "total_tokens": 101}, thread_source="subagent", mtime=20)
            out = codex.build_output(self._args(root, cwd))
            self.assertEqual(out["session_id"], "main")
            self.assertEqual(out["excluded_subagent_sessions"], 1)
            included = codex.build_output(self._args(root, cwd, include_subagents=True))
            self.assertEqual(included["session_id"], "sub")

    def test_missing_model_uses_partial_latest_model_scenario_not_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = str(root / "repo")
            self._write_session(root, "2026/06/10", "rollout-one.jsonl", sid="one", cwd=cwd, ticket="TKT-1", usage={"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 7, "reasoning_output_tokens": 4, "total_tokens": 17}, model=None, mtime=20)
            out = codex.build_output(self._args(root, cwd))
            self.assertEqual(out["source"], "session_jsonl")
            self.assertEqual(out["cost_confidence"], "partial")
            self.assertEqual(out["pricing_scenario_model"], codex.LATEST_OPENAI_SCENARIO_MODEL)
            self.assertIsNotNone(out["estimated_cost_usd"])


if __name__ == "__main__":
    unittest.main()
