"""state.json single-authority store: read/validate, revision CAS, lease re-check.

Pure stdlib. `state.json` is the only run-state authority; every write carries the
writer's observed revision (CAS) and revalidates the directory lease first. A loser
fails loudly naming the revisions and re-reads — nothing is silently merged.

@impl RUB-001"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from ..domain import bundle
from ..domain.state_machine import BundleState
from . import atomic


class BundleUnavailable(RuntimeError):
    """The bundle directory no longer exists — deletion is permanent."""


class LeaseViolation(RuntimeError):
    """The bundle directory's identity changed under a held handle."""


class StateRevisionConflict(RuntimeError):
    """Another writer moved the revision between this writer's read and write."""


class StateCorruption(RuntimeError):
    """state.json exists but cannot be honestly read."""


@dataclass
class BundleHandle:
    root: Path
    identity: tuple[int, int]

    @classmethod
    def open(cls, root: Path) -> "BundleHandle":
        if not root.is_dir():
            raise BundleUnavailable(
                f"bundle {root} is permanently unavailable: the directory does not exist "
                "(deletion is permanent; there is no recovery path)"
            )
        stat = os.stat(root)
        return cls(root=root, identity=(stat.st_dev, stat.st_ino))


def check_lease(handle: BundleHandle) -> None:
    live = os.stat(handle.root)
    live_identity = (live.st_dev, live.st_ino)
    if live_identity != handle.identity:
        raise LeaseViolation(
            f"bundle directory lease mismatch for {handle.root}: captured "
            f"{handle.identity}, live {live_identity} — the directory was replaced or "
            "moved under this writer; refusing to write"
        )


def read_state(handle: BundleHandle) -> BundleState:
    path = handle.root / bundle.state_relative()
    if not path.is_file():
        raise StateCorruption(f"state.json is missing at {path}: the bundle record is incomplete")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise StateCorruption(f"state.json at {path} cannot be parsed: {exc}") from exc
    return BundleState.from_dict(raw)


def write_state(handle: BundleHandle, current: BundleState, next_state: BundleState) -> BundleState:
    check_lease(handle)
    stored = read_state(handle)
    if stored.revision != current.revision:
        raise StateRevisionConflict(
            f"state revision conflict: expected {current.revision}, actual {stored.revision} "
            f"({handle.root}) — re-read the state and retry"
        )
    written = next_state.validate()
    from dataclasses import replace

    written = replace(written, revision=current.revision + 1)
    atomic.atomic_write_text(
        handle.root / bundle.state_relative(),
        json.dumps(written.to_dict(), ensure_ascii=False, indent=2) + "\n",
    )
    return written
