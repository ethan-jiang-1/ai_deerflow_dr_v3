# Tasks

- [x] 1.1 Unit tests red: hash hit, loud miss (known keys + preview), normalization
      stability (dates/UUIDs/reminder blocks stripped). Verify: red measured.
- [x] 1.2 Implement `runtime/fixtures/replay_model.py` (RecordingChatModel +
      ReplayChatModel + normalization). Verify: unit green.
- [x] 1.3 Real recording run (small real question through the recording wrapper) ->
      `tests/fixtures/replay/real-model-io.jsonl` committed; the replay test serves
      the recorded answer deterministically. Verify: observed + recorded.
- [x] 1.4 Gates; receipts; archive; commit.

## Receipt

- [x] red: unit tests red on the missing module (measured). green: 4/4 after implementation (hash hit, loud miss with known keys + Input preview, normalization stability).
- [x] REAL RECORDING: real ChatDeepSeek via the framework's own resolve_class seam + RecordingChatModel delegation — the real answer (EASA 开放类别：视距内 120m、避开人群、<25kg) recorded into tests/fixtures/replay/real-model-io.jsonl (committed, no key inside).
- [x] REPLAY PROOF: ReplayChatModel serves the recorded answer deterministically from the fixture (verified in the venv); the replay tests live in the integration lane (framework-dependent — the unit gate stays stdlib-only per A6's design).
- [x] Gates: VERIFY=0, SMOKE=0, CLOSEOUT=0, STRICT=0, HYG=0, DIFF=0; gitlink ceebf97f unchanged; archive; commit follows.

