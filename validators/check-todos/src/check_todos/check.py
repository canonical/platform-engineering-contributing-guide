"""Detect TODO/FIXME comments in source files."""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from pathlib import Path

from pfe_validators_common import Finding, iter_files

PRACTICE_ID = "PFE-IMPL-004"

SOURCE_SUFFIXES = frozenset(
    {
        ".py", ".pyi", ".sh", ".bash", ".go", ".rs", ".js", ".jsx", ".ts", ".tsx",
        ".c", ".h", ".cc", ".cpp", ".hpp", ".java", ".kt", ".rb", ".lua", ".tf",
        ".yaml", ".yml", ".toml", ".cfg", ".ini", ".j2", ".jinja", ".sql",
    }
)  # fmt: skip

# A comment marker followed (possibly after other text) by a TODO/FIXME token.
_PATTERN = re.compile(r"(?:#|//|/\*|<!--|--|;)[^\n]*?\b(TODO|FIXME)\b")


def scan_text(text: str) -> Iterator[tuple[int, int, str]]:
    """Yield ``(line, column, token)`` for every TODO/FIXME comment in ``text``."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _PATTERN.search(line)
        if match:
            yield lineno, match.start(1) + 1, match.group(1)


def check(paths: Sequence[Path]) -> list[Finding]:
    """Return a finding for each TODO/FIXME comment found under ``paths``."""
    findings: list[Finding] = []
    for path in iter_files(paths, suffixes=SOURCE_SUFFIXES):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line, column, token in scan_text(text):
            findings.append(
                Finding(
                    practice=PRACTICE_ID,
                    path=path,
                    line=line,
                    column=column,
                    message=f"{token} comment found; track it in the backlog and remove it "
                    "before merging",
                )
            )
    return findings
