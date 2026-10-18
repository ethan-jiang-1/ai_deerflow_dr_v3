# Tasks

## 1. Red first

- [x] 1.1 Behavioral case: a concurrent update must survive the step (the payload must build on it, not clobber it)
- [x] 1.2 Shape case: no `write_state(...)` call in `pump_parts/` may nest a `read_state(...)` in its arguments
- [x] 1.3 Prove both are red against the unfixed code, naming the defect precisely

## 2. Fix

- [x] 2.1 Read once inside the function; drive the condition, the derived state, and the CAS expectation from that one read
- [x] 2.2 Apply the same single-read shape to the exhausted path
- [x] 2.3 Leave the CAS implementation, the lease check, and the retry/raise policy untouched (the last is the owner's call)

## 3. Green and lanes

- [x] 3.1 Both new cases pass
- [x] 3.2 The full harness suite passes (behavior preserved on existing paths)
- [x] 3.3 `make smoke` passes; the lint lane passes; the governance suite and all seven checkers pass

## 4. Closeout

- [x] 4.1 Record the deviations, including the vacuous shape assertion that had to be fixed before it could go red
- [x] 4.2 Flip BUG-007 to fixed, add its fix reference, graduate it, and sync the counters
- [x] 4.3 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（**我自己的形态判据一度空转通过——本会话反复警告的那个失效模式，出现在我自己的守卫里**）：形态用例第一次跑**通过**了，而缺陷明明在 `gates.py:80,90`。查因：我写成 `isinstance(inner, ast.Attribute)`——`inner` 是 **`Call`** 而不是 `Attribute`，于是永远走 `getattr(inner.func, "id", "")` 得到空串 ⇒ `offenders` **恒为空** ⇒ 断言空洞通过。发现路径是"**缺陷明明在，为什么它会绿？**"这一异常，而不是它自己报错。修正为 `isinstance(inner.func, ast.Attribute)`（并改成早退 continue 的写法）后，它立刻红并指名 `['gates.py:90', 'gates.py:80']`。**教训：判据写错时它会静默变成"永远通过"，比没有测试更坏——所以"它绿了"必须能被追问。**
- 偏差 2（断言挡住了错误的插入点）：我第一次追加测试时按 `if __name__ == "__main__":` 定位，而该文件**没有**这个 guard ⇒ 我的断言失败、**什么都没写**（正是断言该起的作用）。改为直接追加到文件末尾。
- 偏差 3（lint 抓到 import 顺序）：我把两个 first-party 导入加在了**相对导入之后** ⇒ `I001 Import block is un-sorted`。挪到 first-party 区块后 `All checks passed!`。
- 偏差 4（记录一条**未做**的决定）：本把**没有**引入 `StateRevisionConflict` 的捕获/重试。原因见 design D-3：那会改变终态路径的失败语义，属 owner 保留区；BUG-007 的卡已把它列为需要拍板项。

## Delivery Record

- **外部行为**: **单写者路径行为逐字不变**（既有 254 条全绿 + `make smoke` 30 条 OK；journal 事件名与顺序未动）。**并发路径改变**：别的写者在本步之前落盘时，本步现在**基于它**推进（计数 1+1=2），而不是覆盖它（旧行为得到 1）。修的是"看起来有保护、实际没有"：`write_state` 的 CAS expected 现在与**判定和推导所依据的那一版**是同一次读——`pump.py` 一直是这个形态，本把把 `gates.py` 也对齐。
- **影响面**: `deep_research_harness/src/deerflow_deep_research/runtime/pump_parts/gates.py`（`clarification_step`：两条路径改为单次一致读，+6 行注释说明缺陷）· `deep_research_harness/tests/unit/runtime/test_pump_clarification.py`（新增 `GateWriteConsistencyTest` 两条用例 + 两个导入）· `_backlog` 账本（BUG-007 → 已修并毕业）。**未动**：`bundle_state.py`（CAS 实现本身是对的）· `check_lease` · `pump.py` · 治理侧（七 checker 与套件全绿）。
- **实际跑了什么**: **红先**（行为 `1 != 2`；形态 `['gates.py:90', 'gates.py:80']`）→ 改 → **绿**（两条用例 OK）· `make verify` exit 0（**254** 条，修复前 252 + 新 2）· `make smoke` exit 0（30 条）· **lint 车道** `ruff check src tests tools cli.py` → `All checks passed!` · 治理套件 exit 0（258）· 七 checker + closeout gate 全 0 · 形态判据在修正后**能红**（偏差 1 的实证）。
- **未执行的检查**: **未做真梯/真模型验证**（本缺陷是纯状态写入的并发语义，与模型无关；`make smoke` 覆盖脚本模型车道）· **未测真正的多进程并发**（用例是"先落一次外部写、再走这一步"的确定性交错，不是真并发压测——判据要的是"不静默覆盖"，这一点已证）· 未引入重试/捕获策略（偏差 4，owner 保留）· `expected = 整轮 state` 的更强形态未实现（design D-3）。
