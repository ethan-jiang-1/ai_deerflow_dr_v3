# Design

## Context

事件流事实：AI 消息的 tool_calls（name/args/id）出现在 chunk 与 values 快照两源；
tool 结果消息（tool_call_id + content）同样两源出现；`_consume_turn` 已在两源
收集 calls/answered（澄清判定用）。工具名两梯统一（`web_search`/`web_fetch`）；
fixture 的 FakeWebSearchTool 返回含 query 的罐头文本。目录合同的 "exactly" 只约束
顶层子树，`diagnostics/` 是已声明子树（"process diagnostics to diagnostics/"）。
tests/integration/test_wiring_smoke 已有脚本化工具调用的先例格式
（`{"content": "", "tool_calls": [{"id", "name", "args"}]}` → 框架执行 → 下一
脚本项终答）。

## Goals / Non-Goals

**Goals:**

- run 结束后 `cat diagnostics/searches/*.json` 即可复核每次搜索的 query 与完整
  结果；双源去重；非搜索工具不落盘；孤儿结果不落盘。
- evidence/ 准入合同、journal 合同、顶层目录合同、事件消费语义零变化。

**Non-Goals:**

- 不进 evidence/（裁决明示）；不做引用比对/统计；不做保留策略；不扩工具集。

## Decisions

1. **SearchLog 放 runtime/bundle/（持久化簇）**：与 journal/ledger 同簇的
   diagnostics 事实 owner；独立文件不是 journal 条目（journal 合同不动）。
2. **配对与去重**：`note_call` 建 id→(name, args) 映射（两源 AI 消息都喂）；
   `note_result` 查映射——名字在 SEARCH_TOOL_NAMES 且未写过才落盘
   （`_written` 集合）。chunk 与 values 双源天然经同一去重。
3. **文件名 `gen{N}-{seq:03d}-{name}.json`**：generation 前缀防跨代碰撞（refine
   重跑是新 recorder 实例，seq 从 1 重计）；不把 call_id 放文件名（保持可读
   排序）；call_id 在 JSON payload 内保留可追溯。
4. **接线是旁路 sink**：`_consume_turn` 增可选 `search_log=None` 参数，两源
   的 AI/tool 消息处理处各加一行喂给（None 安全）；返回形状与既有语义不动。
   `run_research` 在读 state 后构造 recorder（generation 已知）。
5. **旅程扩展**：create 注入
   `[{"content": "", "tool_calls": [{"id": "call-s1", "name": "web_search",
   "args": {"query": "无人机 认证壁垒"}}]}, {"content": "Fixture answer with
   cited sources."}]`——框架真执行 FakeWebSearchTool，罐头结果经真 agent loop
   流回；断言 `diagnostics/searches/gen1-001-web_search.json` 存在、arguments
   含 query、content 含罐头文本。gen2 的 refine 脚本保持纯终答（无搜索），
   证明无搜索的 run 合法缺目录（spec 场景的 MAY legally lack）。
6. **测试布局**：`tests/unit/runtime/test_search_log.py`（模块单测：记录/去重/
   非搜索名/孤儿/文件内容）+ test_run_engine 扩展（脚本化搜索回合经
   run_research 全链 → 文件存在——红：模块缺失）；旅程红（无 searches 文件）。

## Risks / Trade-offs

- [values 快照含全 thread 历史导致重写旧代文件] → recorder 是 per-run 实例且
  文件名带 generation；call_id 去重兜底；refine 重跑不重写 gen1 文件（seq 带
  gen 前缀 + call_id 集合是新实例但 gen 前缀隔离）——若 values 确实回放旧代
  工具消息，会以 gen2 前缀重写一份 gen1 已有内容：可接受（generation 标注
  诚实）且罕见；单测锁 gen 隔离行为。
- [大结果无上限] → 已知边界，not-in-scope 显式记录。
- [框架事件形状差异（真实梯）] → 两源都喂 + 孤儿跳过（缺配对不写）；真实梯
  行为 UNVERIFIED 记入回执。
- [旅程脚本改 create 破坏既有断言] → 终答文本保持与 gen2 不同且非空；
  report-gen1 断言（非空 + admit）不变。

## Migration Plan

红先行（模块单测 + run_engine 回合 + 旅程）→ SearchLog + 接线 → verify+smoke
全绿 → spec/docs → closeout → 归档。回滚 = revert（旧 bundle 合法缺目录）。

## Open Questions

无。
