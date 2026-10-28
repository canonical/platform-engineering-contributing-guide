"""Validator logic."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pfe_validators_common import Finding, iter_files

PRACTICE_ID = "PFE-XXX-NNN"


def check(paths: Sequence[Path]) -> list[Finding]:
    """Return findings for files under ``paths``."""
    findings: list[Finding] = []
    for path in iter_files(paths, suffixes={".py"}):
        text = path.read_text(encoding="utf-8")
        if "forbidden" in text:
            findings.append(Finding(PRACTICE_ID, path, "replace with a real rule"))
    return findings
