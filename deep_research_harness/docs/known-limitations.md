# Known Limitations（当前已知限制）

> 面向接手者的**存续中**限制清单（与 change design 的 `## Alternatives` 分层不重复）。
> 每条标注来源与当前处置；已处置条目不在此保留，指向其归档 change。

## 存续中

| 限制 | 来源 | 处置 |
| --- | --- | --- |
| bundle 目录级瞬时不可见（外部进程干扰 gitignored 的 `scopes/`：移动/同步/清理）在读取时曾误报为 `state.json is missing`——诊断已证实 state.json 写路径 temp+replace 原子、无应用内删除者，事故文件在窗口内持续存在（mtime/revision 未变），与 checkpoint full/delta 无因果；读分类已修正（honest-state-read-diagnosis：目录级→unavailable，文件级→带 phase 与 tmp-siblings 证据的 corruption）。存留：兜底内二次读失败会使终态写缺席、bundle 滞留 active（可由 crash-transfer 恢复）。UNVERIFIED：当时触碰 `scopes/` 的外部进程身份；被兜底掩盖的 gen-7 首发异常。 | refine-slim-restart gen-7 尝试 + 专项诊断 | 诊断收口（分类已修，外部条件不可由应用预防） |
| checkpoint delta 依赖框架的 delta-history patch（langgraph 1.2.12 高于验证版 1.2.9）：警告常驻 stderr（非失败），升级 langgraph 前先复查该 patch | switch-checkpoint-delta | 存留告诫（结构未变） |

## 已处置（指针，细节归归档 change）

LLM 失败降级守卫 → `2026-10-03-surface-llm-error-fallback`；CI 集成冒烟 →
`ci-integration-lane`；深研究递归上限（上游 `deerflow/backend/packages/harness/deerflow/client.py:293`）→
`2026-10-04-pass-recursion-limit` + `2026-10-04-raise-recursion-limit`；checkpoint 体积 →
`2026-10-04-switch-checkpoint-delta`；unit lane 网络守卫 → `2026-10-04-guard-unit-lane-network`。
