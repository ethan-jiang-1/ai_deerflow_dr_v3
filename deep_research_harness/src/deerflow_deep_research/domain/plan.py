"""Plan-phase vocabulary: the explicit plan markers and deterministic extraction.

Single owner of the `<research-plan>` protocol vocabulary — the pump's plan gate and
the validator's plan-as-report refusal face both consume these; moving them to the
domain keeps the shared words out of any single consumer (BUG-001's fix: the
admission face needed the markers without importing the run engine).

@impl RUA-002"""

from __future__ import annotations

PLAN_MARKER_OPEN = "<research-plan>"
PLAN_MARKER_CLOSE = "</research-plan>"


def extract_plan(final_text: str) -> str | None:
    """Deterministic plan detection: the inner text between the plan markers.

    Returns None when the markers are absent or the inner text is empty — the honest
    degradation signal. The terminal tool-call picture cannot distinguish a research
    report from a plan (both end in plain text with no final-message tool calls)."""
    if PLAN_MARKER_OPEN not in final_text or PLAN_MARKER_CLOSE not in final_text:
        return None
    inner = final_text.split(PLAN_MARKER_OPEN, 1)[1].split(PLAN_MARKER_CLOSE, 1)[0].strip()
    return inner or None
