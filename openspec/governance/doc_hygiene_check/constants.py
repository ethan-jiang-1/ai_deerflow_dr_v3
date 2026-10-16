"""Declarations the doc-hygiene guard reads: paths, budgets, markers, patterns."""

from __future__ import annotations

from pathlib import Path
import re
import re as _re


ADR_DIR = Path("deep_research_harness/docs/adr")


DOCS_TREE = Path("deep_research_harness/docs")


ADR_INDEX = ADR_DIR / "README.md"


BACKLOG_ROOT = Path("_backlog")


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


BACKLOG_ACTIVE_SURFACES: tuple[str, ...] = ("issues", "bugs")


BACKLOG_ARCHIVE_SURFACES: tuple[str, ...] = (
    "_fixed_bugs",
    "_suspended_bugs",
    "_settled_issues",
    "_suspended_issues",
)


BACKLOG_COUNTERS_FILE = "_archived/README.md"


BACKLOG_NEXT_ID_RE = re.compile(r"\b([A-Z]{3})-(\d{3})\b")


BACKLOG_ARCHIVE_TO_ACTIVE: dict[str, str] = {"_fixed_bugs": "bugs", "_settled_issues": "issues"}


BACKLOG_NUMBERED_SURFACES: tuple[str, ...] = ("issues", "bugs", "_fixed_bugs", "_settled_issues")


BACKLOG_NUMBERED_PREFIXES: dict[str, tuple[str, str]] = {
    "BUG": ("_fixed_bugs", "bugs"),
    "CLS": ("_settled_issues", "issues"),
}


BACKLOG_NEXT_ID_DECL_RE = re.compile(r"Next available \w+ ID:\s*([A-Z]{3})-(\d{3})")


BACKLOG_CARD_HUKOU_LINE_LIMIT = 12


BACKLOG_STATUS_FIELD_RE = re.compile(r"状态[:：]\s*([^\s｜|，,]+)")


BACKLOG_STATUS_VOCABULARY: dict[str, tuple[str, ...]] = {
    "issues": ("推敲中", "等人拍板"),
    "bugs": ("调查中", "修就绪", "已落修", "等人拍板", "待修"),
}


BACKLOG_GRADUATION_PASSED_RE = re.compile(r"毕业门[:：]\s*已过")


BACKLOG_CLOSABLE_RE = re.compile(r"可关闭[:：]\s*是")


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


_COUNT_SPECS_RE = _re.compile(r"(\d+)\s*个\s*能力")


_COUNT_ARCHIVE_RE = _re.compile(r"(\d+)\s*个\s*changes\s*归档")
