# Proposal: Polish Guidance Vocabulary

## Why

plan C4 小件集合：语料吸收的最后一层词汇补丁——三处散落的指导缺口（术语误读栏、
"指南与代码冲突时信谁"、"上游边界与代价"）此前只有零星先例，没有成文位置。

## What Changes

- **CONTEXT-MAP.md 补"常见误读"节**（语料卷一术语表模式）：profile 同名异物、
  "测试绿=质量"混同、`engine/`（裁决）与 pump（运行泵）撞名三个高频误读。
- **`change-guidance/core/change-practice.md` Context Selection 节补一行**：
  指南与代码冲突时信代码及其测试——指南不过期靠 owner，不靠祈祷。
- **`change-guidance/profiles/deerflow-downstream/deerflow-downstream.md` 补
  "Upstream Boundaries"小节**（语料卷三 06 对策表的按需裁剪）：内嵌形态下的
  五条上游负面事实与对策（宿主内部无兼容承诺 / 上游文档=快照 / 无安全 SLA /
  startup-only 与扩展沙箱条目按内嵌形态标注不适用）。

## Capabilities

### New Capabilities

none: 纯指导词汇补丁，无规范级行为变更。

### Modified Capabilities

none: `skip_specs: true` 已声明。

## Impact

- 文件：`CONTEXT-MAP.md`（无预算，入口链外）、`change-guidance/core/
  change-practice.md`、`change-guidance/profiles/deerflow-downstream/
  deerflow-downstream.md`。根 AGENTS（余量 6 字符）与 harness AGENTS
  （预算顶格）刻意不动。
- 守卫：change-guidance checker 保持绿；doc-hygiene 不涉（文件均不在入口链
  预算表）。
- 不触碰 `deerflow/` gitlink。

## Change Focus

- **Primary module / causal owner:** `openspec/change-guidance/`（core + profile）
  —— 指导词汇与上游纪律的语义 owner；CONTEXT-MAP 是词汇站（其 Reading order
  自我声明）。
- **Seam classification:** wiring — 纯指导文本补丁。
- **Question:** 三个高频误读/缺口是否都有了成文的家，且不破任何预算？
- **Necessary adjacent/external contracts:** `check_change_guidance.py`（answers:
  change-guidance 树的片段完整性不因新增节破坏）；doc-budgets（answers: 落点
  避开预算顶格文件）；语料卷三 06（answers: 上游边界清单的内容来源，钉定
  v2.1.0，"上游参考"标注）。
- **Evidence seam:** change-guidance checker + doc-hygiene 退出码直测。
- **Not in scope:** 起步页（plan 明示可选，本仓入口链已够）；C5（独立 change）；
  根/模块 AGENTS 任何改动（预算顶格）。
- **Triggered review policies:** change-admission, local-context

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记。

## Delivery Record

- **外部行为**: （closeout 前填实）
- **影响面**: （closeout 前填实）
- **实际跑了什么**: （closeout 前填实）
- **未执行的检查**: （closeout 前填实）
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者授权全程推进，对交付负最终责任。
