#!/usr/bin/env python3
from __future__ import annotations

import argparse
import errno
import hashlib
import html
import http.client
import ipaddress
import json
import re
import socket
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request
from urllib.request import build_opener

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H_RE = re.compile(r"<h([12])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
MD_HEADING_RE = re.compile(r"^(#{1,2})\s+(.+?)\s*$")
SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
PLACEHOLDER_RE = re.compile(
    r"\b(?:placeholder|todo|tbd|coming soon)\b|x{4,}", re.IGNORECASE
)
MACOS_USER_DIR = "/" + "Users" + "/"
POSIX_HOME_DIR_RE = "/" + "home" + r"/[A-Za-z0-9_.-]+"
WINDOWS_USER_DIR_RE = r"[A-Za-z]:\\" + "Users" + r"\\"
LOCAL_ABSOLUTE_PATH_RE = re.compile(
    r"(?:file://|"
    + re.escape(MACOS_USER_DIR)
    + "|"
    + POSIX_HOME_DIR_RE
    + "|"
    + WINDOWS_USER_DIR_RE
    + ")"
)
PLACEHOLDER_HOSTS = {"example.com", "example.net", "example.org", "example.test"}
SOURCE_LEDGER_DOCS = (
    "docs/harness/research/sources.md",
    "docs/harness/research/research-inbox.md",
    "docs/harness/research/research-sources.lock.json",
)
WITHHELD_ADVERSARIAL_METADATA = "[withheld: adversarial instruction pattern]"
ADVERSARIAL_METADATA_PATTERNS = (
    (
        "ignore-instructions",
        re.compile(
            r"\b(?:ignore|disregard)\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b",
            re.IGNORECASE,
        ),
    ),
    (
        "role-header",
        re.compile(r"\b(?:system|developer|assistant)\s*:", re.IGNORECASE),
    ),
    (
        "prompt-exfiltration",
        re.compile(
            r"\b(?:reveal|print|show|dump)\s+(?:your\s+)?(?:system|developer)\s+prompt\b",
            re.IGNORECASE,
        ),
    ),
    (
        "secret-exfiltration",
        re.compile(
            r"\b(?:exfiltrate|send|upload|post|leak)\b.{0,80}"
            r"\b(?:secret|token|credential|api\s*key|private\s*key)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "sensitive-file-read",
        re.compile(r"(?:~/.ssh|/etc/passwd|\.env\b)", re.IGNORECASE),
    ),
    (
        "unicode-injection",
        re.compile(
            r"\b(?:ignore|instructions?|system|developer|assistant|prompt|"
            r"secret|token|credential|api\s*key|private\s*key|exfiltrate|"
            r"send|upload|leak|delete|bypass|override)\b"
            r".{0,120}[\u200b\u200c\u200d\ufeff\u202a-\u202e\u2066-\u2069]"
            r"|[\u200b\u200c\u200d\ufeff\u202a-\u202e\u2066-\u2069].{0,120}"
            r"\b(?:ignore|instructions?|system|developer|assistant|prompt|"
            r"secret|token|credential|api\s*key|private\s*key|exfiltrate|"
            r"send|upload|leak|delete|bypass|override)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "markdown-exfiltration",
        re.compile(
            r"!\[[^\]]*\]\(\s*https?://[^)]*"
            r"(?:secret|token|credential|api[-_\s]*key|prompt|data)="
            r"|<img\b[^>]*\bsrc\s*=\s*[\"']?https?://[^\"'>\s]*"
            r"(?:secret|token|credential|api[-_\s]*key|prompt|data)=",
            re.IGNORECASE,
        ),
    ),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Refresh metadata for reviewed research source URLs. "
            "This does not search for new sources."
        )
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate research source ledgers without fetching URLs.",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    source_path = root / "docs/harness/research/research-sources.json"
    lock_path = root / "docs/harness/research/research-sources.lock.json"
    inbox_path = root / "docs/harness/research/research-inbox.md"
    data = json.loads(source_path.read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        print("research-sources.json has no sources", file=sys.stderr)
        return 1
    hygiene_errors = validate_research_ledgers(root, data)
    if hygiene_errors:
        print("Research source check failed:", file=sys.stderr)
        for error in hygiene_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    if args.check:
        print("Research source check passed.")
        return 0

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
    lock_path.write_text(
        f"{json.dumps(lock, indent=2, sort_keys=True)}\n", encoding="utf-8"
    )
    inbox_path.write_text(_render_inbox(lock), encoding="utf-8")
    print(f"Refreshed {len(records)} research sources with {failures} failures.")
    return 1 if failures == len(records) else 0


def validate_research_ledgers(root: Path, data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["docs/harness/research/research-sources.json has no sources"]

    seen_ids: dict[str, int] = {}
    seen_urls: dict[str, int] = {}
    source_ids: list[str] = []
    source_urls: list[str] = []
    for index, source in enumerate(sources):
        label = f"docs/harness/research/research-sources.json sources[{index}]"
        if not isinstance(source, dict):
            failures.append(f"{label} must be an object")
            continue
        source_id = _source_string_field(source, "id", label, failures)
        url = _source_string_field(source, "url", label, failures)
        _source_string_field(source, "category", label, failures)
        if source_id:
            source_ids.append(source_id)
            lowered = source_id.lower()
            if not SOURCE_ID_RE.match(source_id):
                failures.append(f"{label}.id must be a stable lowercase id")
            if lowered in seen_ids:
                failures.append(
                    f"{label}.id duplicate source id {source_id!r}; first seen "
                    f"at sources[{seen_ids[lowered]}]"
                )
            else:
                seen_ids[lowered] = index
        if url:
            source_urls.append(url)
            url_key = url.rstrip("/")
            if url_key in seen_urls:
                failures.append(
                    f"{label}.url duplicate source url {url!r}; first seen "
                    f"at sources[{seen_urls[url_key]}]"
                )
            else:
                seen_urls[url_key] = index
            url_error = _source_url_syntax_error(url)
            if url_error:
                failures.append(f"{label}.url {url_error}")

    failures.extend(_validate_research_lock(root, source_ids, source_urls))
    failures.extend(_validate_source_docs(root))
    return failures


def _source_string_field(
    source: dict[str, Any], field: str, label: str, failures: list[str]
) -> str:
    value = source.get(field)
    if not isinstance(value, str) or not value.strip():
        failures.append(f"{label}.{field} must be a non-empty string")
        return ""
    stripped = value.strip()
    if PLACEHOLDER_RE.search(stripped):
        failures.append(f"{label}.{field} must not contain placeholder text")
    if LOCAL_ABSOLUTE_PATH_RE.search(stripped):
        failures.append(f"{label}.{field} must not contain a local absolute path")
    return stripped


def _source_url_syntax_error(url: str) -> str:
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
    except ValueError:
        return "source URL is invalid"
    if parsed.scheme.lower() != "https":
        return "source URL must use https"
    if not hostname:
        return "source URL must include a host"
    if parsed.username or parsed.password:
        return "source URL must not include credentials"
    try:
        port = parsed.port or 443
    except ValueError:
        return "source URL port is invalid"
    if port != 443:
        return "source URL must use the default https port"
    host = hostname.lower().rstrip(".")
    if host in PLACEHOLDER_HOSTS:
        return "source URL must not use a placeholder host"
    if host == "localhost" or host.endswith(".localhost"):
        return "source URL must not target localhost"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not address.is_global:
            return "source URL must target public addresses"
    if parsed.query:
        return "source URL must not include query parameters"
    if parsed.fragment:
        return "source URL must not include a fragment"
    if host == "arxiv.org" and not parsed.path.startswith("/abs/"):
        return "arXiv sources must use canonical /abs/ URLs"
    if LOCAL_ABSOLUTE_PATH_RE.search(url):
        return "source URL must not contain a local absolute path"
    if PLACEHOLDER_RE.search(url):
        return "source URL must not contain placeholder text"
    return ""


def _validate_research_lock(
    root: Path, source_ids: list[str], source_urls: list[str]
) -> list[str]:
    path = root / "docs/harness/research/research-sources.lock.json"
    if not path.exists():
        return []
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    if LOCAL_ABSOLUTE_PATH_RE.search(text):
        failures.append(f"{path.relative_to(root)} contains a local absolute path")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"{path.relative_to(root)} is invalid JSON: {exc}"]
    records = data.get("sources")
    if not isinstance(records, list):
        return [f"{path.relative_to(root)} sources must be a list"]
    if data.get("sourceCount") != len(source_ids):
        failures.append(
            f"{path.relative_to(root)} sourceCount does not match research-sources.json"
        )
    if len(records) != len(source_ids):
        failures.append(
            f"{path.relative_to(root)} source records do not match research-sources.json"
        )
        return failures
    lock_ids = [record.get("id") for record in records if isinstance(record, dict)]
    lock_urls = [record.get("url") for record in records if isinstance(record, dict)]
    if lock_ids != source_ids:
        failures.append(
            f"{path.relative_to(root)} source ids do not match research-sources.json"
        )
    if lock_urls != source_urls:
        failures.append(
            f"{path.relative_to(root)} source urls do not match research-sources.json"
        )
    return failures


def _validate_source_docs(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in SOURCE_LEDGER_DOCS:
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if LOCAL_ABSOLUTE_PATH_RE.search(text):
            failures.append(f"{relative} contains a local absolute path")
    return failures


def _fetch_source(source: dict[str, Any], *, timeout: int) -> dict[str, Any]:
    source_id = str(source.get("id", "unknown"))
    url = str(source.get("url", ""))
    category = str(source.get("category", "uncategorized"))
    base = {"id": source_id, "url": url, "category": category}
    url_error = _source_url_error(url)
    if url_error:
        return {**base, "status": "error", "error": url_error}
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "harnessforge research refresh",
                "Accept": (
                    "application/json,text/html,application/xhtml+xml,"
                    "text/plain;q=0.9,*/*;q=0.1"
                ),
            },
        )
        with _open_url(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 200))
            content_type = response.headers.get("content-type", "")
            raw = response.read(512_000)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {**base, "status": "error", "error": str(exc)}

    text = raw.decode("utf-8", errors="replace")
    title, headings = _extract_metadata(content_type, text)
    adversarial_signals = _adversarial_metadata_signals(
        title, [*headings, *_extract_raw_metadata_fragments(content_type, text)]
    )
    if adversarial_signals:
        title = WITHHELD_ADVERSARIAL_METADATA
        headings = []
    record = {
        **base,
        "status": "ok" if 200 <= status < 400 else "error",
        "httpStatus": status,
        "contentType": content_type.split(";", 1)[0].strip(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "title": title,
        "headings": headings,
    }
    if adversarial_signals:
        record["adversarialSignals"] = adversarial_signals
    return record


@dataclass(frozen=True)
class _ResolvedSource:
    host: str
    port: int
    addresses: tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, ...]


def _source_url_error(url: str) -> str:
    _, error = _resolve_source_url(url)
    return error


def _resolve_source_url(url: str) -> tuple[_ResolvedSource | None, str]:
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
    except ValueError:
        return None, "source URL is invalid"
    if parsed.scheme.lower() != "https":
        return None, "source URL must use https"
    if not hostname:
        return None, "source URL must include a host"
    if parsed.username or parsed.password:
        return None, "source URL must not include credentials"
    try:
        port = parsed.port or 443
    except ValueError:
        return None, "source URL port is invalid"
    if port != 443:
        return None, "source URL must use the default https port"

    host = hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        return None, "source URL must not target localhost"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        try:
            addresses = _resolve_host_addresses(host, port)
        except OSError as exc:
            return None, f"source URL host could not be resolved: {exc}"
    else:
        addresses = [address]
    if any(not address.is_global for address in addresses):
        return None, "source URL must target public addresses"
    return _ResolvedSource(host=host, port=port, addresses=tuple(addresses)), ""


def _resolve_host_addresses(
    host: str, port: int
) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    addresses = []
    resolved = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    for family, _, _, _, sockaddr in resolved:
        if family not in {socket.AF_INET, socket.AF_INET6}:
            continue
        addresses.append(ipaddress.ip_address(sockaddr[0]))
    if not addresses:
        raise OSError("no IP addresses found")
    return addresses


class _ValidatedRedirectHandler(HTTPRedirectHandler):
    def redirect_request(  # type: ignore[override]
        self, req, fp, code, msg, headers, newurl
    ):
        redirect_url = urljoin(getattr(req, "full_url", ""), newurl)
        url_error = _source_url_error(redirect_url)
        if url_error:
            raise URLError(f"redirect target rejected: {url_error}")
        return super().redirect_request(req, fp, code, msg, headers, redirect_url)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(
        self,
        host: str,
        *args: object,
        resolved_source: _ResolvedSource,
        **kwargs: object,
    ) -> None:
        super().__init__(host, *args, **kwargs)
        self._resolved_addresses = resolved_source.addresses
        self._server_hostname = resolved_source.host

    def connect(self) -> None:
        sys.audit("http.client.connect", self, self.host, self.port)
        last_error = None
        for address in self._resolved_addresses:
            try:
                self.sock = self._create_connection(
                    (str(address), self.port), self.timeout, self.source_address
                )
                try:
                    self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                except OSError as exc:
                    if exc.errno != errno.ENOPROTOOPT:
                        raise
                if self._tunnel_host:
                    self._tunnel()
                server_hostname = self._tunnel_host or self._server_hostname
                self.sock = self._context.wrap_socket(
                    self.sock, server_hostname=server_hostname
                )
                return
            except OSError as exc:
                last_error = exc
                if self.sock:
                    self.sock.close()
                    self.sock = None
        if last_error is not None:
            raise last_error
        raise OSError("no validated addresses available")


class _PinnedHTTPSHandler(HTTPSHandler):
    def https_open(self, req: Request):  # type: ignore[override]
        source, error = _resolve_source_url(req.full_url)
        if error or source is None:
            raise URLError(error or "source URL is invalid")

        def connection_factory(
            host: str, timeout: object = None, **kwargs: object
        ) -> _PinnedHTTPSConnection:
            return _PinnedHTTPSConnection(
                host,
                timeout=timeout,
                resolved_source=source,
                **kwargs,
            )

        return self.do_open(connection_factory, req, context=self._context)


def _open_url(request: Request, *, timeout: int):
    opener = build_opener(
        ProxyHandler({}), _ValidatedRedirectHandler, _PinnedHTTPSHandler
    )
    return opener.open(request, timeout=timeout)


def _extract_metadata(content_type: str, text: str) -> tuple[str, list[str]]:
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type == "application/json":
        return _extract_json_metadata(text)
    if media_type in {"text/markdown", "text/plain", "text/x-rst"}:
        title, headings = _extract_plain_text_metadata(text)
        if title or headings:
            return title, headings
    title = _first_match(TITLE_RE, text)
    headings = [_clean(match.group(2)) for match in H_RE.finditer(text)]
    return title, [heading for heading in headings if heading][:8]


def _extract_raw_metadata_fragments(content_type: str, text: str) -> list[str]:
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type in {"text/markdown", "text/plain", "text/x-rst"}:
        fragments = [
            match.group(2)
            for line in text.splitlines()
            if not line[:1].isspace()
            for match in [MD_HEADING_RE.match(line.strip())]
            if match
        ]
        return fragments[:8]
    return [
        *[match.group(1) for match in TITLE_RE.finditer(text)],
        *[match.group(2) for match in H_RE.finditer(text)],
    ][:8]


def _extract_plain_text_metadata(text: str) -> tuple[str, list[str]]:
    lines = text.splitlines()
    markdown_headings: list[tuple[int, str]] = []
    first_heading_index = len(lines)
    for index, line in enumerate(lines):
        if line[:1].isspace():
            continue
        match = MD_HEADING_RE.match(line.strip())
        if match:
            first_heading_index = min(first_heading_index, index)
            level = len(match.group(1))
            heading = _clean_markdown(match.group(2))
            if heading:
                markdown_headings.append((level, heading))
    if markdown_headings:
        title = next(
            (heading for level, heading in markdown_headings if level == 1),
            _first_plain_title(lines[:first_heading_index]),
        )
        if not title:
            title = markdown_headings[0][1]
        return title, [heading for _, heading in markdown_headings[:8]]

    rst_headings = []
    first_heading_index = len(lines)
    for index, line in enumerate(lines[:-1]):
        if line[:1].isspace() or lines[index + 1][:1].isspace():
            continue
        title = line.strip()
        underline = lines[index + 1].strip()
        if (
            title
            and len(underline) >= len(title)
            and set(underline) in ({"="}, {"-"})
        ):
            first_heading_index = min(first_heading_index, index)
            rst_headings.append(_clean_markdown(title))
    rst_headings = [heading for heading in rst_headings if heading]
    if rst_headings:
        title = _first_plain_title(lines[:first_heading_index]) or rst_headings[0]
        return title, rst_headings[:8]

    return "", []


def _first_plain_title(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if set(stripped) in ({"-"}, {"*"}, {"_"}, {"="}):
            continue
        if stripped.startswith((".. ", ":", "[![", "![")):
            continue
        lowered = stripped.lower()
        if lowered.startswith(("**documentation**", "**source code**")):
            continue
        if re.match(r"<h[12]\b", stripped, re.IGNORECASE) or "<em>" in lowered:
            return _clean(stripped)
        if stripped.startswith("<"):
            continue
        title = _clean_markdown(stripped)
        if title:
            return title
    return ""


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


def _adversarial_metadata_signals(title: str, headings: list[str]) -> list[str]:
    metadata = "\n".join([title, *headings])
    return [
        signal
        for signal, pattern in ADVERSARIAL_METADATA_PATTERNS
        if pattern.search(metadata)
    ]


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


def _clean_markdown(text: str) -> str:
    without_badges = re.sub(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)", "", text)
    without_images = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", without_badges)
    without_links = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", without_images)
    without_code = re.sub(r"`([^`]+)`", r"\1", without_links)
    return " ".join(without_code.strip(" #").split())


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
        "The refresh uses the fixed allowlist in `research-sources.json` only.",
        "It does not search the web, discover latest research, or treat fetched",
        "text as trusted instructions.",
        "Suspicious metadata is withheld and recorded as review signals.",
        "",
        "| Source | Status | Signals | Title | Headings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in lock["sources"]:
        title = _escape_pipe(record.get("title") or record.get("error") or "")
        headings = "; ".join(record.get("headings", [])[:4])
        signals = ", ".join(record.get("adversarialSignals", []))
        lines.append(
            "| [{id}]({url}) | {status} | {signals} | {title} | {headings} |".format(
                id=_escape_pipe(record["id"]),
                url=record["url"],
                status=record["status"],
                signals=_escape_pipe(signals),
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
            "- Speculative or vendor-specific claims stay as source notes "
            "until verified.",
        ]
    )
    return "\n".join(lines) + "\n"


def _escape_pipe(text: str) -> str:
    return text.replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
