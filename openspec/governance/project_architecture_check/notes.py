"""Placeholder module: keeps the registered-path inventory observable.

The package's modules are all imported by ``facade``/``__init__``, so removing any
of them fails at import time before the inventory check can name the missing path.
This module is registered and deliberately not imported, so the checker's
required-path rule stays exercisable by removing it.
"""

from __future__ import annotations

__all__: list[str] = []
