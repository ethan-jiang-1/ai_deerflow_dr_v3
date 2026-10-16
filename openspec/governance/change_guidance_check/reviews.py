"""Review-record validators for the three triggered review policies.

@impl CHA-001"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from .constants import (
    CONTROL_PLACEMENT_POLICY,
    CONTROL_PLACEMENT_POSTURES,
    CONTROL_PLACEMENT_REVIEW_COLUMNS,
    CONTROL_PLACEMENT_REVIEW_HEADING,
    NODE_AGENT_CLASSIFICATIONS,
    NODE_AGENT_REVIEW_COLUMNS,
    NODE_AGENT_REVIEW_HEADING,
    NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
    WORKFLOW_OUTCOME_REVIEW_COLUMNS,
    WORKFLOW_OUTCOME_REVIEW_HEADING,
    WORKFLOW_OUTCOME_REVIEW_POLICY,
)
from .helpers import (
    ContractViolation,
    _is_markdown_separator,
    _scoped_code,
    _section_after_heading,
    _single_markdown_table_lines,
    _table_cells,
)

def _review_section(
    container: str,
    *,
    heading: str,
    level: int,
    code: str,
    proposal_path: Path,
) -> str:
    expected_heading = f"{'#' * level} {heading}"
    matches = list(re.finditer(rf"^{re.escape(expected_heading)}\s*$", container, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            code,
            f"proposal selecting {heading!r} must contain exactly one {expected_heading!r}: "
            f"{proposal_path.as_posix()}",
        )
    return _section_after_heading(container, matches[0], maximum_level=level)


def _validate_workflow_outcome_review(
    section: str,
    proposal_path: Path,
    *,
    code_prefix: str,
) -> None:
    table_lines = [line for line in section.splitlines() if _table_cells(line) is not None]
    if len(table_lines) < 3:
        raise ContractViolation(
            _scoped_code(code_prefix, "workflow_outcome_review_shape_invalid"),
            f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r} needs a header, separator, and at least one row: "
            f"{proposal_path.as_posix()}",
        )
    header = _table_cells(table_lines[0])
    separator = _table_cells(table_lines[1])
    assert header is not None and separator is not None
    if header != WORKFLOW_OUTCOME_REVIEW_COLUMNS or not _is_markdown_separator(
        separator, WORKFLOW_OUTCOME_REVIEW_COLUMNS
    ):
        raise ContractViolation(
            _scoped_code(code_prefix, "workflow_outcome_review_shape_invalid"),
            f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if len(cells) != len(WORKFLOW_OUTCOME_REVIEW_COLUMNS) or any(not cell for cell in cells):
            raise ContractViolation(
                _scoped_code(code_prefix, "workflow_outcome_review_shape_invalid"),
                f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r} has an incomplete table row: {proposal_path.as_posix()}",
            )


def _validate_control_placement_review(
    section: str,
    proposal_path: Path,
    triggered_policies: tuple[str, ...],
    *,
    code_prefix: str,
) -> None:
    table_lines = _single_markdown_table_lines(section)
    if table_lines is None or len(table_lines) < 3:
        raise ContractViolation(
            _scoped_code(code_prefix, "control_placement_review_shape_invalid"),
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} needs exactly one header, separator, and at least one row: "
            f"{proposal_path.as_posix()}",
        )
    header = _table_cells(table_lines[0])
    separator = _table_cells(table_lines[1])
    assert header is not None and separator is not None
    if header != CONTROL_PLACEMENT_REVIEW_COLUMNS or not _is_markdown_separator(
        separator, CONTROL_PLACEMENT_REVIEW_COLUMNS
    ):
        raise ContractViolation(
            _scoped_code(code_prefix, "control_placement_review_shape_invalid"),
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )

    has_human_decision = False
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if (
            len(cells) != len(CONTROL_PLACEMENT_REVIEW_COLUMNS)
            or any(not cell for cell in cells)
            or cells == CONTROL_PLACEMENT_REVIEW_COLUMNS
            or _is_markdown_separator(cells, CONTROL_PLACEMENT_REVIEW_COLUMNS)
        ):
            raise ContractViolation(
                _scoped_code(code_prefix, "control_placement_review_shape_invalid"),
                f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} has an incomplete or duplicate table row: "
                f"{proposal_path.as_posix()}",
            )
        if cells[3] not in CONTROL_PLACEMENT_POSTURES:
            raise ContractViolation(
                _scoped_code(code_prefix, "control_placement_review_posture_invalid"),
                f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} uses an unsupported design posture {cells[3]!r}: "
                f"{proposal_path.as_posix()}",
            )
        has_human_decision = has_human_decision or cells[3] == "human-decision"

    if has_human_decision and "human-interaction-integrity" not in triggered_policies:
        raise ContractViolation(
            _scoped_code(code_prefix, "control_placement_human_interaction_policy_missing"),
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} with a human-decision row also requires "
            f"'human-interaction-integrity': {proposal_path.as_posix()}",
        )


def _validate_node_agent_review(section: str, proposal_path: Path, *, code_prefix: str) -> None:
    table_lines = _single_markdown_table_lines(section)
    if table_lines is None or len(table_lines) < 3:
        raise ContractViolation(
            _scoped_code(code_prefix, "node_agent_review_shape_invalid"),
            f"{NODE_AGENT_REVIEW_HEADING!r} needs exactly one header, separator, and at least one row: "
            f"{proposal_path.as_posix()}",
        )
    header = _table_cells(table_lines[0])
    separator = _table_cells(table_lines[1])
    assert header is not None and separator is not None
    if header != NODE_AGENT_REVIEW_COLUMNS or not _is_markdown_separator(separator, NODE_AGENT_REVIEW_COLUMNS):
        raise ContractViolation(
            _scoped_code(code_prefix, "node_agent_review_shape_invalid"),
            f"{NODE_AGENT_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if len(cells) != len(NODE_AGENT_REVIEW_COLUMNS) or any(not cell for cell in cells):
            raise ContractViolation(
                _scoped_code(code_prefix, "node_agent_review_shape_invalid"),
                f"{NODE_AGENT_REVIEW_HEADING!r} has an incomplete table row: {proposal_path.as_posix()}",
            )
        if cells[1] not in NODE_AGENT_CLASSIFICATIONS:
            raise ContractViolation(
                _scoped_code(code_prefix, "node_agent_review_classification_invalid"),
                f"{NODE_AGENT_REVIEW_HEADING!r} uses an unsupported classification {cells[1]!r}: "
                f"{proposal_path.as_posix()}",
            )


_ReviewValidator = Callable[[str, Path, tuple[str, ...], int, str], None]


def _validate_control_placement_review_record(
    body: str, proposal_path: Path, triggered_policies: tuple[str, ...], level: int, prefix: str
) -> None:
    _validate_control_placement_review(body, proposal_path, triggered_policies, code_prefix=prefix)


def _validate_node_agent_review_record(
    body: str, proposal_path: Path, triggered_policies: tuple[str, ...], level: int, prefix: str
) -> None:
    _validate_node_agent_review(body, proposal_path, code_prefix=prefix)


def _validate_workflow_outcome_review_record(
    body: str, proposal_path: Path, triggered_policies: tuple[str, ...], level: int, prefix: str
) -> None:
    _validate_workflow_outcome_review(body, proposal_path, code_prefix=prefix)


# Triggered policy -> (required record heading, violation-code suffix, validator).
# Adding a review policy is one row here plus its validator; the dispatch below
# never grows another branch.
_REVIEW_RECORDS: tuple[tuple[str, str, str, _ReviewValidator], ...] = (
    (
        CONTROL_PLACEMENT_POLICY,
        "Control Placement Review",
        "control_placement_review_missing",
        _validate_control_placement_review_record,
    ),
    (
        NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
        "Node Agent Review",
        "node_agent_review_missing",
        _validate_node_agent_review_record,
    ),
    (
        WORKFLOW_OUTCOME_REVIEW_POLICY,
        "Workflow Outcome Review",
        "workflow_outcome_review_missing",
        _validate_workflow_outcome_review_record,
    ),
)


def _validate_selected_policy_reviews(
    review_container: str,
    triggered_policies: tuple[str, ...],
    proposal_path: Path,
    *,
    review_level: int,
    code_prefix: str,
) -> None:
    """Validate the record each triggered review policy requires.

    Declaration order in ``_REVIEW_RECORDS`` is the reporting order, so a
    proposal missing two records reports the first one in that order — the order
    the hand-written branches used.
    """
    for policy, heading, code_suffix, validator in _REVIEW_RECORDS:
        if policy not in triggered_policies:
            continue
        section = _review_section(
            review_container,
            heading=heading,
            level=review_level,
            code=_scoped_code(code_prefix, code_suffix),
            proposal_path=proposal_path,
        )
        validator(section, proposal_path, triggered_policies, review_level, code_prefix)
