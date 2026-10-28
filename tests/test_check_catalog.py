from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_catalog", REPO_ROOT / "tools" / "check_catalog.py"
)
assert _spec and _spec.loader
check_catalog_mod = importlib.util.module_from_spec(_spec)
sys.modules["check_catalog"] = check_catalog_mod
_spec.loader.exec_module(check_catalog_mod)
check_catalog = check_catalog_mod.check_catalog


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _write(tmp_path / "src" / "impl" / "todos.md", "# TODOs\n")
    _write(tmp_path / "skills" / "s" / "SKILL.md", "Applies PFE-IMPL-001\n")
    for name in ("pyproject.toml", "action.yml"):
        _write(tmp_path / "validators" / "v" / name, "")
    _write(tmp_path / "validators" / "v" / "README.md", "Checks PFE-IMPL-001\n")
    _write(tmp_path / "validators" / "_template" / "README.md", "ignored\n")
    _write(
        tmp_path / "catalog.yaml",
        """
areas: {IMPL: Implementation}
practices:
  - id: PFE-IMPL-001
    title: TODOs
    area: IMPL
    doc: src/impl/todos.md
    skills: [skills/s]
    validators: [validators/v]
""",
    )
    return tmp_path


def test_valid_catalog(repo: Path) -> None:
    assert check_catalog(repo) == []


def test_repository_catalog_is_valid() -> None:
    assert check_catalog(REPO_ROOT) == []


def test_detects_problems(repo: Path) -> None:
    _write(repo / "src" / "impl" / "orphan.md", "")
    _write(repo / "skills" / "orphan" / "SKILL.md", "Mentions PFE-IMPL-999\n")
    catalog = (repo / "catalog.yaml").read_text()
    catalog += """
  - id: PFE-IMPL-001
    title: Duplicate
    area: TEST
    doc: src/missing.md
    validators: [validators/missing]
"""
    (repo / "catalog.yaml").write_text(catalog)
    errors = "\n".join(check_catalog(repo))
    for expected in (
        "PFE-IMPL-001: duplicate ID",
        "ID area does not match",
        "unknown area 'TEST'",
        "doc not found: src/missing.md",
        "validators/missing is missing action.yml",
        "src/impl/orphan.md: documentation page not listed",
        "skills/orphan: not referenced",
        "mentions unknown practice ID PFE-IMPL-999",
    ):
        assert expected in errors


def test_local_only_validator_needs_no_action(repo: Path) -> None:
    (repo / "validators" / "v" / "action.yml").unlink()
    assert "validators/v is missing action.yml" in "\n".join(check_catalog(repo))
    (repo / "validators" / "v" / "pyproject.toml").write_text("[tool.pfe]\nlocal-only = true\n")
    assert check_catalog(repo) == []
