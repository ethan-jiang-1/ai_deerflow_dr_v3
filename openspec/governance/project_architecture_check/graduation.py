"""A graduated bug card lands in the same commit as the work it records.

The rule this encodes was, until now, only a habit: when a bug is fixed, the card's
graduation flip (status to 已修, `git mv` into `_archived/_fixed_bugs/`, both indexes and
the counters) is supposed to land *in the same change* as the implementation. Four
flips were done by hand in one session and every one of them happened to comply — which
is exactly the situation in which an unguarded habit quietly stops happening.

The check is historical, not structural: it asks git which commit first added the card
and whether that commit touched anything outside the ledger. A card that lands alone —
move, index, counter, no implementation — is the failure this looks for.

What it does not claim: that the co-landed work *is* that bug's fix. Co-landing is a
necessary condition and the one a habit can silently drop; the correspondence between
card and change stays a review question (the card's 修复关联 section names it).

Boundary: when git cannot answer — no repository, an untracked card, an unavailable
binary — the rule stays silent rather than failing. The governance fixtures build
temporary trees with no history, and a rule that failed there would be reporting its
own blind spot as a violation.

@impl PRS-001"""

from __future__ import annotations

from pathlib import Path

from gitio import run_git

from .contract import ContractViolation

GRADUATED_BUGS = "_backlog/_archived/_fixed_bugs"
CARD_GLOB = "BUG-*.md"
LEDGER_PREFIX = "_backlog/"


def _git(root: Path, arguments: list[str]):
    """Run git, or return None when there is no git to run."""
    try:
        return run_git(arguments, cwd=root)
    except OSError:
        return None


def _adding_commit(root: Path, relative: str) -> str | None:
    result = _git(root, ["log", "--diff-filter=A", "--format=%H", "--", relative])
    if result is None or result.returncode != 0:
        return None
    commits = result.stdout.split()
    return commits[-1] if commits else None


def _touched_paths(root: Path, commit: str) -> list[str] | None:
    result = _git(root, ["show", "--name-only", "--format=", commit])
    if result is None or result.returncode != 0:
        return None
    return [line for line in result.stdout.splitlines() if line.strip()]


def validate_graduation_lands_with_implementation(root: Path) -> None:
    """Reject a bug card whose graduation commit touched nothing but the ledger."""
    for card in sorted((root / GRADUATED_BUGS).glob(CARD_GLOB)):
        relative = card.relative_to(root).as_posix()
        commit = _adding_commit(root, relative)
        if commit is None:
            continue  # untracked, or no history to read: nothing to judge
        paths = _touched_paths(root, commit)
        if paths is None:
            continue
        if not any(not path.startswith(LEDGER_PREFIX) for path in paths):
            raise ContractViolation(
                "ledger.graduation_without_implementation",
                f"{relative} was graduated by {commit[:12]}, a commit that touched only "
                f"{LEDGER_PREFIX}; the flip must land with the implementation it records",
            )
