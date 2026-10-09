# Issues — 活跃 issue 列表（推敲 → 结论 → 交接）

>
> **CLS 编号权威在 `_done/_settled_issues/`；新号 = 已分配的最大编号 + 1，移入时分配（Next available plan ID: CLS-019）。本文件只列活跃 issue，活跃卡本身不带编号，文件名即标识。**
>
> ⚠️ **文件名必须以日期编码开头：`YYYY-MM-DD-<name>.md`。这是强制约定，不是惯例**——无日期前缀的卡无法按时间排序与追溯（历史经验教训，v2 踩过）。

## 完成一个 issue 的步骤

1. `git mv issues/<name>.md _done/_settled_issues/<name>.md`
2. 更新 `_done/_settled_issues/README.md`（加一行 + 更新 Next available plan ID）
3. 更新本文件（删掉该卡）
4. 更新 `../_done/README.md`（计数 +1 closed）

**issue 是"分析/设计/复盘/推敲"卡，不是活跃 change 本身。** 真正的实施走 `openspec/changes/`；一旦其结论已被 change 吸收或落地，按上方 ritual 关闭。明确暂停的进 [`../_done/_suspended_issues/`](../_done/_suspended_issues/)——挂起不是完成。

---

## 活跃列表

| Issue | 一句话 |
|------|--------|
| [2026-10-09-backlog-governance-reborrow.md](2026-10-09-backlog-governance-reborrow.md) | _backlog 治理反向借鉴：plans→issues 更名 + 活触发器索引 + 门禁补盲（apply 中，adopt-issue-ledger-governance） |

**Next available plan ID: CLS-019**（移入 `_settled_issues/` 时分配）

新方向性工作**必须显性立卡**（驾驭者要求，2026-10-07）：先立卡记录决策与取舍，再走 OpenSpec change 实施；完成后按上方 ritual 关闭归档。

---

## 卡片模板

新建 issue 文件 `YYYY-MM-DD-<name>.md`（日期前缀强制，见上；slug 用 kebab-case）：

```markdown
# Issue: <标题>

> 立卡: YYYY-MM-DD ｜ 状态: 推敲中 ｜ 类型: Feature / Task / 未定 ｜ 毕业门: 未过 ｜ 可关闭: 否

**问题与期望结果：** 什么情况引出了问题，希望得到什么结果，怎么算完成。
**当前情况：** 已经确定什么。
**未决问题：** 还缺什么事实或选择。
**下一步：** 谁来做什么，或等待什么具体条件。

## 已知与未决

## 方案与取舍
关键技术选择与理由（为什么 X 不是 Y），含考虑过的备选与风险（[风险] → 缓解）。

## 落地关联
计划如何变成 `openspec/changes/` 里的 change；毕业后写明 change 名与状态。

## 关闭条件
四态之一（做 / 以后做 / 不做 / 结论已在别处），见 ../README.md 关闭条件表。
```

## 状态词表（机器校验，`check_doc_hygiene.py` 强制）

| 字段 | 词 | 说明 |
|---|---|---|
| `状态` | `推敲中` / `等人拍板` | 活跃区只用这两个；等人拍板的卡诚实停在活跃区，不是完成词 |
| `毕业门` | `未过` / `已过 → <change 名>` | 已过仍滞留活跃区 → 门禁红 |
| `可关闭` | `是` / `否` | 声明"是"仍滞留活跃区 → 门禁红 |
| `类型` | `Feature`（可观察行为会变）/ `Task`（要交出代码、文档、配置或结论）/ `未定` | 分不清写 `未定`；旧卡不回填 |

离开本目录时状态行只改状态词（`已结` / `叫停`），其余字段与正文原样保留，不把正文长说明抄进状态行。
