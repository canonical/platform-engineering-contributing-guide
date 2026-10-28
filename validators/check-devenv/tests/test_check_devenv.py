from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest

from check_devenv import check as mod
from check_devenv.cli import main

SNAP_LIST = (
    "Name      Version  Rev  Tracking       Publisher  Notes\n"
    "opencode  {}  287  latest/stable  ubuntu**   classic\n"
)
GOOD_CONFIG = {"lsp": True, "model": "github-copilot/claude-sonnet-5.5"}


def fake_runner(version: str | None, config: object = GOOD_CONFIG, raw: str | None = None):
    def run(command: Sequence[str], cwd: Path | None) -> str:
        if command[0] == "snap":
            if version is None:
                raise mod.CommandError("not installed")
            return SNAP_LIST.format(version)
        return raw if raw is not None else json.dumps(config)

    return run


@pytest.fixture(autouse=True)
def tools_on_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod.shutil, "which", lambda name: f"/usr/bin/{name}")


@pytest.mark.parametrize(
    ("text", "expected"),
    [("1.19.4", (1, 19, 4)), ("v2.0", (2, 0)), ("1.19.4-rc1", (1, 19, 4)), ("x", None)],
)
def test_parse_version(text: str, expected: tuple[int, ...] | None) -> None:
    assert mod.parse_version(text) == expected


@pytest.mark.parametrize(
    ("version", "ok"),
    [("1.19.4", True), ("1.19.5", True), ("1.20.0", True), ("2.0.0", True), ("1.19.3", False),
     ("1.9.9", False), ("0.99", False)],
)  # fmt: skip
def test_snap_version(version: str, ok: bool) -> None:
    assert (mod.check_snap(fake_runner(version)) == []) is ok


def test_snap_missing() -> None:
    findings = mod.check_snap(fake_runner(None))
    assert "not installed" in findings[0].message


@pytest.mark.parametrize(
    "model",
    ["github-copilot/claude-sonnet-5.5", "anthropic/claude-sonnet-5-5"],
)
def test_model_accepted(model: str) -> None:
    assert mod.check_config({"lsp": {}, "model": model}) == []


@pytest.mark.parametrize(
    "model",
    [None, "anthropic/claude-sonnet-4-5", "github-copilot/claude-sonnet-5", "claude-sonnet-5.5"],
)
def test_model_rejected(model: str | None) -> None:
    config: dict[str, object] = {"lsp": True}
    if model:
        config["model"] = model
    assert len(mod.check_config(config)) == 1


@pytest.mark.parametrize("lsp", [None, False, "yes"])
def test_lsp_rejected(lsp: object) -> None:
    config = {"model": "github-copilot/claude-sonnet-5.5", "lsp": lsp}
    assert "LSP" in mod.check_config(config)[0].message


def test_environment_ok(tmp_path: Path) -> None:
    assert mod.check_environment(tmp_path, fake_runner("1.19.4")) == []


def test_environment_all_wrong(tmp_path: Path) -> None:
    findings = mod.check_environment(tmp_path, fake_runner("1.0.0", config={}))
    assert len(findings) == 3
    assert all(f.practice == mod.PRACTICE_ID and f.path is None for f in findings)


def test_missing_opencode_skips_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod.shutil, "which", lambda name: None)
    findings = mod.check_environment(tmp_path, fake_runner(None))
    assert len(findings) == 1


def test_invalid_json_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(mod.CommandError):
        mod.check_environment(tmp_path, fake_runner("1.19.4", raw="not json"))


def test_cli_error_exit_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(project: Path) -> list[object]:
        raise mod.CommandError("boom")

    monkeypatch.setattr("check_devenv.check.check_environment", boom)
    assert main([str(tmp_path)]) == 2
