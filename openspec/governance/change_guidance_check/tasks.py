"""tasks.md standing-section grammar (Deviation Register, Delivery Record).

@impl CHA-001"""

from __future__ import annotations

from pathlib import Path

from change_guidance_kernel import (
    delivery_record_issues as kernel_delivery_record_issues,
    deviation_register_issues as kernel_deviation_register_issues,
)

from .helpers import ContractViolation, _read_file

def _validate_change_tasks(root: Path, change_root: Path) -> None:
    """Validate standing tasks sections of one active change (@impl CHA-001).

    Grammar only: a tasks.md that exists must carry the two standing sections;
    a missing tasks.md (early planning) is skipped. Section content is judged
    by apply/archive review, never here.
    """
    tasks_path = change_root / "tasks.md"
    if not tasks_path.is_file():
        return
    try:
        tasks_text = tasks_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractViolation(
            "tasks.unreadable",
            f"cannot read active tasks {tasks_path.relative_to(root).as_posix()}: {exc}",
        ) from exc
    relative_tasks_path = tasks_path.relative_to(root)
    for issue in (
        *kernel_deviation_register_issues(tasks_text),
        *kernel_delivery_record_issues(tasks_text),
    ):
        raise ContractViolation(issue.code, f"{relative_tasks_path.as_posix()}: {issue.detail}")
