"""File discovery helpers."""

from __future__ import annotations

import subprocess  # nosec B404
from collections.abc import Iterable, Iterator
from pathlib import Path

_ALWAYS_SKIPPED_DIRS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".tox"})


def _git_files(root: Path) -> list[Path] | None:
    """List tracked and untracked-but-not-ignored files under root, or None outside git."""
    try:
        result = subprocess.run(  # nosec B603 B607
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    names = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return [root / name for name in names if name]


def _walk(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in _ALWAYS_SKIPPED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            yield path


def iter_files(
    paths: Iterable[Path],
    suffixes: Iterable[str] | None = None,
    use_git: bool = True,
) -> Iterator[Path]:
    """Yield files under the given paths.

    Directories are expanded recursively. Inside a git work tree, ignored files are
    skipped. Explicitly passed files are always yielded if they match ``suffixes``.

    Args:
        paths: Files or directories to scan.
        suffixes: Optional file suffixes to keep (e.g. ``{".py"}``).
        use_git: Respect ``.gitignore`` through ``git ls-files`` when possible.
    """
    wanted = frozenset(suffixes) if suffixes is not None else None
    seen: set[Path] = set()
    for path in paths:
        if path.is_dir():
            candidates: Iterable[Path] = (_git_files(path) if use_git else None) or _walk(path)
        else:
            candidates = [path]
        for candidate in sorted(candidates):
            if candidate in seen or not candidate.is_file():
                continue
            if wanted is not None and candidate.suffix not in wanted:
                continue
            seen.add(candidate)
            yield candidate
