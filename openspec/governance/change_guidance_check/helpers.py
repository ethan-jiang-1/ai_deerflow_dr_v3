"""Shared primitives: the violation type, file reading, markdown and field rules.

@impl CHA-001"""

from __future__ import annotations

import re

import markdown_fences
from pathlib import Path

from change_guidance_kernel import (
    comma_separated_values as kernel_comma_separated_values,
    field_value as kernel_field_value,
    table_cells as kernel_table_cells,
)

from .constants import LEGACY_TRIGGERED_POLICIES_FIELD, SEAM_CLASSIFICATION_FIELD, SEAM_CLASSIFICATIONS

class ContractViolation(Exception):
    """A deterministic charter navigation violation."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _read_file(root: Path, relative_path: Path, *, code: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise ContractViolation(code, f"required file is missing: {relative_path.as_posix()}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractViolation(code, f"cannot read {relative_path.as_posix()}: {exc}") from exc


def _require_fragment(text: str, fragment: str, *, code: str, detail: str) -> None:
    if fragment not in text:
        raise ContractViolation(code, detail)


def _line_count(text: str) -> int:
    return len(text.splitlines())

def _without_fences(text: str) -> str:
    """The same text with fenced code blocks blanked out.

    Regex-based parses (heading counts, table-line collection) can then run unchanged:
    a fenced example can no longer masquerade as structure, and the line count — hence
    every reported line number — is preserved (BUG-006).
    """
    return markdown_fences.strip_fenced_code_blocks(text)


def _section_after_heading(proposal: str, match: re.Match[str], *, maximum_level: int) -> str:
    """The text up to the next heading, ignoring headings inside fenced code blocks.

    The section end used to be found with a bare regex, so a fenced example containing
    ``## Something`` truncated the section early and every field after it looked
    missing (BUG-006). This walks the lines instead, so the returned slice still comes
    from the original text.
    """
    start = match.end()
    tail = proposal[start:]
    heading = re.compile(rf"^#{{1,{maximum_level}}} (?!#)")
    lines = tail.split("\n")
    offset = 0
    for line, fenced in zip(lines, markdown_fences.fence_flags(lines), strict=True):
        if not fenced and heading.match(line):
            return tail[:offset]
        offset += len(line) + 1
    return tail


def _field_value(section: str, field: str) -> str | None:
    return kernel_field_value(section, field)


def _scoped_code(code_prefix: str, suffix: str) -> str:
    if code_prefix == "program.workstream":
        return f"program.workstream_{suffix}"
    return f"{code_prefix}.{suffix}"


def _validate_required_fields(
    section: str,
    fields: tuple[str, ...],
    *,
    code: str,
    record_name: str,
    proposal_path: Path,
) -> None:
    for field in fields:
        if _field_value(section, field) is None:
            raise ContractViolation(
                code,
                f"{record_name} field {field!r} is missing or empty: {proposal_path.as_posix()}",
            )


def _validate_legacy_triggered_policies_field(
    section: str,
    *,
    code: str,
    record_name: str,
    proposal_path: Path,
) -> None:
    pattern = re.compile(rf"^- \*\*{re.escape(LEGACY_TRIGGERED_POLICIES_FIELD)}:\*\*", re.MULTILINE)
    if pattern.search(section):
        raise ContractViolation(
            code,
            f"{record_name} uses the retired field {LEGACY_TRIGGERED_POLICIES_FIELD!r}: "
            f"{proposal_path.as_posix()}",
        )


def _validate_seam_classification(
    section: str,
    *,
    code_prefix: str,
    record_name: str,
    proposal_path: Path,
) -> None:
    seam_value = _field_value(section, SEAM_CLASSIFICATION_FIELD)
    if seam_value is None:
        raise ContractViolation(
            _scoped_code(code_prefix, "field_missing"),
            f"{record_name} field {SEAM_CLASSIFICATION_FIELD!r} is missing or empty: "
            f"{proposal_path.as_posix()}",
        )
    value, _, rationale = seam_value.partition(" ")
    if value not in SEAM_CLASSIFICATIONS:
        raise ContractViolation(
            _scoped_code(code_prefix, "seam_classification_invalid"),
            f"{SEAM_CLASSIFICATION_FIELD!r} must be exactly one of "
            f"{', '.join(sorted(SEAM_CLASSIFICATIONS))}, written bare: {proposal_path.as_posix()}",
        )
    if not rationale.strip():
        raise ContractViolation(
            _scoped_code(code_prefix, "seam_classification_rationale_missing"),
            f"{SEAM_CLASSIFICATION_FIELD!r} must give a short rationale after the value: "
            f"{proposal_path.as_posix()}",
        )


def _table_cells(line: str) -> tuple[str, ...] | None:
    return kernel_table_cells(line)


def _is_markdown_separator(cells: tuple[str, ...], columns: tuple[str, ...]) -> bool:
    return len(cells) == len(columns) and all(
        re.fullmatch(r":?-{3,}:?", cell) is not None for cell in cells
    )


def _single_markdown_table_lines(section: str) -> list[str] | None:
    table_blocks: list[list[str]] = []
    current_block: list[str] = []
    for line in section.splitlines():
        if _table_cells(line) is None:
            if current_block:
                table_blocks.append(current_block)
                current_block = []
            continue
        current_block.append(line)
    if current_block:
        table_blocks.append(current_block)
    return table_blocks[0] if len(table_blocks) == 1 else None


def _comma_separated_values(
    value: str,
    *,
    invalid_code: str,
    duplicate_code: str,
    label: str,
    proposal_path: Path,
    validator: re.Pattern[str] | None = None,
) -> tuple[str, ...]:
    raw_values = tuple(item.strip() for item in value.split(","))
    if raw_values and not any(not item for item in raw_values) and len(raw_values) != len(set(raw_values)):
        raise ContractViolation(
            duplicate_code,
            f"{label} must not repeat an identifier: {proposal_path.as_posix()}",
        )
    values = kernel_comma_separated_values(value)
    if values is None or (validator is not None and any(validator.fullmatch(item) is None for item in values)):
        raise ContractViolation(
            invalid_code,
            f"{label} must be a non-empty comma-separated list: {proposal_path.as_posix()}",
        )
    return values
