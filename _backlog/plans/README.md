# Plans — plan/分析文档索引

> 最后更新: 2026-10-04（新增 agent-playbook-and-minimal-release：agent 启动面收归仓库文档 + 发布约束） | `_backlog/plans/` — 活跃 plan 在此（顶层），
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
| [agent-playbook-and-minimal-release](2026-10-04-agent-playbook-and-minimal-release.md) | 两层结构：COMMANDS=入口菜单，playbook/=MD mixed with CLI 子目录；发布面实证=两件套（harness+deerflow submodule，openspec 在外）+ 冷启动判据；待 REVIEW，拟入线 `ratify-agent-playbook-and-minimal-release` |

（空）

**Next available plan ID: CLS-010**（移入 `_closed_plans/` 时分配）

## 已归档（移至 `_done/_closed_plans/`）

| Plan | Change | 归档日期 |
|------|--------|----------|
| CLS-001 execution-roadmap | establish-project-structure（已 archive） | 2026-10-02 |
| CLS-002 borrow-dsh-harness-gap-analysis | add-ci-governance + harden-change-practice-guidance + add-doc-budget-gate（均已 archive） | 2026-10-02 |
| CLS-003 digest-deerflow-native-deep-research | 六裁决推敲定案 + 三份衍生 plan（wiring-structure / bundle-contract / entry-surface）拆解落账 | 2026-10-02 |
| CLS-004 bundle-contract | establish-run-bundle + establish-run-admission（均已 archive；决策 1/2/3/5/6 → 底座 change，决策 4 → 验收收口 change） | 2026-10-03 |
| CLS-005 entry-surface | establish-entry-surface（已 archive；六子命令 + 渲染 + EV2 证据） | 2026-10-03 |
| CLS-006 wiring-structure | remove-graph-layer + establish-embedded-wiring + pin-subagent-knobs（均已 archive；决策 5 以 posture + 守卫处置） | 2026-10-03 |
| CLS-007 stream-adapter-and-live-view | fix-stream-adapter（已 archive；真实流形状适配 + journal 聚合 + token 内联直播） | 2026-10-03 |

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
