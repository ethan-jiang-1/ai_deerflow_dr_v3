# Proposal: Materialize Search Evidence

## Why

Phase 5 第 4 轮裁决：每次搜索/抓取的完整结果只存在于 `checkpoint.sqlite` 里（要用
框架 checkpointer 才能读），报告的引用（"根据 URL X 得出 Y"）物理上不可复核——
引用真实性是深度研究产品的核心质量维度，而它当前连人工复核都做不到。物化是把
checkpoint 里已有的数据投影成可直读文件（可观察性投影，不是新数据），是"引用
可复核"的地基。

## What Changes

- **新增 `runtime/bundle/search_log.py`**（持久化簇）：`SearchLog` 记录器——
  `note_call(call_id, name, arguments)` 建立 id→(工具名, 参数) 映射；
  `note_result(call_id, content)` 对 `SEARCH_TOOL_NAMES`（`web_search` /
  `web_fetch`，两梯同名）的工具按 call_id 去重后落盘
  `diagnostics/searches/gen{N}-{seq:03d}-{name}.json`
  （generation/seq/tool/arguments/content/recorded_at）。
- **run_engine 接线**：`run_research` 构造 SearchLog 并传入 `_consume_turn`；
  AI 消息（chunk 与 values 快照两源）喂 note_call，tool 结果消息（两源）喂
  note_result——chunk 优先、values 兜底，call_id 去重防双写。
- **`evidence/` 准入合同一字不动**：搜索记录落在 `diagnostics/searches/`
  （"process diagnostics to diagnostics/" 既有路由），未过 validator 的原始
  工具输出不冒充已接纳证据。
- **spec delta**：run-bundle **ADDED** requirement "Search and fetch results are
  materialized readably"（目录合同不需要 MODIFIED——`diagnostics/` 是已声明
  子树，`searches/` 是其子目录）。
- **文档同轮**：run-bundle.md artifact 表加行、research-process 质量评估列与
  判断质量段、control-map 未实现清单的 evidence 行更新（"搜索结果已物化到
  diagnostics/searches/ 可直读，仍不自动进 evidence/"）。
- **不变**：admission/validator/ledger、journal 合同、事件消费语义、config、
  checkpoint。

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `run-bundle`: one ADDED requirement — every web_search/web_fetch result is
  materialized as a readable JSON file under `diagnostics/searches/` (generation,
  sequence, tool, arguments, full content, timestamp), deduplicated by tool-call
  id; the directory contract is unchanged (a subdirectory of the declared
  `diagnostics/` subtree); `evidence/` remains admission-only.

## Impact

- 新增：`runtime/bundle/search_log.py`、`tests/unit/runtime/test_search_log.py`。
- 修改：`runtime/run_engine.py`（接线）、test_run_engine（脚本化搜索回合）、
  旅程测试（create 注入搜索回合脚本 + searches 文件断言）、三份文档。
- 触发双 lane：verify（src/tests）+ smoke（cli.py/interaction/旅程）。
- 不触碰：engine/、admission、domain 路径合同（BUNDLE_SUBTREES 不变——
  searches/ 是 diagnostics 子目录）、config、`deerflow/`。

## Change Focus

- **Primary module / causal owner:** `runtime/bundle/search_log.py` 的搜索记录语义——持久化簇的新事实 owner；run_engine 的接线与旅程断言是 conformance 面。
- **Seam classification:** wiring — 事件流中已有数据的确定性投影落盘；无认知面、无准入变化、无新事件消费语义。
- **Question:** 每次搜索/抓取能否在 run 结束后变成 cat 即可复核的文件（含 query 与完整结果），且 evidence/ 准入合同、journal 合同、目录顶层合同零变化？
- **Necessary adjacent/external contracts:** run-bundle（answers: 目录合同不需要 MODIFIED——searches/ 是 diagnostics/ 子目录；ADDED requirement 捕获物化行为；journal 合同不受影响——search log 是独立文件不是 journal 条目）；deerflow-wiring（answers: 事件消费语义不变，SearchLog 是旁路 sink 不改 _consume_turn 的返回形状）；entry-surface（answers: 六动词不变）。
- **Evidence seam:** 红先行（SearchLog 模块缺失 + run_engine 脚本化搜索回合断言文件存在 + 旅程 searches 断言）；verify + smoke 全绿；物化文件内容断言（query + 罐头结果全文）。
- **Not in scope:** evidence/ 自动接纳（裁决明示不进 evidence）；自动引用比对/质量统计（更远议题）；web_fetch 之外的扩展工具集；搜索结果的保留/清理策略（单 bundle 生命周期与 scopes/ 一致）。
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

认知不因果：物化是确定性数据搬运（事件流 → 文件），模型不参与。

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| 搜索结果从 checkpoint-only → 可直读文件 | Human judgment（第 4 轮裁决 B；拒绝轻量索引半吊子） | SearchLog 按 call_id 去重落盘；文件含 arguments 与完整 content | non-bypassable | evidence/ 准入合同不动（原始工具输出不冒充已接纳证据）；journal 合同不动 | 引用复核从"框架 checkpointer 才能读"变"cat 即可" | 红先行：模块缺失红 + 回落绿 |
| 物化位置（evidence/ 冒险 vs diagnostics/searches/） | Human judgment（evidence 语义归 run-admission 合同，不得污染） | diagnostics/ 是已声明子树，"process diagnostics" 路由既有 | non-bypassable | 顶层目录合同零变化；spec ADDED 而非 MODIFIED | 不新增顶层子树；不混入准入产物 | 目录合同既有测试仍绿 |
| 去重与配对（chunk/values 双源） | 无认知候选 | call_id 映射 + 已写集合；chunk 优先 values 兜底 | bounded-repair | 双源重复不双写（call_id 去重）；缺配对的孤儿结果跳过 | 不改事件消费语义，旁路 sink | run_engine 脚本化双源测试 |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| 工具结果无配对调用（孤儿 call_id） | SearchLog 跳过（不写） | 不恢复——无法命名工具与参数的记录是谎言 | 无文件（诚实缺席） | inspect/journal 看工具名 | 孤儿负例测试 |
| 同一 call_id 双源重复 | call_id 去重集合 | 首写生效，后续跳过 | 单文件 | — | 双源测试 |
| searches/ 写失败（磁盘等） | 原子写异常向上传播 | run_engine 既有 framework_error 兜底（failed-resume） | failed-resume（既有语义） | 修复后 refine | 既有兜底路径 |
| 大结果撑磁盘 | 未设上限（裁决未要求） | 记录为已知边界；保留策略 not-in-scope | — | 未来 owning change | tests/README 已知边界行 |
