"""Command line entry point."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from pfe_validators_common import run_cli
from validator_template.check import check


def main(argv: Sequence[str] | None = None) -> int:
    """Run the validator."""
    return run_cli("validator-template", "One-line description (PFE-XXX-NNN).", check, argv)


if __name__ == "__main__":
    sys.exit(main())
