"""Command line entry point."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from check_devenv.check import check
from pfe_validators_common import run_cli


def main(argv: Sequence[str] | None = None) -> int:
    """Run the check-devenv validator."""
    return run_cli(
        "check-devenv",
        "Check the opencode development environment: snap version, LSP and default "
        "model (PFE-DEV-001). The optional path is the project directory whose opencode "
        "config is taken into account.",
        check,
        argv,
    )


if __name__ == "__main__":
    sys.exit(main())
