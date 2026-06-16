#!/usr/bin/env python3
"""Purpose: Normalize reviewed agent token traces into HarnessForge records."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from harnessforge.evidence.token_economics import (
    load_metadata,
    normalize_codex_jsonl_trace,
    write_metric_record,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Normalize a reviewed agent token trace into HarnessForge evidence."
    )
    parser.add_argument(
        "--source",
        choices=("codex-jsonl",),
        required=True,
        help="trace source format",
    )
    parser.add_argument("--input", type=Path, required=True, help="input trace path")
    parser.add_argument(
        "--metadata",
        type=Path,
        required=True,
        help="JSON metadata sidecar for the token-economics record",
    )
    parser.add_argument("--output", type=Path, required=True, help="output JSON path")
    args = parser.parse_args(argv)

    try:
        metadata = load_metadata(args.metadata)
        if args.source == "codex-jsonl":
            record = normalize_codex_jsonl_trace(args.input, metadata)
        else:
            parser.error(f"unsupported source: {args.source}")
        write_metric_record(args.output, record)
    except OSError as exc:
        print(f"normalize-token-trace: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"normalize-token-trace: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
