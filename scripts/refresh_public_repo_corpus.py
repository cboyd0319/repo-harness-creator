#!/usr/bin/env python3
"""Purpose: Validate the offline public-repo fixture corpus metadata."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any

from harnessforge.generation.public_repo_corpus import PUBLIC_REPO_CORPUS, REQUIRED_CATEGORIES

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or refresh HarnessForge public-repo corpus pins."
    )
    parser.add_argument(
        "--verify-remote",
        action="store_true",
        help="run git ls-remote for each fixture repository",
    )
    parser.add_argument("--json", action="store_true", help="print JSON output")
    args = parser.parse_args(argv)
    payload = build_report(verify_remote=args.verify_remote)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_report(payload), end="")
    return 0 if payload["summary"]["errors"] == 0 else 1


def build_report(*, verify_remote: bool = False) -> dict[str, Any]:
    ids: set[str] = set()
    urls: set[str] = set()
    categories = sorted(
        {category for fixture in PUBLIC_REPO_CORPUS for category in fixture.categories}
    )
    errors: list[str] = []
    fixtures: list[dict[str, Any]] = []
    for fixture in PUBLIC_REPO_CORPUS:
        if fixture.id in ids:
            errors.append(f"duplicate fixture id: {fixture.id}")
        ids.add(fixture.id)
        if fixture.url in urls:
            errors.append(f"duplicate fixture url: {fixture.url}")
        urls.add(fixture.url)
        if not SHA_RE.match(fixture.pinned_ref):
            errors.append(f"{fixture.id} pinned_ref is not a 40-character SHA")
        remote = _remote_head(fixture.url) if verify_remote else None
        if remote and remote.get("error"):
            errors.append(f"{fixture.id} remote check failed: {remote['error']}")
        fixtures.append(
            {
                "id": fixture.id,
                "repository": fixture.repository,
                "url": fixture.url,
                "pinnedRef": fixture.pinned_ref,
                "categories": list(fixture.categories),
                "remote": remote,
            }
        )
    missing_categories = [
        category for category in REQUIRED_CATEGORIES if category not in categories
    ]
    errors.extend(f"missing required category: {category}" for category in missing_categories)
    return {
        "schemaVersion": "harnessforge.publicRepoCorpusRefresh.v1",
        "mode": "remote_verify" if verify_remote else "metadata_check",
        "execution": {
            "networkAccess": verify_remote,
            "commandsExecuted": verify_remote,
        },
        "summary": {
            "fixtures": len(fixtures),
            "categories": len(categories),
            "missingCategories": len(missing_categories),
            "errors": len(errors),
        },
        "missingCategories": missing_categories,
        "errors": errors,
        "fixtures": fixtures,
    }


def format_report(payload: dict[str, Any]) -> str:
    lines = [
        "Public repo corpus refresh check",
        f"Mode: {payload['mode']}",
        f"Fixtures: {payload['summary']['fixtures']}",
        f"Errors: {payload['summary']['errors']}",
        "Missing categories: " + (", ".join(payload["missingCategories"]) or "none"),
    ]
    if payload["errors"]:
        lines.append("")
        lines.append("Errors:")
        lines.extend(f"  - {error}" for error in payload["errors"])
    return "\n".join(lines).rstrip() + "\n"


def _remote_head(url: str) -> dict[str, str]:
    try:
        result = subprocess.run(
            ["git", "ls-remote", url, "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"head": "", "error": str(exc)}
    if result.returncode != 0:
        error = result.stderr.strip().splitlines()[:1]
        return {"head": "", "error": error[0] if error else "git ls-remote failed"}
    head = result.stdout.strip().split()
    return {"head": head[0] if head else "", "error": ""}


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
