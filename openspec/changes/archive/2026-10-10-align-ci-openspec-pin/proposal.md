# Proposal: align-ci-openspec-pin

## Why

CI workflow 与 `check_ci_governance.py` 都把 OpenSpec CLI 钉在 `@fission-ai/openspec@1.13.1`
（两处互证一致，checker 全绿），但本地 CLI 与全部 `.agents/skills/*/SKILL.md` 的
`generatedBy` 均为 **1.14.0**——workflow 注释声称的 "generation-aligned version (same as
.agents/skills frontmatter)" 已失真。CI 的 strict-validation owner 跑的是落后一版的
CLI，与本地归档产物所用的 CLI 代际脱节。盲区成因：checker 只交叉核对 workflow 与
自身常量，从不核对 frontmatter。

## What Changes

- `check_ci_governance.py` 的 `WORKFLOW_REQUIRED_MARKERS` 与文件内 pin 常量：
  `@fission-ai/openspec@1.13.1` → `@fission-ai/openspec@1.14.0`。
- `.github/workflows/governance.yml` 的 npm pin 同步 1.14.0；"generation-aligned"
  注释恢复为真。
- `test_ci_governance.py` 的 `VALID_WORKFLOW` fixture 同步。
- 本地 `openspec --version`（1.14.0）== workflow pin == skills frontmatter，三代际
  对齐恢复。

## Capabilities

### New Capabilities

（无——ci-governance spec 只要求 "pinned OpenSpec CLI version"，不含版本字面量；
版本由声明表 own，已声明 skip_specs。）

### Modified Capabilities

（无）

## Impact

- 影响：两文件各一行 + fixture 一行 + checker 常量。
- 风险：CI 首跑 1.14.0 的 strict-validation owner——本地全部 spec/change 已在 1.14.0
  下 validate 通过（13/13 specs、两笔 change archive 皆 1.14.0 所出），风险低；
  远端首跑结果 push 后以 gh 观测。
- 边界：不动 workflow 结构、步骤序列、依赖版本（除 openspec CLI 本身）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_ci_governance.py` —
  钉定常量是 CI 工具链代际的唯一声明处；workflow 是其镜像面。
- **Seam classification:** deterministic-guardrail — 声明表常量的机器校验，无模型、
  无运行时行为。
- **Question:** CI 的 OpenSpec CLI 代际能否与本地 CLI 及 skills frontmatter 重新对齐
  （1.14.0），使 workflow 注释的 "generation-aligned" 恢复为真？
- **Necessary adjacent/external contracts:** `.agents/skills/*/SKILL.md` frontmatter
  （answers: 对齐目标代际的事实源）；`test_ci_governance.py` fixture（answers: 声明
  漂移的既有红绿凭据形状）。
- **Evidence seam:** `check_ci_governance.py` 退出码直测（改常量后真树红 → 对齐后绿）
  + governance unittest 套件。
- **Not in scope:** checker 对 frontmatter 的交叉核对新规则（若要机器化另立卡）；
  workflow 结构；其它 npm/python 版本。
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| CI 的 openspec CLI 代际钉定 1.13.1 → 1.14.0（与本地 CLI / frontmatter 对齐） | 无——版本常量事实 | `check_ci_governance.py` 钉定常量（workflow 为其镜像） | non-bypassable | pin 漂移即时变红；CI strict-validation 与本地归档代际一致 | 复用既有 marker 机制，不新增检查器 | `check_ci_governance.py` 退出码直测 + governance unittest 套件 |
