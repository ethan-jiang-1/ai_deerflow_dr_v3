# Proposal: cross-check-cli-pin-generation

## Why

1.13.1 漂移事故的盲区复盘：checker 只交叉核对 workflow 与自身常量——两处一起陈旧即
全绿，而真相源（`.agents/skills/*/SKILL.md` 的 `generatedBy` frontmatter，即实际产出
本仓全部 spec/change 的 CLI 代际）不在任何校验路径上。align-ci-openspec-pin 修了
代际，没修盲区：下次 skills 以新 CLI 再生、workflow pin 忘跟，同样的静默漂移会再演。

## What Changes

- `check_ci_governance.py` 新增代际交叉核对：从 `.agents/skills/*/SKILL.md` frontmatter
  收集 `generatedBy`，与 workflow 的 `@fission-ai/openspec@X` pin 比对——缺失、歧义
  （多个不同值）、不一致（pin ≠ generatedBy）三类皆红，点名两侧值。
- `test_ci_governance.py` 增三负例（不一致 / frontmatter 缺失 / generatedBy 歧义）
  与一正例（对齐保持绿）。
- `ci-governance` spec 的 "The enforcement declarations are guarded against drift"
  MODIFIED：增加代际交叉核对 SHALL 与 scenario。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `ci-governance`: MODIFIED——"The enforcement declarations are guarded against drift"
  增加：checker SHALL 交叉核对 workflow 钉定的 CLI 代际与 skills frontmatter 的
  `generatedBy`，缺失/歧义/不一致 SHALL fail loudly。

## Impact

- 影响：`check_ci_governance.py`（+一个核对段）、`test_ci_governance.py`（+4 用例）、
  spec delta。当前树 pin 与 frontmatter 均为 1.14.0，新规则上线即绿。
- 风险：`.agents/skills/` 是用户保留区——checker **只读**其 frontmatter（openspec CLI
  自身亦然），不改不写；skills 以新 CLI 再生时 workflow pin 需跟随（这正是对齐耦合
  的目的：代际失配 push 即红，而非静默）。
- 边界：不改 workflow、不改 skills 内容、不引入 npm/pip 依赖。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_ci_governance.py` —
  新核对段；frontmatter 是代际事实源，checker 是其与 workflow pin 的一致性裁决者。
- **Seam classification:** deterministic-guardrail — 文本 frontmatter 与声明表的
  交叉比对，无模型、无运行时。
- **Question:** workflow 的 CLI 钉定代际能否被机器钉到真相源（skills frontmatter），
  使"两处声明一起陈旧"这类静默漂移 push 即红？
- **Necessary adjacent/external contracts:** `ci-governance` spec（answers: 漂移防护
  要求的规范归属）；`.agents/skills/*/SKILL.md`（answers: generatedBy 代际事实源——
  只读消费）。
- **Evidence seam:** governance unittest 套件（4 新用例红先）+ `check_ci_governance.py`
  退出码直测。
- **Not in scope:** 修改 skills 内容；自动 bump pin（对齐仍走 change）；其它工具链
  版本（python/node/uv）的交叉核对。
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| workflow CLI 钉定代际 ← 交叉核对 → skills frontmatter generatedBy | 无——两处文本事实的等值判断 | `check_ci_governance.py` 代际核对段 | non-bypassable | 代际失配/事实源缺失/歧义 push 即红，点名两侧值 | 复用既有 fixture 树与 check() 结构，不新增解析器依赖 | governance unittest 套件红先 + checker 退出码直测 |
