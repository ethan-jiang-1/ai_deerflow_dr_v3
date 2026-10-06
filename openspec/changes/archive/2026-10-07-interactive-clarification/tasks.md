# Tasks

## 1. Run engine interactive hook (red-green)

- [x] 1.1 Red: extend `tests/unit/runtime/test_run_engine.py` with scripted
  unanswered-ask streams — (a) hook returns an answer: run continues on the same
  thread with the answer as message, completes, `auto_proceed_count` stays 0, journal
  carries asked+answered; (b) hook returns empty: falls back to auto-reply, count
  increments, provenance-marked continuation; confirm failure (no `on_clarification`
  parameter exists)
- [x] 1.2 Green: add `on_clarification` to `run_research`/`_drive`; in the detected
  branch deliver the question, journal the three lifecycle events, continue with the
  raw answer or fall through to the auto-reply on decline; `make verify` green

## 2. Entry wiring and interaction surface

- [x] 2.1 Red: interaction tests — the CLI builds a clarification handler only when
  `stdin.isatty()` or `DEEP_RESEARCH_INTERACTIVE` is set (patch both), passes it through
  `run_foreground` to `run_research`; non-interactive passes None; confirm failure
- [x] 2.2 Green: `entry.run_foreground` pass-through; `cli.py` gating + handler (prompt
  via `render`, one `input()` line, empty declines); `render.py` question phrase;
  `make verify` green

## 3. Smoke: subprocess drives the prompt

- [x] 3.1 Add an integration test: `DEEP_RESEARCH_INTERACTIVE=1`, scripted model emits
  an unanswered `ask_clarification` then completes on the answered turn; the CLI
  subprocess receives the answer through piped stdin; assert the run completes
  (not failed-resume), `auto_proceed_count` is 0, and the journal carries the
  asked/answered pair; `make smoke` green

## 4. Docs and gates

- [x] 4.1 Update `docs/playbook/run-research.md` (interactive gotcha: TTY/env gating,
  empty line declines), harness `README.md` chain note, and
  `docs/research-process.md` (the judgment note: asking is the agent's call; the
  harness routes it); doc hygiene green
- [x] 4.2 Full gates: `make verify`, `make smoke`, all governance checkers green;
  fresh receipts recorded; archive the change via the OpenSpec workflow
- [x] 4.3 Optional real-ladder demonstration: a deliberately vague problem on the base
  ladder to observe the agent actually asking (documented as observation, not a gate)
