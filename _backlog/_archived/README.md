# _archived — 已完成/暂停的归档记录

> 最后更新: 2026-10-09（adopt-issue-ledger-governance 更名：_closed_plans → _settled_issues、_suspended_plans → _suspended_issues；closed issues 18） | `_backlog/_archived/` — 已完成内容与明确暂停项的归档根目录。
> **`_archived/` = 归档工作件，coding agent 默认忽略，除非显式点名要读**（`_` 前缀的两类语义见 [`../README.md`](../README.md)）。
>
> 状态总览和查阅指南在本文件。当前该做什么、执行顺序 → 活跃列表见 [`../issues/README.md`](../issues/README.md)（新方向按其卡片模板立 issue）。

## 目录

```
_archived/
├── README.md              # 本文件（状态总览 + 查阅指南）
├── _fixed_bugs/           # 已修复 Bug（编号权威源）
├── _suspended_bugs/       # 悬挂 Bug（暂未确认修复）
├── _settled_issues/       # 已结 Issue（CLS-NNN 台账）
└── _suspended_issues/     # 明确暂停、保留重启条件的 issue/延期跟进
```

---

## 状态总览

### ✅ DONE（已完成/已归档）

| 归档目录 | 数量 | Next ID |
|---------|------|---------|
| `_fixed_bugs/` | 0 | BUG-001 |
| `_settled_issues/` | 18 | CLS-019 |

### ⏸ SUSPENDED（明确暂停）

| 归档目录 | 数量 | 重启方式 |
|---------|------|---------|
| `_suspended_bugs/` | 0 | 确认修复后移回活跃 bug 流程 |
| `_suspended_issues/` | 0 | 显式新优先级决定后移回活跃目录 |

_Closed issue count follows the indexed CLS records; each future move increments the count and Next ID together._

---

## 快速查阅指南

### 想看"现在该做什么"
→ [`../issues/README.md`](../issues/README.md) 的活跃列表。

### 想看 _backlog 的规矩
→ [`../README.md`](../README.md) — 关闭条件四态表、状态词表、搬迁 ritual、刻意不借登记。

### 想看历史决策
→ `_settled_issues/` 下的卡（分析/复盘/推敲，按文件名主题查阅）。

### 想看已明确暂停的工作
→ [`_suspended_issues/`](_suspended_issues/)；其中的记录不是已完成项，只有在重新获准排期时才回到活跃目录。

> 前代仓库 `ai_deerflow_deep_research_v2` 的完整归档（194 个 OpenSpec change、62 个 CLS、82 个 BUG、10 个 DONE）留在 v2 仓库内，不迁移；需要历史决策时回 v2 查。
