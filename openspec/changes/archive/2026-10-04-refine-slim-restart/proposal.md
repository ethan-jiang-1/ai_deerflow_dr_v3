# Proposal

## Why

The EASA evidence arc exposed the refine failure mode: same-thread continuation drags 200+ messages of context so each re-run re-caps — five runs to finish one briefing. A refine should restart light: a fresh thread seeded with a mechanically-derived summary of what the prior generations gathered and concluded.

## What Changes

- `rule_refine(state, direction, *, next_thread_id=None)`: when a fresh thread id is supplied, the refined state carries it and appends the old thread to `prior_thread_ids` (new closed-set field, default empty). Same-thread refine (no id) is unchanged.
- `bundle_actions.refine(handle, direction, *, fresh_context=None)`: with fresh_context, generates the new thread id and writes `request/generation-<N>-context.md` (the seed document) before the transition.
- `client.summarize_prior_thread(checkpoint_path, thread_id) -> str` (framework-lazy): a mechanical projection of the prior thread — message/tool-result counts, the original question, and the prior final-answer excerpt; no model generation.
- Specs: run-bundle MODIFIED (lifecycle requirement gains the fresh-thread refine clause and scenario; the state-authority enumeration gains `prior thread lineage`).

## Capabilities

### New Capabilities
(none)
### Modified Capabilities
- `run-bundle`: the lifecycle and state-authority requirements as above (all scenarios preserved verbatim).

## Impact

- Modified: `domain/state_machine.py`, `domain/bundle.py` (context-file path helper), `runtime/bundle_actions.py`, `runtime/client.py` (summarizer), `tests/unit/test_bundle_domain.py` + `tests/unit/test_bundle_runtime.py` (red-green). No CI/governance/deerflow changes.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/domain/state_machine.py` — the refine rule owns the lineage semantics; the mechanical summarizer is a projection, never an authority.
- **Seam classification:** deterministic-guardrail — thread migration and the summary are pure mechanical code; no model cognition.
- **Question:** How does refine restart a generation on a fresh light thread, seeded with a mechanically-derived context (prior question, material counts, prior answer excerpt), with the prior lineage recorded and old checkpoints untouched?
- **Necessary adjacent/external contracts:** the run-bundle state authority (answers: where prior_thread_ids lives and how the closed field set extends); the checkpointer (answers: the summary's mechanical source — message/tool counts and the last AI excerpt, no invention); the EASA bundle (answers: the live verification subject — five-cap arc vs one-shot light restart).
- **Evidence seam:** unit red-green (new thread + lineage + context file + old checkpoint untouched; same-thread refine unchanged) plus the real EASA refine completing on the light thread.
- **Not in scope:** model-written summaries (cognitive authority forbidden here), CLI flag wiring (rides the entry surface later), spec changes to admission/wiring.
- **Triggered review policies:** change-admission
