# Tasks

> 补记 (2026-10-04): 本文件与 design.md 在归档后补录——脚手架脚本在写 specs 时崩溃，
> 先于本两件工件；以下回执为归档前实测的真实退出码与证据，如实记录。

- [x] 1.1 Unit tests red: engine clean-completion submits final_report (ledger admit + final/ file); fallback completion never submits; admission places final_report at final/<filename>. Receipt: red measured (2 failures). One assertion corrected mid-green (final/ exists by the start contract — the assert targets its contents; disclosed).
- [x] 1.2 Implement the completion submission + placement branch. Receipt: VERIFY=0, SMOKE=0.
- [x] 1.3 Real-ladder proof. Receipt: small real question completed gen-1; final/report-gen1.md exists with the real EASA open-category answer (A1/A2/A3, 25kg, 120m, VLOS); ledger = [(1, 'admit', 'final_report', 'final/report-gen1.md')] — the QC loop closed end-to-end on a real model run.
- [x] 1.4 Full gates. Receipt: GOV=0, CLOSEOUT=0, STRICT=0, DIFF=0; gitlink stage-0 ceebf97f unchanged; archive green (MODIFIED merged: both specs carry the new clauses); commit af2ef88 + this correction commit.
