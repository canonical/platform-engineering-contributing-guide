"""Standard command line for validators."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from pfe_validators_common.findings import Finding
from pfe_validators_common.output import FORMATS, render

Check = Callable[[Sequence[Path]], Sequence[Finding]]

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2


def _default_format() -> str:
    return "github" if os.environ.get("GITHUB_ACTIONS") == "true" else "text"


def run_cli(
    name: str,
    description: str,
    check: Check,
    argv: Sequence[str] | None = None,
) -> int:
    """Parse arguments, run the check and print findings.

    Args:
        name: Program name shown in ``--help``.
        description: Short description shown in ``--help``.
        check: Callable receiving the paths to scan and returning findings.
        argv: Arguments to parse (defaults to ``sys.argv[1:]``).

    Returns:
        ``0`` when no findings, ``1`` when findings were reported, ``2`` on error.
    """
    parser = argparse.ArgumentParser(prog=name, description=description)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path(".")],
        help="files or directories to check (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=FORMATS,
        default=_default_format(),
        help="output format (default: github on GitHub Actions, text otherwise)",
    )
    args = parser.parse_args(argv)

    missing = [p for p in args.paths if not p.exists()]
    if missing:
        print(f"{name}: path not found: {', '.join(map(str, missing))}", file=sys.stderr)
        return EXIT_ERROR

    try:
        findings = list(check(args.paths))
    except Exception as exc:  # noqa: BLE001 - report any failure as a tool error
        print(f"{name}: error: {exc}", file=sys.stderr)
        return EXIT_ERROR

    output = render(findings, args.format)
    if output:
        print(output)
    if args.format != "json":
        print(f"{name}: {len(findings)} finding(s)", file=sys.stderr)
    return EXIT_FINDINGS if findings else EXIT_OK
