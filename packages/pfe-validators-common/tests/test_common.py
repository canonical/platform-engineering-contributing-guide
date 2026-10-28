from __future__ import annotations

import json
from pathlib import Path

import pytest

from pfe_validators_common import Finding, Severity, iter_files, render, run_cli


def test_render_text() -> None:
    finding = Finding("PFE-X-001", Path("a.py"), "bad", line=3, column=5)
    assert render([finding], "text") == "a.py:3:5: error: [PFE-X-001] bad"


def test_render_github_escapes() -> None:
    finding = Finding("PFE-X-001", Path("a,b.py"), "50%\nmore", line=1, severity=Severity.WARNING)
    assert (
        render([finding], "github")
        == "::warning file=a%2Cb.py,line=1,title=PFE-X-001::50%25%0Amore"
    )


def test_render_json() -> None:
    finding = Finding("PFE-X-001", Path("a.py"), "bad")
    assert json.loads(render([finding], "json")) == [
        {
            "practice": "PFE-X-001",
            "path": "a.py",
            "message": "bad",
            "line": None,
            "column": None,
            "severity": "error",
        }
    ]


def test_iter_files_filters_suffix_and_skips_venv(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.txt").write_text("")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "c.py").write_text("")
    files = list(iter_files([tmp_path], suffixes={".py"}, use_git=False))
    assert files == [tmp_path / "a.py"]


@pytest.mark.parametrize(("findings", "code"), [([], 0), ([Finding("P", Path("x"), "m")], 1)])
def test_run_cli_exit_codes(tmp_path: Path, findings: list[Finding], code: int) -> None:
    assert run_cli("t", "d", lambda _paths: findings, [str(tmp_path), "--format", "text"]) == code


def test_run_cli_missing_path(tmp_path: Path) -> None:
    assert run_cli("t", "d", lambda _paths: [], [str(tmp_path / "nope")]) == 2


def test_run_cli_check_error(tmp_path: Path) -> None:
    def boom(_paths: object) -> list[Finding]:
        raise RuntimeError("boom")

    assert run_cli("t", "d", boom, [str(tmp_path)]) == 2


def test_pathless_finding_renders() -> None:
    finding = Finding("PFE-X-001", None, "no file")
    assert render([finding], "text") == "<environment>: error: [PFE-X-001] no file"
    assert render([finding], "github") == "::error title=PFE-X-001::no file"
    assert json.loads(render([finding], "json"))[0]["path"] is None
