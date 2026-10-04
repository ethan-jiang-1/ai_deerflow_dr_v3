#!/usr/bin/env python3
"""Validate the dev-harness doc layer without external packages.


@impl DOB-001

Five mechanical doc-layer rules plus one backlog navigation rule:

1. ADR index <-> directory consistency: every ``NNNN-*.md`` in
   ``deep_research_harness/docs/adr/`` (excluding ``README.md``) is listed in the
   index table, and every ADR listed in the index exists on disk.
2. Relative links resolve: every relative Markdown link in the entry-chain
   documents and in the docs-layer documents points to an existing file.
   ``http(s)``, ``mailto:``, bare ``#anchor``, and angle-bracket targets are
   ignored.
3. Entry-chain and docs-layer documents are UTF-8 and end with a trailing newline.
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
from pathlib import Path

ADR_DIR = Path("deep_research_harness/docs/adr")
DOCS_TREE = Path("deep_research_harness/docs")
ADR_INDEX = ADR_DIR / "README.md"
BACKLOG_ROOT = Path("_backlog")
# `_`-prefixed backlog directories. Each is a retained collection (archived
# work-items or long-lived reference/evidence), never the active work queue.
# The checker requires this list, the filesystem, and the backlog README to
# agree, so a living area cannot hide behind the `_` prefix.
BACKLOG_UNDERSCORE_DIRS: tuple[str, ...] = (
    "_done",
    "_reference",
)
ENTRY_DOCS: tuple[str, ...] = (
    "AGENTS.md",
    "deep_research_harness/AGENTS.md",
    "deep_research_harness/CLAUDE.md",
    "deep_research_harness/README.md",
    "deep_research_harness/docs/README.md",
    "_backlog/README.md",
    "openspec/README.md",
)
# Resident-document character ceilings (rule 6). These are the files an agent
# host loads every session at the repository/module root; the resident layer is
# the denominator of every prompt, so its thickness is budgeted. Counts are
# characters (``len`` of the decoded text), never words. Ceilings ratchet down:
# lowering one is always allowed; raising one requires a one-line justification
# recorded next to the entry below.
DOC_BUDGETS: dict[str, int] = {
    # Root resident instructions (2425 chars measured post doc-hygiene-second-sweep;
    # ratcheted down from 2435).
    "AGENTS.md": 2425,
    # Root Claude entry stub; must stay a thin AGENTS.md import, never a copy.
    "CLAUDE.md": 400,
    # Module change map incl. generated structure block (6863 chars measured post
    # doc-hygiene-second-sweep; ratcheted down from 6864).
    "deep_research_harness/AGENTS.md": 6863,
    # Module Claude entry stub (253 chars at adoption).
    "deep_research_harness/CLAUDE.md": 400,
    # The largest resident-injection layer (11436 chars post
    # remove-requirement-id-tracking + catch-up-doc-truthfulness): config.yaml is
    # injected into every OpenSpec instruction path; the ceiling is deliberately
    # tight against the measured size to stop silent growth.
    "openspec/config.yaml": 11436,
}
DOC_LAYER_DOCS: tuple[str, ...] = (
    # docs/ top-level markdown documents.
    # v3 skeleton inventory: the doc layer grows with its owning changes; every
    # docs/**/*.md on disk must be listed here and every entry must exist.
    "deep_research_harness/docs/README.md",
    "deep_research_harness/docs/local-operations.md",
    "deep_research_harness/docs/known-limitations.md",
    "deep_research_harness/docs/quality-register.md",
    "deep_research_harness/docs/runtime-architecture.md",
    "deep_research_harness/docs/testing-and-evaluation.md",
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


def _rule_adr_index(root: Path) -> list[str]:
    if not (root / ADR_DIR).is_dir():
        # v3 skeleton: the ADR layer does not exist yet; the rule engages as
        # soon as docs/adr/ is created (with or without its index).
        return []
    index = root / ADR_INDEX
    if not index.is_file():
        return [f"ADR index missing: {ADR_INDEX.as_posix()}"]
    present = _adr_ids(root / ADR_DIR)
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


def _rule_links(root: Path) -> list[str]:
    problems: list[str] = []
    for kind, rels in (("entry-chain", ENTRY_DOCS), ("docs-layer", DOC_LAYER_DOCS)):
        for rel in rels:
            doc = root / rel
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


def _rule_encoding_newline(root: Path) -> list[str]:
    problems: list[str] = []
    for kind, rels in (("entry-chain", ENTRY_DOCS), ("docs-layer", DOC_LAYER_DOCS)):
        for rel in rels:
            doc = root / rel
            if not doc.is_file():
                continue  # missing doc already reported by the link rule
            text, decode_problem = _read_utf8(doc)
            if text is None:
                problems.append(f"non-UTF-8 {kind} document: {rel}")
                continue
            if not text.endswith("\n"):
                problems.append(f"{kind} document missing trailing newline: {rel}")
    return problems


def _rule_docs_scope(root: Path) -> list[str]:
    """Reject present docs-tree markdown that the registered scope omits."""
    tree = root / DOCS_TREE
    if not tree.is_dir():
        return []
    registered = set(DOC_LAYER_DOCS)
    problems: list[str] = []
    for path in sorted(tree.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel not in registered:
            problems.append(f"docs-layer markdown not in registered scope: {rel}")
    return problems


def _rule_backlog_underscore(root: Path) -> list[str]:
    """Retained `_`-prefixed backlog directories must be declared and documented.

    A `_` prefix means "retained collection, not the active work queue". Every
    `_`-prefixed directory that exists must be declared in
    ``BACKLOG_UNDERSCORE_DIRS``, every declared directory must exist, and each
    declared name must appear in ``_backlog/README.md`` so the machine list and
    the human index cannot drift apart.
    """
    backlog = root / BACKLOG_ROOT
    if not backlog.is_dir():
        return []
    problems: list[str] = []
    declared = set(BACKLOG_UNDERSCORE_DIRS)
    present = {
        path.name
        for path in backlog.iterdir()
        if path.is_dir() and path.name.startswith("_")
    }
    for name in sorted(present - declared):
        problems.append(f"undeclared _-prefixed backlog directory: {name}")
    for name in BACKLOG_UNDERSCORE_DIRS:
        if name not in present:
            problems.append(f"declared backlog directory missing on disk: {name}")
    readme = backlog / "README.md"
    if readme.is_file():
        text, _ = _read_utf8(readme)
        if text is not None:
            for name in BACKLOG_UNDERSCORE_DIRS:
                if name not in text:
                    problems.append(f"backlog README does not document retained directory: {name}")
    return problems



# Ledger bookkeeping surfaces (rule 7). The "编号、索引、计数三处一致" ritual,
# mechanized: active/archive work-item files must be indexed by their surface
# README, index rows must resolve to disk, and _done/README.md counters must
# match disk. Adding a surface is a visible change to these tables.
BACKLOG_ACTIVE_SURFACES: tuple[str, ...] = ("plans", "bugs")
BACKLOG_ARCHIVE_SURFACES: tuple[str, ...] = (
    "_fixed_bugs",
    "_suspended_bugs",
    "_closed_plans",
    "_suspended_plans",
)
BACKLOG_COUNTERS_FILE = "_done/README.md"
BACKLOG_NEXT_ID_RE = re.compile(r"\b([A-Z]{3})-(\d{3})\b")

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
    "deep_research_harness/docs/runtime-architecture.md",
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
        "(audit plan _backlog/_done/_closed_plans/2026-10-04-fresh-agent-doc-cleanup.md, not-in-scope item)",
}

def _rule_doc_budgets(root: Path) -> list[str]:
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
    for rel, ceiling in DOC_BUDGETS.items():
        doc = root / rel
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



def _rule_ledger_consistency(root: Path) -> list[str]:
    """Ledger bookkeeping surfaces must be mechanically consistent (rule 7).

    The `_backlog` ritual states "编号、索引、计数三处一致"; this rule makes
    the stated ritual a checked invariant: every active/archive work-item file
    is indexed by its surface README, every index row resolves to disk, and
    the `_done/README.md` counters and Next-ID declarations match disk.
    """
    problems: list[str] = []
    backlog = root / "_backlog"
    if not backlog.is_dir():
        return problems

    def _surface_dir(surface: str) -> Path:
        return backlog / surface if surface in BACKLOG_ACTIVE_SURFACES else backlog / "_done" / surface

    def _work_files(surface: str) -> list[Path]:
        surface_dir = _surface_dir(surface)
        if not surface_dir.is_dir():
            return []
        return sorted(p for p in surface_dir.glob("*.md") if p.name != "README.md")

    for surface in (*BACKLOG_ACTIVE_SURFACES, *BACKLOG_ARCHIVE_SURFACES):
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

    counters = backlog / BACKLOG_COUNTERS_FILE
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
                        f"counter mismatch in {BACKLOG_COUNTERS_FILE}: {surface} declares "
                        f"{declared_count} but disk holds {disk_count}"
                    )
                next_match = BACKLOG_NEXT_ID_RE.search(declared_next)
                if not next_match:
                    continue
                prefix, number = next_match.group(1), int(next_match.group(2))
                index = _surface_dir(surface) / "README.md"
                allocated: list[int] = []
                if index.is_file():
                    index_body, _ = _read_utf8(index)
                    for line in (index_body or "").splitlines():
                        if not line.lstrip().startswith("|"):
                            continue  # skip the Next-ID declaration line itself
                        for id_match in BACKLOG_NEXT_ID_RE.finditer(line):
                            if id_match.group(1) == prefix:
                                allocated.append(int(id_match.group(2)))
                for work in _work_files(surface):
                    for id_match in BACKLOG_NEXT_ID_RE.finditer(work.name):
                        if id_match.group(1) == prefix:
                            allocated.append(int(id_match.group(2)))
                expected_next = (max(allocated) + 1) if allocated else 1
                if number != expected_next:
                    problems.append(
                        f"next-ID mismatch in {BACKLOG_COUNTERS_FILE}: {surface} declares "
                        f"{prefix}-{number:03d} but allocation implies {prefix}-{expected_next:03d}"
                    )
    return problems


_COUNT_SPECS_RE = _re.compile(r"(\d+)\s*个\s*能力")
_COUNT_ARCHIVE_RE = _re.compile(r"(\d+)\s*个\s*changes\s*归档")


def _rule_root_counts(root: Path) -> list[str]:
    """Root README inventory counts must match the machine-computed values.

    The checker computes the capability-spec and archived-change counts from
    disk and requires the root README status line to declare exactly those
    numbers, anchored to their inventory nouns. Wording may evolve; numbers
    may not drift (every archive silently ages a hand-written count).
    """
    problems: list[str] = []
    specs_dir = root / "openspec" / "specs"
    archive_dir = root / "openspec" / "changes" / "archive"
    readme = root / "README.md"
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


def _rule_stale_markers(root: Path) -> list[str]:
    """Declared files must not contain declared skeleton-era markers (rule 8).

    A `(file, marker)` pair outside the justification allowlist fails with
    file and line; an unjustified or dangling allowlist entry fails as well,
    so the allowlist cannot become a silent dumping ground.
    """
    problems: list[str] = []
    for rel in STALE_MARKER_FILES:
        doc = root / rel
        if not doc.is_file():
            problems.append(f"missing stale-marker managed path: {rel}")
            continue
        text, decode_problem = _read_utf8(doc)
        if text is None:
            problems.append(f"non-UTF-8 managed file, marker scan skipped: {rel}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for marker in STALE_MARKERS:
                if marker in line and (rel, marker) not in MARKER_ALLOWLIST:
                    problems.append(f"stale narrative marker {marker!r} at {rel}:{line_number}")
    for (rel, marker), justification in MARKER_ALLOWLIST.items():
        if not justification.strip():
            problems.append(f"allowlist entry without justification: ({rel}, {marker!r})")
        if rel not in STALE_MARKER_FILES:
            problems.append(f"allowlist entry for unmanaged file: {rel}")
            continue
        doc = root / rel
        if doc.is_file():
            text, _ = _read_utf8(doc)
            if text is not None and marker not in text:
                problems.append(f"dangling allowlist entry: ({rel}, {marker!r}) no longer matches the file")
    return problems


def violations(root: Path) -> list[str]:
    found: list[str] = []
    found.extend(_rule_adr_index(root))
    found.extend(_rule_links(root))
    found.extend(_rule_encoding_newline(root))
    found.extend(_rule_docs_scope(root))
    found.extend(_rule_backlog_underscore(root))
    found.extend(_rule_doc_budgets(root))
    found.extend(_rule_ledger_consistency(root))
    found.extend(_rule_stale_markers(root))
    found.extend(_rule_root_counts(root))
    return found


def _self_test() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        def write_doc(rel: str, content: str) -> None:
            doc = base / rel
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(content, encoding="utf-8")

        # Clean fixture: every registered document exists with a valid self link,
        # and the ADR index lists every registered ADR id. Derived from the
        # constants so the fixture follows future scope changes.
        for rel in ENTRY_DOCS:
            write_doc(rel, f"# T\n\n[self]({rel.rsplit('/', 1)[-1]})\n")
        adr_ids: list[str] = []
        for rel in DOC_LAYER_DOCS:
            name = rel.rsplit("/", 1)[-1]
            write_doc(rel, f"# T\n\n[self]({name})\n")
            if ADR_FILE_RE.match(name):
                adr_ids.append(name[:4])
        # The clean fixture builds the ADR layer only when the registered scope
        # declares it; with no ``docs/adr/`` entry the directory stays absent and
        # ``_rule_adr_index`` is dormant by its dir-existence guard.

        # Backlog fixture: every declared `_` directory exists and is named in
        # the backlog README, so the clean fixture satisfies the backlog rule.
        backlog = base / BACKLOG_ROOT
        backlog_readme_body = "# T\n\n[self](README.md)\n" + "".join(
            f"- {name}\n" for name in BACKLOG_UNDERSCORE_DIRS
        )
        write_doc((BACKLOG_ROOT / "README.md").as_posix(), backlog_readme_body)
        for name in BACKLOG_UNDERSCORE_DIRS:
            (backlog / name).mkdir(parents=True, exist_ok=True)

        # Budget-managed and marker-managed files not on the entry chain get
        # minimal stubs so the clean fixture satisfies those rules (missing
        # managed paths fail loudly by design).
        for rel in (*DOC_BUDGETS, *STALE_MARKER_FILES):
            if not (base / rel).is_file():
                # An allowlisted marker must stay present in its stub, or the
                # allowlist honestly reports dangling.
                content = "# T\n"
                if any(rel == allowed_rel for allowed_rel, _ in MARKER_ALLOWLIST):
                    content = '"""stub (skeleton)."""\n'
                write_doc(rel, content)

        if violations(base):
            errors.append("self-test: clean fixture must have zero violations")

        # Rule 1 negative: orphan index entry (lists an absent ADR id).
        # Fabricate a minimal ADR layer to engage the dir-existence guard.
        write_doc(
            ADR_INDEX.as_posix(),
            "# ADR Index\n\n| 编号 | 一句话 | 生命周期 |\n|---|---|---|\n",
        )
        index = base / ADR_INDEX
        index.write_text(index.read_text(encoding="utf-8") + "| 9999 | b | current |\n", encoding="utf-8")
        if not any("9999" in v for v in _rule_adr_index(base)):
            errors.append("self-test: ADR index orphan not detected")

        # Rule 2 negative (entry-chain): broken relative link.
        write_doc("deep_research_harness/README.md", "# T\n\nsee [gone.md](gone.md)\n")
        if not any("gone.md" in v for v in _rule_links(base)):
            errors.append("self-test: broken link not detected")

        # Rule 3 negative (entry-chain): missing trailing newline.
        write_doc("openspec/README.md", "# no newline")
        if not any("trailing newline" in v for v in _rule_encoding_newline(base)):
            errors.append("self-test: missing trailing newline not detected")

        # Rule 2 negative (docs-layer): broken relative link.
        write_doc(
            "deep_research_harness/docs/local-operations.md",
            "# T\n\nsee [gone.md](gone.md)\n",
        )
        if not any("gone.md" in v for v in _rule_links(base)):
            errors.append("self-test: docs-layer broken link not detected")

        # Rule 3 negative (docs-layer): missing trailing newline.
        write_doc("deep_research_harness/docs/testing-and-evaluation.md", "# no newline")
        if not any(
            "docs-layer document missing trailing newline" in v
            for v in _rule_encoding_newline(base)
        ):
            errors.append("self-test: docs-layer missing trailing newline not detected")

        # Rule 3 negative (docs-layer): non-UTF-8 bytes.
        bad = base / "deep_research_harness/docs/runtime-architecture.md"
        bad.write_bytes(b"\xff\xfe binary")
        if not any(
            "non-UTF-8 docs-layer document" in v
            for v in _rule_encoding_newline(base)
        ):
            errors.append("self-test: docs-layer non-UTF-8 not detected")

        # Rule 4 negative: present docs markdown missing from the registered scope.
        write_doc("deep_research_harness/docs/zz-unregistered.md", "# extra\n")
        if not any("zz-unregistered.md" in v for v in _rule_docs_scope(base)):
            errors.append("self-test: unregistered docs-layer markdown not detected")

        # Rule 5 negative: undeclared `_`-prefixed backlog directory.
        (backlog / "_zz-undeclared").mkdir(parents=True, exist_ok=True)
        if not any("_zz-undeclared" in v for v in _rule_backlog_underscore(base)):
            errors.append("self-test: undeclared backlog directory not detected")

        # Rule 5 negative: declared directory absent from the backlog README.
        write_doc((BACKLOG_ROOT / "README.md").as_posix(), "# T\n\n[self](README.md)\n")
        if not any(
            "does not document retained directory" in v
            for v in _rule_backlog_underscore(base)
        ):
            errors.append("self-test: undocumented backlog directory not detected")

        # Rule 6 negative: resident document over its character ceiling.
        write_doc("AGENTS.md", "# T\n\n" + "x" * (DOC_BUDGETS["AGENTS.md"] + 1) + "\n")
        if not any("over character budget" in v for v in _rule_doc_budgets(base)):
            errors.append("self-test: over-budget resident document not detected")
        write_doc("AGENTS.md", "# T\n\n[self](AGENTS.md)\n")

        # Rule 6 negative: managed budget path goes missing (deleted managed
        # file must fail loudly — the inherited skip let it pass silently).
        (base / "CLAUDE.md").unlink()
        if not any("missing managed budget path" in v for v in _rule_doc_budgets(base)):
            errors.append("self-test: missing managed budget path not detected")
        write_doc("CLAUDE.md", "# T\n")

        # Rule 7 negatives: ledger index/counter drift must fail loudly.
        ledger = base / "ledger-repo"
        for surface in ("plans", "_done/_closed_plans"):
            surface_dir = ledger / "_backlog" / surface
            surface_dir.mkdir(parents=True, exist_ok=True)
        (ledger / "_backlog" / "plans" / "2026-10-01-demo.md").write_text("# plan\n", encoding="utf-8")
        (ledger / "_backlog" / "plans" / "README.md").write_text("# Plans\n\n（空）\n", encoding="utf-8")
        (ledger / "_backlog" / "_done" / "_closed_plans" / "README.md").write_text(
            "# Closed\n\n| ID | Date | File | Summary |\n|---|---|---|---|\n"
            "| CLS-001 | 2026-10-01 | [2026-10-01-gone.md](2026-10-01-gone.md) | x |\n\n"
            "**Next available plan ID: CLS-002**\n",
            encoding="utf-8",
        )
        (ledger / "_backlog" / "_done" ).mkdir(parents=True, exist_ok=True)
        (ledger / "_backlog" / "_done" / "README.md").write_text(
            "| 归档目录 | 数量 | Next ID |\n|---|---|---|\n"
            "| `_fixed_bugs/` | 0 | BUG-001 |\n| `_closed_plans/` | 1 | CLS-002 |\n",
            encoding="utf-8",
        )
        ledger_problems = _rule_ledger_consistency(ledger)
        for needle in (
            "active ledger surface",
            "dangling index row",
            "counter mismatch",
        ):
            if not any(needle in v for v in ledger_problems):
                errors.append(f"self-test: ledger rule did not detect: {needle}")

        # Rule 7 negative (placement): a work-item row separated from its table
        # header block by a blank line and a fence must fail loudly. Uses a
        # fresh ledger tree; the row references a file that exists on disk so
        # only the placement defect is exercised.
        placed = base / "placement-repo"
        closed = placed / "_backlog" / "_done" / "_closed_plans"
        closed.mkdir(parents=True, exist_ok=True)
        (closed / "2026-10-01-here.md").write_text("# plan\n", encoding="utf-8")
        (closed / "README.md").write_text(
            "# Closed\n\n"
            "```markdown\n"
            "| Plan | 一句话 |\n"
            "|------|--------|\n"
            "```\n"
            "| CLS-001 | 2026-10-01 | [2026-10-01-here.md](2026-10-01-here.md) | ok |\n\n"
            "**Next available plan ID: CLS-002**\n",
            encoding="utf-8",
        )
        placed_problems = _rule_ledger_consistency(placed)
        if not any("placement" in v for v in placed_problems):
            errors.append("self-test: ledger row placement defect not detected")
        contiguous = placed / "_backlog" / "_done" / "_contiguous_plans"
        contiguous.mkdir(parents=True, exist_ok=True)
        (contiguous / "2026-10-01-here.md").write_text("# plan\n", encoding="utf-8")
        (contiguous / "README.md").write_text(
            "# Closed\n\n"
            "| ID | Date | File | Summary |\n"
            "|---|---|---|---|\n"
            "| CLS-001 | 2026-10-01 | [2026-10-01-here.md](2026-10-01-here.md) | ok |\n",
            encoding="utf-8",
        )
        if any("placement" in v for v in _rule_ledger_consistency(contiguous)):
            errors.append("self-test: contiguous table flagged as misplaced")

        # Root-count pinning negative: a README status line whose declared
        # counts differ from the computed inventory must fail loudly.
        counted = base / "counts-repo"
        (counted / "openspec/specs/alpha").mkdir(parents=True, exist_ok=True)
        (counted / "openspec/specs/beta").mkdir(parents=True, exist_ok=True)
        (counted / "openspec/changes/archive/2026-01-01-one").mkdir(parents=True, exist_ok=True)
        readme = counted / "README.md"
        readme.write_text(
            "> specs 主干 5 个能力落地、7 个 changes 归档。\n", encoding="utf-8"
        )
        count_problems = _rule_root_counts(counted)
        if not any("5" in v and "7" in v for v in count_problems):
            errors.append("self-test: drifted root-README count not detected")
        readme.write_text(
            "> specs 主干 2 个能力落地、1 个 changes 归档。\n", encoding="utf-8"
        )
        if _rule_root_counts(counted):
            errors.append("self-test: matching counts flagged as drifted")
        readme.write_text("> 没有声明计数的行。\n", encoding="utf-8")
        if not any("unpinned" in v for v in _rule_root_counts(counted)):
            errors.append("self-test: missing count declaration not detected")

        # Rule 8 negatives: a re-introduced marker fails; an unjustified or
        # dangling allowlist entry fails.
        marker_root = base / "marker-repo"
        marker_doc = marker_root / "AGENTS.md"
        marker_doc.parent.mkdir(parents=True, exist_ok=True)
        for rel in STALE_MARKER_FILES:
            (marker_root / rel).parent.mkdir(parents=True, exist_ok=True)
            content = "# T\n"
            if any(rel == allowed_rel for allowed_rel, _ in MARKER_ALLOWLIST):
                content = '"""stub (skeleton)."""\n'
            (marker_root / rel).write_text(content, encoding="utf-8")
        marker_doc.write_text("# T\n\n当前状态：骨架占位。\n", encoding="utf-8")
        marker_problems = _rule_stale_markers(marker_root)
        if not any("骨架占位" in v and "AGENTS.md:3" in v for v in marker_problems):
            errors.append("self-test: stale marker not detected with file:line")
        marker_doc.write_text("# T\n", encoding="utf-8")
        if _rule_stale_markers(marker_root):
            errors.append("self-test: clean file flagged by marker rule")
        original_allowlist = dict(MARKER_ALLOWLIST)
        MARKER_ALLOWLIST.clear()
        MARKER_ALLOWLIST[(marker_doc.relative_to(marker_root).as_posix(), "(skeleton)")] = ""
        unjustified = _rule_stale_markers(marker_root)
        MARKER_ALLOWLIST.clear()
        MARKER_ALLOWLIST.update(original_allowlist)
        if not any("allowlist entry without justification" in v for v in unjustified):
            errors.append("self-test: unjustified allowlist entry not detected")

    return errors


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
