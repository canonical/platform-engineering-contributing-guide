"""Command line entry point."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from check_todos.check import check
from pfe_validators_common import run_cli


def main(argv: Sequence[str] | None = None) -> int:
    """Run the check-todos validator."""
    return run_cli(
        "check-todos",
        "Report TODO/FIXME comments left in source code (PFE-IMPL-004).",
        check,
        argv,
    )


if __name__ == "__main__":
    sys.exit(main())
