# Design: harden-backlog-next-id-guard

## Context

BUG-002 卡在案（症状/根因/复现齐备）。2026-10-10 同日已完成：Next-ID 推导模型扩为
"归档 ∪ 活跃"（`BACKLOG_ARCHIVE_TO_ACTIVE`）+ self-test 负例（archive-only 声明看红、
∪ 一致声明保持绿）。**未做**：ledger README 内声明行本身的唯一性与声明值一致性校验。
当前树状态：四个编号面 README（`issues/`、`bugs/`、`_archived/_fixed_bugs/`、
`_archived/_settled_issues/`）各恰一条声明、值与推导一致（手工去重后的临时防线），
新规则上线即绿。

## Goals / Non-Goals

- Goals：声明行唯一性（每文件每前缀 ≤1 条）与声明值一致性（== ∪ 推导）进 checker；
  负例先红后绿；推导逻辑单一来源化（counters 检查与声明检查共用，防两处漂移）。
- Non-Goals：不改账本文件内容；不管理挂起池（无编号面）；不引入 YAML frontmatter；
  不动 CI 声明面。

## Approach

1. **推导单一来源**：把 counters 检查内的 ∪ 推导（index 表行 ∪ 归档卡名 ∪ 活跃卡名
   → max+1）抽为 `_derived_next_ids(backlog_root) -> dict[str, int]`（按前缀 BUG/CLS），
   counters 循环与新声明检查共用。
2. **声明扫描**：新增 `_rule` 片段扫四个编号面 README 的非表格行，匹配
   `Next available <PREFIX>-NNN` 声明（复用 `BACKLOG_NEXT_ID_RE`，行锚定
   "Next available" 字面）；每文件每前缀 >1 条 → violation（点名文件与两条冲突声明）；
   恰一条且值 ≠ 推导 → violation（点名文件、声明值、推导值）。
3. **self-test 负例**：在现有 ledger fixture 区追加——负例 A（同文件双声明其一旧值）、
   负例 B（单声明旧值）；断言各自的新 violation 消息被检出；随后改正值断言保持绿。

## Alternatives

- **只约定"单声明点"、不加机器校验**（本次审计已手工去重）——输在：BUG-002 已证明
  该惯例会被同日多次改动无声破坏；无守卫的约定正是缺陷原形。
- **删除全部人读声明、只留 counters 表**——输在：立卡/接收动作发生在 `bugs/`、
  `_settled_issues/` 现场，就地指针有 co-location 价值；删指针把每次取号变成跨目录
  查找，且丢失"声明 vs 推导"这个可检查事实本身。
- **把检查放进 `check_ci_governance` 声明面**——输在：Next-ID 是文档层事实而非 CI
  工作流声明；放错 owner 会制造第二权威。

## Open Questions

none: 检测点、法则出处、负例形状均由 BUG-002 卡与本设计定案。
