#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H_RE = re.compile(r"<h([12])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh harness research metadata.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    source_path = root / "docs/harness/research-sources.json"
    lock_path = root / "docs/harness/research-sources.lock.json"
    inbox_path = root / "docs/harness/research-inbox.md"
    data = json.loads(source_path.read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        print("research-sources.json has no sources", file=sys.stderr)
        return 1

    checked_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    records = []
    failures = 0
    for source in sources:
        if not isinstance(source, dict):
            continue
        record = _fetch_source(source, timeout=args.timeout)
        if record["status"] != "ok":
            failures += 1
        records.append(record)

    lock = {
        "version": 1,
        "checkedAt": checked_at,
        "sourceCount": len(records),
        "failureCount": failures,
        "sources": records,
    }
    lock_path.write_text(f"{json.dumps(lock, indent=2, sort_keys=True)}\n", encoding="utf-8")
    inbox_path.write_text(_render_inbox(lock), encoding="utf-8")
    print(f"Refreshed {len(records)} research sources with {failures} failures.")
    return 1 if failures == len(records) else 0


def _fetch_source(source: dict[str, Any], *, timeout: int) -> dict[str, Any]:
    source_id = str(source.get("id", "unknown"))
    url = str(source.get("url", ""))
    category = str(source.get("category", "uncategorized"))
    base = {"id": source_id, "url": url, "category": category}
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "repo-harness-creator research refresh",
                "Accept": "application/json,text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
            },
        )
        with urlopen(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 200))
            content_type = response.headers.get("content-type", "")
            raw = response.read(512_000)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {**base, "status": "error", "error": str(exc)}

    text = raw.decode("utf-8", errors="replace")
    title, headings = _extract_metadata(content_type, text)
    return {
        **base,
        "status": "ok" if 200 <= status < 400 else "error",
        "httpStatus": status,
        "contentType": content_type.split(";", 1)[0].strip(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "title": title,
        "headings": headings,
    }


def _extract_metadata(content_type: str, text: str) -> tuple[str, list[str]]:
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type == "application/json":
        return _extract_json_metadata(text)
    title = _first_match(TITLE_RE, text)
    headings = [_clean(match.group(2)) for match in H_RE.finditer(text)]
    return title, [heading for heading in headings if heading][:8]


def _extract_json_metadata(text: str) -> tuple[str, list[str]]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return _extract_partial_json_metadata(text)
    if isinstance(parsed, dict):
        info = parsed.get("info")
        if isinstance(info, dict):
            name = str(info.get("name") or "").strip()
            version = str(info.get("version") or "").strip()
            summary = str(info.get("summary") or "").strip()
            title = " ".join(part for part in (name, version) if part)
            headings = [summary] if summary else []
            return title, headings[:8]
        title = str(parsed.get("title") or parsed.get("name") or "").strip()
        headings = [str(key) for key in sorted(parsed)[:8]]
        return title, headings
    return "", []


def _extract_partial_json_metadata(text: str) -> tuple[str, list[str]]:
    name = _json_string_field(text, "name")
    version = _json_string_field(text, "version")
    summary = _json_string_field(text, "summary")
    title = " ".join(part for part in (name, version) if part)
    headings = [summary] if summary else []
    return title, headings[:8]


def _json_string_field(text: str, field: str) -> str:
    match = re.search(rf'"{re.escape(field)}"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
    if not match:
        return ""
    try:
        return str(json.loads(f'"{match.group(1)}"'))
    except json.JSONDecodeError:
        return match.group(1)


def _first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return _clean(match.group(1)) if match else ""


def _clean(text: str) -> str:
    unescaped = html.unescape(TAG_RE.sub(" ", text))
    return " ".join(unescaped.split())


def _render_inbox(lock: dict[str, Any]) -> str:
    lines = [
        "# Research Inbox",
        "",
        f"Last Checked: {lock['checkedAt']}",
        "",
        "This file is generated by `scripts/refresh_research.py`. Review changed",
        "titles, headings, and hashes before promoting source findings into repo",
        "templates, audit checks, or policy.",
        "",
        "| Source | Status | Title | Headings |",
        "| --- | --- | --- | --- |",
    ]
    for record in lock["sources"]:
        title = _escape_pipe(record.get("title") or record.get("error") or "")
        headings = "; ".join(record.get("headings", [])[:4])
        lines.append(
            "| [{id}]({url}) | {status} | {title} | {headings} |".format(
                id=_escape_pipe(record["id"]),
                url=record["url"],
                status=record["status"],
                title=title,
                headings=_escape_pipe(headings),
            )
        )
    lines.extend(
        [
            "",
            "Promotion checklist:",
            "",
            "- Repeated source finding becomes an audit check.",
            "- Repeated operational failure becomes a verification command.",
            "- Repeated policy concern becomes a harness policy doc.",
            "- Speculative or vendor-specific claims stay as source notes until verified.",
        ]
    )
    return "\n".join(lines) + "\n"


def _escape_pipe(text: str) -> str:
    return text.replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
