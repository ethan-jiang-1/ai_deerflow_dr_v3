# Tasks

- [x] 1.1 Add `make record-stream PROBLEM="…" CONFIG=base` (records the full raw event
      stream to `tests/fixtures/replay/real-small-stream.json` via a real run) and write
      `tests/unit/test_event_stream_replay.py` (replay through run_research on a fresh
      bundle; terminal + journal-shape assertions; tamper negative control). Verify: the
      replay test is red until the fixture is recorded (missing fixture = red), then the
      recording run lands the fixture and the replay goes green — measured.
- [x] 1.2 Doctrine doc: the ladder table's replay lane row lands. Verify: doc hygiene 0.
- [x] 1.3 Gates (direct exits); receipts; archive; commit.

## Receipt

- [x] red: replay test red on the missing fixture (measured); then the first recording used the fixture ladder (fake, 10 events) — re-recorded with CONFIG=base: **1386 real events** including real web_search tool_call chunks.
- [x] replay green on the real stream: engine replays 1386 events to completed; tamper negative control surfaces modified tool_calls in the journal (the flat-chunk scar mechanized). One test-path bug fixed mid-flight (fixture parents[2] -> parents[1], disclosed).
- [x] ladder row landed in the doctrine doc; doc hygiene 0.
- [x] gates: VERIFY=0, SMOKE=0 (unit 90 + replay 2 + integration), GOV=0, CLOSEOUT=0, STRICT=0, DIFF=0; gitlink ceebf97f unchanged; archive; commit follows.

