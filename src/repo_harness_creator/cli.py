from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .audit import audit_target, audit_to_dict, format_audit, render_html_report
from .doctor import doctor_json, doctor_report, format_doctor
from .generate import create_harness
from .redact import redact_local_paths
from .update import plan_or_apply_update


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    try:
        return int(args.func(args))
    except BrokenPipeError:
        return 1
    except ValueError as exc:
        print(f"error: {redact_local_paths(str(exc))}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {redact_local_paths(str(exc))}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo-harness",
        description="Create, assess, and maintain AI coding-agent repo harnesses.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    init = subparsers.add_parser("init", help="create missing harness artifacts")
    init.add_argument("--target", type=Path, default=Path.cwd())
    init.add_argument("--agent-file", default="AGENTS.md")
    init.add_argument("--package-manager")
    init.add_argument("--command", dest="commands", action="append", default=[])
    init.add_argument("--project-name")
    init.add_argument("--force", action="store_true")
    init.add_argument("--dry-run", action="store_true")
    init.set_defaults(func=_init)

    audit = subparsers.add_parser("audit", help="score a repository harness")
    audit.add_argument("--target", type=Path, default=Path.cwd())
    audit.add_argument("--json", action="store_true")
    audit.add_argument("--html", type=Path)
    audit.add_argument("--min-score", type=int, default=0)
    audit.set_defaults(func=_audit)

    update = subparsers.add_parser("update", help="plan or apply safe harness corrections")
    update.add_argument("--target", type=Path, default=Path.cwd())
    update.add_argument("--agent-file", default="AGENTS.md")
    update.add_argument("--apply", action="store_true")
    update.add_argument("--force", action="store_true")
    update.add_argument("--json", action="store_true")
    update.set_defaults(func=_update)

    doctor = subparsers.add_parser("doctor", help="check local runtime support")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--strict", action="store_true")
    doctor.set_defaults(func=_doctor)

    return parser


def _init(args: argparse.Namespace) -> int:
    profile, results = create_harness(
        args.target,
        agent_file=args.agent_file,
        force=args.force,
        dry_run=args.dry_run,
        package_manager=args.package_manager,
        commands=tuple(args.commands),
        project_name=args.project_name,
    )
    print(f"Target: {profile.name}")
    print(f"Detected stack: {profile.stack}")
    print("Verification commands:")
    for command in profile.verification_commands:
        print(f"  - {command}")
    print("")
    for result in results:
        relative = _relative(result.path, profile.root)
        suffix = f" ({result.reason})" if result.reason else ""
        print(f"{result.status.upper()} {relative}{suffix}")
    return 0


def _audit(args: argparse.Namespace) -> int:
    result = audit_target(args.target)
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(render_html_report(result), encoding="utf-8")
        print(f"HTML report written to {args.html}")
    if args.json:
        print(json.dumps(audit_to_dict(result), indent=2))
    else:
        print(format_audit(result))
    return 1 if args.min_score and result.overall < args.min_score else 0


def _update(args: argparse.Namespace) -> int:
    before, profile, writes = plan_or_apply_update(
        args.target,
        apply=args.apply,
        force=args.force,
        agent_file=args.agent_file,
    )
    if args.json:
        payload = {
            "before": audit_to_dict(before),
            "applied": args.apply,
            "writes": [
                {
                    "path": _relative(write.path, profile.root if profile else args.target),
                    "status": write.status,
                    "reason": write.reason,
                }
                for write in writes
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0
    print(format_audit(before))
    print("")
    if not args.apply:
        print("No files changed. Re-run with --apply to create missing generated artifacts.")
        return 0
    print("Applied safe corrections:")
    assert profile is not None
    for write in writes:
        suffix = f" ({write.reason})" if write.reason else ""
        print(f"  - {write.status.upper()} {_relative(write.path, profile.root)}{suffix}")
    return 0


def _doctor(args: argparse.Namespace) -> int:
    report = doctor_report()
    if args.json:
        print(doctor_json(report), end="")
    else:
        print(format_doctor(report))
    return 1 if args.strict and not report["ok"] else 0


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return redact_local_paths(str(path))
