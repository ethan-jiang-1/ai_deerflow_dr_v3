# Proposal: Document Binding Knobs and Run Evidence

## Why

2026-10-05 计划 Phase 4 的剩余增量：操作者要说明 binding 必须读 `adapters/client.py`
源码（knob 的实际默认值、谁裁决、哪条测试锁定没有成表）；要追溯一次 run 的
snapshot ↔ journal ↔ admission 关联只能自行拼线索。Phase 1 已提前交付两种 loop
表、skill 三列状态、artifact 权属表；本 change 补齐最后两块并加防漂移守卫。

## What Changes

- **`docs/research-process.md` 新增 binding knob 表**：每个装配旋钮的
  实际默认值（greppable 的 `key=value` 形式）、裁决 owner（`adapters/client.py`
  或 `contracts/client_surface.py` 的 CONSUMED_DEFAULTS）、测试证据
  （mirror 断言 / smoke）。覆盖：config_path 显式解析与 env 钉、checkpointer
  工厂 seam、model_name、thinking_enabled、subagent_enabled、plan_mode、
  available_skills、middlewares 注入、thread_id、recursion_limit per-call 覆盖
  （含 AppConfig 顶层 300 不被消费的疤痕说明）。
- **`docs/run-bundle.md` 新增"一次 run 的证据关联"节**：从 state.json 的
  thread_id 起步，走 assembly-snapshot → journal 事件 → submissions 哈希链 →
  final 的关联 recipe；每步能推出什么、不能推出什么。
- **新增防漂移守卫** `tests/unit/runtime/test_binding_doc_guard.py`：断言
  research-process.md 逐字包含代码侧实际的 `CONSUMED_DEFAULTS` 四对
  key=value 与 `DEEP_RESEARCH_RECURSION_LIMIT` 值（从 adapters 导入常量比对），
  以及 run-bundle.md 携带证据关联节标题。代码改值而文档未跟 → 红。
- **不变**：任何代码/配置/行为零变化；skill 选择与产品质量语义不动
  （Phase 5 决策项）。

## Capabilities

### New Capabilities

<!-- none: 文档内容 + 文档一致性守卫，无 spec 行为变化 -->

### Modified Capabilities

<!-- none -->

## Impact

- 修改：`docs/research-process.md`、`docs/run-bundle.md`（两份已注册文档的
  内容增补，无注册表变化）。
- 新增：`tests/unit/runtime/test_binding_doc_guard.py`（verify lane 触发：
  tests/** 变更；smoke lane surface 未触碰，不欠账）。
- 不触碰：src/、config/、Makefile、注册表、`deerflow/` gitlink（本 change
  读 binding 代码事实但只引用公开常量）。

## Change Focus

- **Primary module / causal owner:** `docs/research-process.md` / `docs/run-bundle.md` 的 binding 与证据可观察性内容——事实源是 `adapters/client.py` 与 `contracts/client_surface.py` 的公开常量，守卫是 conformance 面。
- **Seam classification:** wiring — 文档合同补齐 + 文档-代码一致性守卫，不改认知、状态、准入或绑定行为。
- **Question:** 不读 adapters 源码能否说明每个 binding knob 的实际默认值与证据入口？不读源码能否按 recipe 走完一次 run 的 snapshot→journal→admission 关联？文档 knob 值与代码常量漂移时守卫能否变红？
- **Necessary adjacent/external contracts:** deerflow-wiring（answers: knob 值的事实源是 CONSUMED_DEFAULTS 与 DEEP_RESEARCH_RECURSION_LIMIT，守卫直接 import 比对）；delivery-lanes（answers: 仅 verify lane 触发；smoke surface 未触碰）；doc-truthfulness（answers: 文档是投影不是权威，守卫锁的是投影与事实源的一致）。
- **Evidence seam:** 守卫红先行（表未写时红）→ 表写入后绿；doc hygiene 链接全通；`make verify` 全绿（含新守卫）；`make smoke` 复测（不欠但跑，2s）。
- **Not in scope:** skill 强制加载、refine 自动重跑等 Phase 5 行为决策；snapshot/journal/admission 之间的新机器关联代码（会改行为）；tests/README 重写。
- **Triggered review policies:** local-context, agent-information-map, authority-and-projections, change-admission
