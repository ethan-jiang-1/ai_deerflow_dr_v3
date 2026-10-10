# Proposal: promote-lint-to-ci

## Why

`make lint` 已在本地全绿（establish-lint-lane），但 CI canonical 序列不跑它——lint 绿
只是本地纪律，push 后无人看守，回归只能靠下一次本地自觉。同时发现既有 spec 漂移：
ci-governance 主 spec 的 canonical 序列清单漏了 `make smoke`（ci-integration-lane 以
skip_specs 入 CI 时未走 delta），workflow 实跑五步、spec 只认四步。

## What Changes

- CI workflow（`.github/workflows/governance.yml`）在 `make smoke` 之后新增
  `make lint` 步骤（env 已由 smoke 的 `uv sync` 就绪）。
- `check_ci_governance.py` 的 `WORKFLOW_REQUIRED_MARKERS` 增加 `"make lint"`——workflow
  摘掉该步即 checker 红。
- `test_ci_governance.py`：`VALID_WORKFLOW` fixture 同步加步；负例覆盖
  "gut 掉 make lint 必须失败"。
- `ci-governance` spec 的 "CI runs the governance suite on the acceptance path"
  以 MODIFIED delta 修正：canonical 序列补齐 `make smoke` 并新增 `make lint`。
- `openspec/governance/README.md` 的 CI 段落同步序列描述。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `ci-governance`: MODIFIED——"CI runs the governance suite on the acceptance path"
  的 canonical 序列修正为六步（unittest suite / closeout gate / doc hygiene /
  make verify / make smoke / make lint），scenario 相应扩展。

## Impact

- 影响：workflow +1 步、checker +1 marker、测试 fixture +1 步 +1 负例、spec delta、
  governance README 一段。
- 风险：低——CI 时长 +几秒（ruff 全树 <5s）；失败模式与其它 canonical 步一致
  （非零即 job 红）。
- 边界：不修改 `deerflow/`；不改 pre-commit hook（lint 属 CI，hook 的
  FORBIDDEN_HOOK_MARKERS 语义不变）；不改 lint 规则集。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_ci_governance.py` —
  唯一行为承载是其 workflow 必需 marker 表加一项（及其测试 fixture）；workflow 步骤
  与 spec delta 是同一裁决的两侧。
- **Seam classification:** deterministic-guardrail — canonical 序列封闭清单的机器
  校验；无模型、无运行时行为。
- **Question:** 本地已绿的 lint 能否升入 acceptance path 的机器序列，使 lint 回归
  在 push 即变红，而非依赖下一次本地自觉？
- **Necessary adjacent/external contracts:** `ci-governance` spec（answers: canonical
  序列的规范归属——本 change 同时修正其漏记 smoke 的既有漂移）；
  `test_ci_governance.py` fixture（answers: 声明漂移的既有红绿凭据形状）；
  `openspec/governance/README.md`（answers: 成文标准的 CI 段描述同步）。
- **Evidence seam:** `python3 openspec/governance/check_ci_governance.py` 退出码直测
  （加 marker 后真树红 → 加步骤后绿）+ governance unittest 套件 + 全套门禁。
- **Not in scope:** OpenSpec CLI pin 版本对齐（独立 change 随后）；
  pre-commit hook 扩员；lint 规则集；多 job/矩阵化。
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| lint 从本地纪律升入 CI canonical 序列（第六步） | 无——纯命令序列事实 | `check_ci_governance.py` 必需 marker 表 + workflow 步骤 | non-bypassable | canonical 序列封闭清单不被无声缩减；摘步即 checker 红 | 复用既有 marker 机制与 gut 型负例，不新增检查器 | `check_ci_governance.py` 退出码直测 + governance unittest 套件 |
