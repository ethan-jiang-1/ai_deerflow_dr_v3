"""The frozen Scope value object the rules are run against."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import BACKLOG_ARCHIVE_TO_ACTIVE, BACKLOG_NUMBERED_PREFIXES, BACKLOG_STATUS_VOCABULARY, BACKLOG_UNDERSCORE_DIRS, DOC_BUDGETS, DOC_LAYER_DOCS, ENTRY_DOCS, LINKED_ASSET_DOCS, MARKER_ALLOWLIST, SCOPE_LIMITS, SCOPE_PATHS, SCOPE_REGEXES, SCOPE_SURFACES, STALE_MARKERS, STALE_MARKER_FILES


@dataclass(frozen=True)
class Scope:
    """Frozen input surface for the doc-hygiene rules.

    The declarations (managed document lists, budgets, ledger vocabularies,
    marker tables) stay module constants and remain the human-facing declaring
    tables; ``from_defaults`` is the single place that binds them to one run.
    Nothing downstream reads those constants directly, so a test can build a
    scope with different declarations without touching module state.
    """

    root: Path
    entry_docs: tuple[str, ...]
    doc_layer_docs: tuple[str, ...]
    linked_asset_docs: tuple[str, ...]
    doc_budgets: Mapping[str, int]
    backlog_underscore_dirs: tuple[str, ...]
    backlog_status_vocabulary: Mapping[str, tuple[str, ...]]
    stale_marker_files: tuple[str, ...]
    stale_markers: tuple[str, ...]
    marker_allowlist: Mapping[tuple[str, str], str]
    backlog_archive_to_active: Mapping[str, str]
    backlog_numbered_prefixes: Mapping[str, tuple[str, str]]
    docs: Mapping[str, Path]
    limits: Mapping[str, int]
    regexes: Mapping[str, Any]
    surfaces: Mapping[str, tuple[str, ...]]

    @classmethod
    def from_defaults(cls, root: Path) -> "Scope":
        """Bind the declared tables to one run root.

        The mutable tables are copied, so a caller can never alias module state
        by accident. A case that must vary a declaration (the battery's unjustified
        allowlist entry is the only one today) builds its own scope from here and
        replaces that one field, instead of editing the shipped table.
        """
        return cls(
            root=root,
            entry_docs=ENTRY_DOCS,
            doc_layer_docs=DOC_LAYER_DOCS,
            linked_asset_docs=LINKED_ASSET_DOCS,
            doc_budgets=dict(DOC_BUDGETS),
            backlog_underscore_dirs=BACKLOG_UNDERSCORE_DIRS,
            backlog_status_vocabulary=dict(BACKLOG_STATUS_VOCABULARY),
            stale_marker_files=STALE_MARKER_FILES,
            stale_markers=STALE_MARKERS,
            marker_allowlist=dict(MARKER_ALLOWLIST),
            backlog_archive_to_active=dict(BACKLOG_ARCHIVE_TO_ACTIVE),
            backlog_numbered_prefixes=dict(BACKLOG_NUMBERED_PREFIXES),
            docs=dict(SCOPE_PATHS),
            limits=dict(SCOPE_LIMITS),
            regexes=dict(SCOPE_REGEXES),
            surfaces=dict(SCOPE_SURFACES),
        )
