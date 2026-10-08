# Design

## Context

三处落点均无预算约束（CONTEXT-MAP 在入口链外；change-guidance 文件不受
DOC_BUDGETS 管）；根与模块 AGENTS 预算顶格，是本 change 刻意避开的两块。

## Goals / Non-Goals

**Goals:** 三个误读/缺口各归其位，行数极小。

**Non-Goals:** 起步页；任何预算文件改动；C5。

## Decisions

**D1 误读栏进 CONTEXT-MAP**（它是词汇站的自我定位，语料卷一术语表即此模式），
不进各层 CONTEXT.md（三份，每份都要动）。
**D2 "信代码"行进 change-practice 的 Context Selection**（上下文选择时以
owner 为准正是该节的语义）。
**D3 上游边界小节进 deerflow-downstream profile**（Pin 纪律的邻居；五条按
内嵌形态裁剪，"上游参考"标注钉定版本）。

## Alternatives

- 误读栏进三份 CONTEXT.md：落败——三处维护面，CONTEXT-MAP 已自我定位为
  vocabulary stop。
- 上游边界清单进根 AGENTS：落败——预算顶格，且层次不对。

## Risks / Trade-offs

- [误读栏与各层 CONTEXT 漂移] → 误读栏只列"哪个词有两个 owner/哪个混同最常见"
  并指向各 owner，不复制定义。

## Migration Plan

纯文本，回滚 revert。

## Open Questions

none
