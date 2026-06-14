from __future__ import annotations

import json
import tempfile
import unittest
import contextlib
import io
from io import BytesIO
from pathlib import Path
from unittest import mock

from scripts import refresh_research


class _FakeResponse:
    status = 200
    headers = {"content-type": "text/html; charset=utf-8"}

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return BytesIO(
            b"<html><head><title>Harness Source</title></head>"
            b"<body><h1>Main Finding</h1><h2>Second Finding</h2></body></html>"
        ).read(size)


class RefreshResearchTests(unittest.TestCase):
    def test_refresh_writes_lock_and_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs/harness").mkdir(parents=True)
            (root / "docs/harness/research-sources.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "sources": [
                            {
                                "id": "demo",
                                "url": "https://example.test/source",
                                "category": "test",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with (
                mock.patch.object(refresh_research, "urlopen", return_value=_FakeResponse()),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                code = refresh_research.main(["--root", str(root)])

            lock = json.loads(
                (root / "docs/harness/research-sources.lock.json").read_text(
                    encoding="utf-8"
                )
            )
            inbox = (root / "docs/harness/research-inbox.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(code, 0)
        self.assertEqual(lock["failureCount"], 0)
        self.assertEqual(lock["sources"][0]["title"], "Harness Source")
        self.assertIn("Main Finding", inbox)

    def test_partial_json_metadata_extracts_package_title(self) -> None:
        title, headings = refresh_research._extract_json_metadata(
            '{"info":{"name":"setuptools","version":"82.0.1",'
            '"summary":"Most extensible Python build backend"},'
        )

        self.assertEqual(title, "setuptools 82.0.1")
        self.assertEqual(headings, ["Most extensible Python build backend"])

    def test_research_source_template_matches_repo_source_ids(self) -> None:
        root = Path(__file__).resolve().parents[1]
        repo_sources = json.loads(
            (root / "docs/harness/research-sources.json").read_text(encoding="utf-8")
        )
        template_sources = json.loads(
            (
                root
                / "src/repo_harness_creator/templates/research-sources.json.tmpl"
            ).read_text(encoding="utf-8").replace("{{generated_date}}", "2026-06-14")
        )

        repo_ids = [source["id"] for source in repo_sources["sources"]]
        template_ids = [source["id"] for source in template_sources["sources"]]
        self.assertEqual(repo_ids, template_ids)
        self.assertEqual(len(repo_ids), len(set(repo_ids)))


if __name__ == "__main__":
    unittest.main()
