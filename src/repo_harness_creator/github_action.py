from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from collections.abc import Mapping
from typing import Any

from .audit import audit_target, audit_to_dict, format_audit, render_html_report
from .doctor import doctor_report, format_doctor
from .generate import create_harness
from .redact import redact_local_paths
from .update import plan_or_apply_update


def main() -> int:
    try:
        return run_from_env(os.environ)
    except ValueError as exc:
        print(f"error: {redact_local_paths(str(exc))}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {redact_local_paths(str(exc))}", file=sys.stderr)
        return 2


def run_from_env(env: Mapping[str, str]) -> int:
    command = env.get("INPUT_COMMAND", "audit").strip().lower()
    target = Path(env.get("INPUT_TARGET", ".")).resolve()
    min_score = _int_input(env.get("INPUT_MIN_SCORE", "85"), "min-score")
    fail_on_score = _bool_input(env.get("INPUT_FAIL_ON_SCORE", "true"))
    html_report = env.get("INPUT_HTML_REPORT", "").strip()
    json_report = env.get("INPUT_JSON_REPORT", "").strip()
    changed_files = 0

    if command == "doctor":
        report = doctor_report()
        text = format_doctor(report)
        print(text)
        _summary(env, "Repo Harness Doctor", text)
        _output(
            env,
            {
                "overall-score": "",
                "bottleneck": "",
                "report-json": "",
                "report-html": "",
                "changed-files": "0",
            }
        )
        return 0 if report["ok"] else 1

    if command == "init":
        _, writes = create_harness(
            target,
            agent_file=env.get("INPUT_AGENT_FILE", "AGENTS.md"),
            force=_bool_input(env.get("INPUT_FORCE", "false")),
        )
        changed_files = sum(1 for write in writes if write.status == "written")
        result = audit_target(target)
        _print_writes(target, writes)
    elif command == "update":
        _, _, writes = plan_or_apply_update(
            target,
            apply=_bool_input(env.get("INPUT_APPLY", "false")),
            force=_bool_input(env.get("INPUT_FORCE", "false")),
            agent_file=env.get("INPUT_AGENT_FILE", "AGENTS.md"),
        )
        changed_files = sum(1 for write in writes if write.status == "written")
        result = audit_target(target)
        if writes:
            _print_writes(target, writes)
        else:
            print("No files changed. Set apply=true to create safe missing artifacts.")
    elif command == "audit":
        result = audit_target(target)
    else:
        raise ValueError("command must be one of: audit, init, update, doctor")

    json_path = _write_json_report(json_report, result)
    html_path = _write_html_report(html_report, result)
    text_report = format_audit(result)
    print(text_report)
    _summary(env, "Repo Harness Audit", _summary_markdown(result, changed_files))
    _output(
        env,
        {
            "overall-score": str(result.overall),
            "bottleneck": result.bottleneck,
            "report-json": json_path,
            "report-html": html_path,
            "changed-files": str(changed_files),
        }
    )
    if fail_on_score and result.overall < min_score:
        return 1
    return 0


def _write_json_report(path_text: str, result: Any) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(audit_to_dict(result), indent=2)}\n", encoding="utf-8")
    return str(path)


def _write_html_report(path_text: str, result: Any) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html_report(result), encoding="utf-8")
    return str(path)


def _print_writes(root: Path, writes: tuple[Any, ...]) -> None:
    print("File changes:")
    for write in writes:
        try:
            rel = write.path.resolve().relative_to(root.resolve())
        except ValueError:
            rel = write.path
        suffix = f" ({write.reason})" if write.reason else ""
        print(f"  - {write.status.upper()} {redact_local_paths(str(rel))}{suffix}")


def _summary_markdown(result: Any, changed_files: int) -> str:
    lines = [
        f"- Overall score: `{result.overall}/100`",
        f"- Bottleneck: `{result.bottleneck}`",
        f"- Changed files: `{changed_files}`",
        "",
        "| Domain | Score | Passed |",
        "| --- | ---: | ---: |",
    ]
    for domain in result.domains:
        lines.append(f"| {domain.name} | {domain.score}/5 | {domain.passed}/{domain.total} |")
    if result.recommendations:
        lines.extend(["", "Recommended next actions:"])
        lines.extend(f"- {item}" for item in result.recommendations)
    return "\n".join(lines)


def _summary(env: Mapping[str, str], title: str, body: str) -> None:
    path_text = env.get("GITHUB_STEP_SUMMARY")
    if not path_text:
        return
    path = Path(path_text)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {title}\n\n{body}\n")


def _output(env: Mapping[str, str], values: dict[str, str]) -> None:
    path_text = env.get("GITHUB_OUTPUT")
    if not path_text:
        return
    path = Path(path_text)
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            safe_value = value.replace("\r", " ").replace("\n", " ")
            handle.write(f"{key}={safe_value}\n")


def _bool_input(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_input(value: str | None, name: str) -> int:
    try:
        return int(str(value or "").strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


if __name__ == "__main__":
    raise SystemExit(main())
