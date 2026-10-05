#!/usr/bin/env python3
"""Stable source-checkout launcher for the six-verb CLI.

Interaction is in runtime/interaction; foreground assembly is in runtime/entry.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from deerflow_deep_research.runtime.interaction.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
