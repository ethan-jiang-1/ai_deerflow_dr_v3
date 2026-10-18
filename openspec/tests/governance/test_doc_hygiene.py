#!/usr/bin/env python3
"""Discoverable battery for the doc-hygiene guard.

Before this file existed the guard's negative controls were a 442-line function
inlined in the checker, reachable only through ``--self-test``: the governance
unittest lane never ran them. Now every control is its own test identifier, and
the CLI keeps ``--self-test`` as a thin delegate over the same registry.

The cases themselves live in ``openspec/governance/_battery.py`` (one home).
Assertion text is carried as the test identifier, so a rule that loses a
behaviour names exactly which control went missing.

@impl DOB-001
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

GOVERNANCE = Path(__file__).resolve().parents[2] / "governance"
REPO_ROOT = GOVERNANCE.parents[1]
CHECKER = GOVERNANCE / "check_doc_hygiene.py"

if str(GOVERNANCE) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE))

import _battery  # noqa: E402  (the governance directory is importable above)
import doc_hygiene_check  # noqa: E402  (the rule registry)


def _method_name(case_id: str) -> str:
    """A stable identifier for one control's test method."""
    keep = [ch if (ch.isalnum() or ch == " ") else " " for ch in case_id]
    return "test_control_" + "_".join("".join(keep).split()).lower()


class NegativeControlTests(unittest.TestCase):
    """One test per battery control: the rule must fire, or must not mis-fire."""


def _make_test(case: "_battery.NegativeCase"):
    def test(self) -> None:
        problems = _battery.run_case(case)
        with self.subTest(case=case.case_id, rule=case.rule):
            if case.zero_violations:
                self.assertEqual(
                    problems, [],
                    f"{case.case_id}: expected a clean run, got {problems}",
                )
            elif case.present:
                for needle in case.present:
                    self.assertTrue(
                        any(needle in v for v in problems),
                        f"{case.case_id}: no violation contains {needle!r}; got {problems}",
                    )
            elif case.absent:
                specific = [v for v in problems if "unindexed" not in v]
                for needle in case.absent:
                    self.assertFalse(
                        any(needle in v for v in specific),
                        f"{case.case_id}: violation mis-reported on {needle!r}; got {specific}",
                    )
            else:
                self.fail(f"{case.case_id}: control declares no polarity and cannot fail")

    test.__name__ = _method_name(case.case_id)
    test.__doc__ = f"{case.note} [rule: {case.rule}]"
    return test


for _case in _battery.NEGATIVE_CASES:
    _name = _method_name(_case.case_id)
    if hasattr(NegativeControlTests, _name):  # pragma: no cover - identity guard
        raise AssertionError(f"duplicate control identifier: {_case.case_id!r}")
    setattr(NegativeControlTests, _name, _make_test(_case))


class BatteryInventoryTests(unittest.TestCase):
    """The control inventory answers to its invariant: every rule is covered."""

    #: ``run_rule`` accepts this in place of a rule name and runs every rule; a control
    #: meaning "nothing at all may fire" legitimately targets it.
    WHOLE_CHECKER = "violations"

    def test_every_rule_has_at_least_one_control(self) -> None:
        """Coverage is the invariant; a count was only ever a proxy for it.

        The inventory used to be pinned by exact counts. That cost three hand-syncs in a
        single session (three numbers *and* a paragraph each time) and the paragraph ended
        up contradicting itself about its own figures. What the pin was standing in for is
        coverage: a rule with no control exercises nothing. That is a live risk rather than
        a theoretical one — ``adr_index`` and ``docs_scope`` have exactly one control each,
        so losing either one zeroes a rule's coverage.

        Deliberate trade-off, recorded here so it reads as a choice: losing one of several
        *redundant* controls no longer fails this test. Such a loss changes nothing about
        what any rule can be shown to do, and it appears as an explicit deletion in review.
        The count pin charged a hand-sync for every *addition* to buy that.
        """
        rules = [name for name, _ in doc_hygiene_check.RULES]
        self.assertTrue(rules, "the rule registry is empty, so coverage would pass vacuously")
        covered = {case.rule for case in _battery.NEGATIVE_CASES}
        uncovered = sorted(set(rules) - covered)
        self.assertEqual(uncovered, [], f"rules with no control at all: {uncovered}")

    def test_no_control_names_an_unknown_rule(self) -> None:
        """The converse: a control that targets nothing is not a control."""
        known = {name for name, _ in doc_hygiene_check.RULES} | {self.WHOLE_CHECKER}
        unknown = sorted({case.rule for case in _battery.NEGATIVE_CASES} - known)
        self.assertEqual(unknown, [], f"controls targeting rules that do not exist: {unknown}")

    def test_every_control_declares_its_polarity(self) -> None:
        for case in _battery.NEGATIVE_CASES:
            self.assertTrue(
                case.zero_violations or case.present or case.absent,
                f"{case.case_id} declares no polarity: it would pass vacuously",
            )

    def test_control_identifiers_are_unique(self) -> None:
        ids = [c.case_id for c in _battery.NEGATIVE_CASES]
        self.assertEqual(len(ids), len(set(ids)), "duplicate control identifier")


class CleanFixtureTests(unittest.TestCase):
    """The clean fixture is a positive control: a valid tree yields no violations."""

    def test_clean_fixture_is_a_positive_control(self) -> None:
        self.assertEqual(
            _battery.run_case(_battery.NEGATIVE_CASES[0]), [],
            "the clean fixture must satisfy every rule",
        )


class SelfTestCliContractTests(unittest.TestCase):
    """--self-test keeps its contract: path, exit code, stdout line."""

    def test_self_test_exits_zero_with_the_declared_line(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--self-test"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "doc-hygiene self-test passed.\n")

    def test_plain_mode_exits_zero_on_the_real_tree(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "doc-layer hygiene passed.\n")

    def test_checker_is_importable_without_side_effects(self) -> None:
        """A checker that runs on import cannot be tested; pin the guard order."""
        spec = importlib.util.spec_from_file_location("doc_hygiene_probe", CHECKER)
        module = importlib.util.module_from_spec(spec)
        sys.modules["doc_hygiene_probe"] = module
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))
        self.assertIn("adr_index", [name for name, _ in module.RULES])


if __name__ == "__main__":
    unittest.main()
