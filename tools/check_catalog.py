#!/usr/bin/env python3
"""Validate catalog.yaml and its links to docs, skills and validators.

Checks:
* every practice has a well-formed, unique ID whose area matches its ``area`` field;
* every referenced doc, skill and validator path exists and is well-formed;
* every documentation page under ``src/`` is listed in the catalog;
* every skill and validator is referenced by at least one practice;
* every practice ID mentioned in a skill or validator README exists in the catalog,
  and each skill/validator mentions at least one.

Usage: ``uv run tools/check_catalog.py [REPO_ROOT]``
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ID_RE = re.compile(r"^PFE-([A-Z]+)-(\d{3})$")
ID_TOKEN_RE = re.compile(r"\bPFE-[A-Z]+-\d{3}\b")
STATUSES = frozenset({"active", "draft", "retired"})
REQUIRED_FIELDS = ("id", "title", "area", "doc")
DOC_ROOTS = ("src",)


def _children(root: Path, directory: str) -> list[Path]:
    base = root / directory
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def _check_practice(root: Path, practice: Any, areas: dict[str, str], errors: list[str]) -> None:
    if not isinstance(practice, dict):
        errors.append(f"practice entry is not a mapping: {practice!r}")
        return
    pid = practice.get("id", "<missing id>")
    for field in REQUIRED_FIELDS:
        if not practice.get(field):
            errors.append(f"{pid}: missing required field {field!r}")
    match = ID_RE.match(str(pid))
    if not match:
        errors.append(f"{pid}: ID must match PFE-<AREA>-<NNN>")
    elif match.group(1) != practice.get("area"):
        errors.append(f"{pid}: ID area does not match area {practice.get('area')!r}")
    if practice.get("area") not in areas:
        errors.append(f"{pid}: unknown area {practice.get('area')!r}")
    if practice.get("status", "active") not in STATUSES:
        errors.append(f"{pid}: status must be one of {sorted(STATUSES)}")
    doc = practice.get("doc")
    if doc and not (root / doc).is_file():
        errors.append(f"{pid}: doc not found: {doc}")
    for skill in practice.get("skills") or []:
        if not (root / skill / "SKILL.md").is_file():
            errors.append(f"{pid}: skill not found (no SKILL.md): {skill}")
    for validator in practice.get("validators") or []:
        for required in ("pyproject.toml", "action.yml", "README.md"):
            if not (root / validator / required).is_file():
                errors.append(f"{pid}: validator {validator} is missing {required}")


def _check_mentions(path: Path, root: Path, known: set[str], errors: list[str]) -> None:
    rel = path.relative_to(root)
    if not path.is_file():
        errors.append(f"{rel.parent}: missing {rel.name}")
        return
    mentioned = set(ID_TOKEN_RE.findall(path.read_text(encoding="utf-8")))
    if not mentioned:
        errors.append(f"{rel}: does not mention any practice ID")
    for unknown in sorted(mentioned - known):
        errors.append(f"{rel}: mentions unknown practice ID {unknown}")


def check_catalog(root: Path) -> list[str]:
    """Return a list of human readable errors for the catalog at ``root``."""
    catalog_path = root / "catalog.yaml"
    if not catalog_path.is_file():
        return [f"{catalog_path} not found"]
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    areas: dict[str, str] = data.get("areas") or {}
    practices: list[Any] = data.get("practices") or []
    errors: list[str] = []

    seen: set[str] = set()
    for practice in practices:
        _check_practice(root, practice, areas, errors)
        pid = practice.get("id") if isinstance(practice, dict) else None
        if pid in seen:
            errors.append(f"{pid}: duplicate ID")
        if pid:
            seen.add(pid)

    entries = [p for p in practices if isinstance(p, dict)]
    referenced_docs = {p.get("doc") for p in entries}
    for doc_root in DOC_ROOTS:
        for doc in sorted((root / doc_root).rglob("*.md")):
            rel = doc.relative_to(root).as_posix()
            if rel not in referenced_docs:
                errors.append(f"{rel}: documentation page not listed in catalog.yaml")

    for kind, marker in (("skills", "SKILL.md"), ("validators", "README.md")):
        referenced = {ref.rstrip("/") for p in entries for ref in (p.get(kind) or [])}
        for directory in _children(root, kind):
            rel = directory.relative_to(root).as_posix()
            if rel not in referenced:
                errors.append(f"{rel}: not referenced by any practice in catalog.yaml")
            _check_mentions(directory / marker, root, seen, errors)

    return errors


def main(argv: list[str] | None = None) -> int:
    """Run the catalog check and print errors."""
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    errors = check_catalog(root)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    print(f"check_catalog: {len(errors)} error(s)", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
