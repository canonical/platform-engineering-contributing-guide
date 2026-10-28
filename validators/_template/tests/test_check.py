from __future__ import annotations

from pathlib import Path

from validator_template.check import check


def test_check(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n")
    (tmp_path / "ko.py").write_text("forbidden = 1\n")
    assert [f.path.name for f in check([tmp_path])] == ["ko.py"]
