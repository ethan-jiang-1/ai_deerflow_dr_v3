"""Collection guard: the default gate discovers unit+contract, never integration.

Locks the discovery contract of the test tree (design owner: the 2026-10-05
plan Phase 3): the four unit owner packages carry package markers so recursive
unittest discovery reaches them; ``tests/integration`` deliberately has no
package marker anywhere so the default offline gate cannot import it (the
integration lane is ``make smoke``); and an in-process discovery from ``tests``
yields only ``tests.unit.*`` and ``tests.contract.*`` test ids.
"""

from __future__ import annotations

import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parents[1]
UNIT = TESTS / "unit"
INTEGRATION = TESTS / "integration"

OWNER_PACKAGES = ("domain", "engine", "runtime", "interaction")


def _suite_ids(root: Path = TESTS) -> set[str]:
    suite = unittest.defaultTestLoader.discover(str(root))
    ids: set[str] = set()

    def walk(item: unittest.TestSuite | unittest.TestCase) -> None:
        if isinstance(item, unittest.TestSuite):
            for child in item:
                walk(child)
        else:
            ids.add(item.id())

    walk(suite)
    return ids


class MarkerInvariantsTest(unittest.TestCase):
    def test_owner_and_contract_package_markers_exist(self) -> None:
        missing = [
            str(marker.relative_to(TESTS))
            for marker in [
                *(UNIT / owner / "__init__.py" for owner in OWNER_PACKAGES),
                UNIT / "__init__.py",
                TESTS / "contract" / "__init__.py",
            ]
            if not marker.is_file()
        ]
        self.assertEqual(missing, [], f"missing package markers: {missing}")

    def test_integration_has_no_package_marker_anywhere(self) -> None:
        planted = [
            str(path.relative_to(TESTS))
            for path in INTEGRATION.rglob("__init__.py")
        ]
        self.assertEqual(
            planted, [],
            "tests/integration must stay marker-free for default-gate "
            f"isolation; planted markers found: {planted}",
        )


class DiscoveryScopeTest(unittest.TestCase):
    def test_default_discovery_excludes_integration(self) -> None:
        ids = _suite_ids()
        self.assertTrue(ids, "default discovery found nothing")
        leaked = sorted(i for i in ids if ".integration" in i)
        self.assertEqual(
            leaked, [],
            f"integration tests leaked into the default gate: {leaked}",
        )

    def test_default_discovery_covers_all_owners_and_contract(self) -> None:
        ids = _suite_ids()
        for namespace in (
            *(f"unit.{owner}." for owner in OWNER_PACKAGES),
            "contract.",
        ):
            self.assertTrue(
                any(i.startswith(namespace) for i in ids),
                f"default discovery misses namespace {namespace!r}",
            )


class KnownViolationNegativeControlTest(unittest.TestCase):
    """Proves the failure the guard watches for can actually happen.

    The positive checks above assert the real tree is marker-free in
    ``tests/integration``. This control builds a tree where that invariant is
    broken (the integration directory carries a package marker) and shows, through
    the *same* discovery machinery, that integration tests then leak into the
    default gate's scope. Without this, the guard could pass for the wrong reason
    (for example if discovery stopped recursing at all) and nobody would notice.
    """

    def test_a_marked_integration_directory_leaks_into_default_discovery(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tests"
            (root / "unit" / "demo").mkdir(parents=True)
            (root / "unit" / "__init__.py").write_text("", encoding="utf-8")
            (root / "unit" / "demo" / "__init__.py").write_text("", encoding="utf-8")
            (root / "unit" / "demo" / "test_inside.py").write_text(
                "import unittest\n\n\nclass T(unittest.TestCase):\n"
                "    def test_inside(self):\n        pass\n",
                encoding="utf-8",
            )
            (root / "integration").mkdir(parents=True)
            (root / "integration" / "__init__.py").write_text("", encoding="utf-8")
            (root / "integration" / "test_leaked.py").write_text(
                "import unittest\n\n\nclass L(unittest.TestCase):\n"
                "    def test_leaked(self):\n        pass\n",
                encoding="utf-8",
            )

            # top_level_dir makes the temporary tree the id namespace root, so the
            # control can assert on the discovered prefixes directly.
            ids = _suite_ids(root)
            suite = unittest.defaultTestLoader.discover(str(root), top_level_dir=str(root))
            ids = set()

            def walk(item) -> None:
                if isinstance(item, unittest.TestSuite):
                    for child in item:
                        walk(child)
                else:
                    ids.add(item.id())

            walk(suite)

        leaked = sorted(i for i in ids if i.split(".")[0] == "integration")
        self.assertTrue(
            leaked,
            "a marked integration directory must leak into default discovery — "
            "this control is what proves the guard's positive check can fail; "
            f"discovered ids were {sorted(ids)}",
        )


if __name__ == "__main__":
    unittest.main()
