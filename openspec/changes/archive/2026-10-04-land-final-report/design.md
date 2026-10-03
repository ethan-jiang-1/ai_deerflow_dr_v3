# Design

> 补记 (2026-10-04): 与 tasks.md 同因补录；内容为归档前实际采用的设计。

## Decisions

1. Submission in the engine's clean-completion branch only (fallback/failed/empty never
   submit); filename report-gen<N>.md ties the file to the generation.
2. Placement branch in admission: final_report -> final/<filename> (RUB-001's declared
   routing); everything else unchanged.
3. The final answer text comes from the terminal picture's last AI message (values
   snapshot authoritative), not the chunk buffer.

## Alternatives

CLI-side submission — rejected (second authority). Model-decided admission — rejected
(the project's core ruling).

## Risks / Trade-offs

[Empty-but-completed answers] -> non-empty guard; empty completions skip submission.
