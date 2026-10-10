# Fixed Bugs Index — 已修复 bug 归档

> 最后更新: 2026-10-10（BUG-001 修复关闭：fix-headless-plan-gate） | `_backlog/_archived/_fixed_bugs/` — 已修复 bug 的归档目录。
> 接收来自 [`../../bugs/`](../../bugs/) 的 bug。`_` 前缀 = coding agent 默认忽略。
>
> **本目录是 bug 编号的唯一权威来源——新 bug 的编号 = 已分配的最大编号 + 1（已修复目录 ∪ 活跃目录）。**

## 接收一个修完的 bug

bug 修完后从 `_backlog/bugs/` 通过 `git mv` 移入本目录：
1. 在本文件表格加一行（ID + Date + Title）
2. 更新下面的 "Next available bug ID"
3. 更新 `../../bugs/README.md`（删掉该 bug）
4. 更新 `../README.md`（计数 +1）

---

| ID | Date | Title |
|----|------|-------|
| BUG-001 | 2026-10-10 | [BUG-001-degenerate-plan-as-report.md](BUG-001-degenerate-plan-as-report.md) — headless 跑计划门缺席——计划输出直落 completed 冒充报告（fix-headless-plan-gate；根因确诊与初判修正在卡） |
| BUG-002 | 2026-10-10 | [BUG-002-doc-hygiene-next-id-blindspot.md](BUG-002-doc-hygiene-next-id-blindspot.md) — check_doc_hygiene 的账本 Next-ID 校验读不到活跃 README 声明——同文件双声明漂移全绿通过（harden-backlog-next-id-guard；∪ 推导单源化 + 声明唯一性/一致性双门禁） |

**Next available bug ID: BUG-003**
