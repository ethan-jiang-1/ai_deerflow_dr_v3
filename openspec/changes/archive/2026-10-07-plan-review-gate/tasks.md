# Tasks

## 1. Run engine plan phase (red-green)

- [x] 1.1 Red: extend `tests/unit/runtime/test_run_engine.py` — (a) plan hook: first
  plain-text turn is the plan (not admitted), hook receives it, returned plan is the
  continuation message, `request/plan-gen1.md` materialized, second turn completes
  and admits; (b) amendment: returned plan carries the revision; (c) skip: None
  injects the skip-proceed message, no plan file; (d) degradation: first turn with
  tool calls completes under today's rules with `plan_gate_degraded` journaled, no
  plan file; (e) clarification inside plan phase: ask → answer → plan turn → answer,
  composing with existing rules. Confirm failure (no `on_plan` parameter)
- [x] 1.2 Green: `run_research`/`_drive` gain `on_plan`; `awaiting_plan` loop-local
  phase (generation 1 only); plan-request framing on the first message; plan/decline/
  degrade journal events; atomic materialization via the existing atomic writer;
  stable continuation constants; `make verify` green

## 2. Entry wiring and interaction surface

- [x] 2.1 Red: interaction tests — create builds the plan handler under the same
  TTY/env gate (refine builds none); handler three-way behavior: Enter returns the
  plan unchanged, typed text returns plan + 用户修订意见 append, `s` returns None,
  `q` raises SystemExit; plan renders through the shared module with the stable
  prompt phrases. Confirm failure
- [x] 2.2 Green: `entry.run_foreground` pass-through; `cli.py` handler + create-only
  wiring; `render.py` plan phrase and prompt hint; `make verify` green

## 3. Smoke: subprocess drives the plan gate

- [x] 3.1 Integration tests with `DEEP_RESEARCH_INTERACTIVE=1` and piped stdin over
  the scripted ladder: (a) scripted plan turn then final answer, piped Enter —
  asserts `request/plan-gen1.md` exists, `auto_proceed_count` 0, journal carries
  plan_proposed/plan_confirmed, run completed; (b) piped revision note — asserts the
  amended plan is the file content and the injected continuation; `make smoke` green

## 4. Docs and gates

- [x] 4.1 Update `docs/playbook/run-research.md` (plan gate gotcha: when it engages,
  the three ways, degradation honesty), harness `README.md` chain note,
  `docs/research-process.md` (plan as the gen-1 analog of refine's direction
  document), `docs/run-bundle.md` artifact table (+ `request/plan-gen1.md`),
  `tests/README.md` registrations; doc hygiene green
- [x] 4.2 Full gates: `make verify`, `make smoke`, all governance checkers, plan
  gate; fresh receipts; specs sync (entry-surface, deerflow-wiring MODIFIED;
  run-bundle ADDED); archive; root count follows
- [ ] 4.3 Optional real-ladder demonstration: an interactive-context run observing
  the plan turn, an amendment, and the resulting research shape (observation, not a
  gate)
