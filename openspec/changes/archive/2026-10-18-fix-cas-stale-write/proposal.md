# Proposal: fix-cas-stale-write

## Why

修 **BUG-007**（P1，状态已由 `等人拍板` → `修就绪`；用户已授权按 bug 轨推进到底）。

**缺陷**（`gates.py:80,90`）：`write_state(handle, bundle_state.read_state(handle), state)` 的 CAS
expected 值在**同一个调用表达式里现读**，而**新状态是由更早的 `state`（函数参数）推导的**。于是：

1. expected 与 `write_state` 内部的 `stored` 是同一次现读 ⇒ **CAS 恒真**（`stored.revision !=
   current.revision` 永不成立）；
2. 写入以**新** revision 递增 ⇒ 若有别的写者在这两次读之间落盘，**本次写入静默覆盖它**，而
   revision 看起来连续 ⇒ **last-writer-wins 伪装成受保护**；
3. `check_lease` 只比对目录身份（`st_dev`/`st_ino`），**不是单写者锁** ⇒ CAS 是唯一并发守卫。

**判据（本把的红先）**：在"读"与"写"之间插入一次外部写入，**结果必须保住别人的更新**（而不是覆盖它）。

## What Changes

- **`clarification_step` 的两条路径改为"单次一致读"**：在函数内读一次 `fresh`，
  **判定条件与状态推导都用这一版**，并把**同一个 `fresh` 作为 CAS 的 expected**：
  - 路径 1（自动续答）：`fresh = read_state()` → `if fresh.auto_proceed_count < fresh.auto_proceed_bound:`
    → `state = rule_clarification_step(fresh, detected=True)` → `write_state(handle, fresh, state)`；
  - 路径 2（额度耗尽）：`fresh = read_state()` → `exhausted = rule_clarification_step(fresh, …)`
    → `write_state(handle, fresh, exhausted)`。
  这与同仓 `pump.py:216-240` 的**已验证形态**一致（先读、由该读推导、以该读做 CAS）。
- **红先测试**：行为负例——在调用方的读之后、`clarification_step` 之前插入一次外部写入，断言
  **两份更新都在**（本步 +3、并发 +1 ⇒ 期望 4，而非 3）。**当前形态下该负例必须红**（会得到 3）。
- **形态钉住**：一条结构性断言——`pump_parts/` 里任何 `write_state(...)` 调用**不得**在其参数里嵌套
  `read_state(...)`（那正是本缺陷的签名）。

**语义选择（记录在案）**：**不**把 expected 改成"整轮开始时的 state"。那样窗口更大、能抓整轮内的
并发写，但会让 `StateRevisionConflict` 在终态路径上**抛出**——而生产代码里**无人捕获**它，
等于把静默覆盖换成终态崩溃。**那是更大的语义改动，属 owner 保留区**；本把取"同一次读"的最小修法：
正常单写者下**行为逐字不变**，并发下从"覆盖"变为"保住"（窗口内冲突仍会抛出，与 `pump.py` 现状一致）。

**不变量**：正常路径 journal 事件名与顺序逐字不变 · 状态机语义不变 · `make verify` 与治理套件全绿 ·
治理侧零改动 · harness 只改 `pump_parts/gates.py` 一处。

## Capabilities

### New Capabilities

<!-- none: 修一个既有实现缺陷，不改任何 requirement。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`deep_research_harness/src/deerflow_deep_research/runtime/pump_parts/gates.py`（两条路径的
  读取与推导顺序）· 其单元测试（红先的行为负例 + 形态断言）。
- **不动**：`bundle_state.py` 的 CAS 实现（它是对的，被喂了恒等的两个值）· `check_lease` ·
  `pump.py` 的既有正确形态 · 治理侧 · 其余产品代码。
- **触发车道**：`make verify` · `make smoke` · 治理套件与七个 checker（`harness` 路径变更会触发 CI）。

## Change Focus

- **Primary module / causal owner:** `runtime/pump_parts/gates.py` 的 `clarification_step` ——
  它拥有"澄清额度如何花、状态如何落盘"这一转移。
- **Seam classification:** deterministic-guardrail —— 纯状态转移与并发守卫；无模型参与。
- **Question:** 一次"读—改—写"能否改成**单次一致读**（判定、推导、CAS 的 expected 同源），
  使并发下的静默覆盖变成"保住别人的更新"——而正常单写者路径**行为逐字不变**？
- **Necessary adjacent/external contracts:** `bundle_state.write_state`（answers: CAS 语义 =
  expected revision 必须等于落盘 revision；它本身正确）· `check_lease`（answers: 目录身份校验，
  **不提供互斥**）· `pump.py:216-240`（answers: 同仓已验证的正确形态，本把照它改）·
  `rule_clarification_step`（answers: 纯函数式的状态推导，可对 `fresh` 求值）·
  `StateRevisionConflict` 的捕获面（answers: 生产代码无人捕获 ⇒ 不选会抛出的那条修法）。
- **Evidence seam:** 行为负例**红先**（当前形态得到 3，修后得到 4）· 正常路径回归（既有测试全绿）·
  形态断言（不得内联现读）· `make verify` / `make smoke` · 治理套件与七 checker。
- **Not in scope:** 改 expected 为"整轮开始的 state"（更大的语义改动，owner 保留）· 给
  `StateRevisionConflict` 加重试-或-处理策略（同上）· `bundle_state.py` 与 `check_lease` ·
  其余 CAS 调用点（`pump.py` 已是正确形态）· 治理侧。
- **Triggered review policies:** local-context, change-admission
