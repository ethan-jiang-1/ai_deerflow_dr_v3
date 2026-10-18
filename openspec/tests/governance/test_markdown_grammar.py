"""The fence grammar has one implementation, and that is now enforced.

Five hand-written copies produced four distinct defect classes before they were
consolidated. The rule added here keeps a sixth from appearing — and it is written to
the *measured* boundary: a naive "any fence literal in code" rule flags seven places in
this tree, all of them fixture content. So the rule only fires when the marker is used
as a predicate, and the green cases below are the point of the whole exercise.

@impl PRS-001"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from project_architecture_check.contract import ContractViolation  # noqa: E402
from project_architecture_check.markdown_grammar import (  # noqa: E402
    EXEMPT_MODULES,
    validate_single_fence_grammar,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


class GrammarCase(unittest.TestCase):
    def tree(self, files: dict[str, str]) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        governance = root / "openspec" / "governance"
        governance.mkdir(parents=True)
        for name, body in files.items():
            target = governance / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        return root

    def violation(self, body: str, name: str = "mod.py") -> ContractViolation:
        with self.assertRaises(ContractViolation) as caught:
            validate_single_fence_grammar(self.tree({name: body}))
        return caught.exception


class HandWrittenGrammarTest(GrammarCase):
    def test_a_compiled_fence_pattern_is_reported(self) -> None:
        violation = self.violation('import re\nPATTERN = re.compile(r"^ {0,3}```")\n')
        self.assertEqual(violation.code, "markdown.grammar_duplicated")
        self.assertIn("markdown_fences.py", violation.detail)

    def test_a_fence_startswith_predicate_is_reported(self) -> None:
        self.violation('def f(line):\n    return line.strip().startswith("```")\n')

    def test_a_fence_membership_test_is_reported(self) -> None:
        self.violation('def f(line):\n    return "```" in line\n')

    def test_a_tilde_predicate_is_reported(self) -> None:
        self.violation('def f(line):\n    return line.startswith("~~~")\n')


class LegalShapesTest(GrammarCase):
    def test_a_fence_literal_used_as_content_is_not_reported(self) -> None:
        # This shape is why the rule is narrowed: seven of these live in the battery's
        # fixtures, and flagging them would make the guard a wolf-crier.
        validate_single_fence_grammar(
            self.tree({"mod.py": 'CONTENT = "```\\n- [ ] example\\n```\\n"\n'})
        )

    def test_calling_the_canonical_module_is_not_reported(self) -> None:
        validate_single_fence_grammar(self.tree({
            "mod.py": "import markdown_fences\n\n\ndef f(text):\n"
                      "    return markdown_fences.strip_fenced_code_blocks(text)\n"
        }))

    def test_describing_a_fence_in_a_docstring_is_not_reported(self) -> None:
        validate_single_fence_grammar(self.tree({
            "mod.py": 'def f():\n    """A fence opens with ``` and closes the same way."""\n    return 1\n'
        }))

    def test_the_canonical_module_and_this_rule_are_exempt(self) -> None:
        body = 'def f(line):\n    return line.startswith("```")\n'
        validate_single_fence_grammar(
            self.tree({name: body for name in sorted(EXEMPT_MODULES)})
        )


class RealTreeTest(unittest.TestCase):
    def test_the_governance_tree_has_one_fence_grammar(self) -> None:
        validate_single_fence_grammar(REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
