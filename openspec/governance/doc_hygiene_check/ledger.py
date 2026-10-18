"""Ledger, counter, hukou and placement helpers."""

from __future__ import annotations

from pathlib import Path
import markdown_fences
import re
import re as _re

from .constants import ADR_FILE_RE, BACKLOG_CLOSABLE_RE, BACKLOG_GRADUATION_PASSED_RE, BACKLOG_STATUS_FIELD_RE, INDEX_ROW_RE, MARKDOWN_LINK_RE, BACKLOG_FIX_REFERENCE_REQUIRED_STATUSES
from .scope import Scope


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


def _read_utf8(doc: Path) -> tuple[str | None, str | None]:
    """Return (text, None) or (None, problem) for an undecodable document."""
    try:
        return doc.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "not UTF-8 decodable"


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


def _ledger_surface_dir(scope: Scope, backlog: Path, surface: str) -> Path:
    # Zone split is data-driven: an archive surface is the `_`-prefixed one.
    if scope.regexes["archive_to_active"].match(surface):
        return backlog / "_archived" / surface
    return backlog / surface


def _ledger_work_files(scope: Scope, backlog: Path, surface: str) -> list[Path]:
    surface_dir = _ledger_surface_dir(scope, backlog, surface)
    if not surface_dir.is_dir():
        return []
    return sorted(p for p in surface_dir.glob("*.md") if p.name != "README.md")


def _allocated_numbers(
    scope: Scope, backlog: Path, archive_surface: str, active_surface: str | None, prefix: str
) -> list[int]:
    """Allocated numbers for one prefix across the archive zone and the
    active zone (the ledger rule: 已修复目录 ∪ 活跃目录). Single source for
    the counters check and the README declaration check."""
    allocated: list[int] = []
    index_file = backlog / "_archived" / archive_surface / "README.md"
    if index_file.is_file():
        body, _ = _read_utf8(index_file)
        body_lines = (body or "").splitlines()
        for line, fenced in zip(body_lines, markdown_fences.fence_flags(body_lines), strict=True):
            if fenced:
                continue  # an ID inside a fenced example allocates nothing
            if not line.lstrip().startswith("|"):
                continue  # skip the Next-ID declaration line itself
            for id_match in scope.regexes["next_id"].finditer(line):
                if id_match.group(1) == prefix:
                    allocated.append(int(id_match.group(2)))
    work_files = list(_ledger_work_files(scope, backlog, archive_surface))
    if active_surface:
        work_files.extend(_ledger_work_files(scope, backlog, active_surface))
    for work in work_files:
        for id_match in scope.regexes["next_id"].finditer(work.name):
            if id_match.group(1) == prefix:
                allocated.append(int(id_match.group(2)))
    return allocated


def _change_directory_names(root: Path) -> set[str]:
    """Every change name the repository knows: active directories and archived ones.

    Archived changes are renamed with a date prefix (``2026-10-17-<name>``), so a card
    written after the fact names the bare change and the prefix has to be tolerated.
    """
    changes = root / "openspec" / "changes"
    names = {p.name for p in changes.iterdir() if p.is_dir() and p.name != "archive"} \
        if changes.is_dir() else set()
    archive = changes / "archive"
    if archive.is_dir():
        names |= {p.name for p in archive.iterdir() if p.is_dir()}
    return names


def _card_fix_reference_problems(scope: Scope, backlog: Path) -> list[str]:
    """A card's ``> 修复:`` field names the change that fixed it, and that change exists.

    The field is required once the fix has landed (``已落修`` / ``已修``) and validated
    wherever it appears. No inference is made about the other statuses: a proposed but
    unlanded change is a normal flow, so neither requiring nor forbidding the field there
    would express anything true.
    """
    problems: list[str] = []
    known = _change_directory_names(scope.root)
    for surface in ("bugs", "_fixed_bugs"):
        for card in _ledger_work_files(scope, backlog, surface):
            text, decode_problem = _read_utf8(card)
            if text is None:
                problems.append(f"non-UTF-8 card, fix reference not checked: {surface}/{card.name}")
                continue
            matches = scope.regexes["fix_reference"].findall(text)
            status = BACKLOG_STATUS_FIELD_RE.search(text)
            # Older cards wrote the reference inside the status line's parenthesis
            # ("已修（<change>，archive …）"), which would otherwise hide the state from
            # this rule. Only this helper narrows the word: the shared field pattern keeps
            # its behaviour for the hukou check.
            status_word = _re.split(r"[（(]", status.group(1))[0].strip() if status else ""
            if not matches:
                if status_word in BACKLOG_FIX_REFERENCE_REQUIRED_STATUSES:
                    problems.append(
                        f"card in state {status_word!r} must declare its fixing change as "
                        f"'> 修复: <change-name>': {surface}/{card.name}"
                    )
                continue
            if len(matches) > 1:
                problems.append(f"card declares more than one 修复 reference: {surface}/{card.name}")
                continue
            name = matches[0]
            if not any(entry == name or entry.endswith(f"-{name}") for entry in known):
                problems.append(
                    f"card names a fixing change that does not exist: {name!r}: {surface}/{card.name}"
                )
    return problems


def _ledger_roster_problems(scope: Scope, backlog: Path) -> list[str]:
    """Every work item is indexed, every index row resolves, and every active card
    carries a valid hukou and residency.
    """
    problems: list[str] = []
    for surface in (*scope.surfaces["active"], *scope.surfaces["archive"]):
        surface_dir = _ledger_surface_dir(scope, backlog, surface)
        index = surface_dir / "README.md"
        if not surface_dir.is_dir():
            continue
        work_files = _ledger_work_files(scope, backlog, surface)
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
        block: list[str] = []
        blocks: list[list[str]] = []

        def _flush() -> None:
            if block:
                blocks.append(list(block))
                block.clear()

        index_lines = index_text.splitlines()
        for raw, fenced in zip(index_lines, markdown_fences.fence_flags(index_lines), strict=True):
            if fenced:
                continue  # fenced examples are not ledger rows
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

    return problems


def _ledger_counter_problems(scope: Scope, backlog: Path) -> list[str]:
    """The archived counters table matches the disk roster and the union-derived next ID.
    """
    problems: list[str] = []
    counters = backlog / scope.docs["counters_file"]
    if counters.is_file():
        counters_text, decode_problem = _read_utf8(counters)
        if counters_text is not None:
            for line in counters_text.splitlines():
                row = re.match(r"^\|\s*`([\w-]+?)/`\s*\|\s*(\d+)\s*\|\s*([^|]+)\|", line)
                if not row:
                    continue
                surface, declared_count, declared_next = row.group(1), int(row.group(2)), row.group(3).strip()
                disk_count = len(_ledger_work_files(scope, backlog, surface))
                if declared_count != disk_count:
                    problems.append(
                        f"counter mismatch in {scope.docs['counters_file']}: {surface} declares "
                        f"{declared_count} but disk holds {disk_count}"
                    )
                next_match = scope.regexes["next_id"].search(declared_next)
                if not next_match:
                    continue
                prefix, number = next_match.group(1), int(next_match.group(2))
                allocated = _allocated_numbers(scope, backlog, surface, scope.backlog_archive_to_active.get(surface), prefix)
                expected_next = (max(allocated) + 1) if allocated else 1
                if number != expected_next:
                    problems.append(
                        f"next-ID mismatch in {scope.docs['counters_file']}: {surface} declares "
                        f"{prefix}-{number:03d} but allocation implies {prefix}-{expected_next:03d}"
                    )

    # Next-ID declarations in the numbered ledger READMEs: at most one per file
    # and prefix, and the value must equal the ∪-derived next ID (BUG-002: a
    # duplicated stale declaration passed while the counters table alone stayed
    return problems
