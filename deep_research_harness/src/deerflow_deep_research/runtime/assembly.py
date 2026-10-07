"""Checkout locations and foreground assembly shared by CLI and developer tools.

This module wires existing owners; it does not own state transitions or admission.
Framework and configuration dependencies are imported only for an actual run.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from ..domain import bundle
from . import pump
from .adapters import client
from .bundle import bundle_state

HARNESS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = HARNESS_ROOT.parent
CONFIG_ROOT = HARNESS_ROOT / "config"
# Run-bundle data lives outside the application subtree (the repository-root runs/
# directory), so the application tree holds only product code, tests, docs, config,
# and tools. The root *name* is owned by the domain path contract; this module only
# anchors where it resolves from.
RUNS_ROOT = REPO_ROOT / bundle.RUNS_ROOT_NAME
RUNS_ROOT_ENV = "DEEP_RESEARCH_RUNS_ROOT"
DEERFLOW_DIR = REPO_ROOT / "deerflow"
# Framework runtime state (memory stores, skill projections, user data) lives
# outside the application subtree, pinned via the framework's documented
# DEER_FLOW_HOME seam — same discipline as runs/, never inside product code.
FRAMEWORK_HOME = REPO_ROOT / ".deer-flow"
FRAMEWORK_HOME_ENV = "DEER_FLOW_HOME"


def pin_framework_home() -> Path:
    """Pin the framework home to the repository root and return it.

    Fails loudly if the resolution would land inside the application subtree.
    Call before any framework import or client construction in a run.

    @impl HOME-001
    """

    if FRAMEWORK_HOME == HARNESS_ROOT or HARNESS_ROOT in FRAMEWORK_HOME.parents:
        raise SystemExit(
            f"framework home {FRAMEWORK_HOME} resolved inside the application "
            "subtree — refusing (runtime state never lives in product code)"
        )
    os.environ[FRAMEWORK_HOME_ENV] = str(FRAMEWORK_HOME)
    return FRAMEWORK_HOME


def runs_root() -> Path:
    """Resolve the runs root for this invocation.

    The DEEP_RESEARCH_RUNS_ROOT environment variable redirects resolution (tests,
    tools, non-default checkouts); without it the repository-root default applies.
    """
    override = os.environ.get(RUNS_ROOT_ENV)
    return Path(override) if override else RUNS_ROOT


def config_name_for_composition(composition: str) -> str:
    """Map a bundle's declared composition to the config ladder that continues it.

    Refine continues the bundle's own ladder — a real-model run must not silently
    drop to the fixture ladder, and no fresh ladder choice is offered. Values with
    no wired ladder (the declared-but-unwired `mixed`) fail loudly naming the value.
    """

    mapping = {"fixture": "fixture", "all_real": "base"}
    if composition not in mapping:
        raise ValueError(
            f"composition {composition!r} has no wired config ladder; "
            "refine cannot continue it (declared but unwired)"
        )
    return mapping[composition]


def read_pin(deerflow_dir: Path = DEERFLOW_DIR) -> str:
    """Read the upstream checkout revision using Git metadata only."""
    try:
        result = subprocess.run(
            ["git", "-C", str(deerflow_dir), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"cannot resolve the deerflow pin: {exc}") from exc


def resolve_bundle(runs_root: Path, bundle_id: str) -> bundle_state.BundleHandle:
    """Locate a Bundle in the existing date-bucket layout."""
    if runs_root.is_dir():
        for bucket_dir in sorted(runs_root.iterdir()):
            candidate = bucket_dir / bundle_id
            if bundle.is_valid_bucket(bucket_dir.name) and candidate.is_dir():
                return bundle_state.BundleHandle.open(candidate)
    raise SystemExit(
        f"bundle {bundle_id} is permanently unavailable: no such directory under "
        f"{runs_root} (deletion is permanent; there is no recovery path)"
    )


def resolve_skills(config: dict) -> list[str] | None:
    """Resolve the declared skill posture from a loaded ladder config.

    Absent or null ``skills`` resolves to exactly ``None`` — the unwired binding
    posture, never an empty list (an empty list would be a conscious declaration
    of "no skills"). A declared value must be a list of non-empty skill names and
    passes to the binding verbatim; activation semantics are not decided here.

    @impl SKL-001
    """

    if "skills" not in config or config["skills"] is None:
        return None
    skills = config["skills"]
    if not isinstance(skills, list) or not all(
        isinstance(name, str) and name.strip() for name in skills
    ):
        raise ValueError(
            f"config skills declaration must be a list of non-empty skill names, "
            f"got {skills!r}"
        )
    return skills


def run_foreground(
    handle, *, config_root: Path, config_name: str, thread_id: str, pin: str,
    on_event=None, on_clarification=None, on_plan=None,
):
    """Assemble the configured client/saver and return the run pump's typed state.

    The caller creates the Bundle and owns presentation. Missing runtime dependencies
    propagate to that caller; pump retains all terminal and admission decisions.
    `on_clarification` (interactive contexts) routes the agent's clarifying question
    to the human; without it the engine keeps the bounded automatic continuation.
    """
    with client.bundle_checkpointer(handle) as saver:
        pin_framework_home()
        import yaml

        config = yaml.safe_load(
            client.resolve_config_path(config_root, config_name).read_text(encoding="utf-8")
        )
        bound_client = client.build_client(
            config_root, config_name, checkpointer=saver,
            model_name=config["models"][0]["name"],
            available_skills=resolve_skills(config),
            snapshot_dir=handle.root / "diagnostics", pin=pin,
        )
        return pump.run_research(
            handle, stream_fn=client.make_stream_fn(bound_client, thread_id),
            on_event=on_event, on_clarification=on_clarification, on_plan=on_plan,
        )
