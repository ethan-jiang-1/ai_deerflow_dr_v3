"""Run-bundle domain contract tests: paths, state machine, clarification, journal policy.

@impl RUB-001"""

from __future__ import annotations

import unittest

from deerflow_deep_research.domain import bundle, clarification, journal_policy, state_machine
from deerflow_deep_research.domain.state_machine import RuleViolation


def _active_state(**overrides):
    state = state_machine.rule_start(
        thread_id="0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b",
        owner_pid=4242,
        deerflow_pin="c" * 40,
        composition="all_real",
    )
    for name, value in overrides.items():
        setattr(state, name, value)
    return state


class BundleContractTest(unittest.TestCase):
    def test_declared_subtrees_are_exactly_the_contract(self) -> None:
        self.assertEqual(bundle.BUNDLE_SUBTREES, ("request", "work", "evidence", "final", "diagnostics"))
        self.assertNotIn("synthesis", bundle.BUNDLE_SUBTREES)
        self.assertNotIn("review", bundle.BUNDLE_SUBTREES)

    def test_bucket_and_bundle_id_forms(self) -> None:
        self.assertTrue(bundle.is_valid_bucket("d_20261003"))
        self.assertFalse(bundle.is_valid_bucket("20261003"))
        self.assertFalse(bundle.is_valid_bucket("d_2026103"))
        self.assertTrue(bundle.is_valid_bundle_id("0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b"))
        self.assertFalse(bundle.is_valid_bundle_id("../escape"))
        self.assertFalse(bundle.is_valid_bundle_id("short"))

    def test_bundle_layout_paths(self) -> None:
        root = bundle.bundle_dir("scopes", "d_20261003", "0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b")
        self.assertEqual(root.as_posix(), "scopes/d_20261003/0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b")
        self.assertEqual(bundle.state_relative().as_posix(), "state.json")
        self.assertEqual(bundle.checkpoint_relative().as_posix(), "checkpoint.sqlite")
        self.assertEqual(bundle.journal_relative().as_posix(), "diagnostics/journal.jsonl")
        self.assertEqual(bundle.staging_name("abc"), ".staging-abc")


class StateMachineRulesTest(unittest.TestCase):
    def test_start_creates_active_generation_one(self) -> None:
        state = _active_state()
        self.assertEqual(state.status, "active")
        self.assertEqual(state.generation, 1)
        self.assertEqual(state.revision, 1)
        self.assertFalse(state.cancel_requested)
        self.assertEqual(state.auto_proceed_count, 0)
        self.assertEqual(state.auto_proceed_bound, state_machine.DEFAULT_AUTO_PROCEED_BOUND)
        self.assertEqual(state.auto_proceed_bound, 2)

    def test_start_rejects_illegal_composition(self) -> None:
        with self.assertRaises(RuleViolation) as ctx:
            state_machine.rule_start(
                thread_id="0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b",
                owner_pid=1,
                deerflow_pin="c" * 40,
                composition="half_real",
            )
        self.assertIn("half_real", str(ctx.exception))

    def test_cancel_requests_only_on_active(self) -> None:
        state = _active_state()
        cancelled_request = state_machine.rule_cancel(state)
        self.assertTrue(cancelled_request.cancel_requested)
        self.assertEqual(cancelled_request.status, "active")
        done = state_machine.rule_run_terminal(state, "completed")
        with self.assertRaises(RuleViolation) as ctx:
            state_machine.rule_cancel(done)
        self.assertIn("completed", str(ctx.exception))
        self.assertIn("cancel", str(ctx.exception))

    def test_refine_requires_terminal_and_bumps_generation(self) -> None:
        state = _active_state()
        with self.assertRaises(RuleViolation) as ctx:
            state_machine.rule_refine(state, "深挖成本侧")
        self.assertIn("active", str(ctx.exception))
        self.assertIn("refine", str(ctx.exception))
        done = state_machine.rule_run_terminal(state, "completed")
        refined, record = state_machine.rule_refine(done, "深挖成本侧")
        self.assertEqual(refined.status, "active")
        self.assertEqual(refined.generation, 2)
        self.assertEqual(record.generation, 2)
        self.assertEqual(record.direction_text, "深挖成本侧")
        with self.assertRaises(RuleViolation):
            state_machine.rule_refine(done, "")

    def test_terminal_transitions_follow_the_declared_rules(self) -> None:
        state = _active_state()
        # The pump may not honestly declare `cancelled` without a recorded request.
        with self.assertRaises(RuleViolation):
            state_machine.rule_run_terminal(state, "cancelled")
        requested = state_machine.rule_cancel(state)
        finished = state_machine.rule_run_terminal(requested, "cancelled")
        self.assertEqual(finished.status, "cancelled")
        completed = state_machine.rule_run_terminal(state, "completed")
        self.assertEqual(completed.status, "completed")
        failed = state_machine.rule_run_terminal(state, "failed-resume")
        self.assertEqual(failed.status, "failed-resume")
        # Terminal states are terminal: no further run-terminal outcome applies.
        for outcome in ("completed", "cancelled", "failed-resume"):
            with self.assertRaises(RuleViolation):
                state_machine.rule_run_terminal(completed, outcome)  # type: ignore[arg-type]

    def test_crash_transfer_is_fail_loud(self) -> None:
        state = _active_state()
        self.assertIsNone(state_machine.rule_crash_transfer(state, owner_alive=True))
        transferred = state_machine.rule_crash_transfer(state, owner_alive=False)
        assert transferred is not None
        self.assertEqual(transferred.status, "failed-resume")
        done = state_machine.rule_run_terminal(state, "completed")
        self.assertIsNone(state_machine.rule_crash_transfer(done, owner_alive=False))


class ClarificationRulesTest(unittest.TestCase):
    def test_predicate_detects_unanswered_ask_clarification(self) -> None:
        observation = clarification.TerminalObservation(
            tool_calls=(
                clarification.TerminalToolCall(call_id="c1", name="ask_clarification", arguments='{"question": "范围选哪国市场？"}'),
                clarification.TerminalToolCall(call_id="c2", name="web_search", arguments="{}"),
            ),
            answered_call_ids=frozenset({"c2"}),
        )
        self.assertTrue(clarification.unanswered_ask_clarification(observation))
        answered = clarification.TerminalObservation(
            tool_calls=observation.tool_calls,
            answered_call_ids=frozenset({"c1", "c2"}),
        )
        self.assertFalse(clarification.unanswered_ask_clarification(answered))

    def test_question_text_extraction(self) -> None:
        self.assertEqual(clarification.question_text('{"question": "范围选哪国市场？"}'), "范围选哪国市场？")
        self.assertEqual(clarification.question_text("not json"), "not json")

    def test_bounded_continuation_exhaustion_transfers_to_failed_resume(self) -> None:
        state = _active_state()
        step_one = state_machine.rule_clarification_step(state, detected=True)
        self.assertEqual(step_one.status, "active")
        self.assertEqual(step_one.auto_proceed_count, 1)
        step_two = state_machine.rule_clarification_step(step_one, detected=True)
        self.assertEqual(step_two.status, "active")
        self.assertEqual(step_two.auto_proceed_count, 2)
        exhausted = state_machine.rule_clarification_step(step_two, detected=True)
        self.assertEqual(exhausted.status, "failed-resume")
        self.assertEqual(exhausted.auto_proceed_count, 2)

    def test_no_detection_keeps_state(self) -> None:
        state = _active_state()
        same = state_machine.rule_clarification_step(state, detected=False)
        self.assertEqual(same, state)


class JournalPolicyTest(unittest.TestCase):
    def test_category_set_is_closed(self) -> None:
        self.assertEqual(
            journal_policy.JOURNAL_CATEGORIES,
            ("admission", "lifecycle", "model_tool", "subagent", "validation", "submit", "exhaustion", "terminal"),
        )
        self.assertEqual(journal_policy.check_category("model_tool"), "model_tool")
        with self.assertRaises(RuleViolation) as ctx:
            journal_policy.check_category("gossip")
        self.assertIn("gossip", str(ctx.exception))

    def _entries(self, count: int) -> tuple[journal_policy.JournalEntry, ...]:
        return tuple(
            journal_policy.JournalEntry(
                timestamp=f"2026-10-03T00:00:{i:02d}Z",
                category="admission" if i % 10 == 0 else "model_tool",
                event="e",
                detail={},
            )
            for i in range(count)
        )

    def test_eviction_never_touches_anchors(self) -> None:
        entries = self._entries(30)
        kept = journal_policy.select_retained(entries, bound=10)
        self.assertLessEqual(len(kept), 10)
        kept_index = {id(entry) for entry in kept}
        for i, entry in enumerate(entries):
            if entry.category == "admission":
                self.assertIn(id(entry), kept_index, f"admission anchor {i} evicted")

    def test_compaction_threshold_and_tail(self) -> None:
        self.assertFalse(journal_policy.needs_compaction(10))
        self.assertTrue(journal_policy.needs_compaction(journal_policy.COMPACTION_THRESHOLD))
        entries = self._entries(journal_policy.COMPACTION_THRESHOLD + 5)
        kept = journal_policy.select_compaction_keep(entries)
        kept_index = {id(entry) for entry in kept}
        for i, entry in enumerate(entries):
            if entry.category == "admission":
                self.assertIn(id(entry), kept_index)
        tail = [entry for entry in entries if id(entry) in kept_index and entry.category != "admission"]
        self.assertGreater(len(tail), 0)
        self.assertIs(tail[-1], entries[-1])


class FreshThreadRefineTest(unittest.TestCase):
    def _terminal(self):
        return state_machine.rule_run_terminal(_active_state(), "completed")

    def test_fresh_refine_migrates_thread_and_records_lineage(self) -> None:
        done = self._terminal()
        fresh_id = "0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b"
        refined, _ = state_machine.rule_refine(done, "深挖", next_thread_id=fresh_id)
        self.assertEqual(refined.thread_id, fresh_id)
        self.assertEqual(refined.prior_thread_ids, (done.thread_id,))

    def test_same_thread_refine_is_unchanged(self) -> None:
        done = self._terminal()
        refined, _ = state_machine.rule_refine(done, "深挖")
        self.assertEqual(refined.thread_id, done.thread_id)
        self.assertEqual(refined.prior_thread_ids, ())


class DeliveryDispositionTest(unittest.TestCase):
    """The orthogonal delivered-fact: admitted/rejected/no-answer in state."""

    def test_delivery_field_validates_and_roundtrips(self) -> None:
        from dataclasses import replace

        base = _active_state()
        for delivery, artifact in (
            ("admitted", "final/report-gen1.md"),
            ("rejected", None),
            ("no-answer", None),
            (None, None),
        ):
            with self.subTest(delivery=delivery):
                state = replace(base, delivery=delivery, delivery_artifact=artifact)
                state.validate()
                raw = state.to_dict()
                self.assertEqual(raw["delivery"], delivery)
                self.assertEqual(raw["delivery_artifact"], artifact)
                loaded = state_machine.BundleState.from_dict(raw)
                self.assertEqual(loaded.delivery, delivery)
                self.assertEqual(loaded.delivery_artifact, artifact)

    def test_delivery_validate_rules(self) -> None:
        from dataclasses import replace

        base = _active_state()
        with self.assertRaises(RuleViolation):
            replace(base, delivery="bogus").validate()
        with self.assertRaises(RuleViolation):
            replace(base, delivery="admitted", delivery_artifact=None).validate()
        with self.assertRaises(RuleViolation):
            replace(base, delivery="rejected", delivery_artifact="final/x.md").validate()

    def test_pre_change_state_json_reads_as_not_recorded(self) -> None:
        raw = _active_state().to_dict()
        raw.pop("delivery", None)
        raw.pop("delivery_artifact", None)
        loaded = state_machine.BundleState.from_dict(raw)
        self.assertIsNone(loaded.delivery)
        self.assertIsNone(loaded.delivery_artifact)


if __name__ == "__main__":
    unittest.main()
