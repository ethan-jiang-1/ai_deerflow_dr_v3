# Proposal: harden-cas-conflict-surface

## Why

BUG-007 的修好判据第 3 条**尚未落地**（当时明确留给 owner 拍板）：`clarification_step` 的两条路径
修成单次一致读之后，并发写者若在"读"与"写"之间落盘，`write_state` 会抛
`StateRevisionConflict`——**而生产代码里没有任何捕获者**（只有两个测试）。于是那是一条
**裸 traceback 的失败路径**。

本把把这条决定拍下并落地（用户已授权"推动落地完结"）。

## What Changes

- **决定：抛出（fail loud），不在终态路径上重试。** 依据：
  1. **仓内惯用法**就是"可读的响亮失败"——`assembly.py` 与 `interaction/cli.py` 一共 6 处
     `raise SystemExit("<消息 + Remedy>")`（例：pin 解析失败、`create/refine` 缺框架环境）；
  2. **并发写者意味着同一个 bundle 上有两个驱动**——那是异常场景，静默重试会把它埋掉；
  3. **CAS 已经保证什么都没写坏**：冲突时状态未被修改，失败是安全的，操作员重读即可；
  4. **重试会把风险引入终态路径**：重试意味着重跑"判定 + journal + 写"这一段，
     `auto_continuation` 等 journal 事件会被写两次（可观察行为变化），且分支判定（额度是否耗尽）
     可能已过期——那需要重构整段循环，收益不抵风险。
- **落地（可读失败）**：把 `interaction/cli.py` 的两处 `assembly.run_foreground(...)` 调用收敛成
  一个 `_run_foreground(verb, **kwargs)` 包装，**两个条件各有一个处理器**：`ImportError`（缺框架
  环境，既有行为逐字保留）与 `bundle_state.StateRevisionConflict`（新增：消息 + Remedy）。
- **测试**：
  ① 包装层——stub 掉 `assembly.run_foreground` 抛冲突 ⇒ 断言 `SystemExit`，消息含冲突原因与 Remedy；
  ② **语义**——强制一次"读与写之间被推进"的交错 ⇒ `clarification_step` **抛**
     `StateRevisionConflict`，而**不是**静默覆盖（把 BUG-007 的判据从"不覆盖"补到"冲突可见"）。

**记录在案的备选（本把不做）**：**有界重试**。它确有依据——`write_state` 的异常消息本身写着
"re-read the state and retry"。但正确的重试层次是**整个 run**（或至少整段"判定 + 写"），而不是终态
写入这一处；在那之前，把冲突变成可读失败是诚实且最小的收口。若将来要做，另开一把并先解决
journal 重复与判定过期两个问题。

**不变量**：正常路径**零行为变化**（`make verify` / `make smoke` 全绿，journal 事件名与顺序不变）·
`bundle_state.write_state` 的 CAS 实现与 `check_lease` 不动 · 治理侧不动。

## Capabilities

### New Capabilities

<!-- none: 收紧一个失败语义并把它变得可读，不改任何 requirement。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`deep_research_harness/src/deerflow_deep_research/runtime/interaction/cli.py`（抽
  `_run_foreground` 包装 + 新增冲突处理器）· 其测试。
- **不动**：`pump_parts/gates.py`（BUG-007 的修法已落）· `bundle_state.py` · `pump.py` ·
  `assembly.py` · 治理侧。
- **触发车道**：`make verify` · `make smoke` · lint · 治理套件与七 checker。

## Change Focus

- **Primary module / causal owner:** `runtime/interaction/cli.py` —— 它是 `run_research` 的**调用方
  边界**，也是本仓"领域异常 → 可读失败"的既有落点。
- **Seam classification:** wiring —— 只有一个失败通道的接线；无模型参与。
- **Question:** 一条"CAS 冲突"的失败路径，能否在不改 CAS、不改正常路径行为的前提下，从**裸 traceback**
  变成**带 Remedy 的可读失败**——而"冲突时抛出、不静默覆盖"这条语义被测试钉住？
- **Necessary adjacent/external contracts:** `bundle_state.StateRevisionConflict`（answers: 冲突类型
  与它的消息——注意消息本身建议调用方重试，本把说明为何在**这一层**不重试）·
  `interaction/cli.py` 既有的 `SystemExit(message + Remedy)` 风格（answers: 形态照它写）·
  `assembly.run_foreground`（answers: 两个调用点共用的入口，包装它即可一处收口）·
  `clarification_step`（answers: 冲突的产出点，语义测试直接打它）。
- **Evidence seam:** ① 包装层的 SystemExit 断言 ② 强制交错的语义断言（必须**抛**而不是覆盖）·
  `make verify` / `make smoke` 全绿（正常路径不变）· lint · 治理套件与七 checker。
- **Not in scope:** 有界重试（备选，见上）· 把 `StateCorruption` / `LeaseViolation` 一并接进同一个
  处理器（不同的失败类别，拓宽捕获是另一个决定）· `pump.py` 终态写入的同类暴露面（它有同一形态，
  但改它属另一把）· 治理侧。
- **Triggered review policies:** local-context, change-admission
