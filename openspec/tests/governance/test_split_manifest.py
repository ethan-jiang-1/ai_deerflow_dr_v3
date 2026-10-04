"""Focused stdlib tests for the split project-structure manifest (contract file +
owner-grouped required-paths inventory) in check_project_architecture.py.

Canonical maintained command, from the repository root:

    python3 -m unittest openspec.tests.governance.test_split_manifest

All fixtures are built under temp directories and never mutate the repository.
The checker module is loaded in-process via importlib, exactly like the gate
tests load check_project_gate.

"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
CHECKER = GOVERNANCE_DIR / "check_project_architecture.py"

CONTRACT = """schema_version = 1
contract = "project-structure"
[upstream_gitlink]
path = "deerflow"
# Sample value for a temp-dir fixture only; never compared against the real submodule.
# Kept in sync with the live lock out of hygiene, not correctness.
commit = "ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7"

[package]
source_root = "deep_research_harness/src/deerflow_deep_research"
test_root = "deep_research_harness/tests"
ownership_layers = ["runtime", "domain", "engine", "agents"]
forbidden_source_roots = ["backend", "frontend"]
forbidden_shared_modules = ["utils", "helpers", "common"]

[ignored_paths]
path = "deep_research_harness/.gitignore"
entries = ["generated-output/"]

[inventory]
path = "openspec/governance/required-paths.toml"

[imports]
domain = ["stdlib", "pydantic"]
engine = ["domain"]
agents = ["domain", "deerflow", "langchain"]
runtime = ["domain", "engine", "agents", "deerflow", "httpx", "httpx_sse", "langchain", "langgraph", "openai"]

[guide]
path = "deep_research_harness/AGENTS.md"
begin_marker = "<!-- BEGIN TEST -->"
end_marker = "<!-- END TEST -->"
"""

INVENTORY = """schema_version = 1
contract = "project-structure-inventory"

[paths.structure]
files = [
  "openspec/governance/project-structure.toml",
  "openspec/governance/required-paths.toml",
]
directories = [
  "deep_research_harness/src/deerflow_deep_research",
]

[paths.harness-root]
files = [
  "deep_research_harness/.gitignore",
]
"""

# Pre-change `[imports]` table (six keys incl. the removed grammar) and the
# pre-change mandatory `[node_packages]` table: together they let the
# ownership-layer case reach the old checker's accepting path, so its red today
# is "the grammar-declaring manifest validates", not a wrong-code rejection.
LEGACY_SIX_KEY_IMPORTS = """[imports]
domain = ["stdlib", "pydantic"]
engine = ["domain"]
agents = ["domain", "deerflow", "langchain"]
graph = ["domain", "engine", "nodes", "langgraph"]
nodes = ["domain", "engine", "langgraph", "pydantic"]
runtime = ["domain", "graph", "agents", "deerflow", "httpx", "httpx_sse", "langchain", "langgraph", "openai"]"""

LEGACY_NODE_PACKAGES = """
[node_packages]
root = "deep_research_harness/src/deerflow_deep_research/graph/nodes"
required_files = ["__init__.py", "node.py", "contracts.py"]
optional_files = ["subgraph.py", "capabilities.py"]
forbidden_files = ["fake.py"]
public_export = "NODE_SPEC"
"""


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_project_architecture", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _make_repo(tmp: Path, contract: str = CONTRACT, inventory: str = INVENTORY) -> tuple[Path, object]:
    """Minimal repo fixture: contract + inventory + required files."""
    checker = _load_checker()
    root = tmp / "repo"
    (root / "openspec" / "governance").mkdir(parents=True)
    (root / "deep_research_harness" / "src" / "deerflow_deep_research").mkdir(parents=True)
    (root / "openspec" / "governance" / "project-structure.toml").write_text(contract, encoding="utf-8")
    (root / "openspec" / "governance" / "required-paths.toml").write_text(inventory, encoding="utf-8")
    (root / "deep_research_harness" / ".gitignore").write_text("generated-output/\n", encoding="utf-8")
    return root, checker


class SplitManifestParseTest(unittest.TestCase):
    def test_manifest_parses_grouped_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, checker = _make_repo(Path(td))
            manifest = checker.load_manifest(root)
            triples = {(str(item.path), item.kind, item.owner) for item in manifest.required_paths}
            self.assertEqual(
                triples,
                {
                    ("openspec/governance/project-structure.toml", "file", "structure"),
                    ("openspec/governance/required-paths.toml", "file", "structure"),
                    ("deep_research_harness/src/deerflow_deep_research", "directory", "structure"),
                    ("deep_research_harness/.gitignore", "file", "harness-root"),
                },
            )

    def test_validate_required_paths_passes_on_present_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, checker = _make_repo(Path(td))
            manifest = checker.load_manifest(root)
            checker._validate_required_paths(root, manifest)  # must not raise

    def test_missing_inventory_table_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract = CONTRACT.replace("\n[inventory]\npath = \"openspec/governance/required-paths.toml\"\n", "\n")
            root, checker = _make_repo(Path(td), contract=contract)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "inventory.schema")

    def test_inventory_wrong_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract = CONTRACT.replace(
                'path = "openspec/governance/required-paths.toml"', 'path = "openspec/governance/other.toml"'
            )
            root, checker = _make_repo(Path(td), contract=contract)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "inventory.path")

    def test_inventory_file_missing_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, checker = _make_repo(Path(td))
            (root / "openspec" / "governance" / "required-paths.toml").unlink()
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "inventory.missing")

    def test_inventory_not_self_registered_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            inventory = INVENTORY.replace('  "openspec/governance/required-paths.toml",\n', "")
            root, checker = _make_repo(Path(td), inventory=inventory)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "inventory.unregistered")

    def test_duplicate_path_across_sections_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            inventory = INVENTORY.replace(
                '[paths.structure]\nfiles = [\n  "openspec/governance/project-structure.toml",\n  "openspec/governance/required-paths.toml",\n]\ndirectories = [',
                '[paths.structure]\nfiles = [\n  "deep_research_harness/.gitignore",\n]\ndirectories = [',
            )
            root, checker = _make_repo(Path(td), inventory=inventory)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "path.duplicate")

    def test_ignored_file_must_be_registered(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            inventory = INVENTORY.replace('[paths.harness-root]\nfiles = [\n  "deep_research_harness/.gitignore",\n]\n', "")
            root, checker = _make_repo(Path(td), inventory=inventory)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "manifest.schema")

    def test_deleted_registered_file_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, checker = _make_repo(Path(td))
            (root / "deep_research_harness" / ".gitignore").unlink()
            manifest = checker.load_manifest(root)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker._validate_required_paths(root, manifest)
            self.assertEqual(ctx.exception.code, "path.missing")


class RemovedNodeGrammarTest(unittest.TestCase):
    """Negative controls for the removed node-package grammar (remove-graph-layer).

    Case 1 is the vocabulary flip's red engine: the canonical four-layer manifest
    must validate. Cases 2-4 pin the three loud-failure surfaces named by the
    "Removed node grammar fails loudly" scenario.
    """

    def test_canonical_manifest_without_node_grammar_validates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, checker = _make_repo(Path(td), contract=CONTRACT)
            manifest = checker.load_manifest(root)
            self.assertEqual(
                set(manifest.ownership_layers),
                {"runtime", "domain", "engine", "agents"},
            )

    def test_node_packages_table_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract = CONTRACT + LEGACY_NODE_PACKAGES
            root, checker = _make_repo(Path(td), contract=contract)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "node.grammar_removed")

    def test_non_canonical_ownership_layer_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract = (
                CONTRACT.replace(
                    'ownership_layers = ["runtime", "domain", "engine", "agents"]',
                    'ownership_layers = ["runtime", "domain", "engine", "agents", "graph"]',
                )
                .replace(
                    '[imports]\ndomain = ["stdlib", "pydantic"]\nengine = ["domain"]\n'
                    'agents = ["domain", "deerflow", "langchain"]\n'
                    'runtime = ["domain", "agents", "deerflow", "httpx", "httpx_sse", '
                    '"langchain", "langgraph", "openai"]',
                    LEGACY_SIX_KEY_IMPORTS,
                )
                + LEGACY_NODE_PACKAGES
            )
            root, checker = _make_repo(Path(td), contract=contract)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "manifest.schema")

    def test_extra_imports_layer_key_rejected(self) -> None:
        # Regression pin for the closed `[imports]` vocabulary. The old checker also
        # rejects five-key tables (under the same code), so this case is green before
        # and after the change; cases 1-3 carry the red-before-green proof.
        with tempfile.TemporaryDirectory() as td:
            contract = CONTRACT.replace(
                "[imports]\ndomain",
                '[imports]\ngraph = ["domain", "engine", "nodes"]\ndomain',
            )
            root, checker = _make_repo(Path(td), contract=contract)
            with self.assertRaises(checker.ContractViolation) as ctx:
                checker.load_manifest(root)
            self.assertEqual(ctx.exception.code, "manifest.schema")


if __name__ == "__main__":
    unittest.main()
