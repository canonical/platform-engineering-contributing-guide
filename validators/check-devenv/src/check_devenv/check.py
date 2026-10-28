"""Checks for the opencode development environment."""

from __future__ import annotations

import json
import re
import shutil
import subprocess  # nosec B404
from collections.abc import Callable, Sequence
from pathlib import Path

from pfe_validators_common import Finding

PRACTICE_ID = "PFE-DEV-001"
MIN_VERSION = (1, 19, 4)
MODEL_RE = re.compile(r"^[^/]+/claude-sonnet-5[.-]5$")

# Runs a command and returns its standard output.
Runner = Callable[[Sequence[str], Path | None], str]


class CommandError(RuntimeError):
    """Raised when a command cannot be run or fails."""


def run_command(command: Sequence[str], cwd: Path | None = None) -> str:
    """Run a command and return its standard output."""
    try:
        result = subprocess.run(  # nosec B603
            list(command), cwd=cwd, capture_output=True, text=True, check=True, timeout=120
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CommandError(f"{' '.join(command)}: {exc}") from exc
    return result.stdout


def parse_version(text: str) -> tuple[int, ...] | None:
    """Parse the leading numeric ``major.minor.patch`` of a version string."""
    match = re.match(r"^v?(\d+(?:\.\d+)*)", text.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def _installed_snap_version(run: Runner) -> str | None:
    """Return the opencode snap version, or None if the snap is not installed."""
    if shutil.which("snap") is None:
        return None
    try:
        output = run(["snap", "list", "opencode"], None)
    except CommandError:
        return None
    lines = output.strip().splitlines()
    if len(lines) < 2:
        return None
    columns = lines[1].split()
    return columns[1] if len(columns) > 1 and columns[0] == "opencode" else None


def check_snap(run: Runner) -> list[Finding]:
    """Check that the opencode snap is installed at the minimum version."""
    wanted = ".".join(map(str, MIN_VERSION))
    version = _installed_snap_version(run)
    if version is None:
        return [
            Finding(
                PRACTICE_ID,
                None,
                "opencode snap is not installed; run `sudo snap install opencode --classic`",
            )
        ]
    parsed = parse_version(version)
    if parsed is None:
        return [Finding(PRACTICE_ID, None, f"cannot parse opencode snap version {version!r}")]
    if parsed < MIN_VERSION:
        return [
            Finding(
                PRACTICE_ID,
                None,
                f"opencode snap version {version} is older than {wanted}; "
                "run `sudo snap refresh opencode`",
            )
        ]
    return []


def check_config(config: dict[str, object]) -> list[Finding]:
    """Check LSP and default model in the resolved opencode configuration."""
    findings: list[Finding] = []
    lsp = config.get("lsp")
    if lsp is not True and not isinstance(lsp, dict):
        findings.append(
            Finding(
                PRACTICE_ID,
                None,
                'LSP is not enabled in the opencode config; set `"lsp": true`',
            )
        )
    model = config.get("model")
    if not isinstance(model, str) or not MODEL_RE.match(model):
        findings.append(
            Finding(
                PRACTICE_ID,
                None,
                f"default model is {model!r}; expected Claude Sonnet 5.5, "
                'for example `"model": "github-copilot/claude-sonnet-5.5"`',
            )
        )
    return findings


def _resolved_config(run: Runner, project: Path) -> dict[str, object]:
    output = run(["opencode", "debug", "config"], project)
    try:
        config = json.loads(output)
    except json.JSONDecodeError as exc:
        raise CommandError(f"`opencode debug config` returned invalid JSON: {exc}") from exc
    if not isinstance(config, dict):
        raise CommandError("`opencode debug config` did not return a JSON object")
    return config


def check_environment(project: Path, run: Runner = run_command) -> list[Finding]:
    """Run all checks for the development environment, using ``project`` as config scope."""
    findings = check_snap(run)
    if shutil.which("opencode") is None:
        if not findings:
            findings.append(
                Finding(PRACTICE_ID, None, "`opencode` is not on PATH; is /snap/bin in PATH?")
            )
        return findings
    findings.extend(check_config(_resolved_config(run, project)))
    return findings


def check(paths: Sequence[Path]) -> list[Finding]:
    """Check the environment; the first path (a directory) scopes the opencode config."""
    project = paths[0] if paths else Path(".")
    return check_environment(project if project.is_dir() else project.parent)
