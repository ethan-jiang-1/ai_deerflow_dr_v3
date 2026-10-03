# Tasks

- [x] 1.1 Declare the delta mode in both configs. Verify: make smoke exits 0 (multi-turn + readable checkpoint on delta).
- [x] 1.2 Real run: a small real question; measure the checkpoint size vs the 192K baseline and exercise the prior-thread read. Verify: observed + recorded.
- [x] 1.3 Limitation row closes (with the patch caveat); gates; receipts; archive; commit.

## Receipt

- [x] delta declared in both configs; SMOKE=0 (multi-turn + readable checkpoint ON delta), VERIFY=0.
- [x] REAL RUN on delta: completed; checkpoint 144K vs the 192K full-mode short-run baseline (the deep-run slope benefit is per-step x message-list — the 1.0G monster's growth mode is structurally removed); get_tuple read path OK on delta; report landed in final/. The langgraph-1.2.12 patch warning remains visible in stderr (non-failing) — recorded as the standing caveat.
- [x] limitation row closes (addressed-by-declaration, patch caveat kept); gates below; archive; commit.

