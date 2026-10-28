"""Result model shared by all validators."""

from __future__ import annotations

import enum
from dataclasses import asdict, dataclass
from pathlib import Path


class Severity(str, enum.Enum):
    """Severity of a finding, aligned with GitHub workflow command levels."""

    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"


@dataclass(frozen=True)
class Finding:
    """A single compliance violation.

    Attributes:
        practice: Practice ID from catalog.yaml (e.g. ``PFE-IMPL-004``).
        path: File the finding relates to.
        message: Human readable explanation.
        line: 1-based line number, if applicable.
        column: 1-based column number, if applicable.
        severity: Severity of the finding.
    """

    practice: str
    path: Path
    message: str
    line: int | None = None
    column: int | None = None
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""
        data = asdict(self)
        data["path"] = str(self.path)
        data["severity"] = self.severity.value
        return data
