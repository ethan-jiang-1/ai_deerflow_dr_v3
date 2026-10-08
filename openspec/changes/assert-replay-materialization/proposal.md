# Proposal: Assert Replay Materialization

## Why

plan C6 第一批 · C 面（`_backlog/plans/2026-10-08-application-corpus-adoption.md`）：
录制真实流的回放链路"在跑但没被钉住"——`tests/unit/runtime/test_event_stream_replay.py`
断言了终态与 journal 形状，但对 `diagnostics/searches/` 的物化**零断言**。
`runtime/bundle/search_log.py` 的物化契约（每个配对成功的 web_search/web_fetch
结果成为一个可直读文件）是 A 面"来源可追溯性"的物理基础，也是
`research-process.md` "每次搜索已物化、可直读复核"承诺的机器事实——它必须被
测试钉住。本面是 plan 排序的第一步：零契约变更、纯测试扩充、全部用现存 fixtures。

## What Changes

- **`tests/unit/runtime/test_event_stream_replay.py` 新增物化断言测试**：
  回放 `real-small-stream.json`（1386 事件 = 22 values + 1363 messages-tuple +
  1 end）后断言——`diagnostics/searches/` 恰好物化 **11** 条记录
  （web_search×6 + web_fetch×5，实测探针 2026-10-08 确认）、每条记录含全部
  必需键（generation/seq/tool/arguments/content/call_id）、content 非空。
- **红先于绿**：实现前先以"计数断言对现状红"验证——现状无此断言（新测试直接
  绿是预期；其红证由负例变体承担，见下）。
- **负例（scar 延续既有模式）**：新增一个篡改负例——把 fixture 中一条搜索工具
  结果的 call_id 改为未配对值，断言该条**不**物化（总数 10），钉住"配对去重"
  规则的失败面（物化器对无配对结果的丢弃是**规则**，不是静默吞）。

## Capabilities

### New Capabilities

none: 纯测试扩充；被钉的行为（SearchLog 物化契约）已存在且已实现。

### Modified Capabilities

none: `skip_specs: true` 已声明；run-bundle/run-admission spec 的 requirement
不变——本 change 只把"已经承诺的行为"变成红绿事实。

## Impact

- 文件：仅 `deep_research_harness/tests/unit/runtime/test_event_stream_replay.py`
  （新增两个测试方法 + collections 导入）。
- 车道：`make verify`（unit/runtime 变更）；integration 与治理面零触碰。
- DECLARED_MACHINES / quality-register 不变（本面是测试，不是新机器）。
- `deerflow/` gitlink 不触碰；fixtures 只读。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/unit/runtime/
  test_event_stream_replay.py` —— 录制流回放契约的测试 owner（被钉行为的实现
  owner 是 `runtime/bundle/search_log.py`，本 change 不改它）。
- **Seam classification:** deterministic-guardrail — 纯确定性回放断言（固定
  fixture + 真实 pump/落盘 + 计数断言），无认知角色。
- **Question:** 真实录制流经真实泵回放后，每个配对成功的搜索结果是否恰好物化
  为一条非空、键完整的可读记录，且未配对结果被规则性丢弃？
- **Necessary adjacent/external contracts:** `SearchLog` 物化契约（answers: 文件
  命名、payload 键集、配对去重规则——断言的对象）；`research-process.md` 的
  "已物化可直读复核"承诺（answers: 测试把文档承诺变成机器事实，防文档撒谎）；
  plan C6-A 面前置（answers: searches/ 是来源可追溯性的物理基础，本面先钉住
  它的可靠性）。
- **Evidence seam:** `make verify` 红绿（新测试 + 篡改负例在离线套件内运行，
  fixture 驱动真实 pump 与临时落盘，退出码直测）。
- **Not in scope:** A/B 面 validator 维度与封闭码集；`SearchLog` 实现改动；
  end.usage 接线（D 面）；real-model-io 消费（E 面）。
- **Triggered review policies:** change-admission, local-context
