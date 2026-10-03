"""Run-bundle state machine: the single-authority state facts and pure rules.

Pure stdlib. The transition rules are the semantic decision; the runtime layer is
their only writer. Illegal requests fail loudly naming the current state, the
requested action, and the reason.

@impl RUB-001"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from .bundle import COMPOSITIONS

STATUSES: tuple[str, ...] = ("active", "completed", "cancelled", "failed-resume")
TERMINAL_STATUSES: tuple[str, ...] = ("completed", "cancelled", "failed-resume")
RUN_TERMINAL_OUTCOMES: tuple[str, ...] = ("completed", "cancelled", "failed-resume")
DEFAULT_AUTO_PROCEED_BOUND = 2
_PIN_RE = re.compile(r"^[0-9a-f]{40}$")
_SCHEMA_VERSION = 1


class RuleViolation(ValueError):
    """A pure rule was asked for something the declared contract forbids."""


@dataclass(frozen=True)
class BundleState:
    schema_version: int
    revision: int
    status: str
    thread_id: str
    owner_pid: int
    deerflow_pin: str
    generation: int
    composition: str
    cancel_requested: bool
    auto_proceed_count: int
    auto_proceed_bound: int
    prior_thread_ids: tuple[str, ...] = ()

    def validate(self) -> "BundleState":
        if self.schema_version != _SCHEMA_VERSION:
            raise RuleViolation(
                f"state schema_version must be {_SCHEMA_VERSION}, got {self.schema_version}"
            )
        if self.revision < 1:
            raise RuleViolation(f"state revision must be >= 1, got {self.revision}")
        if self.status not in STATUSES:
            raise RuleViolation(
                f"state status {self.status!r} is outside the closed set {STATUSES}"
            )
        if self.owner_pid < 1:
            raise RuleViolation(f"owner PID must be a positive integer, got {self.owner_pid}")
        if not _PIN_RE.fullmatch(self.deerflow_pin):
            raise RuleViolation(
                "deerflow_pin must be a lower-case 40-hex commit; got "
                f"{self.deerflow_pin!r}"
            )
        if self.generation < 1:
            raise RuleViolation(f"generation must be >= 1, got {self.generation}")
        if self.composition not in COMPOSITIONS:
            raise RuleViolation(
                f"composition {self.composition!r} is outside the closed set {COMPOSITIONS}"
            )
        if self.auto_proceed_count < 0 or self.auto_proceed_bound < 0:
            raise RuleViolation("auto_proceed counters must be non-negative")
        if self.status == "active" and self.auto_proceed_count > self.auto_proceed_bound:
            raise RuleViolation(
                "auto_proceed_count exceeds the bound on an active bundle: "
                f"{self.auto_proceed_count} > {self.auto_proceed_bound}"
            )
        return self


    @classmethod
    def from_dict(cls, raw: dict) -> "BundleState":
        try:
            return cls(
                schema_version=int(raw["schema_version"]),
                revision=int(raw["revision"]),
                status=str(raw["status"]),
                thread_id=str(raw["thread_id"]),
                owner_pid=int(raw["owner_pid"]),
                deerflow_pin=str(raw["deerflow_pin"]),
                generation=int(raw["generation"]),
                composition=str(raw["composition"]),
                cancel_requested=bool(raw["cancel_requested"]),
                auto_proceed_count=int(raw["auto_proceed_count"]),
                auto_proceed_bound=int(raw["auto_proceed_bound"]),
                prior_thread_ids=tuple(str(x) for x in raw.get("prior_thread_ids", [])),
            ).validate()
        except KeyError as exc:
            raise RuleViolation(f"state.json is missing the field {exc.args[0]!r}") from exc
        except (TypeError, ValueError) as exc:
            if isinstance(exc, RuleViolation):
                raise
            raise RuleViolation(f"state.json has a malformed field: {exc}") from exc

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "revision": self.revision,
            "status": self.status,
            "thread_id": self.thread_id,
            "owner_pid": self.owner_pid,
            "deerflow_pin": self.deerflow_pin,
            "generation": self.generation,
            "composition": self.composition,
            "cancel_requested": self.cancel_requested,
            "auto_proceed_count": self.auto_proceed_count,
            "auto_proceed_bound": self.auto_proceed_bound,
            "prior_thread_ids": list(self.prior_thread_ids),
        }


@dataclass(frozen=True)
class RefineRecord:
    generation: int
    direction_text: str


def _require(condition: bool, current_state: str, action: str, reason: str) -> None:
    if not condition:
        raise RuleViolation(
            f"illegal transition: state {current_state!r} does not allow {action!r}: {reason}"
        )


def rule_start(
    *,
    thread_id: str,
    owner_pid: int,
    deerflow_pin: str,
    composition: str,
    auto_proceed_bound: int = DEFAULT_AUTO_PROCEED_BOUND,
) -> BundleState:
    if composition not in COMPOSITIONS:
        raise RuleViolation(
            f"composition {composition!r} is outside the closed set {COMPOSITIONS}"
        )
    return BundleState(
        schema_version=_SCHEMA_VERSION,
        revision=1,
        status="active",
        thread_id=thread_id,
        owner_pid=owner_pid,
        deerflow_pin=deerflow_pin,
        generation=1,
        composition=composition,
        cancel_requested=False,
        auto_proceed_count=0,
        auto_proceed_bound=auto_proceed_bound,
    ).validate()


def rule_cancel(state: BundleState) -> BundleState:
    _require(state.status == "active", state.status, "cancel", "only an active run can request cancellation")
    return replace(state, cancel_requested=True)


def rule_refine(
    state: BundleState, direction_text: str, *, next_thread_id: str | None = None
) -> tuple[BundleState, RefineRecord]:
    _require(
        state.status in TERMINAL_STATUSES,
        state.status,
        "refine",
        "refinement re-runs a terminal bundle as the next generation",
    )
    if not direction_text.strip():
        raise RuleViolation("refine requires non-empty direction text")
    refined = replace(
        state,
        status="active",
        generation=state.generation + 1,
        cancel_requested=False,
        auto_proceed_count=0,
        thread_id=next_thread_id or state.thread_id,
        prior_thread_ids=state.prior_thread_ids + ((state.thread_id,) if next_thread_id else ()),
    ).validate()
    return refined, RefineRecord(generation=refined.generation, direction_text=direction_text)


def rule_run_terminal(state: BundleState, outcome: str) -> BundleState:
    _require(
        outcome in RUN_TERMINAL_OUTCOMES,
        state.status,
        f"run-terminal {outcome!r}",
        f"outcome must be one of {RUN_TERMINAL_OUTCOMES}",
    )
    _require(
        state.status == "active",
        state.status,
        f"run-terminal {outcome!r}",
        "a run-terminal outcome applies only to an active run",
    )
    _require(
        outcome != "cancelled" or state.cancel_requested,
        state.status,
        f"run-terminal {outcome!r}",
        "the pump may not declare cancellation without a recorded cancellation request",
    )
    return replace(state, status=outcome).validate()


def rule_crash_transfer(state: BundleState, *, owner_alive: bool) -> BundleState | None:
    """Fail-loud crash detection: dead owner + active -> failed-resume.

    Returns None when no transfer is legal (owner alive, or the bundle is already
    terminal) — the caller keeps the observed state."""

    if state.status != "active" or owner_alive:
        return None
    return replace(state, status="failed-resume").validate()


def rule_clarification_step(state: BundleState, *, detected: bool) -> BundleState:
    """Bounded clarification continuation inside `active` — never a new state.

    Exhausting the bound is a fail-loud transfer to `failed-resume`; the caller owns
    preserving the unanswered question text into diagnostics."""

    if state.status != "active":
        raise RuleViolation(
            f"illegal transition: state {state.status!r} does not allow "
            f"'clarification-step': continuation applies only to an active run"
        )
    if not detected:
        return state
    if state.auto_proceed_count >= state.auto_proceed_bound:
        return replace(state, status="failed-resume").validate()
    return replace(state, auto_proceed_count=state.auto_proceed_count + 1).validate()
