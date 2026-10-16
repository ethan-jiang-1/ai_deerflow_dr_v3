"""Direct tests for the module-cycle guard.

The rule exists because two cycles were repaired by hand before it did: the
doc-hygiene entry against its battery, and fixtures against registry inside the
battery package. Neither was visible to any other checker, and a module cycle is
the kind of defect that shows up only when the wrong side is imported first.

Every case is built in a temporary tree — nothing here touches the real repository,
and nothing shells out: the rule is called in process, like the checkers do.

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
from project_architecture_check.cycles import validate_no_import_cycles  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]


class CycleCase(unittest.TestCase):
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

    def violation(self, files: dict[str, str]) -> ContractViolation:
        root = self.tree(files)
        with self.assertRaises(ContractViolation) as caught:
            validate_no_import_cycles(root)
        return caught.exception


class CyclicShapesTest(CycleCase):
    def test_two_modules_importing_each_other_are_reported(self) -> None:
        violation = self.violation({"a.py": "from .b import x\n", "b.py": "from .a import x\n"})
        self.assertEqual(violation.code, "import.cycle")
        self.assertIn("a.py", violation.detail)
        self.assertIn("b.py", violation.detail)

    def test_a_three_module_ring_is_reported_even_though_no_pair_is_mutual(self) -> None:
        # A pairwise mutual-import check would pass this tree; the component walk does not.
        violation = self.violation({
            "a.py": "from .b import x\n",
            "b.py": "from .c import x\n",
            "c.py": "from .a import x\n",
        })
        self.assertIn("a.py", violation.detail)
        self.assertIn("c.py", violation.detail)

    def test_same_directory_absolute_imports_are_edges_too(self) -> None:
        # The governance scripts import their siblings by bare name (gitio, roots,
        # markdown_fences) because the directory is on sys.path.
        violation = self.violation({"a.py": "import b\n", "b.py": "import a\n"})
        self.assertEqual(violation.code, "import.cycle")

    def test_a_package_init_cycle_is_reported(self) -> None:
        violation = self.violation({
            "pkg/__init__.py": "from .leaf import x\n",
            "pkg/leaf.py": "from pkg import y\n",
        })
        self.assertIn("pkg/__init__.py", violation.detail)


class LegalShapesTest(CycleCase):
    def test_deferred_import_inside_a_function_is_not_an_edge(self) -> None:
        # This is the repository's established way of breaking a cycle.
        validate_no_import_cycles(self.tree({
            "a.py": "def f():\n    from .b import x\n    return x\n",
            "b.py": "from .a import f\n",
        }))

    def test_a_type_checking_block_is_not_an_edge(self) -> None:
        validate_no_import_cycles(self.tree({
            "a.py": "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from .b import T\n",
            "b.py": "from .a import f\n",
        }))

    def test_a_one_way_facade_reexport_is_not_a_cycle(self) -> None:
        validate_no_import_cycles(self.tree({
            "impl.py": "def f():\n    return 1\n",
            "facade.py": "from .impl import f\n",
        }))

    def test_a_lone_module_is_clean(self) -> None:
        validate_no_import_cycles(self.tree({"only.py": "import ast\n"}))


class RealTreeTest(unittest.TestCase):
    def test_the_repository_has_no_module_cycle(self) -> None:
        # The two cycles this session removed are gone; a new one must fail here.
        validate_no_import_cycles(REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
