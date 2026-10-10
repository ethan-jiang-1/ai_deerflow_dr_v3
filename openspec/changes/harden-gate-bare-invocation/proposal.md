# Proposal: harden-gate-bare-invocation

## Why

`openspec/governance/check_project_gate.py` 裸跑（无参数）以 argparse 缺参 exit 2
收场，报错只说 "the following arguments are required: --phase"，不指向文档。2026-10-10
审计实测（fresh agent 执行链验证）：治理 README 正确记载了 `--phase {plan,closeout}`，
但只跑脚本不看 README 的 agent 会在这第一脚上撞墙——便宜可修的入口毛刺。

## What Changes

- `check_project_gate.py` 的 argparse 增加 epilog：写明两个 phase 的语义分界与
  `openspec/governance/README.md` 的权威位置
- 缺 `--phase` 时的错误路径打印同一指引（argparse error 信息 + epilog 双保险）
- `openspec/tests/governance/test_project_gate.py` 增加负例：裸跑 exit 2 且
  stderr/stdout 含治理 README 指引（红先绿后）
- 无 spec delta：gate 的判定语义（phase 分派、checker 集、退出码契约）零变化，
  只改使用面提示——与 establish-lint-lane 同类的 no-delta change

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

（无）

## Impact

- 影响：1 个脚本的 argparse 元数据 + 1 个治理 unittest 负例
- 风险：极低——不改任何判定路径；`--phase closeout`/`--phase plan` 的既有调用
  （CI canonical 序列、归档 ritual）字节不变
- 边界：**不**给 `--phase` 设默认值——静默默认 closeout 会让"想跑 plan 的人"意外
  执行全量 closeout 检查；显式 phase 是既有契约，指引而非放宽

## Change Focus

- **Primary module / causal owner:** `check_project_gate.py` 的 argparse 使用面——
  判定语义的 owner（phase 分派与 checker 集）不动
- **Seam classification:** deterministic-guardrail — 使用面提示；无模型、无运行时行为，判定路径零改动
- **Question:** 裸跑 gate 的第一脚失败能否自带去处，使 agent 不必先读 README 才知道
  该传什么？
- **Necessary adjacent/external contracts:** `openspec/governance/README.md` 的
  Checker 命令节（`--phase {plan,closeout}` 的成文权威）；治理 unittest 套件
  （负例落点）
- **Evidence seam:** 治理 unittest 红（裸跑缺指引断言失败）→ epilog 落地绿 →
  `check_project_gate.py --phase closeout` exit 0（既有语义回归）→ 裸跑 exit 2 +
  指引在场
- **Not in scope:** `--phase` 默认值；gate 判定语义；checker 集扩张（那是各 owning
  change 的事）
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 裸跑 gate 的失败输出携带 phase 语义与 README 指引 | 无——纯使用面事实 | argparse epilog/error 文本 + 治理 unittest 负例 | non-bypassable | 显式 `--phase` 契约不放宽（无默认值）；既有调用字节不变 | 复用 argparse 原生 error 路径，不加包装层 | unittest 红→绿 + 既有 `--phase closeout` 回归 0 |
