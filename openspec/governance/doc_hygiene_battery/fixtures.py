"""Fixture builders: skeleton trees, one per known violation."""

from __future__ import annotations

from pathlib import Path

from doc_hygiene_check import (
    ADR_INDEX,
    BACKLOG_ROOT,
    BACKLOG_UNDERSCORE_DIRS,
    DOC_BUDGETS,
    DOC_LAYER_DOCS,
    ENTRY_DOCS,
    LINKED_ASSET_DOCS,
    MARKER_ALLOWLIST,
    STALE_MARKER_FILES,
)



# The fence fixtures' snippets (they belong with the builders that use them).
_FENCE_ORPHAN_ROW = "| CLS-777 | 2026-10-01 | [x](x) | orphan row |"
_FENCE_LEDGER_README = "_backlog/_archived/_settled_issues/README.md"

def _write(root: Path, rel: str, content: str) -> None:
    doc = root / rel
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(content, encoding="utf-8")


def _backlog_dirs(root: Path) -> None:
    for name in BACKLOG_UNDERSCORE_DIRS:
        (root / BACKLOG_ROOT / name).mkdir(parents=True, exist_ok=True)


def build_clean_fixture(root: Path) -> None:
    """Every registered document exists with a valid self link.

    Derived from the declaration tables, so the fixture follows a future scope
    change instead of rotting. The ADR layer is built only when the registered
    scope declares it; with no ``docs/adr/`` entry the directory stays absent and
    ``_rule_adr_index`` is dormant by its dir-existence guard.
    """
    for rel in ENTRY_DOCS:
        _write(root, rel, f"# T\n\n[self]({rel.rsplit('/', 1)[-1]})\n")
    for rel in DOC_LAYER_DOCS:
        _write(root, rel, f"# T\n\n[self]({rel.rsplit('/', 1)[-1]})\n")
    for rel in LINKED_ASSET_DOCS:
        _write(root, rel, f"# T\n\n[self]({rel.rsplit('/', 1)[-1]})\n")
    _backlog_dirs(root)
    _write(
        root,
        (BACKLOG_ROOT / "README.md").as_posix(),
        "# T\n\n[self](README.md)\n"
        + "".join(f"- {name}\n" for name in BACKLOG_UNDERSCORE_DIRS),
    )
    # Budget-managed and marker-managed files off the entry chain get minimal
    # stubs: a missing managed path fails loudly by design. An allowlisted marker
    # must stay present in its stub, or the allowlist honestly reports dangling.
    for rel in (*DOC_BUDGETS, *STALE_MARKER_FILES):
        if not (root / rel).is_file():
            allowlisted = any(rel == allowed_rel for allowed_rel, _ in MARKER_ALLOWLIST)
            _write(root, rel, '"""stub (skeleton)."""\n' if allowlisted else "# T\n")


def _is_clean_fixture(root: Path) -> None:
    build_clean_fixture(root)


def _adr_index_orphan(root: Path) -> None:
    build_clean_fixture(root)
    _write(
        root,
        ADR_INDEX.as_posix(),
        "# ADR Index\n\n| 编号 | 一句话 | 生命周期 |\n|---|---|---|\n| 9999 | b | current |\n",
    )


def _broken_entry_chain_link(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "deep_research_harness/README.md", "# T\n\nsee [gone.md](gone.md)\n")


def _dangling_trigger_index_home(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "_backlog/triggers.md", "# triggers\n\n[owner](no-such-owner.md)\n")


def _missing_newline_entry_chain(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "openspec/README.md", "# no newline")


def _broken_docs_layer_link(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "deep_research_harness/docs/local-operations.md", "# T\n\nsee [gone.md](gone.md)\n")


def _broken_asset_doc_link(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "deep_research_harness/tests/README.md", "# tests\n\nsee [gone.md](gone.md)\n")


def _resolvable_asset_doc_link(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "deep_research_harness/tests/README.md", "# T\n\n[self](README.md)\n")


def _docs_layer_missing_newline(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "deep_research_harness/docs/testing-and-evaluation.md", "# no newline")


def _docs_layer_non_utf8(root: Path) -> None:
    build_clean_fixture(root)
    (root / "deep_research_harness/docs/control-map.md").write_bytes(b"\xff\xfe binary")


def _unregistered_docs_markdown(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "deep_research_harness/docs/zz-unregistered.md", "# extra\n")


def _undeclared_backlog_dir(root: Path) -> None:
    build_clean_fixture(root)
    (root / BACKLOG_ROOT / "_zz-undeclared").mkdir(parents=True, exist_ok=True)


def _undocumented_backlog_dir(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, (BACKLOG_ROOT / "README.md").as_posix(), "# T\n\n[self](README.md)\n")


def _over_budget_resident_doc(root: Path) -> None:
    build_clean_fixture(root)
    _write(root, "AGENTS.md", "# T\n\n" + "x" * (DOC_BUDGETS["AGENTS.md"] + 1) + "\n")


def _missing_managed_budget_path(root: Path) -> None:
    build_clean_fixture(root)
    (root / "CLAUDE.md").unlink()


def _ledger_repo(root: Path) -> None:
    """Ledger fixture with index row, file roster, and counters deliberately drifted."""
    for surface in ("issues", "_archived/_settled_issues"):
        (root / "_backlog" / surface).mkdir(parents=True, exist_ok=True)
    _write(root, "_backlog/issues/2026-10-01-demo.md", "# issue\n")
    _write(root, "_backlog/issues/README.md", "# Issues\n\n（空）\n")
    _write(
        root,
        "_backlog/_archived/_settled_issues/README.md",
        "# Settled\n\n| ID | Date | File | Summary |\n|---|---|---|---|\n"
        "| CLS-001 | 2026-10-01 | [2026-10-01-gone.md](2026-10-01-gone.md) | x |\n\n"
        "**Next available issue ID: CLS-002**\n",
    )
    _write(
        root,
        "_backlog/_archived/README.md",
        "| 归档目录 | 数量 | Next ID |\n|---|---|---|\n"
        "| `_fixed_bugs/` | 0 | BUG-001 |\n| `_settled_issues/` | 1 | CLS-002 |\n",
    )


def _allocated_prefix_repo(root: Path) -> None:
    """Numbered ledger where an active card already reserves its number (BUG-002)."""
    _write(
        root,
        "_backlog/bugs/BUG-002-active-hold.md",
        "# BUG-002: x\n\n> 严重级别: P2 | 发现: 2026-10-10 | 状态: 活跃\n\n## 症状\ns\n",
    )
    _write(
        root,
        "_backlog/bugs/README.md",
        "# Active bugs\n\n| Bug | 标题 | 发现 | 状态 |\n|---|---|---|---|\n"
        "| [BUG-002-active-hold.md](BUG-002-active-hold.md) | x | 2026-10-10 | 活跃 |\n",
    )
    _write(root, "_backlog/_archived/_fixed_bugs/BUG-001-fixed.md", "# BUG-001: x\n")
    _write(
        root,
        "_backlog/_archived/_fixed_bugs/README.md",
        "# Fixed\n\n| ID | Date | Title |\n|---|---|---|\n"
        "| BUG-001 | 2026-10-09 | [BUG-001-fixed.md](BUG-001-fixed.md) | x |\n\n"
        "**Next available bug ID: BUG-002**\n",
    )
    _write(
        root,
        "_backlog/_archived/README.md",
        "| 归档目录 | 数量 | Next ID |\n|---|---|---|\n| `_fixed_bugs/` | 1 | BUG-002 |\n",
    )


def _archive_only_next_id(root: Path) -> None:
    _allocated_prefix_repo(root)


def _union_consistent_next_id(root: Path) -> None:
    _allocated_prefix_repo(root)
    _write(
        root,
        "_backlog/_archived/README.md",
        "| 归档目录 | 数量 | Next ID |\n|---|---|---|\n| `_fixed_bugs/` | 1 | BUG-003 |\n",
    )


def _declaration_repo(root: Path) -> None:
    """Numbered ledger with two README declarations for one prefix (one stale)."""
    _write(
        root,
        "_backlog/bugs/BUG-002-active-hold.md",
        "# BUG-002: x\n\n> 严重级别: P2 | 发现: 2026-10-10 | 状态: 活跃\n\n## 症状\ns\n",
    )
    _write(
        root,
        "_backlog/bugs/README.md",
        "# Active bugs\n\n| Bug | 标题 | 发现 | 状态 |\n|---|---|---|---|\n"
        "| [BUG-002-active-hold.md](BUG-002-active-hold.md) | x | 2026-10-10 | 活跃 |\n"
        "\n**Next available bug ID: BUG-003**\n",
    )
    _write(root, "_backlog/_archived/_fixed_bugs/BUG-001-fixed.md", "# BUG-001: x\n")
    _write(
        root,
        "_backlog/_archived/_fixed_bugs/README.md",
        "# Fixed\n\n| ID | Date | Title |\n|---|---|---|\n"
        "| BUG-001 | 2026-10-09 | [BUG-001-fixed.md](BUG-001-fixed.md) | x |\n"
        "\n**Next available bug ID: BUG-002**\n**Next available bug ID: BUG-003**\n",
    )
    _write(
        root,
        "_backlog/_archived/README.md",
        "| 归档目录 | 数量 | Next ID |\n|---|---|---|\n| `_fixed_bugs/` | 1 | BUG-003 |\n",
    )


def _duplicate_next_id_decl(root: Path) -> None:
    _declaration_repo(root)


def _disagreeing_next_id_decl(root: Path) -> None:
    _declaration_repo(root)


def _consistent_single_decl(root: Path) -> None:
    _declaration_repo(root)


def _placement_repo(root: Path) -> None:
    """A work-item row separated from its table header by a blank line and a fence."""
    _write(root, "_backlog/_archived/_settled_issues/2026-10-01-here.md", "# plan\n")
    _write(
        root,
        "_backlog/_archived/_settled_issues/README.md",
        "# Closed\n\n```markdown\n| Plan | 一句话 |\n|------|--------|\n```\n"
        "| CLS-001 | 2026-10-01 | [2026-10-01-here.md](2026-10-01-here.md) | ok |\n\n"
        "**Next available issue ID: CLS-002**\n",
    )


def _ledger_row_placement(root: Path) -> None:
    _placement_repo(root)


def _contiguous_table(root: Path) -> None:
    _write(root, "_backlog/_archived/_contiguous_issues/2026-10-01-here.md", "# plan\n")
    _write(
        root,
        "_backlog/_archived/_contiguous_issues/README.md",
        "# Closed\n\n| ID | Date | File | Summary |\n|---|---|---|---|\n"
        "| CLS-001 | 2026-10-01 | [2026-10-01-here.md](2026-10-01-here.md) | ok |\n",
    )


def _hukou_repo(root: Path) -> None:
    """Active issues carrying every hukou/residency shape, plus the mis-kill card.

    The roster is empty on purpose: unindexed-card problems are expected, and the
    mis-kill check reads hukou-specific problems only.
    """
    _write(root, "_backlog/issues/README.md", "# Issues\n\n（空）\n")
    cards = {
        "2026-10-01-no-hukou.md": "# Issue: no hukou\n",
        "2026-10-02-bad-word.md": "> 立卡: 2026-10-02 ｜ 状态: 已结 ｜ 毕业门: 未过 ｜ 可关闭: 否\n",
        "2026-10-03-graduated.md": "> 立卡: 2026-10-03 ｜ 状态: 推敲中 ｜ 毕业门: 已过 ｜ 可关闭: 否\n",
        "2026-10-04-closable.md": "> 立卡: 2026-10-04 ｜ 状态: 等人拍板 ｜ 毕业门: 未过 ｜ 可关闭: 是\n",
        "2026-10-05-awaiting-human.md": (
            "> 立卡: 2026-10-05 ｜ 状态: 等人拍板 ｜ 毕业门: 未过 ｜ 可关闭: 否\n"
            "\n## 落地关联\n\nS1+S2 已交付，全链路绿。\n"
        ),
    }
    for name, body in cards.items():
        _write(root, f"_backlog/issues/{name}", body)


def _hukou_missing_field(root: Path) -> None:
    _hukou_repo(root)


def _hukou_bad_word(root: Path) -> None:
    _hukou_repo(root)


def _hukou_graduated(root: Path) -> None:
    _hukou_repo(root)


def _hukou_closable(root: Path) -> None:
    _hukou_repo(root)


def _hukou_miskill_awaiting(root: Path) -> None:
    _hukou_repo(root)


def _vocab_repo(root: Path) -> None:
    """Post-rename bug vocabulary shapes: old word, new word, arbitrary word."""
    _write(root, "_backlog/bugs/README.md", "# Bugs\n\n（空）\n")
    for name, word in (
        ("BUG-009-old-active.md", "活跃"),
        ("BUG-010-fix-ready.md", "修就绪"),
        ("BUG-011-bad-word.md", "乱写"),
    ):
        _write(
            root,
            f"_backlog/bugs/{name}",
            f"# BUG-009: x\n\n> 严重级别: P2 | 发现: 2026-10-12 | 状态: {word}\n\n## 症状\ns\n",
        )


def _vocab_old_active(root: Path) -> None:
    _vocab_repo(root)


def _vocab_bad_word(root: Path) -> None:
    _vocab_repo(root)


def _vocab_fix_ready_miskill(root: Path) -> None:
    _vocab_repo(root)


def _counts_repo(root: Path) -> None:
    (root / "openspec/specs/alpha").mkdir(parents=True, exist_ok=True)
    (root / "openspec/specs/beta").mkdir(parents=True, exist_ok=True)
    (root / "openspec/changes/archive/2026-01-01-one").mkdir(parents=True, exist_ok=True)


def _root_count_drift(root: Path) -> None:
    _counts_repo(root)
    _write(root, "README.md", "> specs 主干 5 个能力落地、7 个 changes 归档。\n")


def _root_count_matching(root: Path) -> None:
    _counts_repo(root)
    _write(root, "README.md", "> specs 主干 2 个能力落地、1 个 changes 归档。\n")


def _root_count_unpinned(root: Path) -> None:
    _counts_repo(root)
    _write(root, "README.md", "> 没有声明计数的行。\n")


def _marker_repo(root: Path, allowlist: dict[tuple[str, str], str]) -> None:
    """Declared stale-marker files as clean stubs, plus one re-introduced marker.

    The allowlist is a parameter, never a module-global mutation: the case that
    needs an unjustified entry passes its own table instead of editing the
    declaration the checker ships with. Stubs stay tiny so the budget rule (which
    also manages AGENTS.md) has nothing to report here.
    """
    for rel in STALE_MARKER_FILES:
        allowlisted = any(rel == allowed_rel for allowed_rel, _ in allowlist)
        _write(root, rel, '"""stub (skeleton)."""\n' if allowlisted else "# T\n")
    _write(root, "AGENTS.md", "# T\n\n当前状态：骨架占位。\n")


def _stale_marker_detected(root: Path) -> None:
    _marker_repo(root, dict(MARKER_ALLOWLIST))


def _stale_marker_clean(root: Path) -> None:
    _marker_repo(root, dict(MARKER_ALLOWLIST))
    _write(root, "AGENTS.md", "# T\n")


def _allowlist_unjustified(root: Path) -> None:
    # Tree for the unjustified-entry control: the shipped allowlist's file is clean
    # (no marker text, so its entry cannot dangle) and an extra managed file carries
    # the marker while its own entry has an empty justification.
    _marker_repo(root, {})
    _write(root, "AGENTS.md", "# T\n\n当前状态：骨架占位。\n")


def _append_to_ledger_readme(root: Path, snippet: str) -> None:
    _ledger_repo(root)
    target = root / _FENCE_LEDGER_README
    target.write_text(target.read_text(encoding="utf-8") + "\n" + snippet + "\n", encoding="utf-8")


def _fence_indented_opener_keeps_checking(root: Path) -> None:
    """Four spaces is an indented code block (CommonMark 4.4), not a fence opener.

    The genuine placement defect below it must still be reported: this is the
    mis-kill direction, where a checker silently stops checking.
    """
    _append_to_ledger_readme(root, "    ```\n\n" + _FENCE_ORPHAN_ROW)


def _tilde_fenced_row_is_not_a_ledger_row(root: Path) -> None:
    _append_to_ledger_readme(root, "~~~\n" + _FENCE_ORPHAN_ROW + "\n~~~")


def _fenced_example_id_does_not_allocate(root: Path) -> None:
    _append_to_ledger_readme(root, "~~~\n" + _FENCE_ORPHAN_ROW + "\n~~~")


def _fenced_marker_quote_is_not_stale(root: Path) -> None:
    build_clean_fixture(root)
    doc = root / "AGENTS.md"
    doc.write_text(doc.read_text(encoding="utf-8") + "\n~~~\n骨架占位\n~~~\n", encoding="utf-8")
