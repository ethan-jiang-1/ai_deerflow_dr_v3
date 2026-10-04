"""Record a real run's full raw event stream as a replay fixture.

Real API, explicit opt-in (requires DEEPSEEK_API_KEY in the environment). The fixture
captures type + verbatim data dicts — the replay test owns what it asserts.

@impl DEW-001"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cli import CONFIG_ROOT, _pin, _resolve_bundle  # noqa: E402
from deerflow_deep_research.runtime import bundle_actions, bundle_state, client as cb  # noqa: E402


def main() -> int:
    problem = sys.argv[1] if len(sys.argv) > 1 else "用三句话说明 EASA UAS 开放类别的核心限制"
    config = sys.argv[2] if len(sys.argv) > 2 else "base"
    state = bundle_actions.start(Path("scopes"), problem_text=problem, composition="all_real" if config == "base" else "fixture", deerflow_pin=_pin())
    handle = _resolve_bundle(state.thread_id)
    events = []
    with cb.bundle_checkpointer(handle) as saver:
        client = cb.build_client(CONFIG_ROOT, config, checkpointer=saver, snapshot_dir=handle.root / "diagnostics", pin=_pin())
        for event in client.stream(problem, thread_id=state.thread_id):
            data = getattr(event, "data", None)
            events.append({"type": event.type, "data": data if isinstance(data, dict) else {"_repr": repr(data)[:200]}})
    fixture_dir = Path(__file__).resolve().parents[1] / "fixtures" / "replay"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    fixture = fixture_dir / "real-small-stream.json"
    fixture.write_text(json.dumps({"problem": problem, "config": config, "events": events}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"recorded {len(events)} events -> {fixture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
