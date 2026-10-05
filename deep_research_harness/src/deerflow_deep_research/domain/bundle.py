"""Run-bundle directory contract: the single source of bundle path constants.

Pure stdlib. Every bundle path a harness module needs resolves from here; no second
path declaration may exist (project-structure discipline).

@impl RUB-001"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

# The declared subtree set (v2's synthesis/ and review/ are deliberately absent:
# the research cognition engine is DeerFlow's, and its products route to final/,
# evidence/, diagnostics/).
BUNDLE_SUBTREES: tuple[str, ...] = ("request", "work", "evidence", "final", "diagnostics")

STATE_FILENAME = "state.json"
CHECKPOINT_FILENAME = "checkpoint.sqlite"
JOURNAL_RELATIVE = PurePosixPath("diagnostics/journal.jsonl")
UNANSWERED_QUESTIONS_RELATIVE = PurePosixPath("diagnostics/unanswered-clarifications.json")
REQUEST_PROBLEM_FILENAME = "problem.txt"
RUNS_ROOT_NAME = "runs"

_STAGING_PREFIX = ".staging-"

# v3 bucket = creation-date grouping (d_YYYYMMDD); the v2 hash bucket answered a
# multi-user containment question v3 does not have. Re-pin via an owning change if
# multi-operator semantics arrive.
_BUCKET_RE = re.compile(r"^d_[0-9]{8}$")
_BUNDLE_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)

# Explicit composition recorded at start; anything else is rejected at the boundary.
COMPOSITIONS: tuple[str, ...] = ("fixture", "mixed", "all_real")


def is_valid_bucket(name: str) -> bool:
    return bool(_BUCKET_RE.fullmatch(name))


def is_valid_bundle_id(name: str) -> bool:
    return bool(_BUNDLE_ID_RE.fullmatch(name))


def bucket_for_date(year: int, month: int, day: int) -> str:
    return f"d_{year:04d}{month:02d}{day:02d}"


def bundle_dir(runs_root: str, bucket: str, bundle_id: str) -> PurePosixPath:
    if not is_valid_bucket(bucket):
        raise ValueError(f"invalid run bucket {bucket!r}: expected d_YYYYMMDD")
    if not is_valid_bundle_id(bundle_id):
        raise ValueError(f"invalid bundle id {bundle_id!r}: expected UUID4")
    return PurePosixPath(runs_root) / bucket / bundle_id


def subtree_dirs() -> tuple[PurePosixPath, ...]:
    return tuple(PurePosixPath(name) for name in BUNDLE_SUBTREES)


def state_relative() -> PurePosixPath:
    return PurePosixPath(STATE_FILENAME)


def checkpoint_relative() -> PurePosixPath:
    return PurePosixPath(CHECKPOINT_FILENAME)


def journal_relative() -> PurePosixPath:
    return JOURNAL_RELATIVE


def request_problem_relative() -> PurePosixPath:
    return PurePosixPath("request") / REQUEST_PROBLEM_FILENAME


def refine_request_relative(generation: int) -> PurePosixPath:
    return PurePosixPath("request") / f"refine-{generation}.txt"


def generation_context_relative(generation: int) -> PurePosixPath:
    return PurePosixPath("request") / f"generation-{generation}-context.md"


def staging_name(bundle_id: str) -> str:
    return f"{_STAGING_PREFIX}{bundle_id}"
