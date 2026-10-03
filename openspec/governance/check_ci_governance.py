#!/usr/bin/env python3
"""Validate the CI governance declarations without external packages.

Guards the acceptance-path enforcement surface: the CI workflow's triggers,
path filters, pinned toolchain, single-job discipline, and canonical
governance commands, plus the pre-commit hook's exact cheap-check command
set. Validation is textual marker matching only — it proves the declarations
exist and stay intact; it does not prove GitHub executed them (live CI
execution is out of scope for this checker and is UNVERIFIED locally).

@impl CIG-001"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

WORKFLOW_RELATIVE = Path(".github") / "workflows" / "governance.yml"
HOOK_RELATIVE = Path(".githooks") / "pre-commit"

# Every marker must appear verbatim in the workflow file. Triggers, path
# filters, checkout shape, pinned toolchain, and the four canonical commands.
WORKFLOW_REQUIRED_MARKERS: tuple[str, ...] = (
    "push:",
    "pull_request:",
    "openspec/**",
    "deep_research_harness/**",
    ".github/workflows/governance.yml",
    ".githooks/**",
    "submodules: true",
    "actions/setup-python@v5",
    'python-version: "3.12"',
    "@fission-ai/openspec@1.13.1",
    "python3 -m unittest discover -s openspec/tests/governance -q",
    "python3 openspec/governance/check_project_gate.py --phase closeout",
    "python3 openspec/governance/check_doc_hygiene.py",
    "UV_OFFLINE=1 make verify",
    "astral-sh/setup-uv@v7",
    "make smoke",
)

# The hook runs only the two declared cheap checks. Suite, snapshot,
# type-analysis, and build invocations belong to CI and are forbidden here.
FORBIDDEN_HOOK_MARKERS: tuple[str, ...] = (
    "pytest",
    "unittest",
    "mypy",
    "ruff",
    "make verify",
    "make test",
    "tsc",
    "npm run build",
)

# Every non-comment, non-empty hook line must be one of these (allowlist, so
# any undeclared extra command fails loudly).
ALLOWED_HOOK_LINES: frozenset[str] = frozenset(
    {
        "#!/bin/sh",
        "set -e",
        'cd "$(git rev-parse --show-toplevel)"',
        "git diff --cached --check",
        "python3 openspec/governance/check_doc_hygiene.py",
    }
)

HOOK_REQUIRED_MARKERS: tuple[str, ...] = (
    "git diff --cached --check",
    "python3 openspec/governance/check_doc_hygiene.py",
)


def check(root: Path) -> list[str]:
    """Return the list of CI-governance violations for the tree at ``root``."""
    errors: list[str] = []

    workflow = root / WORKFLOW_RELATIVE
    if not workflow.is_file():
        errors.append(f"CI workflow is missing: {WORKFLOW_RELATIVE.as_posix()}")
    else:
        workflow_text = workflow.read_text(encoding="utf-8")
        for marker in WORKFLOW_REQUIRED_MARKERS:
            if marker not in workflow_text:
                errors.append(
                    f"workflow marker missing: {marker!r} ({WORKFLOW_RELATIVE.as_posix()})"
                )
        job_count = workflow_text.count("runs-on:")
        if job_count != 1:
            errors.append(
                "workflow must declare exactly one job (one runs-on:), "
                f"found {job_count} ({WORKFLOW_RELATIVE.as_posix()})"
            )

    hook = root / HOOK_RELATIVE
    if not hook.is_file():
        errors.append(f"pre-commit hook is missing: {HOOK_RELATIVE.as_posix()}")
    else:
        if not os.access(hook, os.X_OK):
            errors.append(f"pre-commit hook is not executable: {HOOK_RELATIVE.as_posix()}")
        hook_text = hook.read_text(encoding="utf-8")
        for marker in HOOK_REQUIRED_MARKERS:
            if marker not in hook_text:
                errors.append(f"hook marker missing: {marker!r} ({HOOK_RELATIVE.as_posix()})")
        for marker in FORBIDDEN_HOOK_MARKERS:
            if marker in hook_text:
                errors.append(
                    f"hook contains a forbidden suite/build command: {marker!r} "
                    f"({HOOK_RELATIVE.as_posix()})"
                )
        for line in hook_text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped not in ALLOWED_HOOK_LINES:
                errors.append(
                    f"hook contains an undeclared command line: {stripped!r} "
                    f"({HOOK_RELATIVE.as_posix()})"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    """Run the CI-governance check; print violations and return the exit code."""
    parser = argparse.ArgumentParser(description="Validate the CI governance declarations.")
    parser.add_argument("project_root", nargs="?", default=Path.cwd(), type=Path)
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    errors = check(root)
    if errors:
        for error in errors:
            print(f"ERROR [ci.governance] {error}", file=sys.stderr)
        return 1
    print(f"CI governance passed for {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
