# Design

## Context

`SearchLog`（`runtime/bundle/search_log.py`）把配对成功的 web_search/web_fetch
结果物化为 `diagnostics/searches/gen{N}-{seq:03d}-{name}.json`，payload 键集
{generation, seq, tool, arguments, content, call_id, recorded_at}，按 call_id
跨 chunk/values 双源去重，未配对结果不物化。现有回放测试
（`test_event_stream_replay.py`，@impl DEW-001 的 scar）驱动真实
`pump.run_research` 断言终态与 journal，但对物化零覆盖。实测探针
（2026-10-08，临时目录 + 真实泵）：回放 fixture 物化 11 条（6+5），全非空。

## Goals / Non-Goals

**Goals:**

- 物化计数与形状成为红绿事实（11 = 6+5，键完整，content 非空）；
- "未配对不物化"的丢弃被钉为规则（篡改负例），不是静默行为。

**Non-Goals:**

- 不改 SearchLog/pump 任何实现；不加机器、不动 register、不动 spec；
- 不消费 real-model-io.jsonl（E 面）；不做报告内容断言（A/B 面）。

## Decisions

**D1 断言写进既有回放测试类，不新建文件。**
该类已拥有 fixture 装载、bundle 启动、`_stream_fn` 驱动与 scar 模式（@impl
DEW-001）——物化断言是同一契约的补全，分开文件会拆散"回放契约"的完整叙述。
备选落败：新建 test_search_log.py（单测 SearchLog 单元已在物化契约层面被覆盖，
本面的价值是端到端回放链路，归回放测试）。

**D2 负例 = 篡改 call_id 使结果未配对，断言 10 条。**
比"删一个事件"更精确：它钉的是配对规则本身（结果无配对调用即不物化），且
延续文件内既有的 tampered-scar 模式。计数断言 11→10 的差值即规则的作用面。

**D3 计数精确断言（== 11）而非下界断言（>= 1）。**
下界会让"物化悄悄漏记录"变绿（每次丢一条仍 >= 10）；精确计数把 fixture 变成
金样本——泵或物化器任何行为变化都显式红，迫使变更方自觉更新 fixture 预期。

## Alternatives

- **只断言 `>= 1` 条物化**：落败——见 D3，弱断言防不住静默漏记。
- **在 integration smoke（test_cli_journey）里断言物化**：落败——smoke 已有
  create（含搜索物化）旅程覆盖，但那依赖脚本模型；C 面的价值是用**真实录制流**
  钉真实 pump 行为，归 unit 回放测试（离线、进默认门禁）。
- **给 SearchLog 补单元测试**：落败——物化器的单元行为已由本契约的端到端断言
  覆盖；重复单元化只增加维护面，不增加证明力。

## Risks / Trade-offs

- [fixture 是金样本，泵行为合法演进会红] → 接受并声明：这正是钉住的本意；
  演进时变更方随 owning change 更新预期计数（scar 注释在测试内说明来源）。
- [11 这个数字与 fixture 耦合] → fixture 是逐字录制的真实流，稳定资产（git
  管理）；若换 fixture，计数断言随新 fixture 的探针值重写（探针方法记录在
  change 里）。

## Migration Plan

纯测试新增，无迁移。回滚 = 删除两个测试方法。

## Open Questions

none: 探针已实测预期值，断言形态已裁决。
