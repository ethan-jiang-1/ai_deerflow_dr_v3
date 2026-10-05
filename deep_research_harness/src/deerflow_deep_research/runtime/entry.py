"""Checkout locations and foreground assembly shared by CLI and developer tools.

This module wires existing owners; it does not own state transitions or admission.
Framework and configuration dependencies are imported only for an actual run.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..domain import bundle
from . import run_engine
from .adapters import client
from .bundle import bundle_state

HARNESS_ROOT = Path(__file__).resolve().parents[3]
CONFIG_ROOT = HARNESS_ROOT / "config"
SCOPES_ROOT = HARNESS_ROOT / "scopes"
DEERFLOW_DIR = HARNESS_ROOT.parent / "deerflow"


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


def resolve_bundle(scopes_root: Path, bundle_id: str) -> bundle_state.BundleHandle:
    """Locate a Bundle in the existing date-bucket layout."""
    if scopes_root.is_dir():
        for bucket_dir in sorted(scopes_root.iterdir()):
            candidate = bucket_dir / bundle_id
            if bundle.is_valid_bucket(bucket_dir.name) and candidate.is_dir():
                return bundle_state.BundleHandle.open(candidate)
    raise SystemExit(
        f"bundle {bundle_id} is permanently unavailable: no such directory under "
        f"{scopes_root} (deletion is permanent; there is no recovery path)"
    )


def run_foreground(handle, *, config_root: Path, config_name: str, thread_id: str, pin: str, on_event=None):
    """Assemble the configured client/saver and return the run engine's typed state.

    The caller creates the Bundle and owns presentation. Missing runtime dependencies
    propagate to that caller; run_engine retains all terminal and admission decisions.
    """
    with client.bundle_checkpointer(handle) as saver:
        import yaml

        model_name = yaml.safe_load(
            client.resolve_config_path(config_root, config_name).read_text(encoding="utf-8")
        )["models"][0]["name"]
        bound_client = client.build_client(
            config_root, config_name, checkpointer=saver, model_name=model_name,
            snapshot_dir=handle.root / "diagnostics", pin=pin,
        )
        return run_engine.run_research(
            handle, stream_fn=client.make_stream_fn(bound_client, thread_id), on_event=on_event,
        )
