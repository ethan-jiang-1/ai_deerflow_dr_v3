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


def _suite_ids() -> set[str]:
    suite = unittest.defaultTestLoader.discover(str(TESTS))
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


if __name__ == "__main__":
    unittest.main()
