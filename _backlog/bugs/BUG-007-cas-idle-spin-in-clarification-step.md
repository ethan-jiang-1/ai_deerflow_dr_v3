# BUG-007: gates.py 两处状态写入把 CAS 的 expected 值内联现读——CAS 恒真，静默丢失更新

> 严重级别: P1 | 发现: 2026-10-18（原始审计 2026-10-13，见「来源」） | 状态: 等人拍板

## 症状

`clarification_step` 的两处状态写入**看起来有并发保护（revision CAS）、实际没有**：
- `write_state` 的 `current` 参数在**同一个调用表达式里现读**（`bundle_state.read_state(handle)`），
  而 `write_state` 内部**再读一次** `stored` 来比对 revision；
- 两次读几乎必然同值 ⇒ **`stored.revision != current.revision` 永不成立 ⇒ CAS 恒真**；
- 而 `next_state` 是由**更早**读到的 `state` 推导的（函数参数）⇒ 若有别的写者在这两次读之间落盘，
  **本次写入静默覆盖它**，并以**新** revision（`current.revision + 1`）递增。
  **revision 看起来连续，内容却丢了别人的更新**——这是 last-writer-wins，且伪装成受保护。

## 根因

| 位置 | 代码 | 问题 |
|---|---|---|
| `gates.py:80` | `state = bundle_state.write_state(handle, bundle_state.read_state(handle), state)` | expected 内联现读；`state` 由 `rule_clarification_step(state, …)` 从**参数**推导 |
| `gates.py:90` | `written = bundle_state.write_state(handle, bundle_state.read_state(handle), exhausted)` | 同上；`exhausted` 也由**参数** `state` 推导 |
| `bundle_state.py:104-120` | `stored = read_state(handle); if stored.revision != current.revision: raise StateRevisionConflict` | CAS 本身正确；**是被喂了恒等的两个值** |
| `bundle_state.py:53-61` | `check_lease` 比对 `(st_dev, st_ino)` | **不是单写者锁**——它只防"目录被替换或搬走"，**不提供互斥** ⇒ CAS 是唯一的并发守卫，而它恒真 |

**同一个仓里存在正确形态作对照**：`pump.py:216-240` 先 `fresh = read_state(handle)`，再由
`rule_run_terminal(fresh, …)` 推导新状态，最后 `write_state(handle, fresh, state)` ⇒ expected 正是
新状态所依据的那一版，是**自洽的 read-modify-write**。缺陷只在这两处。

**另一面**：`StateRevisionConflict` 在**生产代码里没有任何捕获者**（只有两个测试：
`test_bundle_runtime.py:87` 断言它抛出、`test_state_read_diagnosis.py:97` 捕获）⇒ 一旦 CAS 真的失败
（修好之后就会），这条路径当前会**直接抛出**而不是重试。

## 复现

1. 读到 `state`（调用方循环变量），其 `auto_proceed_count < auto_proceed_bound`；
2. 在 `clarification_step` 内部写入之前，让**另一个写者**推进一次状态（改 revision）；
3. 走进去：`write_state(handle, read_state(handle), state)` —— expected 与 stored **同为最新**
   ⇒ CAS 通过，**别人的那次推进被覆盖**，且 revision 继续 +1（看不出断层）。
   —— 若改为 expected = **推导新状态所依据的那一版**（测试里可用 `state`），同一交错会**抛出**
   `StateRevisionConflict`，即"保护真的存在"。

**检索提示**：记录里的片段把 `bundle_state.read_state` 简写成 `read_state`，**逐字 grep 会漏**
（本会话我漏过一次并据此误判"形态不存在"）。按 `gates.py` 里两处 `write_state(` 找。

## 修好判据

1. 两处的 expected 值是**新状态实际所依据的那一版**——不许在调用表达式里现读；推荐直接采用
   `pump.py` 的已验证形态（`fresh = read_state()` → 由 `fresh` 推导 → `write_state(handle, fresh, …)`）。
2. **红先**：一条负例证明 CAS **能失败**——在"读"与"写"之间插入一次外部写入，写入必须
   **抛 `StateRevisionConflict`（或按 3 的重试策略重试）**，而**不是**静默覆盖。当前形态下这条负例
   必须**红**（先证缺陷）。
3. **定策略**：这两条路径遇到 `StateRevisionConflict` 该**重试**还是**抛出**？若抛出，**调用方必须
   处理**（今天生产代码无人捕获）——这是一条需要拍板的语义决定。
4. 除上述外**可观察行为不变**：journal 事件名集合与顺序逐字不变、终端转移结果不变。
5. `make verify` 与治理套件全绿；`gates.py` 的两处写入形态有测试钉住。

## 来源与授权（为何走 bug 轨而非顺手修）

- 原始审计事实（「事实 12」）出自 2026-10-13 的代码健康度审计；**其详细分析从未落盘**——全库
  只有**决定行**：CLS-025 卡的裁决 **A4**：
  > 顺手修 CAS 空转（事实 12）｜它是**行为正确性**问题（"看起来有保护、实际没有"），走 bug 轨：
  > 症状→根因证据→`修好判据`→授权。夹在重构里改等于悄悄改状态机语义。
- 其后四把 change 都把它列入 Not in scope（`cover-closeout-decisions` · `consolidate-journal-writes`
  ×3 处），措辞一致：「走 bug 轨需授权」。
- **本卡做的正是那条链**：症状（上）· 根因证据（上，本会话在**当前代码**上重新坐实）·
  修好判据（上，含红先）· **授权：待拍板**。
- 本卡**不改任何代码**：状态为 `等人拍板`，等 owner 在「修 / 记录为有意设计 / 仅加重试」之间拍板。
  修好判据 3 是真正需要人决的那一条（重试 vs 抛出会改变状态机语义）。

## 修复关联

（待定——拍板后由对应 change 落地，届时补 `> 修复: <change>` 字段并翻转状态。）
