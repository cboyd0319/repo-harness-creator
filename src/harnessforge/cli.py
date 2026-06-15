from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .audit import audit_target, audit_to_dict, format_audit, render_html_report
from .blueprints import (
    apply_blueprint,
    blueprint_to_dict,
    get_blueprint,
    list_blueprints,
    list_blueprints_to_dict,
)
from .detect import detect_project
from .doctor import doctor_json, doctor_report, format_doctor
from .generate import PLATFORM_CONTRACTS, REVIEW_REQUIRED_FILES, create_harness
from .models import DriftResult, ProjectProfile, WriteResult
from .readiness import (
    ReadinessReport,
    format_readiness,
    inspect_readiness,
    readiness_to_dict,
)
from .redact import redact_local_paths
from .reports import write_json_payload
from .sync import format_sync_check, sync_check_to_dict, sync_exit_code
from .update import build_drift_report, plan_or_apply_update
from .verify import (
    DEFAULT_TIMEOUT_SECONDS,
    build_verify_plan,
    format_verify_plan,
    run_verify_checks,
    verify_report_to_dict,
)

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
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
        prog="harnessforge",
        description="Create, assess, and maintain AI coding-agent repo harnesses.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    inspect = subparsers.add_parser(
        "inspect",
        help="show detected project profile without writing files",
    )
    inspect.add_argument("--target", type=Path, default=Path.cwd())
    inspect.add_argument("--package-manager")
    inspect.add_argument("--command", dest="commands", action="append", default=[])
    inspect.add_argument("--readiness", action="store_true")
    inspect.add_argument(
        "--require-verify-evidence",
        action="store_true",
        help="block readiness unless stored run-mode verify evidence is current and passed",
    )
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(func=_inspect)

    quickstart = subparsers.add_parser(
        "quickstart",
        help="guide a first HarnessForge run without writing files",
    )
    quickstart.add_argument("--target", type=Path, default=Path.cwd())
    quickstart.add_argument("--agent-file", default="AGENTS.md")
    quickstart.add_argument(
        "--platform-contract",
        choices=PLATFORM_CONTRACTS,
        default="cross-platform",
    )
    quickstart.add_argument("--package-manager")
    quickstart.add_argument("--command", dest="commands", action="append", default=[])
    quickstart.add_argument("--project-name")
    quickstart.add_argument(
        "--enhance-existing",
        action="store_true",
        help="preview instruction-file enhancement instead of preserving existing routers",
    )
    quickstart.set_defaults(func=_quickstart)

    init = subparsers.add_parser("init", help="create missing harness artifacts")
    init.add_argument("--target", type=Path, default=Path.cwd())
    init.add_argument("--agent-file", default="AGENTS.md")
    init.add_argument(
        "--platform-contract",
        choices=PLATFORM_CONTRACTS,
        default="cross-platform",
    )
    init.add_argument("--package-manager")
    init.add_argument("--command", dest="commands", action="append", default=[])
    init.add_argument("--project-name")
    init.add_argument(
        "--with-ci-workflow",
        action="store_true",
        help="also scaffold a manual HarnessForge CI workflow",
    )
    init.add_argument(
        "--with-self-heal-workflow",
        action="store_true",
        help="also scaffold a manual self-heal pull-request workflow",
    )
    init.add_argument("--force", action="store_true")
    init.add_argument(
        "--enhance-existing",
        action="store_true",
        help="append reviewed HarnessForge guidance to existing instruction files",
    )
    init.add_argument("--dry-run", action="store_true")
    init.set_defaults(func=_init)

    audit = subparsers.add_parser("audit", help="score a repository harness")
    audit.add_argument("--target", type=Path, default=Path.cwd())
    audit.add_argument("--json", action="store_true")
    audit.add_argument("--html", type=Path)
    audit.add_argument("--min-score", type=int, default=0)
    audit.add_argument(
        "--allow-local-absolute-paths",
        action="store_true",
        help="explicitly allow local absolute paths for this audit run",
    )
    audit.set_defaults(func=_audit)

    update = subparsers.add_parser("update", help="plan or apply safe harness corrections")
    update.add_argument("--target", type=Path, default=Path.cwd())
    update.add_argument("--agent-file", default="AGENTS.md")
    update.add_argument(
        "--platform-contract",
        choices=PLATFORM_CONTRACTS,
        default="cross-platform",
    )
    update.add_argument(
        "--with-ci-workflow",
        action="store_true",
        help="include the optional manual HarnessForge CI workflow",
    )
    update.add_argument(
        "--with-self-heal-workflow",
        action="store_true",
        help="include the optional manual self-heal pull-request workflow",
    )
    update.add_argument("--apply", action="store_true")
    update.add_argument("--force", action="store_true")
    update.add_argument(
        "--enhance-existing",
        action="store_true",
        help="append reviewed HarnessForge guidance to existing instruction files",
    )
    update.add_argument("--drift-report", action="store_true")
    update.add_argument("--json", action="store_true")
    update.set_defaults(func=_update)

    sync = subparsers.add_parser(
        "sync",
        help="check whether safe harness sync would require attention",
    )
    sync.add_argument("--target", type=Path, default=Path.cwd())
    sync.add_argument(
        "--check",
        action="store_true",
        help="run a read-only sync readiness check",
    )
    sync.add_argument("--package-manager")
    sync.add_argument("--command", dest="commands", action="append", default=[])
    sync.add_argument(
        "--require-verify-evidence",
        action="store_true",
        help="block sync unless stored run-mode verify evidence is current and passed",
    )
    sync.add_argument("--json", action="store_true")
    sync.set_defaults(func=_sync)

    verify = subparsers.add_parser(
        "verify",
        help="report project verification checks without running them",
    )
    verify.add_argument("--target", type=Path, default=Path.cwd())
    verify.add_argument("--package-manager")
    verify.add_argument("--command", dest="commands", action="append", default=[])
    verify.add_argument("--json", action="store_true")
    verify.add_argument(
        "--json-report",
        help="write verify JSON to a target-relative report path",
    )
    verify.add_argument(
        "--run",
        action="store_true",
        help="execute planned checks explicitly instead of reporting plan mode",
    )
    verify.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="per-command timeout for --run",
    )
    verify.set_defaults(func=_verify)

    blueprint = subparsers.add_parser(
        "blueprint",
        help="list, inspect, or apply optional harness blueprints",
    )
    blueprint_subparsers = blueprint.add_subparsers(dest="blueprint_command")

    blueprint_list = blueprint_subparsers.add_parser(
        "list",
        help="list built-in blueprint packs",
    )
    blueprint_list.add_argument("--json", action="store_true")
    blueprint_list.set_defaults(func=_blueprint_list)

    blueprint_show = blueprint_subparsers.add_parser(
        "show",
        help="show a built-in blueprint pack",
    )
    blueprint_show.add_argument("blueprint_id", choices=_blueprint_ids())
    blueprint_show.add_argument("--json", action="store_true")
    blueprint_show.set_defaults(func=_blueprint_show)

    blueprint_apply = blueprint_subparsers.add_parser(
        "apply",
        help="write optional blueprint artifacts for project review",
    )
    blueprint_apply.add_argument("blueprint_id", choices=_blueprint_ids())
    blueprint_apply.add_argument("--target", type=Path, default=Path.cwd())
    blueprint_apply.add_argument("--dry-run", action="store_true")
    blueprint_apply.add_argument("--force", action="store_true")
    blueprint_apply.add_argument("--json", action="store_true")
    blueprint_apply.set_defaults(func=_blueprint_apply)

    doctor = subparsers.add_parser("doctor", help="check local runtime support")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--strict", action="store_true")
    doctor.set_defaults(func=_doctor)

    return parser


def _inspect(args: argparse.Namespace) -> int:
    if args.require_verify_evidence and not args.readiness:
        raise ValueError("--require-verify-evidence requires --readiness")
    profile = detect_project(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
    )
    if args.readiness:
        report = inspect_readiness(
            profile,
            require_verify_evidence=args.require_verify_evidence,
        )
        if args.json:
            print(json.dumps(readiness_to_dict(report), indent=2))
        else:
            print(format_readiness(report))
        return 0
    if args.json:
        print(json.dumps(_profile_to_dict(profile), indent=2))
        return 0

    print(f"Target: {profile.name}")
    print(f"Detected stack: {profile.stack}")
    print(f"Languages: {_list_or_none(profile.languages)}")
    print(f"Package managers: {_list_or_none(profile.package_managers)}")
    print(f"Runtime files: {_list_or_none(profile.runtime_files)}")
    print("Verification commands:")
    for command in profile.verification_commands:
        print(f"  - {command}")
    print(f"Workspace markers: {_list_or_none(profile.workspace_markers)}")
    print(f"Routing markers: {_list_or_none(profile.routing_markers)}")
    print("Components:")
    if profile.components:
        for component in profile.components:
            print(f"  - {component}")
    else:
        print("  - none detected")
    return 0


def _quickstart(args: argparse.Namespace) -> int:
    profile, writes = create_harness(
        args.target,
        agent_file=args.agent_file,
        force=False,
        enhance_existing=args.enhance_existing,
        dry_run=True,
        package_manager=args.package_manager,
        commands=tuple(args.commands),
        project_name=args.project_name,
        platform_contract=args.platform_contract,
    )
    report = inspect_readiness(profile)
    print(_format_quickstart(profile, report, writes))
    return 0


def _init(args: argparse.Namespace) -> int:
    profile, results = create_harness(
        args.target,
        agent_file=args.agent_file,
        force=args.force,
        enhance_existing=args.enhance_existing,
        dry_run=args.dry_run,
        package_manager=args.package_manager,
        commands=tuple(args.commands),
        project_name=args.project_name,
        with_ci_workflow=args.with_ci_workflow,
        with_self_heal_workflow=args.with_self_heal_workflow,
        platform_contract=args.platform_contract,
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
    for warning in _preserved_file_warnings(results, profile.root):
        print(warning)
    for warning in _workflow_warnings(args.with_ci_workflow, args.with_self_heal_workflow):
        print(warning)
    return 0


def _audit(args: argparse.Namespace) -> int:
    result = audit_target(
        args.target,
        allow_local_absolute_paths=args.allow_local_absolute_paths,
    )
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
    if args.drift_report:
        drift = build_drift_report(args.target)
        if args.json:
            print(json.dumps({"drift": [_drift_to_dict(item) for item in drift]}, indent=2))
            return 0
        print("Generated file drift report:")
        if not drift:
            print("  - No generated-file metadata found.")
            return 0
        for item in drift:
            suffix = f" ({item.reason})" if item.reason else ""
            print(
                "  - "
                f"{item.path}: file={item.file_status}, "
                f"template={item.template_status}, "
                f"action={item.recommended_action}{suffix}"
            )
        return 0
    before, profile, writes = plan_or_apply_update(
        args.target,
        apply=args.apply,
        force=args.force,
        enhance_existing=args.enhance_existing,
        agent_file=args.agent_file,
        with_ci_workflow=args.with_ci_workflow,
        with_self_heal_workflow=args.with_self_heal_workflow,
        platform_contract=args.platform_contract,
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
    for warning in _preserved_file_warnings(writes, profile.root):
        print(warning)
    for warning in _workflow_warnings(args.with_ci_workflow, args.with_self_heal_workflow):
        print(warning)
    return 0


def _sync(args: argparse.Namespace) -> int:
    if not args.check:
        raise ValueError("sync currently supports only --check")
    profile = detect_project(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
    )
    report = inspect_readiness(
        profile,
        require_verify_evidence=args.require_verify_evidence,
    )
    exit_code = sync_exit_code(report)
    if args.json:
        print(json.dumps(sync_check_to_dict(report, exit_code), indent=2))
    else:
        print(format_sync_check(report))
    return exit_code


def _verify(args: argparse.Namespace) -> int:
    if args.timeout_seconds <= 0:
        raise ValueError("--timeout-seconds must be greater than 0")
    profile = detect_project(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
    )
    if args.run:
        report = run_verify_checks(
            profile,
            explicit_commands=tuple(args.commands),
            timeout_seconds=args.timeout_seconds,
        )
    else:
        report = build_verify_plan(profile, explicit_commands=tuple(args.commands))
    payload = verify_report_to_dict(report)
    json_report = write_json_payload(args.json_report or "", profile.root, payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if json_report:
            print(f"Verify JSON report written to {json_report}")
        print(format_verify_plan(report))
    if not args.run:
        return 0
    if report.verdict == "passed":
        return 0
    if report.verdict == "failed":
        return 1
    return 2


def _doctor(args: argparse.Namespace) -> int:
    report = doctor_report()
    if args.json:
        print(doctor_json(report), end="")
    else:
        print(format_doctor(report))
    return 1 if args.strict and not report["ok"] else 0


def _blueprint_list(args: argparse.Namespace) -> int:
    if args.json:
        print(json.dumps(list_blueprints_to_dict(), indent=2))
        return 0
    print("Available blueprints:")
    for blueprint in list_blueprints():
        domains = ", ".join(blueprint.domains)
        print(f"  - {blueprint.id}: {blueprint.title} ({domains})")
    return 0


def _blueprint_show(args: argparse.Namespace) -> int:
    blueprint = get_blueprint(args.blueprint_id)
    if args.json:
        print(json.dumps(blueprint_to_dict(blueprint), indent=2))
        return 0
    print(f"{blueprint.title} ({blueprint.id})")
    print(blueprint.summary)
    print("")
    print("Review questions:")
    for question in blueprint.review_questions:
        print(f"  - {question}")
    print("")
    print("Generated files:")
    for path in blueprint.generated_files:
        print(f"  - {path}")
    return 0


def _blueprint_apply(args: argparse.Namespace) -> int:
    blueprint, writes = apply_blueprint(
        args.target,
        args.blueprint_id,
        dry_run=args.dry_run,
        force=args.force,
    )
    if args.json:
        payload = {
            "schemaVersion": "harnessforge.blueprintApply.v1",
            "blueprint": blueprint_to_dict(blueprint),
            "target": {"root": None},
            "dryRun": args.dry_run,
            "force": args.force,
            "writes": [
                {
                    "path": _relative(write.path, args.target),
                    "status": write.status,
                    "reason": write.reason,
                }
                for write in writes
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0
    action = "would apply" if args.dry_run else "applied"
    print(f"Blueprint {action}: {blueprint.id}")
    for write in writes:
        suffix = f" ({write.reason})" if write.reason else ""
        print(f"  - {write.status.upper()} {_relative(write.path, args.target)}{suffix}")
    if any(write.status == "skipped" for write in writes):
        print("Existing files preserved. Re-run with --force only after review.")
    return 0


def _format_quickstart(
    profile: ProjectProfile,
    report: ReadinessReport,
    writes: tuple[WriteResult, ...],
) -> str:
    would_create = tuple(
        _relative(result.path, profile.root)
        for result in writes
        if result.status == "would_write"
    )
    would_enhance = tuple(
        _relative(result.path, profile.root)
        for result in writes
        if result.status == "would_enhance"
    )
    preserved = tuple(
        _relative(result.path, profile.root)
        for result in writes
        if result.status == "skipped"
    )
    planned_paths = set(would_create) | set(would_enhance)
    review_placeholders = tuple(
        path for path in REVIEW_REQUIRED_FILES if path in planned_paths
    )
    has_planned_writes = bool(planned_paths)

    lines = [
        f"Quickstart for {profile.name}",
        "",
        "Detected project:",
        f"  - Detected stack: {profile.stack}",
        f"  - Languages: {_list_or_none(profile.languages)}",
        f"  - Package managers: {_list_or_none(profile.package_managers)}",
        f"  - Components: {_list_or_none(profile.components)}",
        "",
        f"Readiness: {report.verdict}",
        "",
    ]
    _append_cli_section(lines, "Blocked reasons", report.blocked_reasons)
    _append_cli_section(lines, "Warnings", report.warnings)
    _append_cli_section(lines, "Source of truth", report.source_of_truth)
    _append_cli_section(lines, "Runnable checks", report.runnable_checks)
    _append_cli_section(lines, "Config precedence", report.config_precedence)
    _append_cli_section(lines, "Existing files preserved", preserved)
    _append_cli_section(lines, "Files HarnessForge would enhance", would_enhance)
    _append_cli_section(lines, "Files HarnessForge would create", would_create)
    _append_cli_section(
        lines,
        "Generated files needing project review",
        review_placeholders,
    )
    _append_cli_section(lines, "Review required", report.review_required)
    _append_cli_section(
        lines,
        "Next actions",
        _quickstart_next_actions(report, has_planned_writes),
    )
    _append_cli_section(
        lines,
        "Next commands",
        _quickstart_commands(report, has_planned_writes),
    )
    return "\n".join(lines).rstrip()


def _quickstart_next_actions(
    report: ReadinessReport, has_planned_writes: bool
) -> tuple[str, ...]:
    if has_planned_writes:
        return report.next_actions
    return tuple(
        action
        for action in report.next_actions
        if not action.startswith("Run harnessforge init ")
    )


def _quickstart_commands(
    report: ReadinessReport, has_planned_writes: bool
) -> tuple[str, ...]:
    if report.verdict == "blocked":
        return (
            "harnessforge inspect --target <repo> --readiness",
            'harnessforge inspect --target <repo> --readiness --command "<check command>"',
            'harnessforge sync --check --target <repo> --command "<check command>"',
        )
    commands = []
    if has_planned_writes:
        commands.extend(
            [
                "harnessforge init --target <repo> --dry-run",
                "harnessforge init --target <repo>",
            ]
        )
    commands.extend(
        [
            "harnessforge audit --target <repo> --min-score 85",
            "harnessforge sync --check --target <repo>",
        ]
    )
    return tuple(commands)


def _profile_to_dict(profile: ProjectProfile) -> dict[str, object]:
    return {
        "name": profile.name,
        "detectedStack": profile.stack,
        "languages": list(profile.languages),
        "packageManagers": list(profile.package_managers),
        "runtimeFiles": list(profile.runtime_files),
        "verificationCommands": list(profile.verification_commands),
        "components": list(profile.components),
        "workspaceMarkers": list(profile.workspace_markers),
        "routingMarkers": list(profile.routing_markers),
        "configPrecedence": list(profile.config_precedence),
    }


def _list_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none detected"


def _append_cli_section(lines: list[str], title: str, values: tuple[str, ...]) -> None:
    if not values:
        return
    lines.append(f"{title}:")
    for value in values:
        lines.append(f"  - {value}")
    lines.append("")


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return redact_local_paths(str(path))


def _drift_to_dict(item: DriftResult) -> dict[str, str]:
    return {
        "path": item.path,
        "ownership": item.ownership,
        "fileStatus": item.file_status,
        "templateStatus": item.template_status,
        "reason": item.reason,
        "recommendedAction": item.recommended_action,
    }


def _workflow_warnings(
    with_ci_workflow: bool, with_self_heal_workflow: bool
) -> tuple[str, ...]:
    if not (with_ci_workflow or with_self_heal_workflow):
        return ()
    return (
        "Optional workflow scaffold review required:",
        "  - replace cboyd0319/harnessforge@<reviewed-commit-sha> before relying on it",
        "  - review workflow permissions, triggers, branch, and pull-request behavior",
        "  - CI sync preflight warnings are advisory by default; blocked "
        "readiness still stops the workflow",
        "  - verify evidence gating is off by default until the project stores "
        "reviewed run-mode evidence",
    )


def _preserved_file_warnings(
    results: tuple[WriteResult, ...], root: Path
) -> tuple[str, ...]:
    preserved = sorted(
        _relative(result.path, root)
        for result in results
        if getattr(result, "status", "") == "skipped"
        and getattr(result, "reason", "") == "exists"
    )
    if not preserved:
        return ()
    shown = ", ".join(preserved[:4])
    if len(preserved) > 4:
        shown += f", and {len(preserved) - 4} more"
    return (
        f"Existing files preserved: {shown}",
        (
            "  - if audit still evaluates old instructions, rerun with "
            "--agent-file HARNESSFORGE_AGENTS.md for a side-by-side entrypoint "
            "or use --force only after review"
        ),
    )


def _blueprint_ids() -> tuple[str, ...]:
    return tuple(blueprint.id for blueprint in list_blueprints())
