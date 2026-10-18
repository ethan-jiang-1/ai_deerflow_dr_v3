"""Deterministic tests for the standing-tasks-sections rule (@impl CHA-001).

Run from the repository root:

    python3 -m unittest discover -s openspec/tests/governance

Fixtures build isolated temp roots and never mutate the repository. The
kernel grammar is exercised pure; the checker wiring is exercised through
_validate_change_tasks on a temp change root. Exit-code semantics: the
checker surfaces each kernel issue as a ContractViolation (exit 1 with a
[code] detail line) — the tests assert the issue codes and details directly.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

import change_guidance_kernel as kernel  # noqa: E402
from check_change_guidance import (  # noqa: E402
    POLICY_REGISTRY,
    ContractViolation,
    _validate_change_tasks,
    _validate_program_proposal,
)


GOOD_REGISTER = "## Deviation Register\n\n- none: planning-time deviation-free\n"
BAD_REGISTER = "## Deviation Register\n\n## Next\n"
BARE_NONE_REGISTER = "## Deviation Register\n\n- none:\n"
GOOD_RECORD = (
    "## Delivery Record\n\n"
    "- **外部行为**: filled at closeout\n"
    "- **影响面**: filled at closeout\n"
    "- **实际跑了什么**: filled at closeout\n"
    "- **未执行的检查**: filled at closeout\n"
)
MISSING_LABEL_RECORD = (
    "## Delivery Record\n\n"
    "- **外部行为**: filled\n"
    "- **影响面**: filled\n"
    "- **实际跑了什么**: filled\n"
)


def _tasks(*sections: str) -> str:
    return "# Tasks\n\n## 1. Work\n\n- [ ] 1.1 do it\n\n" + "\n".join(sections)


class DeviationRegisterGrammarTests(unittest.TestCase):
    def test_explicit_none_passes(self):
        self.assertEqual(kernel.deviation_register_issues(_tasks(GOOD_REGISTER)), ())

    def test_entry_bullets_pass(self):
        register = "## Deviation Register\n\n- renamed helper; ruled by spec §2; landed in tasks 2.1\n"
        self.assertEqual(kernel.deviation_register_issues(_tasks(register)), ())

    def test_missing_section_fails(self):
        issues = kernel.deviation_register_issues("# Tasks\n\n## 1. Work\n\n- [ ] 1.1 do it\n")
        self.assertEqual(issues[0].code, "tasks.deviation_register_missing")

    def test_empty_section_fails(self):
        issues = kernel.deviation_register_issues(_tasks("## Deviation Register\n\nsome prose, no bullets\n"))
        self.assertEqual(issues[0].code, "tasks.deviation_register_empty")

    def test_bare_none_fails(self):
        issues = kernel.deviation_register_issues(_tasks(BARE_NONE_REGISTER))
        self.assertEqual(issues[0].code, "tasks.deviation_register_none_rationale")

    def test_duplicate_section_fails(self):
        issues = kernel.deviation_register_issues(_tasks(GOOD_REGISTER, GOOD_REGISTER))
        self.assertEqual(issues[0].code, "tasks.deviation_register_duplicate")


class DeliveryRecordGrammarTests(unittest.TestCase):
    def test_all_labels_pass(self):
        self.assertEqual(kernel.delivery_record_issues(_tasks(GOOD_RECORD)), ())

    def test_missing_section_fails(self):
        issues = kernel.delivery_record_issues(_tasks(GOOD_REGISTER))
        self.assertEqual(issues[0].code, "tasks.delivery_record_missing")

    def test_missing_label_fails(self):
        issues = kernel.delivery_record_issues(_tasks(MISSING_LABEL_RECORD))
        self.assertEqual(issues[0].code, "tasks.delivery_record_field_missing")
        self.assertIn("未执行的检查", issues[0].detail)

    def test_duplicate_section_fails(self):
        issues = kernel.delivery_record_issues(_tasks(GOOD_RECORD, GOOD_RECORD))
        self.assertEqual(issues[0].code, "tasks.delivery_record_duplicate")


class CheckerWiringTests(unittest.TestCase):
    """_validate_change_tasks raises on grammar violations and skips a missing tasks.md."""

    def _change_root(self, tmp: str, tasks_text: str | None) -> Path:
        root = Path(tmp)
        change_root = root / "openspec" / "changes" / "demo-change"
        change_root.mkdir(parents=True)
        if tasks_text is not None:
            (change_root / "tasks.md").write_text(tasks_text, encoding="utf-8")
        return root

    def test_compliant_tasks_pass_silently(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, _tasks(GOOD_REGISTER, GOOD_RECORD))
            _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")

    def test_missing_tasks_md_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, None)
            _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")

    def test_violation_names_change_and_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, _tasks(MISSING_LABEL_RECORD, GOOD_REGISTER))
            with self.assertRaises(ContractViolation) as ctx:
                _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")
            self.assertEqual(ctx.exception.code, "tasks.delivery_record_field_missing")
            self.assertIn("demo-change/tasks.md", ctx.exception.detail)

    def test_register_violation_names_change_and_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, _tasks(GOOD_RECORD))
            with self.assertRaises(ContractViolation) as ctx:
                _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")
            self.assertEqual(ctx.exception.code, "tasks.deviation_register_missing")


def _workstream_body(owner: str, candidate_id: str, *, drop: str | None = None,
                     extra: str = "", policies: str = "none: 只读校验，不触发任何评审") -> str:
    """One Workstream Focus body: the twelve declared fields, with knobs for the red cases."""
    fields = {
        "Primary module / causal owner": owner,
        "Seam classification": "wiring —— 只在闸门处接线；无模型参与。",
        "Question": "这段文字存在吗",
        "Necessary adjacent/external contracts": "无",
        "Evidence seam": "退出码",
        "Not in scope": "无",
        "Triggered review policies": policies,
        "Candidate / obligation IDs": candidate_id,
        "Target / retirement": "目标",
        "Surface grade": "面",
        "Decision authority": "owner",
        "Negative path / recovery": "恢复",
    }
    if drop is not None:
        del fields[drop]
    return "".join(f"- **{name}:** {value}\n" for name, value in fields.items()) + extra


def _program_proposal(order: str = "alpha, beta", *, budget: str = "c1, c2",
                      alpha_id: str = "alpha", beta_id: str = "beta", both: bool = True,
                      drop_program_field: str | None = None, workstreams_before: bool = False,
                      alpha_body: str | None = None, beta_body: str | None = None) -> str:
    """A program-form proposal; the knobs drive the negative cases."""
    program_fields = {
        "Program outcome": "把一件事做出来",
        "Candidate / obligation budget": budget,
        "Declared workstream order": order,
        "Program decision authority": "owner",
        "Shared archive invariant": "不变",
        "Program failure / recovery": "恢复",
        "Split / expansion rule": "不拆",
        "Not in scope": "别的",
    }
    if drop_program_field is not None:
        del program_fields[drop_program_field]
    program = "## Program Focus\n\n" + "".join(
        f"- **{name}:** {value}\n" for name, value in program_fields.items()
    )
    alpha = f"### Workstream Focus: {alpha_id}\n\n{alpha_body or _workstream_body('mod-a', 'c1')}\n"
    beta = f"### Workstream Focus: {beta_id}\n\n{beta_body or _workstream_body('mod-b', 'c2')}\n"
    if workstreams_before:
        return alpha + beta + "\n" + program
    return program + "\n" + alpha + "\n" + (beta if both else "")


class ProgramModeTests(unittest.TestCase):
    """The program form's direct coverage.

    The mode is kept because it has a real user (2026-10-07-surface-runtime-structure: one
    `## Program Focus` plus three workstreams) and is the only multi-workstream carrier. The
    first round covered the canonical happy path and four codes; this round closes the rest of
    the codes that live inside `_validate_program_proposal` — each with one fixture knob and one
    assertion naming its code.

    These cases call `_validate_program_proposal` directly, matching this file's established
    style. Scope is that function: the workstream-level review-section validation lives in the
    caller and is not covered here.
    """

    def _path(self, tmp: str) -> tuple[Path, Path]:
        root = Path(tmp) / "repo"
        change = root / "openspec" / "changes" / "demo-program"
        change.mkdir(parents=True)
        return root, change / "proposal.md"

    def _raise(self, text: str) -> ContractViolation:
        with tempfile.TemporaryDirectory() as tmp:
            root, path = self._path(tmp)
            with self.assertRaises(ContractViolation) as ctx:
                _validate_program_proposal(root, text, path)
            return ctx.exception

    def _code(self, text: str) -> str:
        return self._raise(text).code

    def _raise_with_documents(self, text: str, policies: tuple[str, ...]) -> ContractViolation:
        """Raise with the named policies' guidance documents materialized in the temp root.

        Declaring a real policy makes `_triggered_policies` read that policy's document from
        the root, so the fixture has to carry it — one file per policy, not a whole tree.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root, path = self._path(tmp)
            for policy in policies:
                document = root / POLICY_REGISTRY[policy].path
                document.parent.mkdir(parents=True, exist_ok=True)
                document.write_text("x\n", encoding="utf-8")
            with self.assertRaises(ContractViolation) as ctx:
                _validate_program_proposal(root, text, path)
            return ctx.exception

    def _code_with_documents(self, text: str, policies: tuple[str, ...]) -> str:
        return self._raise_with_documents(text, policies).code

    def test_a_compliant_program_proposal_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, path = self._path(tmp)
            _validate_program_proposal(root, _program_proposal(), path)

    def test_a_single_workstream_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(both=False)), "program.workstream_count_invalid")

    def test_workstreams_before_the_program_heading_are_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(workstreams_before=True)), "program.mode_invalid")

    def test_a_missing_program_field_is_reported(self) -> None:
        self.assertEqual(
            self._code(_program_proposal(drop_program_field="Program decision authority")),
            "program.field_missing",
        )

    def test_a_declared_order_that_disagrees_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(order="beta, alpha")),
                         "program.workstream_registration_mismatch")

    def test_an_empty_budget_item_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(budget="c1, , c2")),
                         "program.candidate_budget_invalid")

    def test_a_repeated_budget_identifier_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(budget="c1, c1")),
                         "program.candidate_budget_duplicate")

    def test_a_budget_that_disagrees_with_the_workstream_union_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(budget="c1, c2, c3")),
                         "program.candidate_budget_mismatch")

    def test_an_empty_candidate_id_item_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1, , c2")
        self.assertEqual(self._code(_program_proposal(alpha_body=body)),
                         "program.candidate_id_invalid")

    def test_a_repeated_candidate_id_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1, c1")
        self.assertEqual(self._code(_program_proposal(alpha_body=body)),
                         "program.candidate_id_duplicate")

    def test_a_missing_workstream_field_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1", drop="Target / retirement")
        self.assertEqual(self._code(_program_proposal(alpha_body=body)),
                         "program.workstream_field_missing")

    def test_a_duplicate_workstream_id_is_reported(self) -> None:
        # The declared order stays valid and unique: the repeat is inside the headings.
        self.assertEqual(self._code(_program_proposal(beta_id="alpha")),
                         "program.workstream_id_duplicate")

    def test_an_invalid_workstream_id_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(alpha_id="Alpha")),
                         "program.workstream_id_invalid")

    def test_the_legacy_policies_field_in_a_workstream_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1", extra="- **Triggered charter policies:** x\n")
        self.assertEqual(self._code(_program_proposal(alpha_body=body)),
                         "program.workstream_legacy_triggered_policies_field_present")

    def test_a_duplicate_declared_order_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(order="alpha, alpha")),
                         "program.workstream_order_duplicate")

    def test_an_invalid_declared_order_is_reported(self) -> None:
        self.assertEqual(self._code(_program_proposal(order="alpha, Beta")),
                         "program.workstream_order_invalid")

    def test_a_duplicate_workstream_owner_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c2")  # same owner as alpha
        self.assertEqual(self._code(_program_proposal(beta_body=body)),
                         "program.workstream_owner_duplicate")

    # --- The workstream-level review records: three policies, each with a document and a
    # --- level-4 record. The record heading is level 4 for program workstreams (level 2 for
    # --- ordinary proposals), which is why these sections live inside the workstream body.

    MALFORMED_RECORD = "\n#### {heading}\n\n| a | b |\n|---|---|\n| x | y |\n"

    def test_a_declared_policy_without_its_document_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1", policies="control-placement")
        self.assertEqual(self._code(_program_proposal(alpha_body=body)),
                         "program.workstream_triggered_policy_document_missing")

    def test_a_missing_control_placement_record_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1", policies="control-placement")
        self.assertEqual(
            self._code_with_documents(_program_proposal(alpha_body=body), ("control-placement",)),
            "program.workstream_control_placement_review_missing",
        )

    def test_a_malformed_control_placement_record_is_reported(self) -> None:
        record = self.MALFORMED_RECORD.format(heading="Control Placement Review")
        body = _workstream_body("mod-a", "c1", policies="control-placement", extra=record)
        self.assertEqual(
            self._code_with_documents(_program_proposal(alpha_body=body), ("control-placement",)),
            "program.workstream_control_placement_review_shape_invalid",
        )

    def test_a_missing_workflow_outcome_record_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1", policies="workflow-outcome-review")
        self.assertEqual(
            self._code_with_documents(_program_proposal(alpha_body=body), ("workflow-outcome-review",)),
            "program.workstream_workflow_outcome_review_missing",
        )

    def test_a_malformed_workflow_outcome_record_is_reported(self) -> None:
        record = self.MALFORMED_RECORD.format(heading="Workflow Outcome Review")
        body = _workstream_body("mod-a", "c1", policies="workflow-outcome-review", extra=record)
        self.assertEqual(
            self._code_with_documents(_program_proposal(alpha_body=body), ("workflow-outcome-review",)),
            "program.workstream_workflow_outcome_review_shape_invalid",
        )

    def test_a_missing_node_agent_record_is_reported(self) -> None:
        body = _workstream_body("mod-a", "c1", policies="node-agent-workflow-integrity")
        self.assertEqual(
            self._code_with_documents(
                _program_proposal(alpha_body=body), ("node-agent-workflow-integrity",)
            ),
            "program.workstream_node_agent_review_missing",
        )

    def test_a_malformed_node_agent_record_is_reported(self) -> None:
        record = self.MALFORMED_RECORD.format(heading="Node Agent Review")
        body = _workstream_body("mod-a", "c1", policies="node-agent-workflow-integrity", extra=record)
        self.assertEqual(
            self._code_with_documents(
                _program_proposal(alpha_body=body), ("node-agent-workflow-integrity",)
            ),
            "program.workstream_node_agent_review_shape_invalid",
        )
