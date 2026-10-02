# Plans — plan/分析文档索引

> 最后更新: 2026-10-02（DSH 借鉴 plan 关闭：CLS-002，A–F 全吸收；当前主线移交 digest 边界 plan） | `_backlog/plans/` — 活跃 plan 在此（顶层），
> 完成的普通 plan 移入 [`../_done/_closed_plans/`](../_done/_closed_plans/)。
>
> **plan 没有编号，文件名即标识。完成后文件名不变，位置即状态。**
>
> ⚠️ **文件名必须以日期编码开头：`YYYY-MM-DD-<name>.md`。这是强制约定，不是惯例**——
> 无日期前缀的 plan 无法按时间排序与追溯（历史经验教训，v2 踩过）。

## 完成一个 plan 的步骤

1. `git mv plans/<name>.md _done/_closed_plans/<name>.md`
2. 更新 `_done/_closed_plans/README.md`（加一行 + 更新 Next available plan ID）
3. 更新本文件（删掉该 plan）
4. 更新 `../_done/README.md`（计数 +1 closed）

**plan 是"分析/设计/复盘"文档，不是活跃 change 本身。** 真正的实施走 `openspec/changes/`；plan 记录的是思考、取舍、复盘（postmortem），一旦其结论已落地或被 change 吸收即可关闭。

---

## 活跃列表

| Plan | 一句话 |
|------|--------|
| [2026-10-02-digest-deerflow-native-deep-research.md](2026-10-02-digest-deerflow-native-deep-research.md) | 消化 DeerFlow v2.1.0 原生 Deep Research 能力，划定 v3 harness 的职责边界；**当前主线**（决策/方案四问待填，goal 队列第 3 项：change ② 消化四问） |

**Next available plan ID: CLS-001**（移入 `_closed_plans/` 时分配）

## 已归档（移至 `_done/_closed_plans/`）

| Plan | Change | 归档日期 |
|------|--------|----------|
| CLS-001 execution-roadmap | establish-project-structure（已 archive） | 2026-10-02 |
| CLS-002 borrow-dsh-harness-gap-analysis | add-ci-governance + harden-change-practice-guidance + add-doc-budget-gate（均已 archive） | 2026-10-02 |

---

## 卡片模板

新建 plan 文件 `YYYY-MM-DD-<name>.md`（日期前缀强制，见上；slug 用 kebab-case）：

```markdown
# Plan: <标题>

> 类型: 设计 / 分析 / 复盘（postmortem） | 更新: 2026-MM-DD

## 背景 / 现状
触发这份 plan 的问题、当前状态、约束。

## 决策 / 方案
关键技术选择与理由（为什么 X 不是 Y），含考虑过的备选。

## 风险 / 取舍
已知限制、可能出问题的点。格式：[风险] → 缓解。

## 落地关联
计划如何变成 `openspec/changes/` 里的 change（或已被哪个 change 吸收）。
```
