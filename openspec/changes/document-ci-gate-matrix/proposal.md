# Proposal: Document CI Gate Matrix

## Why

plan C5（可选项，机制已够仅写明）：本仓 CI 是单 job 全序列，主仓"契约双端触发"
语义天然满足，但这一语义从未写明——读者无法从文档知道"框架绑定面或应用面任一
变更都会触发完整序列"是刻意设计而非巧合。

## What Changes

- `openspec/governance/README.md` 的 CI 门禁段落补一句双端触发语义：单 job
  canonical 序列使"任一受治理面（应用/框架绑定/spec/治理自身）变更都跑完整
  序列"成为结构事实，主仓的路径分流双端触发原则在此形态下由全序列承担。

## Capabilities

### New Capabilities

none: 文档写明既有语义，无任何机制或 requirement 变更。

### Modified Capabilities

none: `skip_specs: true` 已声明；ci-governance spec 的 requirement 不变。

## Impact

- 文件：`openspec/governance/README.md`（一段一句）。check_ci_governance.py
  校验的是 workflow 声明而非 README 散文，保持绿。
- 不触碰 `deerflow/` gitlink。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/README.md` —— CI 门禁
  叙述的文档 owner（机制本身由 workflow 与 checker 拥有，本 change 只写明）。
- **Seam classification:** wiring — 纯文档一句。
- **Question:** 双端触发语义是否可见于文档？
- **Necessary adjacent/external contracts:** `check_ci_governance.py`（answers:
  文档措辞不进其声明校验面，不产生漂移红灯）；语料卷二 05（answers: 语义出处
  ——主仓 replay E2E 的双端触发动机，"上游参考"）。
- **Evidence seam:** governance checker + doc-hygiene 退出码直测。
- **Not in scope:** 任何 workflow/checker 机制变化；发版门/迁移链（明确不搬）。
- **Triggered review policies:** change-admission

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记。

## Delivery Record

- **外部行为**: （closeout 前填实）
- **影响面**: （closeout 前填实）
- **实际跑了什么**: （closeout 前填实）
- **未执行的检查**: （closeout 前填实）
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者授权全程推进，对交付负最终责任。
