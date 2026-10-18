# Design

## Context

证据见 `proposal.md` — Why。**本把的起点是我上一把的两处错误判断**，它们塑造了整个设计：

| 我上一把的判断 | 实测（探针） |
|---|---|
| 工作流级 review 校验"在**调用方那层**" | 就在 `_validate_program_proposal` 内部（367 行） |
| "需要**整棵树**夹具" | 只需**每个策略一个文档文件**（`POLICY_REGISTRY[policy].path`） |
| review 记录标题 | program 工作流是 **level-4**（`#### X`），普通提案是 level 2——常量里的标题是**裸标题**，level 由调用方拼 |

## Goals / Non-Goals

**Goals:** 覆盖工作流级 review 的 7 个码 · 更正上一把的错误前提（保留原文 + 日期注记）·
实现 diff = 0 · 变异能红 · 不新增 skip。

**Non-Goals:** 余下 3 个形状/取值类码（见 D-3）· 改实现 · 产品代码。

## Decisions

### D-1｜夹具按"每策略一个文档文件"而不是整棵树

- **选**：`_raise_with_documents(text, policies)` 在临时 root 里为命名策略造出 `POLICY_REGISTRY[policy].path`（内容一字节即可）。
- **为什么**：这是探针实测出来的**真实成本**——`_triggered_policies` 只要求该文档**存在**（它读一次），
  并不解析其内容。整棵树是多余的。
- **代价**：夹具多一个 helper。
- **换来**：7 个码的覆盖成本从"一把 change"降到"一个旋钮"。

### D-2｜`policies` 作为工作流级的旋钮，默认保持原样

- **选**：`_workstream_body(..., policies="none: 只读校验，不触发任何评审")`，既有 38 条用例不受影响。
- **为什么**：真实策略会牵动"文档存在 + review 记录存在且形状合法"三层；默认的 `none:` 是**不牵动任何
  一层**的姿态，正典绿例与其余用例因此保持稳定。
- **换来**：新增用例只在需要时才打开这一层。

### D-3｜余下 3 个码明确不做，并写明"为什么不做"

- **选**：不覆盖 `control_placement_review_posture_invalid` ·
  `control_placement_human_interaction_policy_missing` · `node_agent_review_classification_invalid`。
- **为什么**：它们要求先造出**合法形状**的记录（正确的列、正确的行数）再放一个**坏取值**——需要逐个读
  校验器的取值域与列的语义，夹具面比"缺失/畸形"大一档。本把已经把"缺失 + 形状"这一层做完。
- **换来**：范围干净，且**不是"忘了"，而是"记着不做"**（写进 Not in scope 与交付记录）。

### D-4｜更正记录本身是本把的交付物之一

- **选**：在 `cover-program-mode-codes` 的 `tasks.md` 与 `design.md` 各加一条**日期追记**，指出它那两处
  前提被证伪。
- **为什么**：这正是本会话写进账本章程的「归档记录的引用约定」——**指向未来的话被做掉时要追记**，
  而**错误的前提**若不更正，后来者会照着它再判断一次"那半很贵、以后再说"。
- **换取**：记录与现实一致；本把的动机也对后来者可见。

## Risks / Trade-offs

- [策略文档内容为空导致别的检查失败] → 探针实测只要求"存在"（`_read_file` 读一次），一字节内容即可 ✓。
- [level-4 vs level-2 写错导致"记录缺失"误判] → 用例里的畸形记录就是 level-4（`####`），与 program 路径
  一致；这也正是探针第一版（我用 `####` 却仍报 missing）教我的一课：**先确认层级再断言**。
- [更正归档记录被当成改历史] → 保留原文 + 日期注记，符合章程约定（本会话第 4 次使用该约定）。
- [把"不做"写成"忘了"] → D-3 双处记录（Not in scope + 交付记录）。

## Migration Plan

1. 夹具加 `policies` 与 `_raise_with_documents`。
2. 加 7 条用例；跑绿。
3. 变异（关掉工作流级 review 校验 ⇒ 6 条红）——第 7 条在 `_triggered_policies` 中抛，正确不受影响。
4. 追记更正上一把的记录。
5. 门禁；收口。

**回滚**：撤销 diff（7 条用例 + 夹具 helper + 两条追记）。
