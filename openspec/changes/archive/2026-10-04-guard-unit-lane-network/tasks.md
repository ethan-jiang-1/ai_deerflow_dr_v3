# Tasks

- [x] 1.1 Implement the unit-lane socket guard + write the negative control. Verify:
      red (the control proves a connection attempt is blocked, naming the test), then
      the suite green with the control asserting the block.
- [x] 1.2 Limitation row + gates (verify/smoke/closeout/hygiene); receipts; archive;
      commit.

## Receipt

- [x] Guard active for tests/unit (socket construction raises NetworkDisabledError naming the lane and the remedy); negative control proven (a connecting attempt is blocked — red path); VERIFY=0, SMOKE=0 (the integration lane unaffected).
- [x] Limitation row added; gates below; archive; commit.

