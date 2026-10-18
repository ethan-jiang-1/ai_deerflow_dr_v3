"""The rule entry points and the RULES registry."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import markdown_fences

from .constants import MARKDOWN_LINK_RE, _COUNT_ARCHIVE_RE, _COUNT_SPECS_RE
from .scope import Scope
from .ledger import _adr_ids, _indexed_ids, _ledger_counter_problems, _ledger_placement_problems, _ledger_roster_problems, _read_utf8, _card_fix_reference_problems


def _rule_adr_index(scope: Scope) -> list[str]:
    if not (scope.root / scope.docs["adr_dir"]).is_dir():
        # v3 skeleton: the ADR layer does not exist yet; the rule engages as
        # soon as docs/adr/ is created (with or without its index).
        return []
    index = scope.root / scope.docs["adr_index"]
    if not index.is_file():
        return [f"ADR index missing: {scope.docs['adr_index'].as_posix()}"]
    present = _adr_ids(scope.root / scope.docs["adr_dir"])
    indexed = _indexed_ids(index)
    problems: list[str] = []
    missing = sorted(present - indexed)
    orphan = sorted(indexed - present)
    if missing:
        problems.append(f"ADR present but missing from index: {', '.join(missing)}")
    if orphan:
        problems.append(f"ADR index lists missing file: {', '.join(orphan)}")
    return problems


def _rule_links(scope: Scope) -> list[str]:
    problems: list[str] = []
    for kind, rels in (
        ("entry-chain", scope.entry_docs),
        ("docs-layer", scope.doc_layer_docs),
        ("asset-doc", scope.linked_asset_docs),
    ):
        for rel in rels:
            doc = scope.root / rel
            if not doc.is_file():
                problems.append(f"{kind} document missing: {rel}")
                continue
            text, decode_problem = _read_utf8(doc)
            if text is None:
                problems.append(f"non-UTF-8 {kind} document, links not checked: {rel}")
                continue
            for match in MARKDOWN_LINK_RE.finditer(text):
                target = match.group(1).strip()
                if not target or target.startswith(("http://", "https://", "mailto:", "#", "<")):
                    continue
                path_part = target.split("#", 1)[0].split("?", 1)[0].strip()
                if not path_part:
                    continue
                resolved = (doc.parent / path_part).resolve()
                if not resolved.exists():
                    problems.append(f"broken relative link in {rel}: {target}")
    return problems


def _rule_encoding_newline(scope: Scope) -> list[str]:
    problems: list[str] = []
    for kind, rels in (
        ("entry-chain", scope.entry_docs),
        ("docs-layer", scope.doc_layer_docs),
        ("asset-doc", scope.linked_asset_docs),
    ):
        for rel in rels:
            doc = scope.root / rel
            if not doc.is_file():
                continue  # missing doc already reported by the link rule
            text, decode_problem = _read_utf8(doc)
            if text is None:
                problems.append(f"non-UTF-8 {kind} document: {rel}")
                continue
            if not text.endswith("\n"):
                problems.append(f"{kind} document missing trailing newline: {rel}")
    return problems


def _rule_docs_scope(scope: Scope) -> list[str]:
    """Reject present docs-tree markdown that the registered scope omits."""
    tree = scope.root / scope.docs["docs_tree"]
    if not tree.is_dir():
        return []
    registered = set(scope.doc_layer_docs)
    problems: list[str] = []
    for path in sorted(tree.rglob("*.md")):
        rel = path.relative_to(scope.root).as_posix()
        if rel not in registered:
            problems.append(f"docs-layer markdown not in registered scope: {rel}")
    return problems


def _rule_backlog_underscore(scope: Scope) -> list[str]:
    """Retained `_`-prefixed backlog directories must be declared and documented.

    A `_` prefix means "retained collection, not the active work queue". Every
    `_`-prefixed directory that exists must be declared in
    ``BACKLOG_UNDERSCORE_DIRS``, every declared directory must exist, and each
    declared name must appear in ``_backlog/README.md`` so the machine list and
    the human index cannot drift apart.
    """
    backlog = scope.root / scope.docs["backlog_root"]
    if not backlog.is_dir():
        return []
    problems: list[str] = []
    declared = set(scope.backlog_underscore_dirs)
    present = {
        path.name
        for path in backlog.iterdir()
        if path.is_dir() and path.name.startswith("_")
    }
    for name in sorted(present - declared):
        problems.append(f"undeclared _-prefixed backlog directory: {name}")
    for name in scope.backlog_underscore_dirs:
        if name not in present:
            problems.append(f"declared backlog directory missing on disk: {name}")
    readme = backlog / "README.md"
    if readme.is_file():
        text, _ = _read_utf8(readme)
        if text is not None:
            for name in scope.backlog_underscore_dirs:
                if name not in text:
                    problems.append(f"backlog README does not document retained directory: {name}")
    return problems


def _rule_doc_budgets(scope: Scope) -> list[str]:
    """Resident documents listed in ``DOC_BUDGETS`` must fit their ceilings.

    The resident layer is what an agent host loads every session; its size is
    the denominator of every prompt, so each listed file gets a character
    ceiling. Counts use ``len`` of the decoded text so CJK documents are
    measured honestly. A managed file that is missing fails here as a missing
    managed path — the link rule does not cover the root instruction files,
    so this rule owns that failure itself (the inherited skip closed a silent
    gap where deleting a managed file produced no violation).
    """
    problems: list[str] = []
    for rel, ceiling in scope.doc_budgets.items():
        doc = scope.root / rel
        if not doc.is_file():
            problems.append(f"missing managed budget path: {rel}")
            continue
        text, decode_problem = _read_utf8(doc)
        if text is None:
            problems.append(f"non-UTF-8 resident document, budget not checked: {rel}")
            continue
        size = len(text)
        if size > ceiling:
            problems.append(
                f"resident document over character budget: {rel} "
                f"({size} > {ceiling}); shrink it, or justify raising the ceiling "
                f"with a one-line note next to the DOC_BUDGETS entry"
            )
    return problems


def _rule_ledger_consistency(scope: Scope) -> list[str]:
    """Ledger bookkeeping surfaces must be mechanically consistent (rule 7).

    The `_backlog` ritual states "编号、索引、计数三处一致"; this rule makes
    the stated ritual a checked invariant: every active/archive work-item file
    is indexed by its surface README, every index row resolves to disk, the
    `_archived/README.md` counters and Next-ID declarations match disk, and every
    active card carries a vocabulary-checked hukou without a residency
    violation (graduated/closable cards must have left the active zone).
    """
    backlog = scope.root / scope.docs["backlog_root"]
    if not backlog.is_dir():
        return []
    # Three named sub-rules, concatenated in their original order: the
    # violation order is part of the rule's observable output.
    return (
        _ledger_roster_problems(scope, backlog)
        + _ledger_counter_problems(scope, backlog)
        + _ledger_placement_problems(scope, backlog)
        + _card_fix_reference_problems(scope, backlog)
    )


def _rule_root_counts(scope: Scope) -> list[str]:
    """Root README inventory counts must match the machine-computed values.

    The checker computes the capability-spec and archived-change counts from
    disk and requires the root README status line to declare exactly those
    numbers, anchored to their inventory nouns. Wording may evolve; numbers
    may not drift (every archive silently ages a hand-written count).
    """
    problems: list[str] = []
    specs_dir = scope.root / "openspec" / "specs"
    archive_dir = scope.root / "openspec" / "changes" / "archive"
    readme = scope.root / "README.md"
    if not (specs_dir.is_dir() and archive_dir.is_dir() and readme.is_file()):
        return problems
    text, decode_problem = _read_utf8(readme)
    if text is None:
        problems.append("non-UTF-8 root README, count pinning not checked")
        return problems
    computed_specs = sum(1 for p in specs_dir.iterdir() if p.is_dir())
    computed_archive = sum(1 for p in archive_dir.iterdir() if p.is_dir())
    declared_specs = _COUNT_SPECS_RE.search(text)
    declared_archive = _COUNT_ARCHIVE_RE.search(text)
    if declared_specs is None or declared_archive is None:
        problems.append(
            "root README inventory count unpinned: the status line must declare "
            f"both counts (能力: {computed_specs}, changes 归档: {computed_archive})"
        )
        return problems
    if (
        int(declared_specs.group(1)) != computed_specs
        or int(declared_archive.group(1)) != computed_archive
    ):
        problems.append(
            f"root README count drift: declared {declared_specs.group(1)} 个能力 / "
            f"{declared_archive.group(1)} 个 changes 归档, computed "
            f"{computed_specs} / {computed_archive}"
        )
    return problems


def _rule_stale_markers(scope: Scope) -> list[str]:
    """Declared files must not contain declared skeleton-era markers (rule 8).

    A `(file, marker)` pair outside the justification allowlist fails with
    file and line; an unjustified or dangling allowlist entry fails as well,
    so the allowlist cannot become a silent dumping ground.
    """
    problems: list[str] = []
    for rel in scope.stale_marker_files:
        doc = scope.root / rel
        if not doc.is_file():
            problems.append(f"missing stale-marker managed path: {rel}")
            continue
        text, decode_problem = _read_utf8(doc)
        if text is None:
            problems.append(f"non-UTF-8 managed file, marker scan skipped: {rel}")
            continue
        doc_lines = text.splitlines()
        for line_number, (line, fenced) in enumerate(
            zip(doc_lines, markdown_fences.fence_flags(doc_lines), strict=True), start=1
        ):
            if fenced:
                continue  # quoting a forbidden marker inside a fence is documentation
            for marker in scope.stale_markers:
                if marker in line and (rel, marker) not in scope.marker_allowlist:
                    problems.append(f"stale narrative marker {marker!r} at {rel}:{line_number}")
    for (rel, marker), justification in scope.marker_allowlist.items():
        if not justification.strip():
            problems.append(f"allowlist entry without justification: ({rel}, {marker!r})")
        if rel not in scope.stale_marker_files:
            problems.append(f"allowlist entry for unmanaged file: {rel}")
            continue
        doc = scope.root / rel
        if doc.is_file():
            text, _ = _read_utf8(doc)
            if text is not None and marker not in text:
                problems.append(f"dangling allowlist entry: ({rel}, {marker!r}) no longer matches the file")
    return problems


RULES: tuple[tuple[str, Callable[[Scope], list[str]]], ...] = (
    ("adr_index", _rule_adr_index),
    ("links", _rule_links),
    ("encoding_newline", _rule_encoding_newline),
    ("docs_scope", _rule_docs_scope),
    ("backlog_underscore", _rule_backlog_underscore),
    ("doc_budgets", _rule_doc_budgets),
    ("ledger_consistency", _rule_ledger_consistency),
    ("stale_markers", _rule_stale_markers),
    ("root_counts", _rule_root_counts),
)


def violations(root: Path) -> list[str]:
    scope = Scope.from_defaults(root)
    found: list[str] = []
    for _name, rule in RULES:
        found.extend(rule(scope))
    return found
