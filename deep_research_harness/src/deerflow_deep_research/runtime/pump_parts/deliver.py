"""Final-answer delivery: the state-enrichment half of recording a delivery.

The admission submission itself stays in `pump.py`'s `_submit_final_report`, because
`tests/contract/test_entry_chain.py` parses that file and requires the function there
to reach `submit_artifact` (the admission hold point). The `_record_delivery` shell
makes exactly that pinned call and hands the resulting ledger entry here, so the
hold point is neither bypassed nor called twice.

@impl DEW-001"""

from __future__ import annotations

from dataclasses import replace

from ..bundle import bundle_state


def record_delivery(handle, terminal, final_text: str, entry=None) -> object:
    """Record the orthogonal delivery fact in state, given the admission's answer.

    The process fact (terminal) lands first; the delivery fact enriches it through
    the same revision-CAS path. Mapping: ledger admit/replay -> admitted (replay is
    reworked content that materialized), reject -> rejected, empty answer ->
    no-answer. The fine-grained disposition stays in the journal and ledger; state
    answers only "did this generation deliver?". A crash before the enrichment
    write leaves delivery unrecorded (None) — honest, never a torn fact.
    """
    text = (final_text or "").strip()
    if not text:
        delivery, artifact = "no-answer", None
    elif entry is not None and getattr(entry, "disposition", None) in {"admit", "replay"}:
        delivery, artifact = "admitted", entry.artifact_path
    else:
        delivery, artifact = "rejected", None

    fresh = bundle_state.read_state(handle)
    enriched = replace(fresh, delivery=delivery, delivery_artifact=artifact)
    return bundle_state.write_state(handle, fresh, enriched)
