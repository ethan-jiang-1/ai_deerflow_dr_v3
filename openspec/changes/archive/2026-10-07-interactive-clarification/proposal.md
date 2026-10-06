# Proposal

## Why

Today the lead agent can ask a clarifying question (the `ask_clarification` tool is in
its visible surface), but the harness swallows the question: the run engine replies
`[非交互模式·系统自动应答] <问题原文>` and continues on assumptions, up to the
N=2 bound, then fails honestly with the question preserved. For a vague research
request on the real ladder this burns genuine API budget on guessed intent — the
operator's request to reopen the deferred HITL ruling is economically correct: one
round-trip with the human is cheaper than one misdirected research run. The
machinery is 60% present (tool, pure detection, bound, exhaustion preservation);
what is missing is routing the question to the human and feeding the answer back.

## What Changes

- The run engine gains an optional clarification hook (`on_clarification`), exactly
  parallel to the existing optional event hook: when the caller provides it, an
  unanswered `ask_clarification` terminal delivers the question text to the hook,
  and the returned non-empty answer continues the run on the same thread as the
  human's own words (no provenance prefix — it IS the human).
- Foreground `create` and `refine` become interactive when the context allows:
  stdin is a TTY, or `DEEP_RESEARCH_INTERACTIVE=1` is set (the override exists so
  subprocess/smoke contexts can drive the prompt and users can force it on). The
  question renders through the shared rendering module; an empty input declines.
- Declining (empty answer) falls back to today's provenance-marked auto-reply,
  which consumes the auto bound; an answered interactive round does NOT consume
  the bound (the bound exists to stop blind guessing — a human answer is not a
  guess; the human is the loop breaker and can decline at any question).
- Headless behavior (no TTY, no override) is byte-identical to today: auto-reply,
  bound N=2, exhaustion → `failed-resume` with questions preserved.
- No mandatory questionnaire is added: the model's own judgment of "is this clear
  enough to search" remains the trigger (the operator's explicit requirement).
- The ask and its resolution are journaled as `lifecycle` events
  (`clarification_asked`, `clarification_answered`, `clarification_declined`); the
  journal's closed category set is unchanged.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `run-bundle`: the clarification-continuation requirement now distinguishes
  interactive rounds (human answer, do not consume the bound) from automatic
  replies (decline or headless, consume the bound); exhaustion semantics
  unchanged.
- `deerflow-wiring`: the run-engine requirement now routes an unanswered
  clarification to a provided hook (same-thread continuation with the answer)
  and keeps the provenance-marked auto-reply as the fallback and headless path.
- `entry-surface`: the rendering requirement extends the optional-hook pattern to
  the clarification hook — the question renders through the shared module, and
  interactive contexts gate on TTY or explicit environment override so a
  non-interactive context never blocks on stdin.

## Impact

- Code: `runtime/run_engine.py` (`on_clarification` parameter, journal events),
  `runtime/entry.py` (pass-through), `runtime/interaction/cli.py` (TTY/env gating,
  handler construction, prompt), `runtime/interaction/render.py` (question
  rendering).
- Tests: `tests/unit/runtime/test_run_engine.py` (interactive handler cases),
  new interaction unit tests (gating + handler wiring), a smoke journey test
  driving the prompt through a subprocess with `DEEP_RESEARCH_INTERACTIVE=1` and
  piped stdin (scripted ladder — zero credentials).
- Docs: `docs/playbook/run-research.md` (interactive gotcha), harness `README.md`
  chain note, `docs/research-process.md` clarification judgment note.
- No state-machine transitions change; no journal category changes; no CLI verb
  changes; headless/smoke behavior unchanged.

## Change Focus

- **Primary module / causal owner:** `runtime/run_engine.py` — owns the
  continuation loop that today auto-replies; routing an unanswered clarification
  to a human hook is a run-loop decision (the run-bundle spec assigns the
  re-invocation loop to the wiring owner).
- **Seam classification:** human-decision — the change inserts a genuine human
  decision point into the run loop; no prompt is authored (the human's words are
  fed back verbatim) and no admission rule changes.
- **Question:** When the lead agent judges a research request too vague to search
  well and asks a clarifying question, how does the harness deliver that question
  to the operator and continue the run with the answer, without breaking
  headless contexts or the bounded-continuation guarantees?
- **Necessary adjacent/external contracts:** run-bundle bound semantics (does an answered round consume the auto bound?), entry-surface rendering vocabulary (does the question render through the shared module?), deerflow-wiring engine honesty rules (does the same-thread re-invocation and terminal honesty hold?), smoke lane (can a subprocess drive the prompt without a TTY?).
- **Evidence seam:** red-green on `tests/unit/runtime/test_run_engine.py`
  (scripted unanswered-ask stream) first; interaction gating unit tests; then a
  smoke journey test with piped stdin; `make verify` + `make smoke` + governance
  checkers green as the gate.
- **Not in scope:** mandatory pre-flight questionnaires (create-time gates),
  new CLI verbs or flags, state-machine transitions, journal category changes,
  asynchronous answer across processes (a `answer` verb), upstream framework
  changes, forcing the deep-research skill.
- **Triggered review policies:** human-interaction-integrity, control-and-recovery
