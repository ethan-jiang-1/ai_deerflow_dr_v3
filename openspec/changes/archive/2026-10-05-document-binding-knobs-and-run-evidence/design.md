# Design

## Context

binding 事实源：`adapters/contracts/client_surface.py` 的 CONSUMED_DEFAULTS
（thinking True / subagent True / plan_mode False / available_skills None）、
CONSTRUCTOR_PARAMS、CONSUMED_STREAM_KWARGS（thread_id, recursion_limit）、
CHECKPOINTER_SEAM；`adapters/client.py` 的 DEEP_RESEARCH_RECURSION_LIMIT=1000
（per-call 覆盖；AppConfig 顶层 300 不被嵌入式路径消费——疤痕注释在两处源码）、
resolve_config_path 显式解析 + env 钉、middlewares 注入 snapshot。mirror 测试
（test_wiring_mirror）已锁默认值与转发；smoke 锁真 saver 与 snapshot。两份目标
文档均已在 DOC_LAYER_DOCS / required-paths 注册——本 change 零注册表编辑。

## Goals / Non-Goals

**Goals:**

- 不读 adapters 源码即可回答"每个 knob 实际是什么、谁裁决、哪条测试锁定"。
- 不读源码即可按 recipe 关联一次 run 的五类证据。
- 文档 knob 值与代码常量的漂移被守卫咬住（红）。

**Non-Goals:**

- 不加任何机器关联代码（改行为，越出 Phase 4 的"只加可观察性与文档合同"）；
- 不动 skill 选择与质量语义（Phase 5 人的决策）。

## Decisions

1. **knob 表放在 research-process.md**（研究认知/binding 地图的既有 owner），
   "实际默认值"列用 greppable 的 `` `key=value` `` 反引号形式（守卫逐字断言）；
   owner 列区分"裁决处"（CONSUMED_DEFAULTS 镜像 vs client 装配代码）；证据列
   只登记真实存在的测试（mirror 断言名 / smoke），不发明覆盖率声明。
2. **traceability recipe 放在 run-bundle.md**（artifact 权属的既有 owner），
   标题定为 `## 一次 run 的证据关联`（守卫断言标题存在）：state.json 的
   thread_id → checkpoint；assembly-snapshot（首次装配）→ journal（工具/
   subagent/admission disposition 事件时间线）→ submissions 哈希链 → final；
   每步写明"能推出/不能推出"；inspect 是把五者一次看全的入口。
3. **守卫（tests/unit/runtime/test_binding_doc_guard.py）**：从
   `adapters.client` 导入 DEEP_RESEARCH_RECURSION_LIMIT、从
   `adapters.contracts.client_surface` 导入 CONSUMED_DEFAULTS，断言
   research-process.md 文本逐字包含每个 `f"{k}={v}"` 与
   `recursion_limit={limit}`；断言 run-bundle.md 含证据关联标题。红先行：
   守卫先写、表未建 → 红。文档是投影：守卫不复制表格结构，只锁值与标题
   （表怎么排版可以自由演进）。
4. **smoke 不欠但跑**：env 已热、2 秒，receipt 里记为 belt-and-braces。

## Risks / Trade-offs

- [代码改 knob 值 → 文档红灯逼同步] → 这正是设计意图；同步 = 改表 + 改值，
  守卫确保不会漏。
- [守卫字符串断言太脆（排版变即红）] → 只锁 `key=value` 子串与节标题，不锁
  表格结构。
- [recipe 陈述过头（暗示机器已有关联 ID）] → 措辞明确"关联键是同 bundle 目录
  + thread_id + journal 条目"，不声称存在跨文件外键。

## Migration Plan

守卫（红）→ 两节内容写入（绿）→ hygiene/verify → closeout + 回执 → 归档。
回滚 = revert。

## Open Questions

无。
