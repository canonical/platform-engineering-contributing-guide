from __future__ import annotations

from pathlib import Path

import pytest

from check_todos.check import PRACTICE_ID, check, scan_text
from check_todos.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("# TODO: x", [(1, 3, "TODO")]),
        ("x = 1  # FIXME", [(1, 10, "FIXME")]),
        ("// TODO", [(1, 4, "TODO")]),
        ("/* please TODO */", [(1, 11, "TODO")]),
        ("-- TODO sql", [(1, 4, "TODO")]),
        ("todo = 'TODO'", []),
        ("# TODOS are plural", []),
        ("def todo(): pass", []),
    ],
)
def test_scan_text(line: str, expected: list[tuple[int, int, str]]) -> None:
    assert list(scan_text(line)) == expected


def test_check_bad_fixtures() -> None:
    findings = check([FIXTURES / "bad"])
    assert {(f.path.name, f.line) for f in findings} == {
        ("example.py", 2),
        ("example.py", 3),
        ("example.go", 1),
    }
    assert all(f.practice == PRACTICE_ID for f in findings)


def test_check_good_fixtures() -> None:
    assert check([FIXTURES / "good"]) == []


def test_main_exit_codes() -> None:
    assert main([str(FIXTURES / "good"), "--format", "text"]) == 0
    assert main([str(FIXTURES / "bad"), "--format", "text"]) == 1
