#!/usr/bin/env python3
"""Enforce declared code-size budgets over the governance checkers themselves.

Nothing watched these scripts' own size until this gate existed: the import
matrix in `check_project_architecture.py` walks the harness source root only, and
`DOC_BUDGETS` manages resident instruction documents in characters. A checker grew
to 1,473 lines with no alarm, and stages 1–2 of the code-health work paid that
down by hand. This is the machine that notices next time.

Declared ceilings only fall. Lowering one is an ordinary edit; raising one needs a
one-line justification next to the entry, because the number is the whole point.

@impl DOB-001"""

from __future__ import annotations

import argparse
import ast
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

GOVERNANCE_DIR = Path("openspec/governance")
LONG_FUNCTION_THRESHOLD = 50


@dataclass(frozen=True)
class FileBudget:
    """A managed file's ceilings: total lines, and functions above the threshold."""

    max_lines: int
    max_long_functions: int


# ---------------------------------------------------------------------------
# Ceilings ratchet DOWN. Lowering one is an ordinary edit. Raising one requires
# a one-line justification here, next to the entry, in the same diff.
#
# Every number below is the measured value at adoption (establish-code-budgets,
# 2026-10-16), i.e. the file exactly fills its budget: this gate starts green and
# only ever gets tighter on its own.
#
# Measure AFTER the last edit to a file, never before. Adoption measured
# check_ci_governance.py at 189 lines and then the same change added three
# declaration lines to it (192) -- the gate caught exactly that drift on its own
# first real run, which is the behaviour it exists for.
# ---------------------------------------------------------------------------
CODE_BUDGETS: dict[str, FileBudget] = {
    # The guard split into doc_hygiene_check/ (thin entry as of 2026-10-16).
    "check_doc_hygiene.py": FileBudget(max_lines=87, max_long_functions=0),
    "doc_hygiene_check/__init__.py": FileBudget(max_lines=143, max_long_functions=0),
    "doc_hygiene_check/cli.py": FileBudget(max_lines=47, max_long_functions=0),
    "doc_hygiene_check/constants.py": FileBudget(max_lines=237, max_long_functions=0),
    "doc_hygiene_check/ledger.py": FileBudget(max_lines=322, max_long_functions=1),
    "doc_hygiene_check/rules.py": FileBudget(max_lines=283, max_long_functions=0),
    "doc_hygiene_check/scope.py": FileBudget(max_lines=67, max_long_functions=0),
    # The battery split into doc_hygiene_battery/ (thin re-export as of 2026-10-17).
    "_battery.py": FileBudget(max_lines=118, max_long_functions=0),
    "doc_hygiene_battery/__init__.py": FileBudget(max_lines=226, max_long_functions=0),
    "doc_hygiene_battery/fixtures.py": FileBudget(max_lines=448, max_long_functions=0),
    "doc_hygiene_battery/registry.py": FileBudget(max_lines=386, max_long_functions=0),
    # 464 -> 445: its local fence stripper moved to markdown_fences.py.
    "check_project_specs.py": FileBudget(max_lines=445, max_long_functions=2),
    "change_guidance_check/proposals.py": FileBudget(max_lines=462, max_long_functions=3),
    "project_architecture_check/manifest.py": FileBudget(max_lines=433, max_long_functions=3),
    "change_guidance_check/guidance.py": FileBudget(max_lines=408, max_long_functions=3),
    "project_architecture_check/imports.py": FileBudget(max_lines=332, max_long_functions=0),
    "project_architecture_check/cycles.py": FileBudget(max_lines=203, max_long_functions=0),
    "project_architecture_check/markdown_grammar.py": FileBudget(max_lines=119, max_long_functions=0),
    "project_architecture_check/graduation.py": FileBudget(max_lines=75, max_long_functions=0),
    "check_project_gate.py": FileBudget(max_lines=261, max_long_functions=0),
    "markdown_fences.py": FileBudget(max_lines=83, max_long_functions=0),
    # The fence rule moved to markdown_fences.py (295 -> 257); the split follow-up stands.
    "selected_change_closeout.py": FileBudget(max_lines=257, max_long_functions=1),
    "change_guidance_check/reviews.py": FileBudget(max_lines=248, max_long_functions=1),
    "check_proof_receipts.py": FileBudget(max_lines=232, max_long_functions=1),
    "change_guidance_check/constants.py": FileBudget(max_lines=197, max_long_functions=0),
    "project_architecture_check/inspect_tree.py": FileBudget(max_lines=191, max_long_functions=1),
    "check_ci_governance.py": FileBudget(max_lines=192, max_long_functions=1),
}


def _long_functions(path: Path) -> list[tuple[str, int]]:
    """(name, length) of every function longer than the declared threshold."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            if length > LONG_FUNCTION_THRESHOLD:
                found.append((node.name, length))
    return sorted(found, key=lambda item: item[1], reverse=True)


def violations(
    root: Path,
    budgets: dict[str, FileBudget] | None = None,
    *,
    base_dir: Path = GOVERNANCE_DIR,
) -> list[str]:
    """Every managed file that is missing, too long, or too full of long functions.

    ``base_dir`` exists so the self-test can point the same rule at a temporary
    tree; production callers never pass it.
    """
    table = CODE_BUDGETS if budgets is None else budgets
    base = root / base_dir
    problems: list[str] = []
    for relative, budget in sorted(table.items()):
        path = base / relative
        if not path.is_file():
            problems.append(f"missing managed code path: {(base_dir / relative).as_posix()}")
            continue
        text = path.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        if lines > budget.max_lines:
            problems.append(
                f"governance script over line budget: {relative} ({lines} > {budget.max_lines}); "
                "shrink it, or justify raising the ceiling with a one-line note next to the "
                "CODE_BUDGETS entry"
            )
        long_functions = _long_functions(path)
        if len(long_functions) > budget.max_long_functions:
            worst = ", ".join(f"{name} ({length}L)" for name, length in long_functions)
            problems.append(
                f"governance script over long-function budget: {relative} "
                f"({len(long_functions)} > {budget.max_long_functions} functions longer than "
                f"{LONG_FUNCTION_THRESHOLD} lines: {worst}); split them, or justify raising the "
                "ceiling with a one-line note next to the CODE_BUDGETS entry"
            )
    return problems


def _self_test() -> list[str]:
    """Planted defects: an over-limit file and an over-length function must be reported."""
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "governance"   # mirrors GOVERNANCE_DIR, one level down
        base.mkdir(parents=True)
        budgets = {
            "too_long.py": FileBudget(max_lines=5, max_long_functions=0),
            "too_many_long_functions.py": FileBudget(max_lines=500, max_long_functions=0),
            "fine.py": FileBudget(max_lines=50, max_long_functions=1),
        }

        (base / "too_long.py").write_text("x = 1\n" * 40, encoding="utf-8")
        body = "\n".join(f"    y{i} = {i}" for i in range(60))
        (base / "too_many_long_functions.py").write_text(
            f"def long_one():\n{body}\n\n\ndef short():\n    return 1\n", encoding="utf-8"
        )
        (base / "fine.py").write_text("def short():\n    return 1\n", encoding="utf-8")

        found = violations(Path(tmp), budgets, base_dir=Path("governance"))
        if not any("over line budget: too_long.py" in problem for problem in found):
            errors.append("self-test: over-limit file not detected")
        if not any("over long-function budget: too_many_long_functions.py" in problem for problem in found):
            errors.append("self-test: over-length function not detected")
        if any("fine.py" in problem for problem in found):
            errors.append("self-test: a file inside its budget was flagged")

        missing = violations(
            Path(tmp), {"absent.py": FileBudget(max_lines=1, max_long_functions=0)},
            base_dir=Path("governance"),
        )
        if not any("missing managed code path: governance/absent.py" in problem for problem in missing):
            errors.append("self-test: missing managed file not detected")

        if not missing:
            errors.append("self-test: missing-path branch unreachable")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--self-test", action="store_true", help="run negative-control fixtures")
    args = parser.parse_args(argv)

    if args.self_test:
        errs = _self_test()
        if errs:
            print("code-budget self-test FAILED:", file=sys.stderr)
            print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
            return 1
        print("code-budget self-test passed.")
        return 0

    found = violations(Path(args.project_root).resolve())
    if found:
        print("governance code-budget violations:", file=sys.stderr)
        print("\n".join(f"- {v}" for v in found), file=sys.stderr)
        return 1
    print("governance code budgets passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
