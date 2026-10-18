# Design

## Context

证据见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 冲突类型 | `bundle_state.StateRevisionConflict`；消息本身写着 "re-read the state and retry" |
| 生产代码捕获面 | **零**（只有两个测试：一个断言它抛、一个捕获） |
| 仓内"可读失败"惯用法 | `raise SystemExit("<消息 + Remedy>")`，共 6 处（`assembly.py` 3 · `interaction/cli.py` 3） |
| 两个调用点 | `cmd_create` / `cmd_refine` 各一处 `try: assembly.run_foreground(...) except ImportError` |
| 契约测试 | `contract/test_entry_chain.py` 用 **AST** 断言"动词必须调到 `run_foreground`"（防绕过） |

## Goals / Non-Goals

**Goals:** 拍下冲突策略并落地 · 冲突从裸 traceback 变成**带 Remedy 的可读失败** ·
"冲突时抛出而非吞掉"被测试钉住 · 正常路径零行为变化 · 契约测试的**意图**保留。

**Non-Goals:** 有界重试（备选，见 D-2）· 把 `StateCorruption`/`LeaseViolation` 一并接进来 ·
`pump.py` 终态写入的同类暴露面 · 治理侧。

## Decisions

### D-1｜抛出（fail loud），在调用方边界变成可读失败

- **选**：`interaction/cli.py` 抽 `_run_foreground(verb, *, remedy, **kwargs)`，两个动词共用；
  它有两个处理器——`ImportError`（既有消息**逐字保留**）与 `StateRevisionConflict`（新增：说明
  "另一个写者推进了这个 bundle" + Remedy："确保同一 bundle 只有一个 run，然后重读状态重试"）。
- **为什么**：① 仓内惯用法就是可读的响亮失败；② 并发写者意味着**同一 bundle 上有两个驱动**——异常
  场景，值得暴露；③ **CAS 已经保证什么都没写坏**（冲突时状态未修改），失败是安全的；④ 边界放在
  调用方而不是 `gates.py`：`SystemExit` 是 CLI 关注点，运行时层保持"抛类型化异常"的诚实。
- **代价**：冲突时 run 停止，操作员需重跑命令。
- **换来**：一条本来会以 traceback 结束的路径，变成一句能照做的提示。

### D-2｜**不**在终态路径上有界重试（记录在案的备选）

- **选**：本把不做重试。
- **为什么**：`write_state` 的异常消息确实建议"re-read and retry"，所以重试**有依据**；但正确的重试
  层次是**整段"判定 + journal + 写"**或整个 run，而不是终态写入那一处。在那一处重试会带来两个真问题：
  ① **journal 事件写两次**（`auto_continuation` 等可观察行为变化）；② **分支判定过期**（重读后额度
  可能已耗尽，而判定已在旧值上做过）。解决它们要重构整段循环，收益不抵风险。
- **代价**：罕见的冲突会让 run 失败一次。
- **换来**：改动小、行为保守、无隐藏的行为变化。**将来要做，另开一把**（先解决上面两个问题）。

### D-3｜契约测试跟一跳，而不是删掉断言

- **选**：`test_entry_chain.py` 的 `run_foreground` 断言改为"直接调用**或**经 `_run_foreground`"，
  `start`/`refine`/`resolve_bundle` 三条**仍是字面断言**。
- **为什么**：那条契约的**意图**是"动词不得绕过 bundle actions / 前景装配"。重构后链路仍在
  （`cmd_create → _run_foreground → assembly.run_foreground`），只是多了一跳；**删掉断言**会真的
  丢掉守卫，**照搬字面断言**则会与"失败通道收敛到一处"的设计冲突。
- **代价**：契约测试多了一个小辅助函数（`_reaches_foreground_assembly`）。
- **换来**：绕过仍然会红（既不调 `run_foreground` 也不调该助手的动词照样失败），意图逐字保留。

## Risks / Trade-offs

- [重构让动词绕过前景装配] → D-3：契约测试跟一跳但**不放松**，绕过仍红。
- [顺手拓宽捕获面] → 明确只捕获冲突；`StateCorruption`/`LeaseViolation` 是不同的失败类别（前者是
  损坏、后者是目录被换），接进来是另一个决定，写进 Not in scope。
- [既有 ImportError 消息被改写] → 用参数化 `verb` + `remedy` 逐字复现原消息，并有测试断言 refine
  那条**完整字符串相等**。
- [测试手搓异常与真实异常不同] → 偏差 1：手搓 `ImportError` **没有 `.name`**，消息成了
  "missing module: None"；真实导入错误才有 `.name`，测试补上。

## Migration Plan

1. `cli.py` 抽 `_run_foreground` + 两个调用点收敛。
2. 契约测试跟一跳（D-3）。
3. 三条新用例：冲突 → 带 Remedy 的 SystemExit；ImportError 消息逐字；强制交错 ⇒ **抛出**（语义）。
4. 车道：verify / smoke / lint / 治理套件 / 七 checker / closeout。
5. 收口：按账本新约定**追记** BUG-007 的卡（判据 3 已落地）。

**回滚**：撤销 diff（两个调用点恢复各自的 try/except、契约测试回字面断言、新用例删除）。
