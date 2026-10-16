#!/usr/bin/env python3
"""Validate the Change Guidance charter and policy routing without external packages.


@impl CHA-001"""

from __future__ import annotations

import sys
from pathlib import Path

# Self-sufficient import of the implementation package: this entry point runs
# from the governance directory, from CI, and from a copied temporary repository
# (the governance fixtures copy it by path together with change_guidance_kernel).
_GOVERNANCE_DIR = str(Path(__file__).resolve().parent)
if _GOVERNANCE_DIR not in sys.path:
    sys.path.insert(0, _GOVERNANCE_DIR)

import change_guidance_check as _impl  # noqa: E402

main = _impl.main


def __getattr__(name: str):
    """Delegate every other attribute to the implementation package.

    Tests address this module by name (``ContractViolation``,
    ``_validate_change_tasks``). Delegating the whole surface keeps that
    reachability intact without this file re-listing names that would drift from
    the package.
    """
    return getattr(_impl, name)


if __name__ == "__main__":
    raise SystemExit(main())
