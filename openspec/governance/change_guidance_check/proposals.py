"""Proposal-side validation: authoring pointer, focus cards, programs, changes.

@impl CHA-001"""

from __future__ import annotations

import re
from pathlib import Path

from .constants import (
    APPLY_GUIDANCE,
    ARCHIVE_GUIDANCE,
    CHANGES_ROOT,
    CLOSEOUT_EVIDENCE_GUIDANCE,
    CONFIG_PATH,
    CONTEXT_EXPANSION_SENTENCE,
    CONTROL_PLACEMENT_POLICY,
    CONTROL_PLACEMENT_REVIEW_HEADING,
    CONTROL_PLACEMENT_TASKS_RULE,
    FOCUS_FIELDS,
    FOCUS_HEADING,
    LEGACY_TRIGGERED_POLICIES_FIELD,
    NODE_AGENT_REVIEW_HEADING,
    NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
    OPERATION_GUIDANCE_ADVISORY_BOUNDARY,
    PROGRAM_FOCUS_FIELDS,
    PROGRAM_FOCUS_HEADING,
    PROGRAM_ROUTE_ANCHOR,
    TRIGGERED_POLICIES_FIELD,
    WORKFLOW_OUTCOME_REVIEW_POLICY,
    WORKSTREAM_FIELDS,
    WORKSTREAM_ID_PATTERN,
)
from .helpers import (
    ContractViolation,
    _comma_separated_values,
    _field_value,
    _read_file,
    _require_fragment,
    _scoped_code,
    _section_after_heading,
    _validate_legacy_triggered_policies_field,
    _validate_required_fields,
    _validate_seam_classification,
)
from .registry import POLICY_REGISTRY, WorkstreamFocus
from .reviews import _validate_selected_policy_reviews
from .tasks import _validate_change_tasks

def _validate_authoring_pointer(root: Path) -> None:
    config = _read_file(root, CONFIG_PATH, code="config.missing")
    if LEGACY_TRIGGERED_POLICIES_FIELD in config:
        raise ContractViolation(
            "config.legacy_triggered_policies_rule_present",
            f"OpenSpec configuration uses the retired field {LEGACY_TRIGGERED_POLICIES_FIELD!r}: "
            f"{CONFIG_PATH.as_posix()}",
        )
    _require_fragment(
        config,
        "openspec/change-guidance/README.md",
        code="config.charter_pointer_missing",
        detail=f"OpenSpec configuration lacks the Change Guidance pointer: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        FOCUS_HEADING,
        code="config.focus_rule_missing",
        detail=f"OpenSpec configuration lacks the Focus Card rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        FOCUS_FIELDS[0],
        code="config.focus_rule_missing",
        detail=f"OpenSpec configuration lacks the primary-module field: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        TRIGGERED_POLICIES_FIELD,
        code="config.triggered_policies_rule_missing",
        detail=f"OpenSpec configuration lacks the triggered-policy rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTROL_PLACEMENT_POLICY,
        code="config.control_placement_review_rule_missing",
        detail=f"OpenSpec configuration lacks the control-placement review rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTROL_PLACEMENT_REVIEW_HEADING,
        code="config.control_placement_review_rule_missing",
        detail=f"OpenSpec configuration lacks the Control Placement Review record rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTROL_PLACEMENT_TASKS_RULE,
        code="config.control_placement_task_rule_missing",
        detail=f"OpenSpec configuration lacks the control-placement task obligation: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        "only when the selected proposal declares it",
        code="config.operation_guidance_selection_boundary_missing",
        detail=(
            "OpenSpec operation guidance must limit control-placement review to the selected proposal: "
            f"{CONFIG_PATH.as_posix()}"
        ),
    )
    _require_fragment(
        config,
        APPLY_GUIDANCE,
        code="config.operation_apply_guidance_missing",
        detail=f"OpenSpec configuration lacks the apply operation guidance: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        ARCHIVE_GUIDANCE,
        code="config.operation_archive_guidance_missing",
        detail=f"OpenSpec configuration lacks the archive operation guidance: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        OPERATION_GUIDANCE_ADVISORY_BOUNDARY,
        code="config.operation_guidance_advisory_boundary_missing",
        detail=f"OpenSpec operation guidance lacks its advisory boundary: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CLOSEOUT_EVIDENCE_GUIDANCE,
        code="config.closeout_evidence_guidance_missing",
        detail=(
            "OpenSpec operation guidance lacks the caller-declared committed-range route: "
            f"{CONFIG_PATH.as_posix()}"
        ),
    )
    _require_fragment(
        config,
        WORKFLOW_OUTCOME_REVIEW_POLICY,
        code="config.workflow_outcome_review_rule_missing",
        detail=f"OpenSpec configuration lacks the workflow-outcome review rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
        code="config.node_agent_workflow_integrity_rule_missing",
        detail=(
            "OpenSpec configuration lacks the node-agent workflow-integrity rule: "
            f"{CONFIG_PATH.as_posix()}"
        ),
    )
    _require_fragment(
        config,
        NODE_AGENT_REVIEW_HEADING,
        code="config.node_agent_workflow_integrity_rule_missing",
        detail=f"OpenSpec configuration lacks the Node Agent Review record rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTEXT_EXPANSION_SENTENCE,
        code="config.context_expansion_rule_missing",
        detail=f"OpenSpec configuration lacks its context-expansion rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        PROGRAM_ROUTE_ANCHOR,
        code="config.program_route_missing",
        detail=f"OpenSpec configuration lacks the bounded-program route: {CONFIG_PATH.as_posix()}",
    )


def _triggered_policies(
    root: Path,
    focus_section: str,
    proposal_path: Path,
    *,
    code_prefix: str = "focus",
    record_name: str = "Focus Card",
) -> tuple[str, ...]:
    value = _field_value(focus_section, TRIGGERED_POLICIES_FIELD)
    if value is None:
        raise ContractViolation(
            _scoped_code(code_prefix, "field_missing"),
            f"{record_name} field {TRIGGERED_POLICIES_FIELD!r} is missing or empty: {proposal_path.as_posix()}",
        )

    field_pattern = re.compile(
        rf"^- \*\*{re.escape(TRIGGERED_POLICIES_FIELD)}:\*\*[ \t]*(?P<value>\S[^\n]*)$",
        re.MULTILINE,
    )
    match = field_pattern.search(focus_section)
    assert match is not None
    following_line = next(
        (line for line in focus_section[match.end() :].splitlines() if line.strip()),
        "",
    )
    if following_line and following_line[0].isspace():
        raise ContractViolation(
            _scoped_code(code_prefix, "triggered_policies_continuation_invalid"),
            f"{TRIGGERED_POLICIES_FIELD!r} must be a single-line comma-separated list: "
            f"{proposal_path.as_posix()}",
        )

    if value == "none":
        raise ContractViolation(
            _scoped_code(code_prefix, "triggered_policies_rationale_missing"),
            f"{TRIGGERED_POLICIES_FIELD!r} must give a short rationale after 'none:': {proposal_path.as_posix()}",
        )
    if value.startswith("none:"):
        if not value.removeprefix("none:").strip():
            raise ContractViolation(
                _scoped_code(code_prefix, "triggered_policies_rationale_missing"),
                f"{TRIGGERED_POLICIES_FIELD!r} must give a short rationale after 'none:': "
                f"{proposal_path.as_posix()}",
            )
        return ()

    policies = tuple(policy.strip() for policy in value.split(","))
    if not policies or any(not policy or policy not in POLICY_REGISTRY for policy in policies):
        raise ContractViolation(
            _scoped_code(code_prefix, "triggered_policy_unknown"),
            f"{TRIGGERED_POLICIES_FIELD!r} must list canonical policy names or 'none: <rationale>': "
            f"{proposal_path.as_posix()}",
        )
    for policy in policies:
        document = POLICY_REGISTRY[policy]
        _read_file(
            root,
            document.path,
            code=_scoped_code(code_prefix, "triggered_policy_document_missing"),
        )
    return policies


def _workstream_sections(proposal: str, program_match: re.Match[str], proposal_path: Path) -> tuple[WorkstreamFocus, ...]:
    matches = list(re.finditer(r"^### Workstream Focus:(?P<stable_id>[^\n]*)$", proposal, flags=re.MULTILINE))
    if len(matches) < 2:
        raise ContractViolation(
            "program.workstream_count_invalid",
            f"Program Focus needs at least two Workstream Focus records: {proposal_path.as_posix()}",
        )
    if any(match.start() < program_match.end() for match in matches):
        raise ContractViolation(
            "program.mode_invalid",
            f"Workstream Focus records must follow {PROGRAM_FOCUS_HEADING!r}: {proposal_path.as_posix()}",
        )

    workstreams: list[WorkstreamFocus] = []
    stable_ids: set[str] = set()
    for match in matches:
        raw_stable_id = match.group("stable_id")
        stable_id = raw_stable_id.strip()
        if not raw_stable_id.startswith(" ") or WORKSTREAM_ID_PATTERN.fullmatch(stable_id) is None:
            raise ContractViolation(
                "program.workstream_id_invalid",
                f"Workstream Focus has an invalid stable ID {stable_id!r}: {proposal_path.as_posix()}",
            )
        if stable_id in stable_ids:
            raise ContractViolation(
                "program.workstream_id_duplicate",
                f"Workstream Focus repeats stable ID {stable_id!r}: {proposal_path.as_posix()}",
            )
        stable_ids.add(stable_id)
        workstreams.append(
            WorkstreamFocus(
                stable_id=stable_id,
                section=_section_after_heading(proposal, match, maximum_level=3),
            )
        )
    return tuple(workstreams)


def _validate_program_proposal(root: Path, proposal: str, proposal_path: Path) -> None:
    program_matches = list(re.finditer(r"^## Program Focus\s*$", proposal, flags=re.MULTILINE))
    if len(program_matches) != 1:
        raise ContractViolation(
            "program.mode_invalid",
            f"program proposal must contain exactly one {PROGRAM_FOCUS_HEADING!r}: {proposal_path.as_posix()}",
        )
    program_section = _section_after_heading(proposal, program_matches[0], maximum_level=3)
    _validate_required_fields(
        program_section,
        PROGRAM_FOCUS_FIELDS,
        code="program.field_missing",
        record_name="Program Focus",
        proposal_path=proposal_path,
    )
    program_values = {
        field: _field_value(program_section, field)
        for field in PROGRAM_FOCUS_FIELDS
    }
    assert all(value is not None for value in program_values.values())
    budget = _comma_separated_values(
        program_values["Candidate / obligation budget"] or "",
        invalid_code="program.candidate_budget_invalid",
        duplicate_code="program.candidate_budget_duplicate",
        label="Candidate / obligation budget",
        proposal_path=proposal_path,
    )
    declared_order = _comma_separated_values(
        program_values["Declared workstream order"] or "",
        invalid_code="program.workstream_order_invalid",
        duplicate_code="program.workstream_order_duplicate",
        label="Declared workstream order",
        proposal_path=proposal_path,
        validator=WORKSTREAM_ID_PATTERN,
    )

    workstreams = _workstream_sections(proposal, program_matches[0], proposal_path)
    workstream_ids = tuple(workstream.stable_id for workstream in workstreams)
    if declared_order != workstream_ids:
        raise ContractViolation(
            "program.workstream_registration_mismatch",
            f"Declared workstream order must exactly match Workstream Focus records: {proposal_path.as_posix()}",
        )

    owners: set[str] = set()
    candidate_ids: list[str] = []
    for workstream in workstreams:
        _validate_legacy_triggered_policies_field(
            workstream.section,
            code="program.workstream_legacy_triggered_policies_field_present",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
            proposal_path=proposal_path,
        )
        _validate_required_fields(
            workstream.section,
            WORKSTREAM_FIELDS,
            code="program.workstream_field_missing",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
            proposal_path=proposal_path,
        )
        _validate_seam_classification(
            workstream.section,
            code_prefix="program.workstream",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
            proposal_path=proposal_path,
        )
        owner = _field_value(workstream.section, "Primary module / causal owner")
        assert owner is not None
        if owner in owners:
            raise ContractViolation(
                "program.workstream_owner_duplicate",
                f"Workstream Focus repeats primary module / causal owner {owner!r}: {proposal_path.as_posix()}",
            )
        owners.add(owner)
        workstream_candidate_ids = _comma_separated_values(
            _field_value(workstream.section, "Candidate / obligation IDs") or "",
            invalid_code="program.candidate_id_invalid",
            duplicate_code="program.candidate_id_duplicate",
            label=f"Workstream Focus {workstream.stable_id!r} Candidate / obligation IDs",
            proposal_path=proposal_path,
        )
        if any(candidate_id in candidate_ids for candidate_id in workstream_candidate_ids):
            raise ContractViolation(
                "program.candidate_id_duplicate",
                f"Candidate / obligation IDs must be unique across workstreams: {proposal_path.as_posix()}",
            )
        candidate_ids.extend(workstream_candidate_ids)
        triggered_policies = _triggered_policies(
            root,
            workstream.section,
            proposal_path,
            code_prefix="program.workstream",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
        )
        _validate_selected_policy_reviews(
            workstream.section,
            triggered_policies,
            proposal_path,
            review_level=4,
            code_prefix="program.workstream",
        )

    if set(budget) != set(candidate_ids):
        raise ContractViolation(
            "program.candidate_budget_mismatch",
            f"Candidate / obligation budget must exactly match the workstream union: {proposal_path.as_posix()}",
        )


def _validate_ordinary_proposal(root: Path, proposal: str, proposal_path: Path) -> None:
    matches = list(re.finditer(r"^## Change Focus\s*$", proposal, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "focus.heading_missing",
            f"proposal must contain exactly one {FOCUS_HEADING!r}: {proposal_path.as_posix()}",
        )
    focus_section = _section_after_heading(proposal, matches[0], maximum_level=2)
    _validate_legacy_triggered_policies_field(
        focus_section,
        code="focus.legacy_triggered_policies_field_present",
        record_name="Focus Card",
        proposal_path=proposal_path,
    )
    _validate_required_fields(
        focus_section,
        FOCUS_FIELDS,
        code="focus.field_missing",
        record_name="Focus Card",
        proposal_path=proposal_path,
    )
    _validate_seam_classification(
        focus_section,
        code_prefix="focus",
        record_name="Focus Card",
        proposal_path=proposal_path,
    )
    triggered_policies = _triggered_policies(root, focus_section, proposal_path)
    _validate_selected_policy_reviews(
        proposal,
        triggered_policies,
        proposal_path,
        review_level=2,
        code_prefix="focus",
    )


def _validate_active_changes(root: Path) -> None:
    changes_root = root / CHANGES_ROOT
    if not changes_root.exists():
        return
    if not changes_root.is_dir():
        raise ContractViolation(
            "focus.changes_root_kind",
            f"changes root is not a directory: {CHANGES_ROOT.as_posix()}",
        )

    active_changes = sorted(
        path
        for path in changes_root.iterdir()
        if path.is_dir() and path.name != "archive" and not path.name.startswith(".")
    )
    for change_root in active_changes:
        proposal_path = change_root / "proposal.md"
        if not proposal_path.is_file():
            raise ContractViolation(
                "focus.proposal_missing",
                f"active change lacks proposal.md: {proposal_path.relative_to(root).as_posix()}",
            )
        try:
            proposal = proposal_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ContractViolation(
                "focus.proposal_unreadable",
                f"cannot read active proposal {proposal_path.relative_to(root).as_posix()}: {exc}",
            ) from exc
        relative_proposal_path = proposal_path.relative_to(root)
        program_count = len(re.findall(r"^## Program Focus\s*$", proposal, flags=re.MULTILINE))
        workstream_count = len(re.findall(r"^### Workstream Focus:", proposal, flags=re.MULTILINE))
        if program_count or workstream_count:
            if program_count != 1 or re.search(r"^## Change Focus\s*$", proposal, flags=re.MULTILINE):
                raise ContractViolation(
                    "program.mode_invalid",
                    "ordinary and program proposal forms are exclusive: "
                    f"{relative_proposal_path.as_posix()}",
                )
            _validate_program_proposal(root, proposal, relative_proposal_path)
        else:
            _validate_ordinary_proposal(root, proposal, relative_proposal_path)
        _validate_change_tasks(root, change_root)
