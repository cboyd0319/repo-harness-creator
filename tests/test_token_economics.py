from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harnessforge.evidence.token_economics import normalize_codex_jsonl_trace


REPO_ROOT = Path(__file__).resolve().parents[1]


def _metadata() -> dict[str, object]:
    return {
        "target": {
            "repoLabel": "demo",
            "commit": "abc123",
            "platform": "macos-26",
        },
        "task": {
            "id": "demo.readme-fix",
            "category": "docs",
            "description": "Make a small README correction.",
            "heldOut": True,
        },
        "agent": {
            "name": "Codex CLI",
            "version": "test",
            "provider": "OpenAI",
            "model": "gpt-test",
        },
        "harnessProfile": {
            "name": "minimal",
            "description": "Root routers only.",
            "changedSurfaces": ["AGENTS.md"],
        },
        "mechanism": {
            "name": "instruction_routing",
            "expectedTokenEffect": "mixed",
            "expectedExecutionEffect": "improve",
            "risk": "Short routers may omit task-relevant detail.",
        },
        "context": {
            "startupFiles": ["AGENTS.md"],
            "lazyLoadedFiles": ["README.md"],
            "staticPrefixChars": 100,
            "dynamicContextChars": 50,
            "loadedHarnessChars": 150,
            "contextWindowTokens": 200000,
        },
        "outcome": {
            "completed": True,
            "verificationVerdict": "passed",
            "qualityScore": 1.0,
            "worstCaseQuality": 1.0,
            "failureMode": None,
        },
        "evidenceRefs": ["docs/harness/evidence/token-economics/demo.json"],
        "limitations": ["Fixture trace; not a live provider run."],
        "promotionStatus": "inconclusive",
    }


class TokenEconomicsTests(unittest.TestCase):
    def test_codex_jsonl_trace_normalizes_to_metric_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp) / "codex.jsonl"
            trace.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "turn.completed",
                                "usage": {
                                    "input_tokens": 1000,
                                    "cached_input_tokens": 200,
                                    "output_tokens": 50,
                                    "reasoning_output_tokens": 25,
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "tool_call",
                                    "name": "read_file",
                                    "path": "README.md",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "item.started",
                                "item": {
                                    "type": "command_execution",
                                    "command": "/bin/zsh -lc \"sed -n '1,20p' docs/harness/research/note.md\"",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "command_execution",
                                    "command": "/bin/zsh -lc \"sed -n '1,20p' docs/harness/research/note.md\"",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "command_execution",
                                    "command": "/bin/zsh -lc 'head -c 12000 feature_list.json'",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "tool_call",
                                    "name": "shell",
                                    "command": "python3 -m unittest tests/test_demo.py",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "tool_call",
                                    "name": "apply_patch",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "type": "file_change",
                                    "path": "demo.py",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "turn.completed",
                                "usage": {
                                    "input_tokens": 800,
                                    "cached_input_tokens": 300,
                                    "output_tokens": 40,
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            record = normalize_codex_jsonl_trace(
                trace,
                _metadata(),
                recorded_at="2026-06-16T12:00:00Z",
            )

        schema = json.loads(
            (
                REPO_ROOT
                / "docs"
                / "harness"
                / "research"
                / "token-economics-metric.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(set(schema["required"]) - {"cost"}, set(record))
        self.assertEqual(
            record["schemaVersion"], "harnessforge.tokenEconomicsMetric.v1"
        )
        self.assertEqual(record["recordedAt"], "2026-06-16T12:00:00Z")
        self.assertEqual(
            record["tokens"],
            {
                "source": "agent_usage_report",
                "startupInput": 1000,
                "cacheWriteInput": None,
                "cacheReadInput": 500,
                "uncachedRepeatedInput": None,
                "output": 90,
                "reasoningOutput": 25,
                "total": 1915,
            },
        )
        self.assertEqual(
            record["trajectory"],
            {
                "turns": 2,
                "toolCalls": 6,
                "fileReads": 3,
                "searchCalls": 0,
                "editCalls": 2,
                "verificationRuns": 1,
                "retries": 0,
                "durationSeconds": None,
            },
        )

    def test_codex_jsonl_trace_rejects_malformed_jsonl_with_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp) / "codex.jsonl"
            trace.write_text('{"type":"turn.completed"}\nnot json\n', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "line 2"):
                normalize_codex_jsonl_trace(trace, _metadata())

    def test_committed_token_economics_records_have_required_shape(self) -> None:
        schema = json.loads(
            (
                REPO_ROOT
                / "docs"
                / "harness"
                / "research"
                / "token-economics-metric.schema.json"
            ).read_text(encoding="utf-8")
        )
        records = sorted(
            (
                REPO_ROOT
                / "docs"
                / "harness"
                / "evidence"
                / "token-economics"
            ).glob("*.json")
        )

        self.assertTrue(records)
        required = set(schema["required"])
        token_required = set(schema["properties"]["tokens"]["required"])
        trajectory_required = set(schema["properties"]["trajectory"]["required"])
        for path in records:
            with self.subTest(path=path.name):
                raw = path.read_text(encoding="utf-8")
                record = json.loads(raw)
                self.assertEqual(
                    record["schemaVersion"], "harnessforge.tokenEconomicsMetric.v1"
                )
                self.assertLessEqual(required, set(record))
                self.assertLessEqual(token_required, set(record["tokens"]))
                self.assertLessEqual(trajectory_required, set(record["trajectory"]))
                self.assertNotIn("/Users/", raw)
                self.assertNotIn("C:\\Users", raw)


if __name__ == "__main__":
    unittest.main()
