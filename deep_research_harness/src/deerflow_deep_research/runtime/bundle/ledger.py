"""The disposition ledger: an append-only sha256 hash chain over closed entries.

Pure stdlib. `evidence/submissions.jsonl` is the bundle's traceability record: every
entry commits to its predecessor and to the submitted content's hash; reading verifies
the whole chain and fails loudly at the first broken link. Exactly one writer owns
commits, and a commit without an engine-rendered verdict is refused — the hold point
is enforced on the only write path.

@impl RUA-001"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from typing import Any

from ...domain.state_machine import RuleViolation
from ...engine.verdicts import DISPOSITIONS, ValidatorVerdict
from . import atomic
from .bundle_state import BundleHandle, check_lease

GENESIS_PREV_HASH = "0" * 64
LEDGER_RELATIVE = "evidence/submissions.jsonl"

_ENTRY_FIELDS = frozenset(
    {
        "seq",
        "ts",
        "disposition",
        "kind",
        "filename",
        "artifact_path",
        "content_hash",
        "result_code",
        "reasons",
        "replay_of",
        "prev_hash",
        "entry_hash",
    }
)


class LedgerTampered(RuntimeError):
    """The ledger cannot be honestly read — the chain is broken or a field was edited."""


class VerdictlessCommit(RuntimeError):
    """A disposition was committed without an engine-rendered verdict."""


class VerdictContradiction(RuntimeError):
    """The committed record disagrees with the verdict it claims to carry."""


@dataclass(frozen=True)
class LedgerEntry:
    seq: int
    timestamp: str
    disposition: str
    kind: str
    filename: str
    artifact_path: str
    content_hash: str
    result_code: str
    reasons: tuple[str, ...]
    replay_of: int | None
    prev_hash: str
    entry_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "ts": self.timestamp,
            "disposition": self.disposition,
            "kind": self.kind,
            "filename": self.filename,
            "artifact_path": self.artifact_path,
            "content_hash": self.content_hash,
            "result_code": self.result_code,
            "reasons": list(self.reasons),
            "replay_of": self.replay_of,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "LedgerEntry":
        keys = set(raw.keys())
        if keys != _ENTRY_FIELDS:
            unknown = sorted(keys - _ENTRY_FIELDS)
            missing = sorted(_ENTRY_FIELDS - keys)
            raise LedgerTampered(
                f"ledger entry has an unexpected field set (unknown={unknown}, missing={missing}) "
                "— structural tampering"
            )
        reasons = tuple(str(reason) for reason in raw["reasons"])
        replay_of = raw["replay_of"]
        return cls(
            seq=int(raw["seq"]),
            timestamp=str(raw["ts"]),
            disposition=str(raw["disposition"]),
            kind=str(raw["kind"]),
            filename=str(raw["filename"]),
            artifact_path=str(raw["artifact_path"]),
            content_hash=str(raw["content_hash"]),
            result_code=str(raw["result_code"]),
            reasons=reasons,
            replay_of=int(replay_of) if replay_of is not None else None,
            prev_hash=str(raw["prev_hash"]),
            entry_hash=str(raw["entry_hash"]),
        )


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _entry_hash(prev_hash: str, entry_without_hash: dict[str, Any]) -> str:
    return hashlib.sha256((prev_hash + _canonical(entry_without_hash)).encode("utf-8")).hexdigest()


def ledger_path(handle: BundleHandle) -> "Path":
    from pathlib import Path

    return handle.root / Path(LEDGER_RELATIVE)


def read_ledger(handle: BundleHandle) -> tuple[LedgerEntry, ...]:
    path = ledger_path(handle)
    if not path.is_file():
        return ()
    entries: list[LedgerEntry] = []
    expected_prev = GENESIS_PREV_HASH
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerTampered(
                f"ledger corrupted at {path} line {number}: not valid JSON ({exc}) — "
                "repair is manual and visible"
            ) from exc
        entry = LedgerEntry.from_dict(raw)
        if entry.prev_hash != expected_prev:
            raise LedgerTampered(
                f"ledger chain broken at seq {entry.seq}: prev_hash points at "
                f"{entry.prev_hash[:12]}… but the chain expects {expected_prev[:12]}…"
            )
        recomputed = _entry_hash(entry.prev_hash, {k: v for k, v in entry.to_dict().items() if k != "entry_hash"})
        if recomputed != entry.entry_hash:
            raise LedgerTampered(
                f"ledger chain broken at seq {entry.seq}: recorded entry_hash does not "
                "match the recomputed hash — the entry was edited after the fact"
            )
        if entry.seq != number:
            raise LedgerTampered(
                f"ledger sequence broken at line {number}: expected seq {number}, found {entry.seq} "
                "— entries were inserted or removed"
            )
        if entry.disposition not in DISPOSITIONS:
            raise LedgerTampered(
                f"ledger entry seq {entry.seq} carries disposition {entry.disposition!r} "
                f"outside the closed set {DISPOSITIONS}"
            )
        entries.append(entry)
        expected_prev = entry.entry_hash
    return tuple(entries)


def commit_entry(handle: BundleHandle, entry: LedgerEntry, *, verdict: ValidatorVerdict | None) -> LedgerEntry:
    """The single commit path: refuses verdict-less or verdict-contradicting records,
    verifies the existing chain, then appends the next link."""

    if verdict is None:
        raise VerdictlessCommit(
            "refusing to commit a disposition without an engine-rendered verdict — "
            "that would bypass the admission hold point"
        )
    if entry.disposition not in DISPOSITIONS:
        raise RuleViolation(
            f"disposition {entry.disposition!r} is outside the closed set {DISPOSITIONS}"
        )
    if verdict.result_code != entry.result_code:
        raise VerdictContradiction(
            f"record result_code {entry.result_code!r} disagrees with the rendered verdict "
            f"{verdict.result_code!r}"
        )
    if verdict.content_hash != entry.content_hash:
        raise VerdictContradiction(
            "record content_hash disagrees with the rendered verdict — the commitment "
            "must be the hash the validator rendered"
        )
    if entry.disposition in {"admit", "replay"} and verdict.result_code != "ok":
        raise VerdictContradiction(
            f"disposition {entry.disposition!r} requires an ok verdict, got "
            f"{verdict.result_code!r}"
        )

    existing = read_ledger(handle)
    prev_hash = existing[-1].entry_hash if existing else GENESIS_PREV_HASH
    seq = existing[-1].seq + 1 if existing else 1
    without_hash = {
        "seq": seq,
        "ts": entry.timestamp,
        "disposition": entry.disposition,
        "kind": entry.kind,
        "filename": entry.filename,
        "artifact_path": entry.artifact_path,
        "content_hash": entry.content_hash,
        "result_code": entry.result_code,
        "reasons": list(entry.reasons),
        "replay_of": entry.replay_of,
        "prev_hash": prev_hash,
    }
    final = replace(
        entry,
        seq=seq,
        prev_hash=prev_hash,
        entry_hash=_entry_hash(prev_hash, without_hash),
    )
    check_lease(handle)
    atomic.append_line(
        ledger_path(handle), json.dumps(final.to_dict(), ensure_ascii=False) + "\n"
    )
    return final
