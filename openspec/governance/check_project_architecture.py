#!/usr/bin/env python3
"""Validate the permanent project-structure registry without external packages.


@impl PRS-001"""

from __future__ import annotations

import sys
from pathlib import Path

# Self-sufficient import of the implementation package: this entry point runs
# from the governance directory, from CI, and from a copied temporary repository
# (the governance fixtures copy it by path). Putting this file's own directory
# first makes a copied entry point resolve its own sibling package instead of
# reaching back into the original checkout.
_GOVERNANCE_DIR = str(Path(__file__).resolve().parent)
if _GOVERNANCE_DIR not in sys.path:
    sys.path.insert(0, _GOVERNANCE_DIR)

import project_architecture_check as _impl  # noqa: E402

main = _impl.main


def __getattr__(name: str):
    """Delegate every other attribute to the implementation package.

    Tests and fixtures reach into this module by name (``load_manifest``,
    ``ContractViolation``, and rule predicates such as
    ``_validate_required_paths``). Delegating the whole surface keeps that
    reachability intact without this file re-listing names that would then drift
    from the package.
    """
    return getattr(_impl, name)


if __name__ == "__main__":
    raise SystemExit(main())
