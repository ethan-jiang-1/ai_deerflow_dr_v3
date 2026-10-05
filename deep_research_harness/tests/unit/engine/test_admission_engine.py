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
        "content": "认证壁垒调研笔记".encode("utf-8"),
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

    def test_result_codes_are_the_declared_six(self) -> None:
        self.assertEqual(
            verdicts.RESULT_CODES,
            ("ok", "schema_malformed", "missing_provenance", "empty_content", "hash_mismatch", "duplicate_content"),
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

        content = "重复证据".encode("utf-8")
        digest = hashlib.sha256(content).hexdigest()
        verdict = validator.validate(
            _submission(content=content), _context(admitted_hashes=frozenset({digest}))
        )
        self.assertEqual(verdict.result_code, "duplicate_content")

    def test_rejected_history_does_not_duplicate(self) -> None:
        import hashlib

        content = "曾被打回的证据".encode("utf-8")
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
