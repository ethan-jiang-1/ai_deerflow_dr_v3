"""Direct unit coverage for the closeout tool's decision logic.

The tool was un-importable until the 2026-10-16 rename, so all seven of its decision
functions had **zero** direct coverage: they could only be reached end to end through
a subprocess. End-to-end cannot see rejection paths — a validator that only ever ran
on valid input looks identical to one that really refuses invalid input. These tests
drive the functions directly (a real ``import``) and give every guard a refusal case,
so each one is shown able to fail.

The tool's own file is not modified by this change; a decision that turns out to be
wrong is recorded rather than silently repaired here.

@impl DEW-001"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GOVERNANCE = REPO_ROOT / "openspec" / "governance"


def _import_tool():
    sys.path.insert(0, str(GOVERNANCE))
    try:
        import selected_change_closeout as tool  # noqa: PLC0415 — the import IS the point
    finally:
        sys.path.remove(str(GOVERNANCE))
    return tool


TOOL = _import_tool()


class TempCase(unittest.TestCase):
    """A temporary directory that several cases use as a stand-in repository."""

    def temp_dir(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name).resolve()


class AttestationParsingTest(TempCase):
    def valid_payload(self) -> dict:
        return {
            "change_name": "some-change",
            "repository_identity": "some-identity",
            "base_commit": "a" * 40,
            "head_commit": "b" * 40,
        }

    def test_accepts_a_complete_attestation(self) -> None:
        parsed = TOOL._parse_attestation(self.valid_payload())
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.change_name, "some-change")
        self.assertEqual(parsed.head_commit, "b" * 40)

    def test_rejects_a_non_mapping(self) -> None:
        for value in ([], "text", 7, None):
            with self.subTest(value=value):
                self.assertIsNone(TOOL._parse_attestation(value))

    def test_rejects_every_missing_field(self) -> None:
        for field in TOOL.REQUIRED_ATTESTATION_FIELDS:
            with self.subTest(missing=field):
                payload = self.valid_payload()
                del payload[field]
                self.assertIsNone(TOOL._parse_attestation(payload))

    def test_rejects_blank_and_non_string_fields(self) -> None:
        for field, bad in (
            ("change_name", "   "),
            ("repository_identity", ""),
            ("base_commit", 40),
            ("head_commit", None),
        ):
            with self.subTest(field=field, bad=bad):
                payload = self.valid_payload()
                payload[field] = bad
                self.assertIsNone(TOOL._parse_attestation(payload))


class PlanningHomeTest(TempCase):
    def test_finds_the_nearest_planning_home(self) -> None:
        root = self.temp_dir()
        (root / "openspec" / "changes").mkdir(parents=True)
        deep = root / "a" / "b" / "c"
        deep.mkdir(parents=True)
        self.assertEqual(TOOL._planning_home(deep), root)

    def test_returns_none_when_no_planning_home_exists(self) -> None:
        root = self.temp_dir()
        (root / "a" / "b").mkdir(parents=True)
        self.assertIsNone(TOOL._planning_home(root / "a" / "b"))


class ActiveChangeRootTest(TempCase):
    def planning_home_with(self, change_name: str) -> Path:
        root = self.temp_dir()
        (root / "openspec" / "changes" / change_name).mkdir(parents=True)
        previous = Path.cwd()
        os.chdir(root)
        self.addCleanup(os.chdir, previous)
        return root

    def test_resolves_an_existing_change(self) -> None:
        root = self.planning_home_with("real-change")
        resolved = TOOL._active_change_root("real-change")
        self.assertEqual(resolved, (root / "openspec" / "changes" / "real-change").resolve())

    def test_rejects_path_shaped_names(self) -> None:
        self.planning_home_with("real-change")
        for name in ("", ".", "..", "a/b", "../real-change", "nested/real-change"):
            with self.subTest(name=name):
                self.assertIsNone(TOOL._active_change_root(name))

    def test_returns_none_for_an_unknown_change(self) -> None:
        self.planning_home_with("real-change")
        self.assertIsNone(TOOL._active_change_root("absent-change"))


class ResolvedCommitTest(TempCase):
    def repository(self) -> Path:
        repo = self.temp_dir()
        for command in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "t@example.invalid"],
            ["git", "config", "user.name", "test"],
        ):
            subprocess.run(command, cwd=repo, check=True, capture_output=True)
        (repo / "file.txt").write_text("content\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "one"], cwd=repo, check=True, capture_output=True)
        return repo

    def test_resolves_a_real_commit(self) -> None:
        repo = self.repository()
        resolved = TOOL._resolved_commit(repo, "HEAD")
        self.assertIsNotNone(resolved)
        self.assertEqual(len(resolved), 40)
        self.assertTrue(all(character in "0123456789abcdef" for character in resolved))

    def test_returns_none_for_an_unknown_reference(self) -> None:
        repo = self.repository()
        self.assertIsNone(TOOL._resolved_commit(repo, "no-such-ref"))


class VerifyBoundaryRejectionTest(TempCase):
    def test_an_unknown_change_is_rejected_without_a_change_root(self) -> None:
        root = self.temp_dir()
        (root / "openspec" / "changes").mkdir(parents=True)
        previous = Path.cwd()
        os.chdir(root)
        self.addCleanup(os.chdir, previous)
        attestation = TOOL.Attestation("absent-change", "identity", "a" * 40, "b" * 40)
        record, change_root = TOOL._verify_boundary(attestation)
        self.assertIsNone(change_root)
        self.assertEqual(record["schema_version"], TOOL.SCHEMA_VERSION)
        self.assertIn("result", record)
        self.assertIn("condition", record)


class FencedCodeBlockTest(TempCase):
    """A checkbox inside a fenced code block is an example, not a task (BUG-003).

    These tests are the inversion of the two that locked the defect: they used to assert
    the fenced line WAS collected, and named the way to invert them. The parser is now
    fence-aware (CommonMark 4.5), so the assertions read the other way round.
    """

    def labels(self, text: str) -> set[str]:
        root = self.temp_dir()
        (root / "tasks.md").write_text(text, encoding="utf-8")
        return TOOL._unchecked_task_labels(root)

    def test_a_fenced_checkbox_is_not_a_task(self) -> None:
        labels = self.labels(
            "# Tasks\n\n- [ ] real task\n\n```\n- [ ] example inside a fence\n```\n"
        )
        self.assertEqual(labels, {"real task"})

    def test_text_after_a_closing_fence_is_scanned_again(self) -> None:
        labels = self.labels("- [ ] before\n```\n- [ ] fenced\n```\n- [ ] after\n")
        self.assertEqual(labels, {"before", "after"})

    def test_a_tilde_fence_is_a_fence_too(self) -> None:
        labels = self.labels("- [ ] before\n~~~\n- [ ] fenced\n~~~\n- [ ] after\n")
        self.assertEqual(labels, {"before", "after"})

    def test_a_longer_closing_fence_closes(self) -> None:
        labels = self.labels("- [ ] before\n````\n- [ ] fenced\n`````\n- [ ] after\n")
        self.assertEqual(labels, {"before", "after"})

    def test_a_shorter_closing_fence_does_not_close(self) -> None:
        labels = self.labels("- [ ] before\n````\n- [ ] fenced\n```\n- [ ] still fenced\n")
        self.assertEqual(labels, {"before"})

    def test_an_opening_fence_may_carry_an_info_string(self) -> None:
        labels = self.labels("- [ ] before\n```python\n- [ ] fenced\n```\n- [ ] after\n")
        self.assertEqual(labels, {"before", "after"})

    def test_a_closing_fence_with_trailing_text_does_not_close(self) -> None:
        labels = self.labels(
            "- [ ] before\n```\n- [ ] fenced\n``` not a close\n- [ ] after\n"
        )
        self.assertEqual(labels, {"before"})

    def test_an_unclosed_fence_runs_to_the_end(self) -> None:
        labels = self.labels("- [ ] before\n```\n- [ ] fenced\n- [ ] also fenced\n")
        self.assertEqual(labels, {"before"})

    def test_an_indented_four_space_fence_is_indented_code_not_a_fence(self) -> None:
        # Documented scoping decision: tasks.md legitimately nests task items four
        # spaces deep, so only fences are skipped, never indented code.
        labels = self.labels("    ```\n- [ ] a deeply nested task\n")
        self.assertEqual(labels, {"a deeply nested task"})

    def test_the_defect_no_longer_reaches_review_validation(self) -> None:
        root = self.temp_dir()
        (root / "closeout-evidence").mkdir(parents=True)
        (root / "tasks.md").write_text("```\n- [ ] fenced example\n```\n", encoding="utf-8")
        payload, problem = TOOL._validate_review(
            {"disposition": "review-required", "task_references": ["fenced example"]},
            root,
            root / "closeout-evidence" / "review.json",
        )
        self.assertIsNone(payload)
        self.assertEqual(problem["condition"], "unknown-unchecked-task")


class UncheckedTaskLabelsTest(TempCase):
    def tasks_file(self, text: str) -> Path:
        root = self.temp_dir()
        (root / "tasks.md").write_text(text, encoding="utf-8")
        return root

    def test_parses_the_three_bullet_markers(self) -> None:
        root = self.tasks_file(
            "- [ ] dash\n* [ ] star\n+ [ ] plus\n  - [ ] indented\n"
        )
        self.assertEqual(
            TOOL._unchecked_task_labels(root), {"dash", "star", "plus", "indented"}
        )

    def test_ignores_checked_tasks_and_blank_labels(self) -> None:
        root = self.tasks_file("- [x] done\n- [X] also\n- [ ]    \n- [ ] kept\n")
        self.assertEqual(TOOL._unchecked_task_labels(root), {"kept"})

    def test_a_missing_tasks_file_yields_nothing(self) -> None:
        self.assertEqual(TOOL._unchecked_task_labels(self.temp_dir()), set())

    def test_non_task_lines_are_ignored(self) -> None:
        root = self.tasks_file("# Heading\nprose\n1. [ ] numbered\n- [] malformed\n")
        self.assertEqual(TOOL._unchecked_task_labels(root), set())


class ValidateReviewTest(TempCase):
    def change_root(self) -> Path:
        root = self.temp_dir()
        (root / "closeout-evidence").mkdir(parents=True)
        (root / "tasks.md").write_text("- [ ] alpha\n- [ ] beta\n", encoding="utf-8")
        return root

    def output_inside(self, change_root: Path) -> Path:
        return change_root / "closeout-evidence" / "review.json"

    def test_accepts_a_review_required_payload(self) -> None:
        root = self.change_root()
        payload, problem = TOOL._validate_review(
            {"disposition": "review-required", "task_references": ["alpha"]},
            root,
            self.output_inside(root),
        )
        self.assertIsNone(problem)
        self.assertEqual(payload, {"disposition": "review-required", "task_references": ["alpha"]})

    def test_accepts_an_inconclusive_payload(self) -> None:
        root = self.change_root()
        payload, problem = TOOL._validate_review(
            {"disposition": "inconclusive", "evidence_limitation": "no reviewer available"},
            root,
            self.output_inside(root),
        )
        self.assertIsNone(problem)
        self.assertEqual(payload["disposition"], "inconclusive")

    def test_rejects_an_output_path_outside_the_evidence_root(self) -> None:
        root = self.change_root()
        payload, problem = TOOL._validate_review(
            {"disposition": "inconclusive", "evidence_limitation": "x"},
            root,
            root / "elsewhere.json",
        )
        self.assertIsNone(payload)
        self.assertEqual(problem["condition"], "output-path-outside-evidence")

    def test_rejects_a_non_mapping_payload(self) -> None:
        root = self.change_root()
        payload, problem = TOOL._validate_review(["not"], root, self.output_inside(root))
        self.assertIsNone(payload)
        self.assertEqual(problem["condition"], "missing-review-payload")

    def test_rejects_an_unsupported_disposition(self) -> None:
        root = self.change_root()
        for disposition in ("approved", "", None, 3):
            with self.subTest(disposition=disposition):
                payload, problem = TOOL._validate_review(
                    {"disposition": disposition}, root, self.output_inside(root)
                )
                self.assertIsNone(payload)
                self.assertEqual(problem["condition"], "unsupported-disposition")

    def test_rejects_review_required_without_usable_references(self) -> None:
        root = self.change_root()
        for references in (None, [], "alpha", ["alpha", ""], ["alpha", 3]):
            with self.subTest(references=references):
                payload, problem = TOOL._validate_review(
                    {"disposition": "review-required", "task_references": references},
                    root,
                    self.output_inside(root),
                )
                self.assertIsNone(payload)
                self.assertEqual(problem["condition"], "missing-task-reference")

    def test_rejects_a_reference_that_is_not_an_unchecked_task(self) -> None:
        root = self.change_root()
        payload, problem = TOOL._validate_review(
            {"disposition": "review-required", "task_references": ["gamma"]},
            root,
            self.output_inside(root),
        )
        self.assertIsNone(payload)
        self.assertEqual(problem["condition"], "unknown-unchecked-task")

    def test_rejects_inconclusive_without_a_limitation(self) -> None:
        root = self.change_root()
        for limitation in (None, "", "   ", 7):
            with self.subTest(limitation=limitation):
                payload, problem = TOOL._validate_review(
                    {"disposition": "inconclusive", "evidence_limitation": limitation},
                    root,
                    self.output_inside(root),
                )
                self.assertIsNone(payload)
                self.assertEqual(problem["condition"], "missing-evidence-limitation")


if __name__ == "__main__":
    unittest.main()


class VerifyBoundaryTest(TempCase):
    """The full boundary check: success, plus each way it can refuse."""

    def repository(self) -> Path:
        repo = self.temp_dir()
        for command in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "t@example.invalid"],
            ["git", "config", "user.name", "test"],
            ["git", "config", "commit.gpgsign", "false"],
        ):
            subprocess.run(command, cwd=repo, check=True, capture_output=True)
        change = repo / "openspec" / "changes" / "the-change"
        change.mkdir(parents=True)
        (change / "tasks.md").write_text("- [ ] alpha\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "one"], cwd=repo, check=True, capture_output=True)
        previous = Path.cwd()
        os.chdir(repo)
        self.addCleanup(os.chdir, previous)
        return repo

    def head(self, repo: Path) -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
        ).stdout.strip()

    def attestation(self, repo: Path, base: str, head: str):
        return TOOL.Attestation("the-change", str(repo), base, head)

    def test_verifies_a_declared_committed_range(self) -> None:
        repo = self.repository()
        head = self.head(repo)
        record, change_root = TOOL._verify_boundary(self.attestation(repo, head, head))
        self.assertEqual(record["result"], "boundary-verified")
        self.assertEqual(record["base_commit"], head)
        self.assertEqual(record["head_commit"], head)
        self.assertEqual(record["range"], f"{head}..{head}")
        self.assertIn("diff_summary", record)
        self.assertIsInstance(record["diff_summary"]["changed_path_count"], int)
        self.assertEqual(len(record["diff_summary"]["sha256"]), 64)
        self.assertEqual(change_root, (repo / "openspec" / "changes" / "the-change").resolve())

    def test_rejects_a_relative_repository_identity(self) -> None:
        repo = self.repository()
        head = self.head(repo)
        record, change_root = TOOL._verify_boundary(
            TOOL.Attestation("the-change", "relative/path", head, head)
        )
        self.assertEqual(record["condition"], "repository-mismatch")
        self.assertIsNone(change_root)

    def test_rejects_an_unknown_commit(self) -> None:
        repo = self.repository()
        record, _ = TOOL._verify_boundary(self.attestation(repo, "0" * 40, self.head(repo)))
        self.assertEqual(record["condition"], "unknown-commit")

    def test_rejects_head_drift(self) -> None:
        repo = self.repository()
        base = self.head(repo)
        (repo / "second.txt").write_text("second\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "two"], cwd=repo, check=True, capture_output=True)
        record, _ = TOOL._verify_boundary(self.attestation(repo, base, base))
        self.assertEqual(record["condition"], "head-drift")

    def test_rejects_a_dirty_worktree(self) -> None:
        repo = self.repository()
        head = self.head(repo)
        (repo / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")
        record, _ = TOOL._verify_boundary(self.attestation(repo, head, head))
        self.assertEqual(record["condition"], "dirty-worktree")
