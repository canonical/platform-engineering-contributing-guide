"""Output formatters for findings."""

from __future__ import annotations

import json
from collections.abc import Sequence

from pfe_validators_common.findings import Finding

FORMATS = ("text", "github", "json")


def _escape_property(value: str) -> str:
    return (
        value.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


def _escape_data(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _text(finding: Finding) -> str:
    location = str(finding.path) if finding.path is not None else "<environment>"
    if finding.line is not None:
        location += f":{finding.line}"
        if finding.column is not None:
            location += f":{finding.column}"
    return f"{location}: {finding.severity.value}: [{finding.practice}] {finding.message}"


def _github(finding: Finding) -> str:
    props = []
    if finding.path is not None:
        props.append(f"file={_escape_property(str(finding.path))}")
    if finding.line is not None:
        props.append(f"line={finding.line}")
    if finding.column is not None:
        props.append(f"col={finding.column}")
    props.append(f"title={_escape_property(finding.practice)}")
    return f"::{finding.severity.value} {','.join(props)}::{_escape_data(finding.message)}"


def render(findings: Sequence[Finding], fmt: str) -> str:
    """Render findings in the requested format (``text``, ``github`` or ``json``)."""
    if fmt == "json":
        return json.dumps([f.to_dict() for f in findings], indent=2)
    if fmt == "github":
        return "\n".join(_github(f) for f in findings)
    if fmt == "text":
        return "\n".join(_text(f) for f in findings)
    raise ValueError(f"unknown format {fmt!r}, expected one of {FORMATS}")
