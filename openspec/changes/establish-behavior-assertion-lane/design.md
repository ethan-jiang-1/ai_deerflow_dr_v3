# Design

## Context

The registered-machine pattern (`engine/machines.py` `DECLARED_MACHINES` ↔
`docs/quality-register.md`, drift-tested) is the established way a pure quality machine
lands; `source-traceability` (CLS-017 C6) is the freshest precedent. The stunt ladder
(`docs/testing-and-evaluation.md`) declares level 4 as "对真实运行的 trace 断言（工具
选择/token/时长），显式 opt-in 的质量观察" with status ⬜. Journal shape was profiled on
2026-10-09 over the recorded runs: `model_tool_call` entries carry a `calls` list of tool
names; every entry carries `ts` and `category`/`event`; `subagent_event` carries delegated
work; **there is no structured token field** (tokens appear only inside content strings).
Local run storage (`runs/`) is gitignored evidence; fixtures extracted verbatim from it
are the established bridge (`real-small-stream.json` precedent). See proposal.md — Why for
the trigger and the owning-spec instruction (CLS-017:114).

## Goals / Non-Goals

**Goals:**

- Level 4 exists as spec semantics plus one machine, all red-green-able from existing
  recorded assets, with the token dimension honestly excluded rather than faked.
- The `test-evidence` owning main spec lands with requirements that outlive this change
  (ladder honesty, pure derivation, observe-not-admit, sample provenance).

**Non-Goals:**

- No token assertion (no structured journal field; parsing content strings would fake the
  dimension — registered as a declared limit instead).
- No live-bundle CLI (entry-surface's six verbs unchanged; a `profile` verb is a later
  trigger), no E/F/G work, no admission-path changes, no model or prompt surfaces.

## Decisions

1. **Profile derives from journal only, as a pure module at the engine seam.** Input is
   the parsed journal lines (list of dicts — I/O stays at the test/fixture boundary), so
   the function is deterministic and unit-testable exactly like `traceability.py`.
   Alternative rejected: reading bundle directories directly — couples the machine to
   local storage layout and puts I/O inside the seam.
2. **Tool names are a closed declared vocabulary.** The profile counts calls by name and
   the known-tool set is declared in the module (`web_search`, `web_fetch`, `task`,
   `ask_clarification`, … from the recorded corpus); unknown tool names are surfaced, not
   silently bucketed. Matches the admission-vocabulary discipline (small closed sets).
3. **Expectations are declared data, checked by pure comparison; the degenerate negative
   is an expectation family, not a special code path.** "At least one search-or-fetch
   call" is the degenerate-research guard asserted like any other expectation — red on a
   zero-research journal, naming the face. Alternative rejected: a bespoke "quality
   verdict" — that would drift toward admission semantics the spec forbids.
4. **Fixture choice: the 2026-10-05 34-event run (`5bb2c343`) — the richest recorded
   journal on disk** (web_search×9, web_fetch×3, task×1, subagent_event×31), extracted
   verbatim with a provenance header comment. Pinning the richest run exercises every
   profile field with real values. Alternative rejected: the smaller clarification run —
   pins almost nothing.
5. **The real-model-io consumer is an integration test beside `test_replay_model.py`**,
   asserting replay fidelity of the retained sample and stating provenance limits in the
   test docstring (spec scenario). The registry tables (`tests/README.md`,
   `fixtures/README.md`) flip their "no consumer" notes to name the consumer.
6. **Spec scoping: `test-evidence` owns semantics, not the register mechanism.** The
   machine↔register sync requirement already lives in `run-admission` (RUA-001 family);
   the new spec references observation semantics and does not duplicate the sync rule —
   one fact, one owner.

## Risks / Trade-offs

- [Fixture provenance rots] → the fixture header records the source bundle id and
  extraction date; the registry row links the pair.
- [Journal schema drift (framework re-pin)] → profile reads tolerant `dict.get` shapes
  over the recorded corpus but pins the fixture; a schema break shows as red pinning
  first (the intended tripwire), and the deerflow-downstream re-review trigger governs
  the re-pin moment.
- [Level-4 scope creep toward admission] → the spec's observe-not-admit requirement plus
  the output type (no verdict codes) keep the boundary mechanical, not just written.

## Migration Notes

Apply order: red-first tests (drift/pinning/degenerate/replay-consumer each seen red on
seeded violations) → `behavior_profile.py` + `DECLARED_MACHINES` entry + register row →
fixture extraction → docs/ladder/registry sync → full receipts (`make verify`, doc
hygiene, closeout gate) → archive under the standing apply authorization.
