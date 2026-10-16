"""The control registry and the runners that judge it."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from pathlib import Path
import tempfile

from doc_hygiene_check import (
    RULES,
    Scope,
    violations,
)
from .fixtures import _adr_index_orphan, _allowlist_unjustified, _archive_only_next_id, _broken_asset_doc_link, _broken_docs_layer_link, _broken_entry_chain_link, _consistent_single_decl, _contiguous_table, _dangling_trigger_index_home, _disagreeing_next_id_decl, _docs_layer_missing_newline, _docs_layer_non_utf8, _duplicate_next_id_decl, _fence_indented_opener_keeps_checking, _fenced_example_id_does_not_allocate, _fenced_marker_quote_is_not_stale, _hukou_bad_word, _hukou_closable, _hukou_graduated, _hukou_miskill_awaiting, _hukou_missing_field, _is_clean_fixture, _ledger_repo, _ledger_row_placement, _missing_managed_budget_path, _missing_newline_entry_chain, _over_budget_resident_doc, _resolvable_asset_doc_link, _root_count_drift, _root_count_matching, _root_count_unpinned, _stale_marker_clean, _stale_marker_detected, _tilde_fenced_row_is_not_a_ledger_row, _undeclared_backlog_dir, _undocumented_backlog_dir, _union_consistent_next_id, _unregistered_docs_markdown, _vocab_bad_word, _vocab_fix_ready_miskill, _vocab_old_active


CLEAN_FIXTURE = "clean fixture must have zero violations"


ADR_INDEX_ORPHAN = "ADR index orphan not detected"


BROKEN_LINK = "broken link not detected"


DANGLING_TRIGGER_INDEX_HOME = "dangling trigger-index home link not detected"


MISSING_TRAILING_NEWLINE = "missing trailing newline not detected"


DOCS_LAYER_BROKEN_LINK = "docs-layer broken link not detected"


ASSET_DOC_BROKEN_LINK = "asset-doc broken link not detected"


ASSET_DOC_RESOLVABLE_LINK = "asset-doc resolvable link flagged"


DOCS_LAYER_MISSING_NEWLINE = "docs-layer missing trailing newline not detected"


DOCS_LAYER_NON_UTF8 = "docs-layer non-UTF-8 not detected"


UNREGISTERED_DOCS_MARKDOWN = "unregistered docs-layer markdown not detected"


UNDECLARED_BACKLOG_DIR = "undeclared backlog directory not detected"


UNDOCUMENTED_BACKLOG_DIR = "undocumented backlog directory not detected"


OVER_BUDGET_RESIDENT_DOC = "over-budget resident document not detected"


MISSING_MANAGED_BUDGET_PATH = "missing managed budget path not detected"


LEDGER_UNINDEXED_WORK_ITEM = "ledger rule did not detect: active ledger surface"


LEDGER_DANGLING_INDEX_ROW = "ledger rule did not detect: dangling index row"


LEDGER_COUNTER_MISMATCH = "ledger rule did not detect: counter mismatch"


ARCHIVE_ONLY_NEXT_ID = "archive-only Next-ID allocation not detected"


UNION_CONSISTENT_NEXT_ID = "union-consistent Next-ID declaration flagged"


DUPLICATE_NEXT_ID_DECL = "duplicate next-ID declaration not detected"


DISAGREEING_NEXT_ID_DECL = "disagreeing next-ID declaration not detected"


CONSISTENT_SINGLE_DECL = "consistent single declaration flagged as duplicate"


LEDGER_ROW_PLACEMENT = "ledger row placement defect not detected"


CONTIGUOUS_TABLE = "contiguous table flagged as misplaced"


HUKOU_MISSING_FIELD = "card hukou rule did not detect: missing 状态 hukou"


HUKOU_BAD_WORD = "card hukou rule did not detect: outside declared vocabulary"


HUKOU_GRADUATED = "card hukou rule did not detect: 毕业门：已过"


HUKOU_CLOSABLE = "card hukou rule did not detect: 可关闭：是"


HUKOU_MISKILL_AWAITING = "hukou rule mis-killed awaiting card"


VOCAB_OLD_ACTIVE = "post-rename 活跃 bug card not detected as out-of-vocabulary"


VOCAB_BAD_WORD = "out-of-vocabulary bug word not detected"


VOCAB_FIX_READY_MISKILL = "修就绪 bug card mis-killed by vocabulary rule"


ROOT_COUNT_DRIFT = "drifted root-README count not detected"


ROOT_COUNT_MATCHING = "matching counts flagged as drifted"


ROOT_COUNT_UNPINNED = "missing count declaration not detected"


STALE_MARKER_DETECTED = "stale marker not detected with file:line"


STALE_MARKER_CLEAN = "clean file flagged by marker rule"


FENCE_INDENTED_OPENER_KEEPS_CHECKING = "an indented fence opener hid a real ledger defect"


TILDE_FENCED_ROW_NOT_A_LEDGER_ROW = "a tilde-fenced example read as a ledger row"


FENCED_EXAMPLE_ID_NOT_ALLOCATED = "a fenced example allocated a ledger ID"


FENCED_MARKER_QUOTE_NOT_STALE = "a fenced marker quote reported as stale"


ALLOWLIST_UNJUSTIFIED = "unjustified allowlist entry not detected"


@dataclass(frozen=True)
class NegativeCase:
    """One battery case: an owning rule, a tree, an identity, and its polarity.

    ``must_fire`` is the polarity of the control. A **negative control** proves the
    rule can fail and must return at least one violation. An **over-fire control**
    proves a legitimate shape is not mis-reported and must return none. Both are
    controls the guard cannot lose, and both are individually identified here so a
    regression names the behaviour it broke.
    """

    case_id: str
    rule: str
    build: Callable[[Path], None]
    note: str
    # ``present``: violation substrings that must appear (the negative control).
    # ``absent``: violation substrings that must NOT appear (the over-fire / mis-kill
    # control). ``zero_violations`` demands an entirely clean run — the clean fixture.
    # A green control carries no ``present``, because the tree may legitimately hold
    # unrelated violations; what the control protects is the absence of one class.
    present: tuple[str, ...] = ()
    absent: tuple[str, ...] = ()
    zero_violations: bool = False
    # Scope field overrides for cases that must vary a declaration table itself
    # (the unjustified-allowlist control is the only one today). Everything else
    # runs against the shipped declarations.
    scope_overrides: Mapping[str, object] = field(default_factory=dict)


def _c(
    case_id: str,
    rule: str,
    build: Callable[[Path], None],
    note: str,
    *,
    present: tuple[str, ...] = (),
    absent: tuple[str, ...] = (),
    zero_violations: bool = False,
    scope_overrides: Mapping[str, object] | None = None,
) -> NegativeCase:
    return NegativeCase(
        case_id=case_id,
        rule=rule,
        build=build,
        note=note,
        present=present,
        absent=absent,
        zero_violations=zero_violations,
        scope_overrides=dict(scope_overrides or {}),
    )


NEGATIVE_CASES: tuple[NegativeCase, ...] = (
    _c(CLEAN_FIXTURE, "violations", _is_clean_fixture,
       "the clean fixture itself: every registered document present and valid",
       zero_violations=True),
    _c(ADR_INDEX_ORPHAN, "adr_index", _adr_index_orphan,
       "index lists an ADR id that no file backs", present=("9999",)),
    _c(BROKEN_LINK, "links", _broken_entry_chain_link,
       "entry-chain relative link points nowhere", present=("gone.md",)),
    _c(DANGLING_TRIGGER_INDEX_HOME, "links", _dangling_trigger_index_home,
       "trigger index row whose owner record does not exist",
       present=("_backlog/triggers.md", "no-such-owner.md")),
    _c(MISSING_TRAILING_NEWLINE, "encoding_newline", _missing_newline_entry_chain,
       "entry-chain document without a trailing newline", present=("trailing newline",)),
    _c(DOCS_LAYER_BROKEN_LINK, "links", _broken_docs_layer_link,
       "docs-layer relative link points nowhere", present=("gone.md",)),
    _c(ASSET_DOC_BROKEN_LINK, "links", _broken_asset_doc_link,
       "asset-document link points nowhere (the 2026-10-10 audit class)",
       present=("tests/README.md", "gone.md")),
    _c(ASSET_DOC_RESOLVABLE_LINK, "links", _resolvable_asset_doc_link,
       "a resolvable asset-document link must not be flagged (over-fire control)",
       absent=("tests/README.md",)),
    _c(DOCS_LAYER_MISSING_NEWLINE, "encoding_newline", _docs_layer_missing_newline,
       "docs-layer document without a trailing newline",
       present=("docs-layer document missing trailing newline",)),
    _c(DOCS_LAYER_NON_UTF8, "encoding_newline", _docs_layer_non_utf8,
       "docs-layer document that is not UTF-8 decodable",
       present=("non-UTF-8 docs-layer document",)),
    _c(UNREGISTERED_DOCS_MARKDOWN, "docs_scope", _unregistered_docs_markdown,
       "present docs markdown missing from the registered scope",
       present=("zz-unregistered.md",)),
    _c(UNDECLARED_BACKLOG_DIR, "backlog_underscore", _undeclared_backlog_dir,
       "`_`-prefixed backlog directory outside the declaration",
       present=("_zz-undeclared",)),
    _c(UNDOCUMENTED_BACKLOG_DIR, "backlog_underscore", _undocumented_backlog_dir,
       "declared `_` directory absent from the backlog README",
       present=("does not document retained directory",)),
    _c(OVER_BUDGET_RESIDENT_DOC, "doc_budgets", _over_budget_resident_doc,
       "managed resident document above its character ceiling",
       present=("over character budget",)),
    _c(MISSING_MANAGED_BUDGET_PATH, "doc_budgets", _missing_managed_budget_path,
       "managed budget path deleted must fail loudly, not pass silently",
       present=("missing managed budget path",)),
    _c(LEDGER_UNINDEXED_WORK_ITEM, "ledger_consistency", _ledger_repo,
       "active work item that its surface README does not index",
       present=("active ledger surface",)),
    _c(LEDGER_DANGLING_INDEX_ROW, "ledger_consistency", _ledger_repo,
       "index row whose linked file does not exist", present=("dangling index row",)),
    _c(LEDGER_COUNTER_MISMATCH, "ledger_consistency", _ledger_repo,
       "archive counters disagreeing with the disk roster", present=("counter mismatch",)),
    _c(ARCHIVE_ONLY_NEXT_ID, "ledger_consistency", _archive_only_next_id,
       "next-ID derived from the archive zone only, ignoring a filed active card (BUG-002)",
       present=("next-ID mismatch", "_fixed_bugs")),
    _c(UNION_CONSISTENT_NEXT_ID, "ledger_consistency", _union_consistent_next_id,
       "the union-consistent next ID must stay green (over-fire control)",
       absent=("next-ID mismatch",)),
    _c(DUPLICATE_NEXT_ID_DECL, "ledger_consistency", _duplicate_next_id_decl,
       "two next-ID declarations for one prefix in one README (BUG-002)",
       present=("duplicate next-ID declaration in _fixed_bugs/README.md",)),
    _c(DISAGREEING_NEXT_ID_DECL, "ledger_consistency", _disagreeing_next_id_decl,
       "single declaration disagreeing with the union-derived next ID",
       present=("next-ID declaration disagrees in _fixed_bugs/README.md",)),
    _c(CONSISTENT_SINGLE_DECL, "ledger_consistency", _consistent_single_decl,
       "a consistent single declaration must not be called a duplicate (over-fire control)",
       absent=("duplicate next-ID declaration in bugs/README.md",)),
    _c(LEDGER_ROW_PLACEMENT, "ledger_consistency", _ledger_row_placement,
       "work-item row separated from its table header block", present=("placement",)),
    _c(CONTIGUOUS_TABLE, "ledger_consistency", _contiguous_table,
       "a contiguous table must not be flagged as misplaced (over-fire control)",
       absent=("placement",)),
    _c(HUKOU_MISSING_FIELD, "ledger_consistency", _hukou_missing_field,
       "active card without a 状态 field in its first 12 lines",
       present=("missing 状态 hukou",)),
    _c(HUKOU_BAD_WORD, "ledger_consistency", _hukou_bad_word,
       "active card status word outside the declared vocabulary",
       present=("outside declared vocabulary",)),
    _c(HUKOU_GRADUATED, "ledger_consistency", _hukou_graduated,
       "graduated card still sitting in the active zone", present=("毕业门：已过",)),
    _c(HUKOU_CLOSABLE, "ledger_consistency", _hukou_closable,
       "card declaring itself closable while still in the active zone",
       present=("可关闭：是",)),
    _c(HUKOU_MISKILL_AWAITING, "ledger_consistency", _hukou_miskill_awaiting,
       "an awaiting-human card with delivery prose must stay green (mis-kill control)",
       absent=("2026-10-05-awaiting-human.md",)),
    _c(VOCAB_OLD_ACTIVE, "ledger_consistency", _vocab_old_active,
       "post-rename `活跃` bug card is out of vocabulary",
       present=("outside declared vocabulary", "BUG-009-old-active.md")),
    _c(VOCAB_BAD_WORD, "ledger_consistency", _vocab_bad_word,
       "arbitrary out-of-vocabulary bug status word",
       present=("outside declared vocabulary", "BUG-011-bad-word.md")),
    _c(VOCAB_FIX_READY_MISKILL, "ledger_consistency", _vocab_fix_ready_miskill,
       "`修就绪` is legal and must not be mis-killed (mis-kill control)",
       absent=("BUG-010-fix-ready.md",)),
    _c(ROOT_COUNT_DRIFT, "root_counts", _root_count_drift,
       "root README declaring counts the inventory contradicts",
       present=("5", "7")),
    _c(ROOT_COUNT_MATCHING, "root_counts", _root_count_matching,
       "matching counts must not be flagged as drifted (over-fire control)",
       zero_violations=True),
    _c(ROOT_COUNT_UNPINNED, "root_counts", _root_count_unpinned,
       "status line declaring no counts at all", present=("unpinned",)),
    _c(STALE_MARKER_DETECTED, "stale_markers", _stale_marker_detected,
       "re-introduced skeleton marker reported with file:line",
       present=("骨架占位", "AGENTS.md:3")),
    _c(STALE_MARKER_CLEAN, "stale_markers", _stale_marker_clean,
       "clean managed file must not be flagged (over-fire control)",
       zero_violations=True),
    _c(ALLOWLIST_UNJUSTIFIED, "stale_markers", _allowlist_unjustified,
       "allowlist entry carrying no justification",
       present=("allowlist entry without justification",),
       scope_overrides={
           "marker_allowlist": {("AGENTS.md", "骨架占位"): "   "},
       }),
    _c(FENCE_INDENTED_OPENER_KEEPS_CHECKING, "ledger_consistency",
       _fence_indented_opener_keeps_checking,
       "a four-space-indented fence opener must not silence the rest of the file",
       present=("ledger row placement defect",)),
    _c(TILDE_FENCED_ROW_NOT_A_LEDGER_ROW, "ledger_consistency",
       _tilde_fenced_row_is_not_a_ledger_row,
       "a tilde-fenced example is not a ledger row",
       absent=("ledger row placement defect",)),
    _c(FENCED_EXAMPLE_ID_NOT_ALLOCATED, "ledger_consistency",
       _fenced_example_id_does_not_allocate,
       "an ID inside a fenced example allocates nothing",
       absent=("allocation implies",)),
    _c(FENCED_MARKER_QUOTE_NOT_STALE, "stale_markers", _fenced_marker_quote_is_not_stale,
       "quoting a forbidden marker inside a fence is documentation, not a stale marker",
       absent=("stale narrative marker",)),
)


def run_rule(rule: str, root: Path, overrides: Mapping[str, object] | None = None) -> list[str]:
    """Run one rule against one tree, with optional declaration-table overrides."""
    from check_doc_hygiene import RULES, violations

    if rule == "violations":
        return violations(root)
    scope = Scope.from_defaults(root)
    if overrides:
        scope = replace(scope, **overrides)
    for name, check in RULES:
        if name == rule:
            return check(scope)
    raise KeyError(f"unknown doc-hygiene rule in the battery: {rule!r}")


def run_case(case: NegativeCase) -> list[str]:
    """Build the case's own temporary tree and return its rule's violations."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        case.build(root)
        return run_rule(case.rule, root, case.scope_overrides)


def case_holds(case: NegativeCase, problems: list[str]) -> bool:
    """Whether one case's control holds for one rule run.

    A negative control holds when every ``present`` substring appears; an over-fire
    or mis-kill control holds when no ``absent`` substring appears; the clean
    fixture holds when the run is entirely clean. A case with none of the three
    declared holds vacuously, which the battery test rejects.
    """
    if case.zero_violations:
        return not problems
    if case.present:
        return all(any(needle in v for v in problems) for needle in case.present)
    if case.absent:
        # Mirrors the original battery's ``hukou_only`` filter: an empty fixture
        # roster legitimately produces "unindexed work item" noise, and a mis-kill
        # control protects against hukou/rule-specific reports, not that noise.
        specific = [v for v in problems if "unindexed" not in v]
        return not any(needle in v for v in specific for needle in case.absent)
    return False


def failing_controls() -> list[str]:
    """Run every case and return the identities whose control does not hold."""
    return [c.case_id for c in NEGATIVE_CASES if not case_holds(c, run_case(c))]
