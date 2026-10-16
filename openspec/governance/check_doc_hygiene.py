#!/usr/bin/env python3
"""Validate the dev-harness doc layer without external packages.


@impl DOB-001

Five mechanical doc-layer rules plus one backlog navigation rule, plus the
post-skeleton mechanizations (ledger bookkeeping surfaces with card hukou and
residency, declared stale-narrative markers, root README count pinning):

1. ADR index <-> directory consistency: every ``NNNN-*.md`` in
   ``deep_research_harness/docs/adr/`` (excluding ``README.md``) is listed in the
   index table, and every ADR listed in the index exists on disk.
2. Relative links resolve: every relative Markdown link in the entry-chain
   documents, in the docs-layer documents, and in the harness test/tools asset
   documents (``LINKED_ASSET_DOCS``) points to an existing file.
   ``http(s)``, ``mailto:``, bare ``#anchor``, and angle-bracket targets are
   ignored. Fragment and query suffixes do not participate in existence
   checking; anchors are deliberately NOT validated (line anchors track
   implementations) — an exclusion by declared limitation, not by omission.
3. Entry-chain, docs-layer, and asset documents are UTF-8 and end with a trailing newline.
4. Docs-layer scope completeness: every Markdown document actually present under
   ``deep_research_harness/docs/`` is registered in ``DOC_LAYER_DOCS``, so coverage
   cannot silently shrink when new documents are added. Registered but absent
   documents are reported by rules 2 and 3 instead.
5. Backlog ``_`` convention: every ``_``-prefixed directory that exists under
   ``_backlog/`` is declared in ``BACKLOG_UNDERSCORE_DIRS``, every declared
   directory exists, and each declared name is documented in ``_backlog/README.md``.
   This keeps the ``_`` prefix meaning "retained collection, not the active work
   queue" instead of drifting back into "actively edited but hidden".
6. Entry-chain character budgets: each resident document listed in
   ``DOC_BUDGETS`` must not exceed its character ceiling. Counts are characters,
   not words: ``wc -w``-style counting treats CJK text as one word per run and
   would be loose by an order of magnitude. Budgets apply only to listed files —
   routed-to documents are deliberately unbudgeted. Ceilings ratchet down:
   lowering one is always allowed; raising one requires a one-line justification
   recorded next to the entry.

A docs-layer document is a Markdown document under ``deep_research_harness/docs/``
— the top-level ``docs/*.md`` documents, plus any sublayer the enumeration
declares (operator runbooks, frozen evidence, decision records). Non-Markdown
files under that tree are out of scope. The scope is an explicit enumeration:
adding a docs document without registering it here turns rule 4 red on the next
run.

This checker is self-contained and standalone: it is NOT aggregated into
``check_project_gate.py`` (PRS-009 owns the six-component closeout) and is NOT
wired into the Harness ``make verify`` gate, which stays application-independent.
"""

from __future__ import annotations

import argparse
import re as _re
import re
import sys
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ADR_DIR = Path("deep_research_harness/docs/adr")
DOCS_TREE = Path("deep_research_harness/docs")
ADR_INDEX = ADR_DIR / "README.md"
BACKLOG_ROOT = Path("_backlog")
# `_`-prefixed backlog directories. Each is a retained collection (archived
# work-items or long-lived reference/evidence), never the active work queue.
# The checker requires this list, the filesystem, and the backlog README to
# agree, so a living area cannot hide behind the `_` prefix.
BACKLOG_UNDERSCORE_DIRS: tuple[str, ...] = (
    "_archived",
    "_research",
)
ENTRY_DOCS: tuple[str, ...] = (
    "AGENTS.md",
    "deep_research_harness/AGENTS.md",
    "deep_research_harness/CLAUDE.md",
    "deep_research_harness/README.md",
    "deep_research_harness/docs/README.md",
    "_backlog/README.md",
    "_backlog/AGENTS.md",
    "_backlog/triggers.md",
    "openspec/README.md",
)
# Resident-document character ceilings (rule 6). These are the files an agent
# host loads every session at the repository/module root; the resident layer is
# the denominator of every prompt, so its thickness is budgeted. Counts are
# characters (``len`` of the decoded text), never words. Ceilings ratchet down:
# lowering one is always allowed; raising one requires a one-line justification
# recorded next to the entry below.
DOC_BUDGETS: dict[str, int] = {
    # Root resident instructions (2345 chars measured post the 2026-10-12 fresh-agent
    # audit second round; ratcheted down from 2425).
    "AGENTS.md": 2345,
    # Root Claude entry stub; must stay a thin AGENTS.md import, never a copy.
    "CLAUDE.md": 400,
    # Module change map incl. generated structure block (6344 chars measured
    # post the 2026-10-12 fresh-agent audit second round; ratcheted down from 6835).
    "deep_research_harness/AGENTS.md": 6344,
    # Module Claude entry stub (253 chars at adoption).
    "deep_research_harness/CLAUDE.md": 400,
    # The largest resident-injection layer (11436 chars post
    # remove-requirement-id-tracking + catch-up-doc-truthfulness): config.yaml is
    # injected into every OpenSpec instruction path; the ceiling is deliberately
    # tight against the measured size to stop silent growth.
    "openspec/config.yaml": 11436,
    # Backlog agent doorplate (1195 chars measured at adoption,
    # make-backlog-process-explicit 2026-10-12): a thin positions/walks/tickets/
    # vocabulary pointer layer that owns no fact, so the ceiling is pinned to
    # the measured size to stop silent growth.
    "_backlog/AGENTS.md": 1195,
}
DOC_LAYER_DOCS: tuple[str, ...] = (
    # docs/ top-level markdown documents.
    # v3 skeleton inventory: the doc layer grows with its owning changes; every
    # docs/**/*.md on disk must be listed here and every entry must exist.
    "deep_research_harness/docs/README.md",
    "deep_research_harness/docs/control-map.md",
    "deep_research_harness/docs/local-operations.md",
    "deep_research_harness/docs/known-limitations.md",
    "deep_research_harness/docs/quality-register.md",
    "deep_research_harness/docs/run-bundle.md",
    "deep_research_harness/docs/research-process.md",
    "deep_research_harness/docs/skills/deep-research/README.md",
    "deep_research_harness/docs/skills/deep-research/SKILL.md",
    "deep_research_harness/docs/testing-and-evaluation.md",
    "deep_research_harness/docs/playbook/run-research.md",
)

LINKED_ASSET_DOCS: tuple[str, ...] = (
    # Harness test/tools asset documents swept by the link (and newline) rules.
    # These sit outside the docs/ tree, so they are deliberately NOT in
    # DOC_LAYER_DOCS — that list also feeds the docs-scope completeness rule,
    # which is scoped to docs/ only. The 2026-10-10 fresh-agent audit found 18
    # live dead links on these surfaces (grouping/rename changes had missed the
    # relative paths). Expanding this list is a visible change to the declaring
    # table (owning change: widen-doc-link-guard-scope).
    "deep_research_harness/tests/README.md",
    "deep_research_harness/tests/fixtures/README.md",
    "deep_research_harness/tools/README.md",
)

ADR_FILE_RE = re.compile(r"^\d{4}-.*\.md$")
INDEX_ROW_RE = re.compile(r"^\|\s*(\d{4})\s*\|")
MARKDOWN_LINK_RE = re.compile(r"\]\(([^)\s][^)]*)\)")


def _adr_ids(adir: Path) -> set[str]:
    return {
        path.name[:4]
        for path in adir.glob("*.md")
        if path.name != "README.md" and ADR_FILE_RE.match(path.name)
    }


def _indexed_ids(index: Path) -> set[str]:
    text = index.read_text(encoding="utf-8")
    return {
        match.group(1)
        for line in text.splitlines()
        if (match := INDEX_ROW_RE.match(line))
    }


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


def _read_utf8(doc: Path) -> tuple[str | None, str | None]:
    """Return (text, None) or (None, problem) for an undecodable document."""
    try:
        return doc.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "not UTF-8 decodable"


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



# Ledger bookkeeping surfaces (rule 7). The "编号、索引、计数三处一致" ritual,
# mechanized: active/archive work-item files must be indexed by their surface
# README, index rows must resolve to disk, and _archived/README.md counters must
# match disk. Adding a surface is a visible change to these tables.
BACKLOG_ACTIVE_SURFACES: tuple[str, ...] = ("issues", "bugs")
BACKLOG_ARCHIVE_SURFACES: tuple[str, ...] = (
    "_fixed_bugs",
    "_suspended_bugs",
    "_settled_issues",
    "_suspended_issues",
)
BACKLOG_COUNTERS_FILE = "_archived/README.md"
BACKLOG_NEXT_ID_RE = re.compile(r"\b([A-Z]{3})-(\d{3})\b")
# Numbered ledger allocation spans BOTH zones — the ledger rule states
# "新号 = 已分配的最大编号 + 1（已修复目录 ∪ 活跃目录）": a filed active card
# reserves its number. Next-ID derivation must therefore scan the active
# counterpart too; archive-only scanning let a declared next ID collide with
# an already-filed active card (2026-10-10 audit, BUG-002).
BACKLOG_ARCHIVE_TO_ACTIVE: dict[str, str] = {"_fixed_bugs": "bugs", "_settled_issues": "issues"}
# Numbered ledger READMEs whose "Next available … ID" declaration lines are
# checker-managed: at most one declaration per file and prefix, and the value
# must equal the allocation-derived next ID (BUG-002).
BACKLOG_NUMBERED_SURFACES: tuple[str, ...] = ("issues", "bugs", "_fixed_bugs", "_settled_issues")
BACKLOG_NUMBERED_PREFIXES: dict[str, tuple[str, str]] = {
    "BUG": ("_fixed_bugs", "bugs"),
    "CLS": ("_settled_issues", "issues"),
}
BACKLOG_NEXT_ID_DECL_RE = re.compile(r"Next available \w+ ID:\s*([A-Z]{3})-(\d{3})")

# Card hukou and residency (rule 7 continuation). Every active card carries a
# 状态 field within its first 12 lines whose word belongs to the surface's
# declared vocabulary; a card whose graduation field reads 已过 or which
# declares 可关闭：是 fails while it sits in the active zone. The residency
# match anchors on those termination-state fields only — delivery adjectives
# in the card body never red-line an honest awaiting-human card (the
# mis-kill class the borrowing source documented and fixed in 2026-10-08).
BACKLOG_CARD_HUKOU_LINE_LIMIT = 12
BACKLOG_STATUS_FIELD_RE = re.compile(r"状态[:：]\s*([^\s｜|，,]+)")
# Bug-track vocabulary (make-backlog-process-explicit, 2026-10-12): `活跃` is
# renamed `调查中` (it collided with "活跃区" once multiple active-zone words
# existed; the gerund restores symmetry with the issues side's `推敲中`) and
# gains `修就绪` (fix-ready: the flip carries the propose ticket), `已落修`
# (fix landed, acceptance unproven), and `等人拍板` (shared with issues).
# `待修` keeps its parked semantics (diagnosed, unscheduled, suspended pool).
# Zero active bug cards existed at the flip, so no card carried the old word.
BACKLOG_STATUS_VOCABULARY: dict[str, tuple[str, ...]] = {
    "issues": ("推敲中", "等人拍板"),
    "bugs": ("调查中", "修就绪", "已落修", "等人拍板", "待修"),
}
BACKLOG_GRADUATION_PASSED_RE = re.compile(r"毕业门[:：]\s*已过")
BACKLOG_CLOSABLE_RE = re.compile(r"可关闭[:：]\s*是")

# Stale-narrative markers (rule 8). A declared closed list of resident and
# doc-layer files must not contain a declared skeleton-era marker outside the
# justification allowlist; an unjustified or dangling allowlist entry fails.
STALE_MARKERS: tuple[str, ...] = (
    "骨架占位",
    "骨架期占位",
    "响亮占位",
    "预留位，尚未建档",
    "骨架期",
    "(skeleton)",
    "scaffolding until their owning changes",
)
STALE_MARKER_FILES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "CONTEXT-MAP.md",
    "deep_research_harness/README.md",
    "deep_research_harness/AGENTS.md",
    "deep_research_harness/COMMANDS.md",
    "deep_research_harness/CONTEXT.md",
    "deep_research_harness/docs/README.md",
    "deep_research_harness/docs/local-operations.md",
    "deep_research_harness/docs/known-limitations.md",
    "deep_research_harness/docs/quality-register.md",
    "deep_research_harness/docs/control-map.md",
    "deep_research_harness/docs/run-bundle.md",
    "deep_research_harness/docs/research-process.md",
    "deep_research_harness/docs/testing-and-evaluation.md",
    "deep_research_harness/tests/README.md",
    "deep_research_harness/src/deerflow_deep_research/__init__.py",
    "deep_research_harness/src/deerflow_deep_research/domain/__init__.py",
    "deep_research_harness/src/deerflow_deep_research/engine/__init__.py",
    "deep_research_harness/src/deerflow_deep_research/runtime/__init__.py",
    "deep_research_harness/src/deerflow_deep_research/agents/__init__.py",
)
MARKER_ALLOWLIST: dict[tuple[str, str], str] = {
    ("deep_research_harness/src/deerflow_deep_research/agents/__init__.py", "(skeleton)"):
        "the agents layer is genuinely empty; its fate is a deferred owning decision "
        "(audit plan _backlog/_archived/_settled_issues/2026-10-04-fresh-agent-doc-cleanup.md, not-in-scope item)",
}

# The per-run input surface of the rules. Rules never read module globals
# directly: the frozen ``Scope`` carries the declaration tables and the derived
# collections, so a rule is a function of its scope alone and a test can drive
# it without mutating module state (change: extract-doc-hygiene-test-battery).
SCOPE_PATHS: tuple[tuple[str, Path], ...] = (
    ("adr_dir", ADR_DIR),
    ("docs_tree", DOCS_TREE),
    ("adr_index", ADR_INDEX),
    ("backlog_root", BACKLOG_ROOT),
    ("counters_file", Path(BACKLOG_COUNTERS_FILE)),
)
SCOPE_LIMITS: tuple[tuple[str, int], ...] = (
    ("card_hukou_line_limit", BACKLOG_CARD_HUKOU_LINE_LIMIT),
)
SCOPE_REGEXES: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("next_id", BACKLOG_NEXT_ID_RE),
    ("next_id_decl", BACKLOG_NEXT_ID_DECL_RE),
    ("archive_to_active", re.compile(r"^_(?:fixed_bugs|settled_issues)$")),
)
SCOPE_SURFACES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("active", BACKLOG_ACTIVE_SURFACES),
    ("archive", BACKLOG_ARCHIVE_SURFACES),
    ("numbered", BACKLOG_NUMBERED_SURFACES),
)


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



def _card_hukou_problems(scope: Scope, surface: str, card: Path) -> list[str]:
    """Active-card hukou and residency (rule 7 continuation).

    Every active card carries a ``状态`` field in its first 12 lines whose
    word belongs to the surface's declared vocabulary; a card whose status
    line declares ``毕业门：已过`` or ``可关闭：是`` fails while it still sits
    in the active zone. Anchored on the declared fields only — an awaiting
    ``等人拍板`` card with delivery language in its body stays green.
    """
    text, decode_problem = _read_utf8(card)
    if text is None:
        return [f"non-UTF-8 active card, hukou not checked: {surface}/{card.name}"]
    head = "\n".join(text.splitlines()[:scope.limits["card_hukou_line_limit"]])
    problems: list[str] = []
    status = BACKLOG_STATUS_FIELD_RE.search(head)
    vocabulary = scope.backlog_status_vocabulary.get(surface, ())
    if status is None:
        problems.append(
            f"active card missing 状态 hukou in first "
            f"{scope.limits['card_hukou_line_limit']} lines: {surface}/{card.name}"
        )
    elif status.group(1).strip() not in vocabulary:
        problems.append(
            f"active card status word {status.group(1)!r} outside declared "
            f"vocabulary {vocabulary}: {surface}/{card.name}"
        )
    if BACKLOG_GRADUATION_PASSED_RE.search(head):
        problems.append(
            f"graduated card still in active zone (毕业门：已过): {surface}/{card.name}"
        )
    if BACKLOG_CLOSABLE_RE.search(head):
        problems.append(
            f"card declared closable but still in active zone (可关闭：是): "
            f"{surface}/{card.name}"
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
    problems: list[str] = []
    backlog = scope.root / scope.docs["backlog_root"]
    if not backlog.is_dir():
        return problems

    def _surface_dir(surface: str) -> Path:
        # Zone split is data-driven: an archive surface is the `_`-prefixed one.
        if scope.regexes["archive_to_active"].match(surface):
            return backlog / "_archived" / surface
        return backlog / surface

    def _work_files(surface: str) -> list[Path]:
        surface_dir = _surface_dir(surface)
        if not surface_dir.is_dir():
            return []
        return sorted(p for p in surface_dir.glob("*.md") if p.name != "README.md")

    def _allocated_numbers(archive_surface: str, active_surface: str | None, prefix: str) -> list[int]:
        """Allocated numbers for one prefix across the archive zone and the
        active zone (the ledger rule: 已修复目录 ∪ 活跃目录). Single source for
        the counters check and the README declaration check."""
        allocated: list[int] = []
        index_file = backlog / "_archived" / archive_surface / "README.md"
        if index_file.is_file():
            body, _ = _read_utf8(index_file)
            for line in (body or "").splitlines():
                if not line.lstrip().startswith("|"):
                    continue  # skip the Next-ID declaration line itself
                for id_match in scope.regexes["next_id"].finditer(line):
                    if id_match.group(1) == prefix:
                        allocated.append(int(id_match.group(2)))
        work_files = list(_work_files(archive_surface))
        if active_surface:
            work_files.extend(_work_files(active_surface))
        for work in work_files:
            for id_match in scope.regexes["next_id"].finditer(work.name):
                if id_match.group(1) == prefix:
                    allocated.append(int(id_match.group(2)))
        return allocated

    for surface in (*scope.surfaces["active"], *scope.surfaces["archive"]):
        surface_dir = _surface_dir(surface)
        index = surface_dir / "README.md"
        if not surface_dir.is_dir():
            continue
        work_files = _work_files(surface)
        if work_files and not index.is_file():
            problems.append(f"ledger surface with work items missing its README index: {surface}")
            continue
        if not index.is_file():
            continue
        index_text, decode_problem = _read_utf8(index)
        if index_text is None:
            problems.append(f"non-UTF-8 ledger index, consistency not checked: {surface}/README.md")
            continue
        for work in work_files:
            if work.name not in index_text:
                problems.append(
                    f"active ledger surface has an unindexed work item: {surface}/{work.name}"
                )
        if surface in scope.surfaces["active"]:
            for work in work_files:
                problems.extend(_card_hukou_problems(scope, surface, work))
        for link in MARKDOWN_LINK_RE.findall(index_text):
            target = link.split("#", 1)[0].strip()
            if not target.endswith(".md"):
                continue
            if not (surface_dir / target).is_file():
                problems.append(f"dangling index row in {surface}/README.md: {target}")

        # Placement: every table row must sit inside a real table block —
        # contiguous with a header separator. Blank lines, prose, or fences
        # between a row and its header shatter the table (observed twice as
        # the B3/B5 recurrence); such blocks fail naming the surface.
        in_fence = False
        block: list[str] = []
        blocks: list[list[str]] = []

        def _flush() -> None:
            if block:
                blocks.append(list(block))
                block.clear()

        for raw in index_text.splitlines():
            if raw.strip().startswith("```"):
                _flush()
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if raw.strip():
                block.append(raw)
            else:
                _flush()
        _flush()
        for blk in blocks:
            if not any(line.lstrip().startswith("|") for line in blk):
                continue
            has_separator = any(
                _re.match(r"^\|[\s:\-|]+\|?\s*$", line) for line in blk
            )
            if not (has_separator and all(line.lstrip().startswith("|") for line in blk)):
                problems.append(
                    f"ledger row placement defect in {surface}/README.md: "
                    "table rows separated from their header block"
                )

    counters = backlog / scope.docs["counters_file"]
    if counters.is_file():
        counters_text, decode_problem = _read_utf8(counters)
        if counters_text is not None:
            for line in counters_text.splitlines():
                row = re.match(r"^\|\s*`([\w-]+?)/`\s*\|\s*(\d+)\s*\|\s*([^|]+)\|", line)
                if not row:
                    continue
                surface, declared_count, declared_next = row.group(1), int(row.group(2)), row.group(3).strip()
                disk_count = len(_work_files(surface))
                if declared_count != disk_count:
                    problems.append(
                        f"counter mismatch in {scope.docs['counters_file']}: {surface} declares "
                        f"{declared_count} but disk holds {disk_count}"
                    )
                next_match = scope.regexes["next_id"].search(declared_next)
                if not next_match:
                    continue
                prefix, number = next_match.group(1), int(next_match.group(2))
                allocated = _allocated_numbers(surface, scope.backlog_archive_to_active.get(surface), prefix)
                expected_next = (max(allocated) + 1) if allocated else 1
                if number != expected_next:
                    problems.append(
                        f"next-ID mismatch in {scope.docs['counters_file']}: {surface} declares "
                        f"{prefix}-{number:03d} but allocation implies {prefix}-{expected_next:03d}"
                    )

    # Next-ID declarations in the numbered ledger READMEs: at most one per file
    # and prefix, and the value must equal the ∪-derived next ID (BUG-002: a
    # duplicated stale declaration passed while the counters table alone stayed
    # consistent).
    for surface in scope.surfaces["numbered"]:
        surface_dir = _surface_dir(surface)
        index = surface_dir / "README.md"
        if not index.is_file():
            continue
        index_text, _ = _read_utf8(index)
        if index_text is None:
            continue
        declarations: dict[str, list[tuple[int, str]]] = {}
        for line_no, line in enumerate(index_text.splitlines(), 1):
            decl_match = scope.regexes["next_id_decl"].search(line)
            if decl_match:
                declarations.setdefault(decl_match.group(1), []).append(
                    (int(decl_match.group(2)), f"line {line_no}")
                )
        for prefix in sorted(declarations):
            entries = declarations[prefix]
            if len(entries) > 1:
                problems.append(
                    f"duplicate next-ID declaration in {surface}/README.md: prefix {prefix} declared "
                    f"{len(entries)} times ({', '.join(f'{value:03d} at {where}' for value, where in entries)})"
                )
            prefix_pair = scope.backlog_numbered_prefixes.get(prefix)
            if not prefix_pair:
                continue
            declared_allocated = _allocated_numbers(prefix_pair[0], prefix_pair[1], prefix)
            derived_next = (max(declared_allocated) + 1) if declared_allocated else 1
            for value, where in entries:
                if value != derived_next:
                    problems.append(
                        f"next-ID declaration disagrees in {surface}/README.md: {prefix}-{value:03d} at {where} "
                        f"but allocation implies {prefix}-{derived_next:03d}"
                    )
    return problems


_COUNT_SPECS_RE = _re.compile(r"(\d+)\s*个\s*能力")
_COUNT_ARCHIVE_RE = _re.compile(r"(\d+)\s*个\s*changes\s*归档")


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
        for line_number, line in enumerate(text.splitlines(), start=1):
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


# Rule registration: declaration order is the reporting order, so this tuple
# is the dispatch (adding a rule is one function plus one entry here).
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


def _self_test() -> list[str]:
    """Run the negative-control battery and return the failing case identities.

    Thin delegate by design: the cases and their assertion identities live in
    ``_battery.py`` (one home), and the governance unittest battery
    (``tests/governance/test_doc_hygiene.py``) drives the same registry. This
    module keeps the CLI contract — command, stdout, exit codes — not a second
    copy of the assertions.
    """
    import _battery

    return _battery.failing_controls()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true", help="run negative-control fixtures")
    args = parser.parse_args()

    if args.self_test:
        errs = _self_test()
        if errs:
            print("doc-hygiene self-test FAILED:", file=sys.stderr)
            print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
            return 1
        print("doc-hygiene self-test passed.")
        return 0

    found = violations(args.project_root.resolve())
    if found:
        print("doc-layer hygiene violations:", file=sys.stderr)
        print("\n".join(f"- {v}" for v in found), file=sys.stderr)
        return 1
    print("doc-layer hygiene passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
