# Tasks

> 补记 (2026-10-04): 本工件集为归档后补录——实现先行于流程（e2a21d8），实现 diff 未变；
> 回执为当期实测。

- [x] 1.1 The guard (COMMANDS/Makefile/cli consistency + register pairing) implemented and
      green; the first run caught REAL structure (loop-tuple indirection under-reporting
      four verbs) — the guard was corrected to pin the declared COMMANDS tuple.
- [x] 1.2 Negative control measured in-session: removing a documented make target from
      COMMANDS.md turned the guard red; restored green.
- [x] 1.3 Gates: VERIFY=0 (105 tests), GOV=0, CLOSEOUT=0, HYG=0, DIFF=0; gitlink
      ceebf97f unchanged.
- [x] 1.4 This artifact set + archive + commit (the standing discipline's correction
      commit).
