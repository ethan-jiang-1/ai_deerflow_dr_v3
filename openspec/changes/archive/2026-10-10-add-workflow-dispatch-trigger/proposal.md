# Proposal: add-workflow-dispatch-trigger

## Why

本次远端 CI 暴露一个运维死角：push 后发现某提交带病（doc hygiene 红），修复提交只动了
根 README——不在 paths 过滤内、不触发 CI，于是 HEAD 已修好、远端最后一个 run 却永远
停留在红，且没有任何合法手段对 HEAD 重跑门禁（gh rerun 锁定原 SHA、空提交不匹配
paths、manufacture 触发=游戏门禁）。需要一个对操作者合法的重跑入口。

## What Changes

- `.github/workflows/governance.yml` 的 `on:` 增加 `workflow_dispatch:`（手动触发，
  对当前 HEAD 跑完整 canonical 序列；由有写权限的操作者显式发起）。
- `check_ci_governance.py` 的 `WORKFLOW_REQUIRED_MARKERS` 增加 `"workflow_dispatch:"`
  ——触发器被摘即 checker 红。
- `test_ci_governance.py`：fixture 同步 + 新负例（移除 dispatch 必须失败）。
- `ci-governance` spec 的 "CI runs the governance suite on the acceptance path"
  MODIFIED：触发面在 push/PR 之外增加手动 dispatch；"Path-filtered triggers" 场景
  语义不变（编辑无关文件仍不能强触/绕过——dispatch 是写权限者的显式动作，不是
  无关面绕道）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `ci-governance`: MODIFIED——"CI runs the governance suite on the acceptance path"
  的触发句扩展（+manual `workflow_dispatch`），并新增一个 dispatch 场景。

## Impact

- 影响：workflow +2 行、checker +1 marker、测试 fixture +2 行 +1 负例、spec delta。
- 风险：低——dispatch 不改 push/PR 行为；无 concurrency 冲突（同 group 取消旧 run）。
- 边界：不改步骤序列、不改 paths 过滤、不改 hook。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_ci_governance.py` —
  触发器封闭清单加一项；workflow 是其镜像面。
- **Seam classification:** deterministic-guardrail — 声明表机器校验，无模型、无运行时。
- **Question:** 操作者能否在不制造无关提交的前提下对 HEAD 合法重跑完整门禁，且该
  触发器本身被机器钉死不可无声摘除？
- **Necessary adjacent/external contracts:** `ci-governance` spec（answers: 触发面的
  规范归属与 push/PR 语义不变性）；`test_ci_governance.py` fixture（answers: 负例形状）。
- **Evidence seam:** `check_ci_governance.py` 退出码直测（红先：加 marker 后真树红 →
  加触发器转绿）+ governance unittest 套件。
- **Not in scope:** paths 过滤变更；scheduled 触发；多 job；其它 CI 平台。
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 触发面加手动 dispatch（写权限者显式重跑） | 写权限者的显式动作（人拍板何时跑） | `check_ci_governance.py` marker 表 + workflow `on:` 块 | non-bypassable | 触发器清单不被无声缩减；paths 过滤语义不变（无关文件仍不能强触） | 复用既有 marker 机制与 gut 型负例 | `check_ci_governance.py` 退出码直测 + governance unittest 套件 |
