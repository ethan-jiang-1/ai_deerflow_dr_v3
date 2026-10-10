"""Journal policy: the closed category set, bounded retention, and compaction.

Pure stdlib. The journal is append-only JSONL; retention runs on write and never
evicts an `admission` anchor; compaction preserves anchors plus the most recent tail.
The materializing writer lives in runtime/journal.py.

@impl RUB-001"""

from __future__ import annotations

from dataclasses import dataclass

from .state_machine import RuleViolation

JOURNAL_CATEGORIES: tuple[str, ...] = (
    "admission",
    "lifecycle",
    "model_tool",
    "subagent",
    "validation",
    "submit",
    "exhaustion",
    "terminal",
)

# Anchors are the quality-record: once written, retention may never drop them.
ANCHORED_CATEGORIES: frozenset[str] = frozenset({"admission"})

# Entry-count bound; compaction proactively rewrites at the threshold.
JOURNAL_BOUND = 1000
COMPACTION_THRESHOLD = 800
COMPACTION_TAIL = 200


def check_category(category: str) -> str:
    if category not in JOURNAL_CATEGORIES:
        raise RuleViolation(
            f"journal category {category!r} is outside the closed set {JOURNAL_CATEGORIES}"
        )
    return category


@dataclass(frozen=True)
class JournalEntry:
    timestamp: str
    category: str
    event: str
    detail: dict

    def validate(self) -> JournalEntry:
        check_category(self.category)
        if not self.timestamp:
            raise RuleViolation("journal entry requires a timestamp")
        if not self.event:
            raise RuleViolation("journal entry requires an event")
        return self

    def to_dict(self) -> dict:
        return {
            "ts": self.timestamp,
            "category": self.category,
            "event": self.event,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> JournalEntry:
        return cls(
            timestamp=raw.get("ts", ""),
            category=raw.get("category", ""),
            event=raw.get("event", ""),
            detail=raw.get("detail", {}),
        ).validate()


def select_retained(
    entries: tuple[JournalEntry, ...], *, bound: int = JOURNAL_BOUND
) -> tuple[JournalEntry, ...]:
    """Bounded retention with priority eviction: oldest non-anchored entries go
    first; `admission` anchors are never evicted."""

    if len(entries) <= bound:
        return entries
    anchors = tuple(entry for entry in entries if entry.category in ANCHORED_CATEGORIES)
    others = tuple(entry for entry in entries if entry.category not in ANCHORED_CATEGORIES)
    keep_others = max(bound - len(anchors), 0)
    return anchors + others[-keep_others:]


def needs_compaction(entry_count: int, *, threshold: int = COMPACTION_THRESHOLD) -> bool:
    return entry_count >= threshold


def select_compaction_keep(
    entries: tuple[JournalEntry, ...],
    *,
    tail: int = COMPACTION_TAIL,
) -> tuple[JournalEntry, ...]:
    """Compaction keeps every anchor plus the most recent non-anchored tail."""

    anchors = tuple(entry for entry in entries if entry.category in ANCHORED_CATEGORIES)
    others = tuple(entry for entry in entries if entry.category not in ANCHORED_CATEGORIES)
    return anchors + others[-tail:]
