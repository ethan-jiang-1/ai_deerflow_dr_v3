# Design

## Context

The EASA deep-research run crashed with a raw GraphRecursionError after ~10 tool rounds
(limit 100 steps); the engine let it propagate; the bundle stayed active until status
crash-transferred it; the checkpoint kept everything (23 messages / 13 tool results).
The postmortem plan pins both fixes. Policy routing: change-admission; skip_specs:
conformance to declared fail-loud/terminal-honesty requirements.

## Decisions

1. The guard wraps run_research's stream loop only (framework boundary); harness-code
   defects still raise (red tests catch them). The disposition reuses rule_run_terminal
   on a fresh read; the journal entry carries the exception class.
2. recursion_limit 300 as a conservative start (framework max 1000); a deeper run that
   still caps fails loudly under the guard, and the limit is then adjusted on evidence.
3. The refine re-run of the crashed bundle (same thread) is the live verification: the
   model sees its gathered material in the checkpoint and completes the briefing.

## Alternatives

- Retrying inside the engine — rejected: a competing controller; the framework owns
  retries. - Catching Exception globally in the CLI — rejected: the state transition
  belongs to the engine (single write path).

## Risks / Trade-offs

[300 insufficient] → loud failure again, adjust on evidence. [Guard masks harness bugs]
→ only stream/framework exceptions at the loop boundary; unit red-green pins the shape.

## Migration Plan

Red-green guard test → config + CLI tweaks → verify/smoke → refine re-run of bundle
997fe460 as live proof → receipts → archive → plan closes CLS-008 → commit.

## Open Questions

(none)
