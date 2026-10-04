# Known Limitations（当前已知限制）

> 面向接手者的**存续中**限制清单（与 change design 的 `## Alternatives` 分层不重复）。
> 每条标注来源与当前处置；已处置条目不在此保留，指向其归档 change。

## 存续中

| 限制 | 来源 | 处置 |
| --- | --- | --- |
| 大 bundle 上 state.json 瞬时缺失（fail-loud StateCorruption 兜底，无静默损坏） | refine-slim-restart gen-7 尝试 | 待诊断（疑似 FS 压力） |
| checkpoint delta 依赖框架的 delta-history patch（langgraph 1.2.12 高于验证版 1.2.9）：警告常驻 stderr（非失败），升级 langgraph 前先复查该 patch | switch-checkpoint-delta | 存留告诫（结构未变） |

## 已处置（指针，细节归归档 change）

LLM 失败降级守卫 → `2026-10-03-surface-llm-error-fallback`；CI 集成冒烟 →
`ci-integration-lane`；深研究递归上限（上游 `deerflow/backend/packages/harness/deerflow/client.py:293`）→
`2026-10-04-pass-recursion-limit` + `2026-10-04-raise-recursion-limit`；checkpoint 体积 →
`2026-10-04-switch-checkpoint-delta`；unit lane 网络守卫 → `2026-10-04-guard-unit-lane-network`。
