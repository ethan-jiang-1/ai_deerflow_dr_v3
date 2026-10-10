# Proposal: widen-doc-link-guard-scope

## Why

doc-hygiene checker 的相对链接规则只覆盖 entry-chain 与 docs-layer 两份封闭清单；
`deep_research_harness/tests/README.md`、`tests/fixtures/README.md`、`tools/README.md`
三份测试/工具资产文档在范围外。2026-10-10 fresh-agent 全库审计实测：tests 目录按
owner 分组重排（2026-10-05 group-unit-tests-by-owner）与 runtime 改名
（2026-10-07 surface-runtime-structure）后，三份文档里 **18 条相对死链**存活至今
（15 + 3），恰是新 agent「加测试」必经地图——人工清扫已修（1bb28b2），但没有
机器守卫，同类漂移会再来。

## What Changes

- checker 的 `_rule_links`（与编码/换行规则同批）范围扩至三份资产文档
  （`tests/README.md`、`tests/fixtures/README.md`、`tools/README.md`）——新清单
  `LINKED_ASSET_DOCS`，与既有 entry-chain / docs-layer 列同一规则引擎
- checker `--self-test` 负例电池新增案例：临时树中资产文档含死链 → 红；
  修复 → 绿（红先绿后，规则自身可证伪）
- 文档同步：governance README 的 `check_doc_hygiene.py` 行措辞
  「入口链与 docs 层的相对链接」→「入口链、docs 层与测试/工具资产文档的相对链接」
- spec delta：doc-truthfulness **ADDED** requirement——受管文档面的相对链接
  SHALL 在盘上可解析（把既有+扩面后的链接规则落进规范，此前该规则无 spec 归属）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `doc-truthfulness`: ADDED requirement「Managed doc surfaces' relative links resolve
  on disk」——链接规则的规范归属 + 扩面后的封闭清单语义

## Impact

- 影响：checker 一条规则的范围清单 + self-test 一案例 + governance README 一行 +
  doc-truthfulness 主 spec 一条 ADDED requirement
- 风险：低——三份文档当前 0 死链（人工清扫后实测 568 链接全通过），规则上线即绿；
  未来死链在 CI doc-hygiene 步（已在 canonical 序列）当场红
- 边界：不改链接规则引擎本身（ MARKDOWN_LINK_RE、http/mailto/# 跳过、锚点截断语义
  不变）；不覆盖 openspec/changes/archive/ 与 `_backlog/_archived/`（归档 = 历史上下文，
  按其自身政策不追溯）；不做锚点存在性校验（行号锚随实现漂移，锁文件存在性即可——
  限制写进 spec 与 checker docstring）

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` 的
  `_rule_links` 范围清单——链接规则的行为承载
- **Seam classification:** deterministic-guardrail — 纯文件存在性的机器校验；无模型、无运行时行为
- **Question:** 链接规则的受管面能否扩到测试/工具资产文档，使「分组重排/改名漏改
  相对路径」这一漂移类在 CI 当场红？
- **Necessary adjacent/external contracts:** doc-truthfulness 主 spec（本 change 给
  链接规则以规范归属）；checker `--self-test` 负例电池（红绿凭据形状）；CI canonical
  序列已含 doc hygiene 步（无需改 workflow/spec ci-governance）
- **Evidence seam:** self-test 红（临时树资产文档死链 → 非零退出并点名）→ 扩面绿 →
  真树全绿（`check_doc_hygiene` exit 0）→ 治理 unittest 套件全绿
- **Not in scope:** 锚点存在性校验；归档面链接追溯；markdown lint（格式类规则非本仓
  守卫哲学）；`check_release_face` 的 COMMANDS 路由检查（独立已有）
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 三份资产文档的相对链接 SHALL 盘上可解析 | 无——纯文件存在性事实 | `_rule_links` 扩面 + `LINKED_ASSET_DOCS` 封闭清单 + self-test 负例 | non-bypassable | 受管面扩张必须改声明清单（visible change），不可静默扩权 | 复用同一链接引擎与 self-test 电池，不新增 checker | self-test 红→绿 + 真树 exit 0 + 治理 unittest 全绿 |
