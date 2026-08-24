"""Command-line interface for AltRecheck."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .gitrepo import GitRepository, GitRepositoryError
from .models import Finding, Report
from .scanner import scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="altrecheck",
        description="Flag changed images whose alternative text did not change.",
    )
    parser.add_argument("--base", default="HEAD^", help="Base Git revision (default: HEAD^)")
    parser.add_argument("--head", default="HEAD", help="Head Git revision (default: HEAD)")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository directory")
    parser.add_argument(
        "--format", choices=("text", "json", "github"), default="text", help="Output format"
    )
    parser.add_argument("--no-fail", action="store_true", help="Exit 0 even when findings exist")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _render_text(report: Report) -> str:
    if not report.findings:
        return f"AltRecheck: clear ({len(report.changes)} changed images checked)"
    lines = [f"AltRecheck: {len(report.findings)} alt-text review finding(s)"]
    for finding in report.findings:
        alt = "missing" if finding.alt is None else repr(finding.alt)
        lines.append(
            f"{finding.document}:{finding.line}: warning [{finding.rule}] "
            f"{finding.message} image={finding.image_path!r} alt={alt}"
        )
    return "\n".join(lines)


def _escape_command(value: str, *, property_value: bool = False) -> str:
    escaped = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if property_value:
        escaped = escaped.replace(":", "%3A").replace(",", "%2C")
    return escaped


def _render_github_finding(finding: Finding) -> str:
    document = _escape_command(finding.document, property_value=True)
    message = _escape_command(f"{finding.message} Image: {finding.image_path}")
    title = _escape_command(f"AltRecheck: {finding.rule}", property_value=True)
    return f"::warning file={document},line={finding.line},title={title}::{message}"


def _render(report: Report, output_format: str) -> str:
    if output_format == "json":
        return report.to_json()
    if output_format == "github":
        if not report.findings:
            return f"AltRecheck: clear ({len(report.changes)} changed images checked)"
        return "\n".join(_render_github_finding(item) for item in report.findings)
    return _render_text(report)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = scan_repository(GitRepository(args.repo), args.base, args.head)
    except GitRepositoryError as error:
        print(f"altrecheck: error: {error}", file=sys.stderr)
        return 2
    print(_render(report, args.format))
    return 0 if args.no_fail or not report.findings else 1
