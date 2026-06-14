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

    def test_refresh_rejects_non_public_urls_before_fetching(self) -> None:
        sources = [
            {"id": "file", "url": "file:///etc/passwd", "category": "test"},
            {"id": "http", "url": "http://example.com/source", "category": "test"},
            {"id": "local", "url": "https://localhost/source", "category": "test"},
            {"id": "loopback", "url": "https://127.0.0.1/source", "category": "test"},
            {"id": "private", "url": "https://10.0.0.1/source", "category": "test"},
            {
                "id": "credentials",
                "url": "https://user:pass@example.com/source",
                "category": "test",
            },
        ]

        with mock.patch.object(refresh_research, "urlopen") as urlopen:
            records = [
                refresh_research._fetch_source(source, timeout=1)
                for source in sources
            ]

        self.assertTrue(all(record["status"] == "error" for record in records))
        urlopen.assert_not_called()

    def test_partial_json_metadata_extracts_package_title(self) -> None:
        title, headings = refresh_research._extract_json_metadata(
            '{"info":{"name":"setuptools","version":"82.0.1",'
            '"summary":"Most extensible Python build backend"},'
        )

        self.assertEqual(title, "setuptools 82.0.1")
        self.assertEqual(headings, ["Most extensible Python build backend"])

    def test_plain_text_metadata_extracts_markdown_headings(self) -> None:
        title, headings = refresh_research._extract_metadata(
            "text/plain",
            "# demo [![CI](https://example.test/badge.svg)](https://example.test)\n"
            "\n"
            "## Install\n"
            "## Contribute\n",
        )

        self.assertEqual(title, "demo")
        self.assertEqual(headings, ["demo", "Install", "Contribute"])

    def test_plain_text_metadata_uses_intro_when_markdown_has_no_h1(self) -> None:
        title, headings = refresh_research._extract_metadata(
            "text/plain",
            "![Logo](https://example.test/logo.png)\n"
            "\n"
            "Useful project tagline.\n"
            "\n"
            "## Install\n",
        )

        self.assertEqual(title, "Useful project tagline.")
        self.assertEqual(headings, ["Install"])

    def test_plain_text_metadata_uses_html_intro_when_present(self) -> None:
        title, headings = refresh_research._extract_metadata(
            "text/plain",
            '<p align="center">\n'
            "  <em>Fast and useful.</em>\n"
            "</p>\n"
            "\n"
            "**Documentation**: [https://example.test](https://example.test)\n"
            "\n"
            "## Install\n",
        )

        self.assertEqual(title, "Fast and useful.")
        self.assertEqual(headings, ["Install"])

    def test_plain_text_metadata_uses_html_heading_when_present(self) -> None:
        title, headings = refresh_research._extract_metadata(
            "text/plain",
            '<h2 align="center">The Useful Tool</h2>\n'
            "\n"
            "> a tagline\n"
            "\n"
            "## Install\n",
        )

        self.assertEqual(title, "The Useful Tool")
        self.assertEqual(headings, ["Install"])

    def test_plain_text_metadata_extracts_rst_headings(self) -> None:
        title, headings = refresh_research._extract_metadata(
            "text/plain",
            "demo\n"
            "====\n"
            "\n"
            "Install\n"
            "-------\n",
        )

        self.assertEqual(title, "demo")
        self.assertEqual(headings, ["demo", "Install"])

    def test_plain_text_metadata_skips_indented_rst_code_blocks(self) -> None:
        title, headings = refresh_research._extract_metadata(
            "text/plain",
            "demo\n"
            "====\n"
            "\n"
            "    content of test_sample.py\n"
            "    -------------------------\n"
            "\n"
            "Features\n"
            "--------\n",
        )

        self.assertEqual(title, "demo")
        self.assertEqual(headings, ["demo", "Features"])

    def test_plain_text_metadata_skips_indented_markdown_code_comments(self) -> None:
        title, headings = refresh_research._extract_metadata(
            "text/plain",
            ".. image:: https://example.test/logo.svg\n"
            "\n"
            "The demo framework helps with tests.\n"
            "\n"
            "    # content of test_sample.py\n"
            "\n"
            "Features\n"
            "--------\n",
        )

        self.assertEqual(title, "The demo framework helps with tests.")
        self.assertEqual(headings, ["Features"])

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
