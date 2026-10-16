"""Upstream gitlink validation: metadata only, never a compatibility claim.

@impl PRS-001"""

from __future__ import annotations

import re
import stat
from pathlib import Path

from gitio import run_git

from .contract import GIT_COMMIT_RE, ContractViolation, StructureManifest

def _run_git_metadata(arguments: list[str]) -> "CompletedProcess[str]":
    """Run one git metadata command; an unavailable git binary is a loud violation.

    The invocation is shared (``gitio.run_git``); this raising posture is this
    checker's own error semantics and stays here.
    """
    try:
        return run_git(arguments[1:] if arguments[:1] == ["git"] else arguments)
    except OSError as exc:
        raise ContractViolation("gitlink.command_unavailable", "cannot execute required upstream gitlink metadata command") from exc


def _validate_upstream_gitlink(root: Path, manifest: StructureManifest) -> None:
    """Validate only the declared gitlink's filesystem and Git metadata.

    """

    boundary = root / manifest.upstream_gitlink.path
    try:
        boundary_stat = boundary.lstat()
    except OSError as exc:
        raise ContractViolation("gitlink.path_missing", f"cannot inspect upstream gitlink path: {manifest.upstream_gitlink.path}") from exc
    if stat.S_ISLNK(boundary_stat.st_mode):
        raise ContractViolation("gitlink.path_symlink", f"upstream gitlink path is a symlink: {manifest.upstream_gitlink.path}")
    if not stat.S_ISDIR(boundary_stat.st_mode):
        raise ContractViolation("gitlink.path_kind", f"upstream gitlink path is not a directory: {manifest.upstream_gitlink.path}")
    try:
        (boundary / ".git").lstat()
    except OSError as exc:
        raise ContractViolation("gitlink.nested_metadata", "upstream gitlink lacks nested Git metadata") from exc

    index_command = [
        "git",
        "-C",
        str(root),
        "ls-files",
        "--stage",
        "-z",
        "--",
        manifest.upstream_gitlink.path.as_posix(),
    ]
    index_result = _run_git_metadata(index_command)
    if index_result.returncode != 0:
        raise ContractViolation("gitlink.index_query", "cannot inspect upstream gitlink index entry")
    records = [record for record in index_result.stdout.split("\0") if record]
    if len(records) != 1:
        raise ContractViolation("gitlink.index_shape", "upstream gitlink index entry must be exactly one stage-zero record")
    entry_match = re.fullmatch(r"(\d{6}) ([0-9a-f]{40}) (\d)\t(.+)", records[0])
    if entry_match is None:
        raise ContractViolation("gitlink.index_shape", "upstream gitlink index entry is malformed")
    mode, index_commit, stage, index_path = entry_match.groups()
    if index_path != manifest.upstream_gitlink.path.as_posix() or stage != "0":
        raise ContractViolation("gitlink.index_shape", "upstream gitlink index entry must be stage zero at the declared path")
    if mode != "160000":
        raise ContractViolation("gitlink.index_entry", "upstream index entry must have gitlink mode 160000")
    if index_commit != manifest.upstream_gitlink.commit:
        raise ContractViolation("gitlink.index_commit", "upstream gitlink index commit differs from the declared lock")

    nested_root = str(boundary)
    head_command = ["git", "-C", nested_root, "rev-parse", "--verify", "HEAD"]
    head_result = _run_git_metadata(head_command)
    if head_result.returncode != 0:
        raise ContractViolation("gitlink.head_query", "cannot resolve upstream gitlink HEAD")
    head_commit = head_result.stdout.strip()
    if not GIT_COMMIT_RE.fullmatch(head_commit):
        raise ContractViolation("gitlink.head_query", "upstream gitlink HEAD output is malformed")
    if head_commit != manifest.upstream_gitlink.commit:
        raise ContractViolation("gitlink.head_commit", "upstream gitlink HEAD differs from the declared lock")

    status_command = ["git", "-C", nested_root, "status", "--porcelain=v1", "--untracked-files=all"]
    status_result = _run_git_metadata(status_command)
    if status_result.returncode != 0:
        raise ContractViolation("gitlink.status_query", "cannot inspect upstream gitlink cleanliness")
    if status_result.stdout:
        raise ContractViolation("gitlink.status_dirty", "upstream gitlink worktree is not clean")
