"""The run journal: append-only JSONL with bounded honest retention.

Pure stdlib. Retention runs on write (entry-count bound, priority eviction, anchors
never evicted); compaction proactively rewrites at the threshold keeping anchors plus
the recent tail; a corrupted tail fails the read loudly instead of being silently
truncated. The retention/compaction *policy* is domain code — this module only
materializes it.

@impl RUB-001"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ...domain import bundle, journal_policy
from ...domain.journal_policy import JournalEntry, select_compaction_keep, select_retained
from . import atomic
from .bundle_state import BundleHandle, check_lease

# Module-level policy knobs (patch targets for focused negative-control tests).
JOURNAL_BOUND = journal_policy.JOURNAL_BOUND
COMPACTION_THRESHOLD = journal_policy.COMPACTION_THRESHOLD
COMPACTION_TAIL = journal_policy.COMPACTION_TAIL


def now_iso() -> str:
    """The timestamp every journal entry carries (one clock for all writers)."""
    return datetime.now(UTC).isoformat()


def journal_entry(handle: BundleHandle, category: str, event: str, detail: dict) -> None:
    """Append one validated journal entry.

    The vocabulary check lives here on purpose: the pump path already validated,
    the bundle path did not, so the same write had two contracts. One strict
    implementation means an unregistered category fails loudly wherever it is
    written from.
    """
    append_entry(
        handle,
        JournalEntry(timestamp=now_iso(), category=category, event=event, detail=detail).validate(),
    )


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


def tail_journal(journal_path: Path, position: int = 0):
    """Read new journal entries from ``position`` (character offset).

    Returns ``(entries, reached_terminal, new_position)``: ``reached_terminal`` is True
    once a ``terminal`` entry has been rendered — the bounded watch exits there."""

    from ...domain.journal_policy import JournalEntry

    entries: list[JournalEntry] = []
    reached_terminal = False
    if not journal_path.is_file():
        return entries, reached_terminal, position
    text = journal_path.read_text(encoding="utf-8")
    for line in text[position:].splitlines():
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue  # a partially written tail line is re-read on the next poll
        entry = JournalEntry.from_dict(raw)
        entries.append(entry)
        if entry.category == "terminal":
            reached_terminal = True
    return entries, reached_terminal, position + len(text[position:])
