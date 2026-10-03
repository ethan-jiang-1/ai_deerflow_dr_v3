"""Contract mirror package: typed declarations of the borrowed DeerFlow surfaces.

Shape only, never implementation. See client_surface.py for the consumed surface.

@impl DEW-001"""

from . import client_surface

__all__ = ["client_surface"]
