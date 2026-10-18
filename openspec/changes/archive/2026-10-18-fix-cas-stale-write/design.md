# Design

## Context

证据见 `proposal.md` — Why。**红先已证**（修复前）：

| 用例 | 修复前 | 修复后 |
|---|---|---|
| 行为：并发写必须存活 | **红** `AssertionError: 1 != 2 : the step overwrote a concurrent update instead of building on it` | 绿 |
| 形态：不得在实参里现读 | **红** `gate writes CAS against an inline read: ['gates.py:90', 'gates.py:80']` | 绿 |
| 既有全套 | 254 条 | **254 条全绿**（行为不变） |

## Goals / Non-Goals

**Goals:** 判定 / 推导 / CAS expected **同源**（单次一致读）· 红先 → 绿 · 正常路径行为不变 ·
两条车道（verify + smoke）与 lint 全绿 · 治理侧零改动。

**Non-Goals:** 改 `bundle_state.py` 的 CAS 实现 · 改 `check_lease` · 把 expected 改成"整轮开始的
state"（更大语义改动，owner 保留）· 给 `StateRevisionConflict` 定重试策略（同上）。

## Decisions

### D-1｜单次一致读：判定、推导、CAS expected 同源

- **选**：函数内 `fresh = read_state(handle)`；条件用 `fresh`、`rule_clarification_step(fresh, …)`
  推导、`write_state(handle, fresh, …)` 做 CAS。**照同仓 `pump.py:216-240` 的已验证形态。**
- **为什么**：缺陷的本质是**payload 与 CAS expected 来自不同的读**。让它们同源，就同时消掉了
  ① "检查恒真"与② "内容陈旧仍通过"这两半。只修一半（例如只把 expected 换成参数 `state`）会把
  静默覆盖换成**抛出**——而生产代码无人捕获 `StateRevisionConflict`。
- **代价**：多一次读（可忽略）。
- **换来**：并发下从"覆盖"变为"保住"；单写者下行为逐字不变。

### D-2｜条件也读 `fresh`，而不是只改写入

- **选**：`if fresh.auto_proceed_count < fresh.auto_proceed_bound:`。
- **为什么**：若条件仍读调用方的旧视图，而写入基于 `fresh`，则可能在"额度已被别人用尽"时**多花一次**
  （写出 `count > bound`）。**判据与它作用的对象必须是同一版**——这是本缺陷的同类错误，不能在修复里
  重犯。
- **代价**：条件与写入都基于 `fresh`，读起来多一步。
- **换来**：整条转移在**一版状态**上自洽。

### D-3｜不加"expected = 整轮 state"的重试/抛出策略

- **选**：明确**不**在本把引入重试或捕获。
- **为什么**：那会改变终态路径的失败语义（今天无人捕获 `StateRevisionConflict`），属 owner 保留区；
  BUG-007 的卡把这条列为需要拍板项，而用户授权的是"按 bug 轨推进"，不是"改状态机失败语义"。
- **代价**：并发窗口内的冲突仍会抛出（与 `pump.py` 现状一致）。
- **换来**：本把是**最小、行为保守**的修复。

### D-4｜形态断言与行为断言并存

- **选**：两条用例——行为（并发更新存活）+ 形态（`write_state` 实参里不得嵌套 `read_state`）。
- **为什么**：行为断言证明"现在对"，形态断言让**缺陷的签名**（内联现读）在将来重现时立刻红。
- **换来**：修的与防的是同一件事。

## Risks / Trade-offs

- [修完改变正常路径行为] → 既有 254 条全绿 + `make smoke` 30 条 OK。
- [我的形态判据空转] → **真的发生了**（见偏差 1），被"缺陷明明在却通过"这一异常揪出并修正。
- [import 顺序 lint] → 被 lint 车道抓住（偏差 3）。
- [把 owner 保留的决定偷偷做掉] → D-3 明确不做，并写进 Not in scope。

## Migration Plan

1. 红先：写两条用例，**先证红**（行为 + 形态各一）。
2. 改 `gates.py` 两条路径为单次一致读。
3. 绿：新用例 + 全套 254 + `make smoke` + lint + 治理套件与七 checker。
4. 收口：BUG-007 → `已修`（补 `> 修复:` 字段）+ 毕业进 `_fixed_bugs/`；计数器 +1；门禁；推送。

**回滚**：`git revert`（`gates.py` 两处 + 两条用例 + 卡片）。
