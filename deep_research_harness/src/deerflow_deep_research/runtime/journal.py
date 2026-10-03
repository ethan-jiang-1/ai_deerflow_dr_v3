"""The run journal: append-only JSONL with bounded honest retention.

Pure stdlib. Retention runs on write (entry-count bound, priority eviction, anchors
never evicted); compaction proactively rewrites at the threshold keeping anchors plus
the recent tail; a corrupted tail fails the read loudly instead of being silently
truncated. The retention/compaction *policy* is domain code — this module only
materializes it.

@impl RUB-001"""

from __future__ import annotations

import json
from pathlib import Path

from ..domain import bundle, journal_policy
from ..domain.journal_policy import JournalEntry, select_compaction_keep, select_retained
from . import atomic
from .bundle_state import BundleHandle, check_lease

# Module-level policy knobs (patch targets for focused negative-control tests).
JOURNAL_BOUND = journal_policy.JOURNAL_BOUND
COMPACTION_THRESHOLD = journal_policy.COMPACTION_THRESHOLD
COMPACTION_TAIL = journal_policy.COMPACTION_TAIL


class JournalCorruption(RuntimeError):
    """The journal cannot be honestly read — never silently truncated."""


def journal_path(handle: BundleHandle) -> Path:
    return handle.root / bundle.journal_relative()


def append_entry(handle: BundleHandle, entry: JournalEntry) -> None:
    entry.validate()
    check_lease(handle)
    atomic.append_line(
        journal_path(handle), json.dumps(entry.to_dict(), ensure_ascii=False) + "\n"
    )
    entries = read_entries(handle)
    if len(entries) >= COMPACTION_THRESHOLD:
        _rewrite(handle, select_compaction_keep(entries, tail=COMPACTION_TAIL))
    elif len(entries) > JOURNAL_BOUND:
        _rewrite(handle, select_retained(entries, bound=JOURNAL_BOUND))


def read_entries(handle: BundleHandle) -> tuple[JournalEntry, ...]:
    path = journal_path(handle)
    if not path.is_file():
        return ()
    entries: list[JournalEntry] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise JournalCorruption(
                f"journal tail corrupted at {path} line {number}: not valid JSON ({exc}) — "
                "repair is manual and visible; refusing to truncate silently"
            ) from exc
        entries.append(JournalEntry.from_dict(raw))
    return tuple(entries)


def _rewrite(handle: BundleHandle, kept: tuple[JournalEntry, ...]) -> None:
    payload = "".join(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n" for entry in kept)
    atomic.atomic_write_text(journal_path(handle), payload)
