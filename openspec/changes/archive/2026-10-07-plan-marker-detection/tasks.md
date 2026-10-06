# Tasks

## 1. Marker detection (red-green)

- [x] 1.1 Red: update plan-phase unit tests to marked turn shapes (hook receives the
  inner text without markers; file/injection carry the inner text); add the demo
  regression — a research-report turn with no markers (tool calls or not) completes
  ungated with `plan_gate_degraded` journaled and no spurious prompt; confirm failure
- [x] 1.2 Green: framing suffix gains the marker protocol; engine gates only on
  marker presence, extracts the inner text, degrades on absence or empty inner text;
  `make verify` green

## 2. Smoke regression journeys

- [x] 2.1 Update the two plan journeys' scripted plan turn to wrap the plan in
  markers; add the degradation journey (scripted single-turn report without markers,
  piped stdin untouched) asserting completion without gating and
  `plan_gate_degraded` in the journal; `make smoke` green

## 3. Docs and gates

- [x] 3.1 One-line notes in playbook and research-process (markers are the gate's
  engagement protocol; marker-less turns degrade honestly); registrations; full
  gates; specs sync (deerflow-wiring MODIFIED); archive; root count follows
