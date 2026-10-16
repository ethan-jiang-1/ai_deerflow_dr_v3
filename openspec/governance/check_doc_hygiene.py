"""Doc-layer hygiene: the guard's command line and its public surface.

The implementation lives in `doc_hygiene_check/`; this file keeps the name the CI
workflow, the pre-commit hook and the path registry call it by, and re-exports the
whole surface so existing importers (`import check_doc_hygiene`) keep working.

@impl DEW-001"""

from __future__ import annotations

import sys

import doc_hygiene_check as _implementation
from doc_hygiene_check import *  # noqa: F403 — the surface below is declared explicitly

__all__ = [
    "ADR_DIR",
    "DOCS_TREE",
    "ADR_INDEX",
    "BACKLOG_ROOT",
    "BACKLOG_UNDERSCORE_DIRS",
    "ENTRY_DOCS",
    "DOC_BUDGETS",
    "DOC_LAYER_DOCS",
    "LINKED_ASSET_DOCS",
    "ADR_FILE_RE",
    "INDEX_ROW_RE",
    "MARKDOWN_LINK_RE",
    "BACKLOG_ACTIVE_SURFACES",
    "BACKLOG_ARCHIVE_SURFACES",
    "BACKLOG_COUNTERS_FILE",
    "BACKLOG_NEXT_ID_RE",
    "BACKLOG_ARCHIVE_TO_ACTIVE",
    "BACKLOG_NUMBERED_SURFACES",
    "BACKLOG_NUMBERED_PREFIXES",
    "BACKLOG_NEXT_ID_DECL_RE",
    "BACKLOG_CARD_HUKOU_LINE_LIMIT",
    "BACKLOG_STATUS_FIELD_RE",
    "BACKLOG_STATUS_VOCABULARY",
    "BACKLOG_GRADUATION_PASSED_RE",
    "BACKLOG_CLOSABLE_RE",
    "STALE_MARKERS",
    "STALE_MARKER_FILES",
    "MARKER_ALLOWLIST",
    "SCOPE_PATHS",
    "SCOPE_LIMITS",
    "SCOPE_REGEXES",
    "SCOPE_SURFACES",
    "_COUNT_SPECS_RE",
    "_COUNT_ARCHIVE_RE",
    "Scope",
    "_adr_ids",
    "_indexed_ids",
    "_read_utf8",
    "_card_hukou_problems",
    "_ledger_surface_dir",
    "_ledger_work_files",
    "_allocated_numbers",
    "_ledger_roster_problems",
    "_ledger_counter_problems",
    "_ledger_placement_problems",
    "_rule_adr_index",
    "_rule_links",
    "_rule_encoding_newline",
    "_rule_docs_scope",
    "_rule_backlog_underscore",
    "_rule_doc_budgets",
    "_rule_ledger_consistency",
    "_rule_root_counts",
    "_rule_stale_markers",
    "RULES",
    "violations",
    "_self_test",
    "main",
]


def __getattr__(name: str):
    """Forward anything this facade did not list, so a missed name is not an ImportError."""
    try:
        return getattr(_implementation, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None


if __name__ == "__main__":
    sys.exit(main())
