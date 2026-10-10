"""Run-admission engine tests: closed vocabularies, validator rules, gate derivation,
quality-register sync.

@impl RUA-001"""

from __future__ import annotations

import unittest
from pathlib import Path

from deerflow_deep_research.domain import admission
from deerflow_deep_research.engine import gate, machines, validator, verdicts
from deerflow_deep_research.engine.gate import GateRequirement
from deerflow_deep_research.engine.validator import AdmissionContext, ArtifactSubmission

_REGISTER = Path(__file__).resolve().parents[3] / "docs" / "quality-register.md"


def _submission(**overrides) -> ArtifactSubmission:
    kwargs: dict = {
        "kind": "evidence",
        "filename": "supply-chain-notes.md",
        "content": "认证壁垒调研笔记".encode(),
        "provenance": {"producer": "research-skill"},
    }
    kwargs.update(overrides)
    return ArtifactSubmission(**kwargs)


def _context(**overrides) -> AdmissionContext:
    kwargs: dict = {"admitted_hashes": frozenset(), "rejected_hashes": {}}
    kwargs.update(overrides)
    return AdmissionContext(**kwargs)


class ClosedVocabulariesTest(unittest.TestCase):
    def test_artifact_kinds_are_closed(self) -> None:
        self.assertEqual(admission.ARTIFACT_KINDS, ("evidence", "final_report"))

    def test_result_codes_are_the_declared_set(self) -> None:
        self.assertEqual(
            verdicts.RESULT_CODES,
            (
                "ok",
                "schema_malformed",
                "missing_provenance",
                "empty_content",
                "duplicate_content",
                "report_structure_violation",
            ),
        )

    def test_dispositions_are_the_closed_three(self) -> None:
        self.assertEqual(verdicts.DISPOSITIONS, ("admit", "reject", "replay"))

    def test_phase_verdicts_are_pass_or_blocked(self) -> None:
        self.assertEqual(verdicts.PHASE_VERDICTS, ("pass", "blocked"))


class ValidatorRulesTest(unittest.TestCase):
    def test_clean_submission_is_ok_with_empty_reasons(self) -> None:
        verdict = validator.validate(_submission(), _context())
        self.assertEqual(verdict.result_code, "ok")
        self.assertEqual(verdict.reasons, ())
        self.assertEqual(verdict.content_hash, __import__("hashlib").sha256(_submission().content).hexdigest())

    def test_structured_final_report_is_ok(self) -> None:
        body = (
            "成本结构分析正文，长度足以越过结构地板，包含具体判断与依据："
            "认证壁垒集中在两国互认缺失与原产地标记两类，细分如下。短期看关税"
            "与认证周期是主要变量，长期看本地化生产比例决定合规成本的上限与下限。"
            "另外，出口企业还需要评估目标市场的监管通告节奏与合规文件准备周期，"
            "这两项共同决定了整个准入时间线的弹性区间。"
        )
        report = "## 结论\n\n" + body + "\n\n## Sources\n\n- https://fixture.example/a\n- https://fixture.example/b\n"
        verdict = validator.validate(
            _submission(kind="final_report", filename="r.md", content=report.encode()), _context()
        )
        self.assertEqual(verdict.result_code, "ok")

    def _structure_verdict(self, content: bytes) -> object:
        return validator.validate(_submission(kind="final_report", filename="r.md", content=content), _context())

    def test_non_utf8_final_report_is_rejected(self) -> None:
        verdict = self._structure_verdict(b"\xff\xfe broken")
        self.assertEqual(verdict.result_code, "report_structure_violation")
        self.assertTrue(any("UTF-8" in reason for reason in verdict.reasons))

    def test_plan_marked_final_report_is_rejected_even_when_structure_mimics_a_report(self) -> None:
        """BUG-001's refusal face: a plan wrapped in the protocol's markers is not a
        report — even when it carries headings and a Sources-class section (the
        observed degenerate plan satisfied both via its deliverables section)."""
        body = (
            "研究计划正文，长度足以越过结构地板：调研角度覆盖法规基线与成员国差异两类，"
            "查询策略以官方公报、行业解读与交叉验证三个来源类型为主，先广度后深度。"
            "交付物为运营人合规清单与来源清单，边界聚焦开放类别，Specific 与 Certified"
            "仅作边界说明；假设以 EU 层面统一规则为主，成员国仅抽样提示差异。"
            "红线情形触发转 Specific 类别或其他授权的，在清单中单列升级提示。"
        )
        plan_as_report = (
            "<research-plan>\n## 一、调研角度\n\n" + body +
            "\n\n## Sources\n\n- https://fixture.example/a\n</research-plan>\n"
        )
        verdict = self._structure_verdict(plan_as_report.encode())
        self.assertEqual(verdict.result_code, "report_structure_violation")
        self.assertTrue(any("plan" in reason for reason in verdict.reasons))
        stripped = plan_as_report.replace("<research-plan>\n", "").replace("\n</research-plan>\n", "\n")
        self.assertEqual(
            self._structure_verdict(stripped.encode()).result_code, "ok",
            "the same text without the markers must still admit",
        )

    def test_headingless_final_report_is_rejected(self) -> None:
        verdict = self._structure_verdict(b"no heading here, just a plain short body without any markdown title")
        self.assertEqual(verdict.result_code, "report_structure_violation")
        self.assertTrue(any("heading" in reason for reason in verdict.reasons))

    def test_sourcesless_final_report_is_rejected(self) -> None:
        verdict = self._structure_verdict("## 结论\n\n正文有标题但没有来源节，正文写得足够长以越过长度地板。".encode())
        self.assertEqual(verdict.result_code, "report_structure_violation")
        self.assertTrue(any("Sources" in reason for reason in verdict.reasons))

    def test_overshort_final_report_is_rejected(self) -> None:
        verdict = self._structure_verdict("## 结论\n\n## Sources\n\n太短。".encode())
        self.assertEqual(verdict.result_code, "report_structure_violation")
        self.assertTrue(any("characters" in reason for reason in verdict.reasons))

    def test_structure_rules_do_not_apply_to_evidence(self) -> None:
        verdict = validator.validate(_submission(content="太短的调研笔记。".encode()), _context())
        self.assertEqual(verdict.result_code, "ok")

    def test_unknown_kind_is_schema_malformed(self) -> None:
        verdict = validator.validate(_submission(kind="blueprint"), _context())
        self.assertEqual(verdict.result_code, "schema_malformed")
        self.assertTrue(any("blueprint" in reason for reason in verdict.reasons))

    def test_unsafe_filenames_are_schema_malformed(self) -> None:
        for bad in ("../escape.md", "sub/dir.md", "", ".", "a\\b.md"):
            with self.subTest(filename=bad):
                verdict = validator.validate(_submission(filename=bad), _context())
                self.assertEqual(verdict.result_code, "schema_malformed")

    def test_missing_provenance_producer_is_caught(self) -> None:
        verdict = validator.validate(_submission(provenance={}), _context())
        self.assertEqual(verdict.result_code, "missing_provenance")
        verdict = validator.validate(_submission(provenance={"producer": ""}), _context())
        self.assertEqual(verdict.result_code, "missing_provenance")

    def test_empty_content_is_caught(self) -> None:
        verdict = validator.validate(_submission(content=b""), _context())
        self.assertEqual(verdict.result_code, "empty_content")

    def test_duplicate_admitted_content_is_caught(self) -> None:
        import hashlib

        content = "重复证据".encode()
        digest = hashlib.sha256(content).hexdigest()
        verdict = validator.validate(
            _submission(content=content), _context(admitted_hashes=frozenset({digest}))
        )
        self.assertEqual(verdict.result_code, "duplicate_content")

    def test_rejected_history_does_not_duplicate(self) -> None:
        import hashlib

        content = "曾被打回的证据".encode()
        digest = hashlib.sha256(content).hexdigest()
        verdict = validator.validate(
            _submission(content=content), _context(rejected_hashes={digest: 4})
        )
        self.assertEqual(verdict.result_code, "ok")


class GateDerivationTest(unittest.TestCase):
    def test_covered_requirements_pass(self) -> None:
        requirements = (GateRequirement(kind="evidence", minimum=2), GateRequirement(kind="final_report", minimum=1))
        verdict = gate.derive_gate(
            requirements, admitted_counts={"evidence": 2, "final_report": 1}
        )
        self.assertEqual(verdict.phase_verdict, "pass")
        self.assertEqual(verdict.unmet, ())

    def test_blocked_names_exactly_the_unmet(self) -> None:
        requirements = (GateRequirement(kind="evidence", minimum=2), GateRequirement(kind="final_report", minimum=1))
        verdict = gate.derive_gate(requirements, admitted_counts={"evidence": 2, "final_report": 0})
        self.assertEqual(verdict.phase_verdict, "blocked")
        self.assertEqual(verdict.unmet, ("final_report",))

    def test_no_requirements_passes_vacuously(self) -> None:
        verdict = gate.derive_gate((), admitted_counts={})
        self.assertEqual(verdict.phase_verdict, "pass")


class QualityRegisterSyncTest(unittest.TestCase):
    def test_register_names_every_declared_machine(self) -> None:
        register_text = _REGISTER.read_text(encoding="utf-8")
        missing = [name for name, _ in machines.DECLARED_MACHINES if name not in register_text]
        self.assertEqual(missing, [], f"quality register is missing machines: {missing}")

    def test_declared_machines_carry_invariants(self) -> None:
        for name, invariant in machines.DECLARED_MACHINES:
            self.assertTrue(name, "machine name must be non-empty")
            self.assertTrue(invariant, f"machine {name} must declare its invariant")


if __name__ == "__main__":
    unittest.main()
