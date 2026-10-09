# Design

## Context

The assets: a 10-line model journal (plan turn, seven tool turns, one middleware
content turn, report turn) and a 28-record search corpus, both from the post-BUG-001
acceptance run (bundle 55c35d44). The goal: replay them through the real framework
graph with zero credentials. Development was measurement-driven: every design decision
below was forced by a loud failure, not chosen a priori.

## Goals / Non-Goals

**Goals:** zero-credential complete-graph replay with verbatim report and loud
divergence signals; the level-3 ladder proof; everything green.

**Non-Goals:** no operator-facing replay config (test-lane wiring; config set
unchanged); no key-based journey matching (measured unsuitable); no subagent replay
(the journey had none); no new recording.

## Decisions

1. **Order-based serving with a process-shared cursor.** Key matching failed first:
   three distinct first-turn keys for the same problem across three assemblies
   (e96eb2e776fa real / 4ce402058705 CLI-scripted / 75b4270c727d direct) — the
   framework's first-turn framing varies with model config and environment. Order-based
   serving replaces it; the recorded keys stay as provenance. The cursor is
   module-level shared because the framework constructs the model per agent-build —
   per-instance cursors made each instance re-serve line 1 (measured: the "final
   report" came back plan-marked and BUG-001's new admission face rejected it by name).
2. **The serving queue is the agent subsequence.** Mid-journey content-only lines are
   middleware calls by proof-of-continuation (an agent turn ending in plain text ends
   the agent loop; the recorded journey continued past them). The queue serves: first
   line (plan), all tool-call lines, last line (report). The replay assembly disables
   summarization so the middleware instance never competes for the queue (its trigger
   point is context-size-dependent — the framing variance that killed key matching
   would also re-order its calls).
3. **The corpus stays (tool, arguments)-keyed.** Queries are stable across assemblies
   (unlike framing); 28 unique pairs, zero duplicates measured. A corpus miss fails
   loudly — the tool layer's staleness signal.
4. **Exhaustion is the structural-divergence signal.** A model call beyond the recorded
   journey raises loudly ("the graph made a call the recorded journey never made") —
   the replay proves graph-structure fidelity, and the signal replaces key matching for
   that purpose.
5. **`bind_tools` joins the mechanism's `_Base`** (return self, the ScriptedChatModel
   precedent): the default raises NotImplementedError, surfaced the first time the
   replay drove the real agent chain — the E-1 tests called `_generate` directly and
   never crossed the binding path.
6. **The test's config is derived from fixture.yaml** (three `use:` swaps,
  summarization disabled, web_fetch added) inside a temp root: the checked-in config
   set stays {base, fixture, record}; the zero-credential claim is structural (no
   `$VAR` reference in the derived config, asserted by the test).

## Risks / Trade-offs

- [Framing drift on framework re-pin breaks the replay] → the exhaustion and corpus
  misses fail loudly; the deerflow-downstream re-review trigger governs the re-pin
  moment; re-recording is the remedy (the knob is landed).
- [Order-based serving could mask a content divergence] → the verbatim-report
  assertion pins the endpoint; a mid-journey divergence that still lands the recorded
  report is indistinguishable from the recorded journey at the observable surface —
  the honest limit of order-based replay, documented here.
- [The shared cursor couples instances] → scoped by fixture root (a new root resets);
  single-process test lane; acceptable for the seam's purpose.

## Migration Notes

Already applied and green in the working tree (development was red-green per failure);
this change packages it: providers + fixture + test landed first, receipts follow
(`make verify`, `make smoke`, the replay test, doc-hygiene, closeout gate), then
archive and the E card's CLS-021 closure.
