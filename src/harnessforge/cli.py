from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .assessment.audit import audit_target, audit_to_dict, format_audit, render_html_report
from .core.doctor import doctor_json, doctor_report, format_doctor
from .core.models import DriftResult, ProjectProfile, WriteResult
from .core.redact import redact_local_paths
from .core.reports import write_json_payload
from .evidence.effectiveness import (
    build_effectiveness_assessment,
    format_effectiveness_assessment,
)
from .evidence.release_check import (
    build_release_check,
    format_release_check,
    release_check_exit_code,
    write_markdown_release_check,
)
from .evidence.report import build_report, format_report, write_markdown_report
from .generation.blueprints import (
    apply_blueprint,
    blueprint_to_dict,
    get_blueprint,
    list_blueprints,
    list_blueprints_to_dict,
)
from .generation.generate import (
    PLATFORM_CONTRACTS,
    REVIEW_REQUIRED_FILES,
    build_enhance_existing_plan,
    create_harness,
    empty_enhance_existing_plan,
)
from .generation.public_repo_corpus import (
    build_public_repo_corpus_report,
    format_public_repo_corpus_report,
)
from .generation.update import build_drift_report, plan_or_apply_update
from .project.detect import detect_project
from .project.finalize_review import (
    build_review_finalization_plan,
    format_review_finalization_plan,
)
from .project.file_coverage import build_file_coverage_report
from .project.indexer import build_index_report, format_index_report
from .project.nested_instructions import build_nested_instruction_plan
from .project.planner import build_diff_plan, diff_plan_to_dict, format_diff_plan
from .project.readiness import (
    ReadinessReport,
    format_readiness,
    inspect_readiness,
    readiness_to_dict,
)
from .project.session import (
    build_session_report,
    format_session_report,
    session_report_to_dict,
)
from .project.state_migration import (
    build_state_migration_plan,
    format_state_migration_plan,
)
from .project.sync import format_sync_check, sync_check_to_dict, sync_exit_code
from .project.verify import (
    DEFAULT_TIMEOUT_SECONDS,
    build_verify_plan,
    compact_verify_report_to_dict,
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

    index = subparsers.add_parser(
        "index",
        help="build a read-only structural repository index",
    )
    index.add_argument("--target", type=Path, default=Path.cwd())
    index.add_argument("--package-manager")
    index.add_argument("--command", dest="commands", action="append", default=[])
    index.add_argument(
        "--max-files",
        type=int,
        default=4000,
        help="maximum number of repository files to include in the structural index",
    )
    index.add_argument(
        "--component-limit",
        type=int,
        default=80,
        help="maximum number of detected components to include in the index",
    )
    index.add_argument("--json", action="store_true")
    index.set_defaults(func=_index)

    effectiveness = subparsers.add_parser(
        "effectiveness",
        help="assess stored harness effectiveness evidence without running benchmarks",
    )
    effectiveness.add_argument("--target", type=Path, default=Path.cwd())
    effectiveness.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="target-relative effectiveness evidence JSON path",
    )
    effectiveness.add_argument("--json", action="store_true")
    effectiveness.set_defaults(func=_effectiveness)

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
        "--max-files",
        type=int,
        default=4000,
        help="maximum number of repository files to scan for the dry-run plan",
    )
    quickstart.add_argument(
        "--component-limit",
        type=int,
        default=80,
        help="maximum number of detected components to include in the dry-run plan",
    )
    quickstart.add_argument(
        "--enhance-existing",
        action="store_true",
        help="preview instruction-file enhancement instead of preserving existing routers",
    )
    quickstart.add_argument(
        "--interactive",
        action="store_true",
        help=(
            "emit an interactive-ready decision plan; no prompts are shown unless "
            "a future interactive runner is added"
        ),
    )
    quickstart.add_argument("--json", action="store_true")
    quickstart.set_defaults(func=_quickstart)

    corpus = subparsers.add_parser(
        "corpus",
        help="run the offline public-repo fixture quality corpus",
    )
    corpus.add_argument("--json", action="store_true")
    corpus.add_argument(
        "--min-score",
        type=int,
        default=0,
        help="minimum acceptable fixture quality score",
    )
    corpus.set_defaults(func=_corpus)

    enhance = subparsers.add_parser(
        "enhance",
        help="review existing instruction files without writing files",
    )
    enhance.add_argument("--target", type=Path, default=Path.cwd())
    enhance.add_argument("--agent-file", default="AGENTS.md")
    enhance.add_argument("--package-manager")
    enhance.add_argument("--command", dest="commands", action="append", default=[])
    enhance.add_argument("--json", action="store_true")
    enhance.set_defaults(func=_enhance)

    finalize_review = subparsers.add_parser(
        "finalize-review",
        help="finalize first-agent review evidence with explicit writes",
    )
    finalize_review.add_argument("--target", type=Path, default=Path.cwd())
    finalize_review.add_argument("--package-manager")
    finalize_review.add_argument(
        "--command",
        dest="commands",
        action="append",
        default=[],
    )
    finalize_review.add_argument(
        "--reviewed-by",
        action="append",
        default=[],
        help="reviewer name to record in first-agent review evidence",
    )
    finalize_review.add_argument(
        "--evidence-ref",
        action="append",
        default=[],
        help="target-relative evidence reference to record",
    )
    finalize_review.add_argument(
        "--accept-detected-high-risk",
        action="store_true",
        help="record accepted advisory evidence for detected high-risk surfaces",
    )
    finalize_review.add_argument(
        "--apply",
        action="store_true",
        help="write finalized review evidence; default is dry-run",
    )
    finalize_review.add_argument(
        "--yes",
        action="store_true",
        help="confirm apply-mode review finalization in non-interactive runs",
    )
    finalize_review.add_argument("--json", action="store_true")
    finalize_review.add_argument(
        "--json-report",
        help="write finalization JSON to a target-relative path",
    )
    finalize_review.set_defaults(func=_finalize_review)

    migrate_state = subparsers.add_parser(
        "migrate-state",
        help="plan or apply legacy progress/session state migration",
    )
    migrate_state.add_argument("--target", type=Path, default=Path.cwd())
    migrate_state.add_argument(
        "--apply",
        action="store_true",
        help="write the current-state.md migration section; default is dry-run",
    )
    migrate_state.add_argument(
        "--yes",
        action="store_true",
        help="confirm apply-mode state migration in non-interactive runs",
    )
    migrate_state.add_argument("--json", action="store_true")
    migrate_state.add_argument(
        "--json-report",
        help="write migration JSON to a target-relative path",
    )
    migrate_state.set_defaults(func=_migrate_state)

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
        "--max-files",
        type=int,
        default=4000,
        help="maximum number of repository files to scan while generating the harness",
    )
    init.add_argument(
        "--component-limit",
        type=int,
        default=80,
        help="maximum number of detected components to include while generating",
    )
    init.add_argument(
        "--with-ci-workflow",
        action="store_true",
        help="also scaffold a manual HarnessForge CI workflow",
    )
    init.add_argument("--force", action="store_true")
    init.add_argument(
        "--yes",
        action="store_true",
        help="confirm destructive overwrite behavior in non-interactive runs",
    )
    init.add_argument(
        "--enhance-existing",
        action="store_true",
        help="append reviewed HarnessForge guidance to existing instruction files",
    )
    init.add_argument("--dry-run", action="store_true")
    init.add_argument(
        "--json",
        action="store_true",
        help="write the dry-run init plan as JSON",
    )
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
        "--max-files",
        type=int,
        default=4000,
        help="maximum number of repository files to scan while updating the harness",
    )
    update.add_argument(
        "--component-limit",
        type=int,
        default=80,
        help="maximum number of detected components to include while updating",
    )
    update.add_argument("--apply", action="store_true")
    update.add_argument("--force", action="store_true")
    update.add_argument(
        "--yes",
        action="store_true",
        help="confirm apply-mode update behavior in non-interactive runs",
    )
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

    session = subparsers.add_parser(
        "session",
        help="show a read-only restart snapshot for a target repository",
    )
    session.add_argument("--target", type=Path, default=Path.cwd())
    session.add_argument("--json", action="store_true")
    session.set_defaults(func=_session)

    report = subparsers.add_parser(
        "report",
        help="compose a read-only harness status report",
    )
    report.add_argument("--target", type=Path, default=Path.cwd())
    report.add_argument("--package-manager")
    report.add_argument("--command", dest="commands", action="append", default=[])
    report.add_argument(
        "--max-files",
        type=int,
        default=4000,
        help="maximum number of repository files to include in the index summary",
    )
    report.add_argument(
        "--component-limit",
        type=int,
        default=80,
        help="maximum number of detected components to include in the index summary",
    )
    report.add_argument(
        "--require-verify-evidence",
        action="store_true",
        help="include release-gate verify evidence blockers in readiness",
    )
    report.add_argument(
        "--since",
        help="include read-only docs fan-out analysis for changes since this git ref",
    )
    report.add_argument(
        "--require-docs-fanout-budget",
        action="store_true",
        help="return a blocking status when docs fan-out exceeds the budget",
    )
    report.add_argument("--json", action="store_true")
    report.add_argument(
        "--json-report",
        help="write report JSON to a target-relative path",
    )
    report.add_argument(
        "--markdown-report",
        help="write report Markdown to a target-relative path",
    )
    report.set_defaults(func=_report)

    release_check = subparsers.add_parser(
        "release-check",
        help="assemble read-only release readiness evidence",
    )
    release_check.add_argument("--target", type=Path, default=Path.cwd())
    release_check.add_argument("--package-manager")
    release_check.add_argument("--command", dest="commands", action="append", default=[])
    release_check.add_argument("--min-score", type=int, default=85)
    release_check.add_argument(
        "--max-files",
        type=int,
        default=4000,
        help="maximum number of repository files to include in the index summary",
    )
    release_check.add_argument(
        "--component-limit",
        type=int,
        default=80,
        help="maximum number of detected components to include in the index summary",
    )
    release_check.add_argument(
        "--since",
        help="include read-only docs fan-out analysis for changes since this git ref",
    )
    release_check.add_argument(
        "--require-docs-fanout-budget",
        action="store_true",
        help="block when docs fan-out exceeds the budget",
    )
    release_check.add_argument(
        "--require-sbom",
        action="store_true",
        help="block unless an existing SPDX or CycloneDX SBOM is detected",
    )
    release_check.add_argument("--json", action="store_true")
    release_check.add_argument(
        "--json-report",
        help="write release-check JSON to a target-relative path",
    )
    release_check.add_argument(
        "--markdown-report",
        help="write release-check Markdown to a target-relative path",
    )
    release_check.set_defaults(func=_release_check)

    plan = subparsers.add_parser(
        "plan",
        help="map changed files to a read-only verification plan",
    )
    plan.add_argument("--target", type=Path, default=Path.cwd())
    plan.add_argument(
        "--since",
        default="HEAD",
        help="git revision or ref to diff against",
    )
    plan.add_argument("--package-manager")
    plan.add_argument("--command", dest="commands", action="append", default=[])
    plan.add_argument("--json", action="store_true")
    plan.set_defaults(func=_plan)

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
        "--evidence-summary",
        help=(
            "write compact verify evidence JSON without stdout/stderr previews "
            "to a target-relative path"
        ),
    )
    verify.add_argument(
        "--run",
        action="store_true",
        help="execute planned checks explicitly instead of reporting plan mode",
    )
    verify.add_argument(
        "--yes",
        action="store_true",
        help="confirm target command execution in non-interactive runs",
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
    blueprint_apply.add_argument(
        "--yes",
        action="store_true",
        help="confirm blueprint writes in non-interactive runs",
    )
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
        if profile.component_scan_truncated:
            print(
                "  - REVIEW REQUIRED: component inventory reached the "
                f"{profile.component_scan_limit}-component detection limit"
            )
    else:
        print("  - none detected")
    return 0


def _index(args: argparse.Namespace) -> int:
    profile = detect_project(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
        max_files=args.max_files,
        max_components=args.component_limit,
    )
    report = build_index_report(profile)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_index_report(report))
    return 0


def _effectiveness(args: argparse.Namespace) -> int:
    profile = detect_project(args.target)
    report = build_effectiveness_assessment(
        profile,
        evidence_paths=tuple(args.evidence),
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_effectiveness_assessment(report))
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
        max_files=args.max_files,
        max_components=args.component_limit,
    )
    report = inspect_readiness(profile)
    if args.json:
        print(json.dumps(_quickstart_to_dict(args, profile, report, writes), indent=2))
    else:
        print(
            _format_quickstart(
                profile,
                report,
                writes,
                max_files=args.max_files,
                component_limit=args.component_limit,
            )
        )
        if args.interactive:
            return _quickstart_interactive_prompt(args, writes)
    return 0


def _quickstart_interactive_prompt(
    args: argparse.Namespace,
    writes: tuple[WriteResult, ...],
) -> int:
    planned_writes = tuple(
        write for write in writes if write.status in {"would_write", "would_enhance"}
    )
    if not planned_writes:
        print("\nInteractive: no generated writes are planned.")
        return 0
    if not sys.stdin.isatty():
        print(
            "\nInteractive prompts skipped because stdin is not a TTY. "
            "Run the shown init command when ready to write."
        )
        return 0
    answer = input("\nWrite the planned HarnessForge files now? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        print("No files written.")
        return 0
    _, applied = create_harness(
        args.target,
        agent_file=args.agent_file,
        force=False,
        enhance_existing=args.enhance_existing,
        dry_run=False,
        package_manager=args.package_manager,
        commands=tuple(args.commands),
        project_name=args.project_name,
        platform_contract=args.platform_contract,
        max_files=args.max_files,
        max_components=args.component_limit,
    )
    print("Writes:")
    for write in applied:
        suffix = f" ({write.reason})" if write.reason else ""
        print(f"  - {write.status.upper()} {_relative(write.path, args.target)}{suffix}")
    return 0


def _quickstart_to_dict(
    args: argparse.Namespace,
    profile: ProjectProfile,
    report: ReadinessReport,
    writes: tuple[WriteResult, ...],
) -> dict[str, object]:
    planned_paths = sorted(
        _relative(result.path, profile.root)
        for result in writes
        if result.status in {"would_write", "would_enhance"}
    )
    preserved = sorted(
        _relative(result.path, profile.root)
        for result in writes
        if result.status == "skipped"
    )
    decisions = {
        "agentFile": args.agent_file,
        "platformContract": args.platform_contract,
        "packageManager": args.package_manager,
        "projectName": args.project_name,
        "enhanceExisting": bool(args.enhance_existing),
        "verificationCommands": list(args.commands),
        "maxFiles": args.max_files,
        "componentLimit": args.component_limit,
        "writeMode": "dry_run",
    }
    return {
        "schemaVersion": "harnessforge.quickstartPlan.v1",
        "mode": "read_only",
        "interactive": bool(args.interactive),
        "target": {
            "name": profile.name,
            "root": None,
        },
        "detectedStack": profile.stack,
        "repositoryScan": _scan_to_dict(profile),
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
        },
        "decisions": decisions,
        "readiness": readiness_to_dict(report),
        "nestedInstructionPlan": build_nested_instruction_plan(profile),
        "plannedWrites": planned_paths,
        "preservedFiles": preserved,
        "reviewRequired": list(report.review_required),
        "reproducibleCommands": {
            "quickstart": _quickstart_repro_command(args),
            "init": _quickstart_init_repro_command(args),
            "sync": _quickstart_sync_repro_command(args),
        },
    }


def _quickstart_repro_command(args: argparse.Namespace) -> str:
    parts = [
        "harnessforge",
        "quickstart",
        "--target",
        "<repo>",
        "--agent-file",
        args.agent_file,
        "--platform-contract",
        args.platform_contract,
        "--max-files",
        str(args.max_files),
        "--component-limit",
        str(args.component_limit),
    ]
    if args.package_manager:
        parts.extend(["--package-manager", args.package_manager])
    for command in args.commands:
        parts.extend(["--command", _quote_command(command)])
    if args.project_name:
        parts.extend(["--project-name", _quote_command(args.project_name)])
    if args.enhance_existing:
        parts.append("--enhance-existing")
    if args.interactive:
        parts.append("--interactive")
    return " ".join(parts)


def _quickstart_init_repro_command(args: argparse.Namespace) -> str:
    parts = [
        "harnessforge",
        "init",
        "--target",
        "<repo>",
        "--dry-run",
        "--agent-file",
        args.agent_file,
        "--platform-contract",
        args.platform_contract,
        "--max-files",
        str(args.max_files),
        "--component-limit",
        str(args.component_limit),
    ]
    if args.package_manager:
        parts.extend(["--package-manager", args.package_manager])
    for command in args.commands:
        parts.extend(["--command", _quote_command(command)])
    if args.project_name:
        parts.extend(["--project-name", _quote_command(args.project_name)])
    if args.enhance_existing:
        parts.append("--enhance-existing")
    return " ".join(parts)


def _quickstart_sync_repro_command(args: argparse.Namespace) -> str:
    parts = ["harnessforge", "sync", "--check", "--target", "<repo>"]
    if args.package_manager:
        parts.extend(["--package-manager", args.package_manager])
    for command in args.commands:
        parts.extend(["--command", _quote_command(command)])
    return " ".join(parts)


def _quote_command(value: str) -> str:
    if not value:
        return "''"
    if any(char.isspace() for char in value) or any(char in value for char in "\"'"):
        return json.dumps(value)
    return value


def _confirm_destructive(
    action: str,
    *,
    confirmed: bool,
    details: tuple[str, ...],
) -> None:
    if confirmed:
        return
    if not sys.stdin.isatty():
        raise ValueError(
            f"{action} can change repository state and requires --yes "
            "in non-interactive runs"
        )
    print(f"WARNING: {action} can change repository state.", file=sys.stderr)
    for detail in details:
        print(f"- {detail}", file=sys.stderr)
    answer = input("Type 'yes' to continue: ").strip()
    if answer != "yes":
        raise ValueError(f"{action} cancelled")


def _corpus(args: argparse.Namespace) -> int:
    payload = build_public_repo_corpus_report()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(format_public_repo_corpus_report(payload), end="")
    minimum = int(payload["summary"]["minimumScore"])
    return 1 if args.min_score and minimum < args.min_score else 0


def _enhance(args: argparse.Namespace) -> int:
    profile = detect_project(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
    )
    plan = build_enhance_existing_plan(profile, agent_file=args.agent_file)
    payload = _enhance_command_to_dict(profile, plan)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(_format_enhance_plan(profile, plan))
    return 0


def _enhance_command_to_dict(
    profile: ProjectProfile,
    plan: dict[str, object],
) -> dict[str, object]:
    return {
        "schemaVersion": "harnessforge.enhanceCommand.v1",
        "mode": "review",
        "target": {
            "name": profile.name,
            "root": None,
        },
        "detectedStack": profile.stack,
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
        },
        "verificationCommands": list(profile.verification_commands),
        "enhanceExistingPlan": plan,
    }


def _format_enhance_plan(
    profile: ProjectProfile,
    plan: dict[str, object],
) -> str:
    summary = plan.get("summary", {})
    files = plan.get("files", [])
    lines = [
        f"Enhance review for {profile.name}",
        "Mode: review only",
        f"Detected stack: {profile.stack}",
        f"Files reviewed: {_summary_value(summary, 'files')}",
        f"Would enhance: {_summary_value(summary, 'wouldEnhance')}",
        f"Review findings: {_summary_value(summary, 'reviewFindings')}",
        f"Proposed edits: {_summary_value(summary, 'proposedEdits')}",
        f"Patch previews: {_summary_value(summary, 'patchPreviews')}",
        "No files were changed.",
    ]
    if not files:
        lines.append("No existing instruction files were found.")
        return "\n".join(lines)
    lines.append("")
    lines.append("Files:")
    file_items = files if isinstance(files, list) else []
    for item in file_items:
        if not isinstance(item, dict):
            continue
        lines.extend(_format_enhance_file(item))
    return "\n".join(lines)


def _summary_value(summary: object, key: str) -> object:
    if isinstance(summary, dict):
        return summary.get(key, 0)
    return 0


def _format_enhance_file(item: dict[str, object]) -> list[str]:
    path = item.get("path", "<unknown>")
    status = item.get("status", "unknown")
    lines = [f"  - {path}: {status}"]
    coverage = item.get("sectionCoverage", {})
    if isinstance(coverage, dict):
        missing = coverage.get("missing", [])
        if missing:
            lines.append(f"    missing sections: {_join_values(missing)}")
    findings = item.get("findings", [])
    if isinstance(findings, list) and findings:
        lines.append(
            "    findings: "
            + ", ".join(
                str(finding.get("type", "unknown"))
                for finding in findings
                if isinstance(finding, dict)
            )
        )
    proposed = item.get("proposedEdits", [])
    if isinstance(proposed, list) and proposed:
        lines.append(
            "    proposed edits: "
            + ", ".join(
                str(edit.get("action", "unknown"))
                for edit in proposed
                if isinstance(edit, dict)
            )
        )
    return lines


def _join_values(values: object) -> str:
    if isinstance(values, list):
        return ", ".join(str(value) for value in values)
    return str(values)


def _finalize_review(args: argparse.Namespace) -> int:
    if args.apply:
        preview = build_review_finalization_plan(
            args.target,
            apply=False,
            accept_detected_high_risk=args.accept_detected_high_risk,
            explicit_package_manager=args.package_manager,
            explicit_commands=tuple(args.commands),
            reviewed_by=tuple(args.reviewed_by),
            evidence_refs=tuple(args.evidence_ref),
        )
        if preview.payload["review"]["requiresHighRiskAcceptanceFlag"]:
            raise ValueError(
                "review finalization detected high-risk surfaces; rerun with "
                "--accept-detected-high-risk to record accepted advisory evidence"
            )
        _confirm_destructive(
            "finalize-review --apply",
            confirmed=args.yes,
            details=(
                "writes first-agent review evidence and task retirement state",
                "refreshes manifest metadata for reviewed generated files",
            ),
        )
    plan = build_review_finalization_plan(
        args.target,
        apply=args.apply,
        accept_detected_high_risk=args.accept_detected_high_risk,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
        reviewed_by=tuple(args.reviewed_by),
        evidence_refs=tuple(args.evidence_ref),
    )
    json_path = write_json_payload(args.json_report or "", args.target, plan.payload)
    if args.json:
        output = dict(plan.payload)
        output["jsonReport"] = json_path
        print(json.dumps(output, indent=2))
    else:
        print(format_review_finalization_plan(plan.payload), end="")
        if json_path:
            print(f"JSON report written: {json_path}")
    return 0


def _migrate_state(args: argparse.Namespace) -> int:
    if args.apply:
        _confirm_destructive(
            "migrate-state --apply",
            confirmed=args.yes,
            details=(
                "writes or updates current-state.md in the target repository",
                "preserves legacy progress.md and session-handoff.md for review",
            ),
        )
    plan = build_state_migration_plan(args.target, apply=args.apply)
    json_path = write_json_payload(args.json_report or "", args.target, plan.payload)
    if args.json:
        output = dict(plan.payload)
        output["jsonReport"] = json_path
        print(json.dumps(output, indent=2))
    else:
        print(format_state_migration_plan(plan.payload), end="")
        if json_path:
            print(f"JSON report written: {json_path}")
    return 0


def _init(args: argparse.Namespace) -> int:
    if args.json and not args.dry_run:
        raise ValueError("init --json currently requires --dry-run")
    if args.force and not args.dry_run:
        _confirm_destructive(
            "init --force",
            confirmed=args.yes,
            details=(
                "may overwrite existing generated harness files",
                "preserved project-owned files should be reviewed first",
            ),
        )
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
        platform_contract=args.platform_contract,
        max_files=args.max_files,
        max_components=args.component_limit,
    )
    if args.json:
        print(
            json.dumps(
                _init_plan_to_dict(profile, results, args),
                indent=2,
            )
        )
        return 0
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
    if args.dry_run:
        for line in _nested_instruction_lines(profile):
            print(line)
    for warning in _preserved_file_warnings(results, profile.root):
        print(warning)
    for warning in _workflow_warnings(args.with_ci_workflow):
        print(warning)
    return 0


def _init_plan_to_dict(
    profile: ProjectProfile,
    results: tuple[WriteResult, ...],
    args: argparse.Namespace,
) -> dict[str, object]:
    enhance_plan = (
        build_enhance_existing_plan(
            profile,
            agent_file=args.agent_file,
            writes=results,
        )
        if args.enhance_existing
        else empty_enhance_existing_plan(profile, agent_file=args.agent_file)
    )
    return {
        "schemaVersion": "harnessforge.initPlan.v1",
        "mode": "dry_run",
        "target": {
            "name": profile.name,
            "root": None,
        },
        "detectedStack": profile.stack,
        "repositoryScan": _scan_to_dict(profile),
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
        },
        "verificationCommands": list(profile.verification_commands),
        "nestedInstructionPlan": build_nested_instruction_plan(profile),
        "writes": [
            {
                "path": _relative(result.path, profile.root),
                "status": result.status,
                "reason": result.reason,
            }
            for result in results
        ],
        "enhanceExistingPlan": enhance_plan,
    }


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
    if args.apply:
        _confirm_destructive(
            "update --apply",
            confirmed=args.yes,
            details=(
                "writes harness corrections inside the target repository",
                "use --drift-report first when reviewing generated-file changes",
            ),
        )
    before, profile, writes = plan_or_apply_update(
        args.target,
        apply=args.apply,
        force=args.force,
        enhance_existing=args.enhance_existing,
        agent_file=args.agent_file,
        with_ci_workflow=args.with_ci_workflow,
        platform_contract=args.platform_contract,
        max_files=args.max_files,
        max_components=args.component_limit,
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
    for warning in _workflow_warnings(args.with_ci_workflow):
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


def _session(args: argparse.Namespace) -> int:
    report = build_session_report(args.target)
    if args.json:
        print(json.dumps(session_report_to_dict(report), indent=2))
    else:
        print(format_session_report(report))
    return 0


def _report(args: argparse.Namespace) -> int:
    payload = build_report(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
        max_files=args.max_files,
        max_components=args.component_limit,
        require_verify_evidence=args.require_verify_evidence,
        require_docs_fanout_budget=args.require_docs_fanout_budget,
        since=args.since,
    )
    target = args.target.resolve()
    json_report = write_json_payload(args.json_report or "", target, payload)
    markdown_report = write_markdown_report(
        args.markdown_report or "",
        target,
        payload,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return _report_exit_code(payload)
    if markdown_report:
        print(f"Markdown report written to {markdown_report}")
    if json_report:
        print(f"JSON report written to {json_report}")
    print(format_report(payload))
    return _report_exit_code(payload)


def _report_exit_code(payload: dict[str, object]) -> int:
    docs_fanout = payload.get("docsFanout", {})
    if isinstance(docs_fanout, dict):
        contract = docs_fanout.get("contract", {})
        if isinstance(contract, dict) and contract.get("verdict") == "blocked":
            return 2
    return 0


def _release_check(args: argparse.Namespace) -> int:
    payload = build_release_check(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
        max_files=args.max_files,
        max_components=args.component_limit,
        min_score=args.min_score,
        require_docs_fanout_budget=args.require_docs_fanout_budget,
        require_sbom=args.require_sbom,
        since=args.since,
    )
    target = args.target.resolve()
    json_report = write_json_payload(args.json_report or "", target, payload)
    markdown_report = write_markdown_release_check(
        args.markdown_report or "",
        target,
        payload,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return release_check_exit_code(payload)
    if markdown_report:
        print(f"Markdown release check written to {markdown_report}")
    if json_report:
        print(f"JSON release check written to {json_report}")
    print(format_release_check(payload))
    return release_check_exit_code(payload)


def _plan(args: argparse.Namespace) -> int:
    profile = detect_project(
        args.target,
        explicit_package_manager=args.package_manager,
        explicit_commands=tuple(args.commands),
    )
    report = build_diff_plan(
        profile,
        since=args.since,
        explicit_commands=tuple(args.commands),
    )
    if args.json:
        print(json.dumps(diff_plan_to_dict(report), indent=2))
    else:
        print(format_diff_plan(report))
    return 0


def _verify(args: argparse.Namespace) -> int:
    if args.timeout_seconds <= 0:
        raise ValueError("--timeout-seconds must be greater than 0")
    if args.run:
        _confirm_destructive(
            "verify --run",
            confirmed=args.yes,
            details=(
                "executes target repository verification commands",
                "commands may write files or perform project-defined side effects",
            ),
        )
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
    summary_payload = compact_verify_report_to_dict(report)
    evidence_summary = write_json_payload(
        args.evidence_summary or "",
        profile.root,
        summary_payload,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if json_report:
            print(f"Verify JSON report written to {json_report}")
        if evidence_summary:
            print(f"Verify evidence summary written to {evidence_summary}")
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
    if not args.dry_run:
        _confirm_destructive(
            "blueprint apply",
            confirmed=args.yes,
            details=(
                "writes optional blueprint artifacts inside the target repository",
                "use --dry-run first and review generated artifacts before apply",
            ),
        )
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
    *,
    max_files: int = 4000,
    component_limit: int = 80,
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
    nested_plan = build_nested_instruction_plan(profile)
    _append_cli_section(
        lines,
        "Nested AGENTS.md candidates",
        _nested_instruction_candidate_lines(nested_plan),
    )
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
        _quickstart_commands(
            report,
            has_planned_writes,
            max_files=max_files,
            component_limit=component_limit,
        ),
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
    report: ReadinessReport,
    has_planned_writes: bool,
    *,
    max_files: int = 4000,
    component_limit: int = 80,
) -> tuple[str, ...]:
    if report.verdict == "blocked":
        return (
            "harnessforge inspect --target <repo> --readiness",
            'harnessforge inspect --target <repo> --readiness --command "<check command>"',
            'harnessforge sync --check --target <repo> --command "<check command>"',
        )
    commands = []
    if has_planned_writes:
        max_files_suffix = (
            f" --max-files {max_files}" if max_files != 4000 else ""
        )
        component_limit_suffix = (
            f" --component-limit {component_limit}"
            if component_limit != 80
            else ""
        )
        commands.extend(
            [
                "harnessforge init --target <repo> --dry-run"
                f"{max_files_suffix}{component_limit_suffix}",
                "harnessforge init --target <repo>"
                f"{max_files_suffix}{component_limit_suffix}",
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
        "verificationCommandDetails": _verification_command_details_to_dict(profile),
        "components": list(profile.components),
        "fileScan": _scan_to_dict(profile),
        "componentScan": _component_scan_to_dict(profile),
        "workspaceMarkers": list(profile.workspace_markers),
        "routingMarkers": list(profile.routing_markers),
        "configPrecedence": list(profile.config_precedence),
    }


def _scan_to_dict(profile: ProjectProfile) -> dict[str, object]:
    return {
        "fileCount": len(profile.files),
        "maxFiles": profile.file_scan_limit,
        "truncated": profile.file_scan_truncated,
        "coverage": build_file_coverage_report(profile),
        "componentScan": _component_scan_to_dict(profile),
    }


def _component_scan_to_dict(profile: ProjectProfile) -> dict[str, object]:
    return {
        "limit": profile.component_scan_limit,
        "includedCount": len(profile.components),
        "totalCount": profile.component_scan_total,
        "omittedCount": len(profile.component_overflow),
        "truncated": profile.component_scan_truncated,
        "omittedExamples": list(profile.component_overflow[:20]),
    }


def _verification_command_details_to_dict(
    profile: ProjectProfile,
) -> list[dict[str, str]]:
    return [
        {
            "command": record.command,
            "commandClass": record.command_class,
            "scope": record.scope,
            "sourceType": record.source_type,
            "sourcePath": record.source_path,
            "sourceDetail": record.source_detail,
            "confidence": record.confidence,
        }
        for record in profile.verification_command_records
    ]


def _nested_instruction_lines(profile: ProjectProfile) -> tuple[str, ...]:
    candidates = _nested_instruction_candidate_lines(
        build_nested_instruction_plan(profile)
    )
    if not candidates:
        return ()
    return (
        "REVIEW REQUIRED nested AGENTS.md candidates:",
        *(f"  - {candidate}" for candidate in candidates),
    )


def _nested_instruction_candidate_lines(plan: dict[str, object]) -> tuple[str, ...]:
    if plan.get("status") != "review_required":
        return ()
    candidates = plan.get("candidateComponents", [])
    if not isinstance(candidates, list):
        return ()
    lines = [
        str(item["instructionPath"])
        for item in candidates[:10]
        if isinstance(item, dict) and isinstance(item.get("instructionPath"), str)
    ]
    if plan.get("candidateListTruncated"):
        lines.append("... more candidates in JSON output")
    return tuple(lines)


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
        return path.resolve().relative_to(root.resolve()).as_posix()
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


def _workflow_warnings(with_ci_workflow: bool) -> tuple[str, ...]:
    if not with_ci_workflow:
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
