# Plan: 接线与结构定案（wiring-structure）

> 类型: 设计 | 更新: 2026-10-02 | 来源: digest 边界 plan 六裁决推敲（裁决 #1/#3/#5 + 用户契约镜像要求）

## 背景 / 现状

六项裁决已定（见 digest plan 修订节）：接线路 = **embedded DeerFlowClient**；外层编排 = **普通状态机**
（非 LangGraph 图）；middleware = **只配置不编写**。用户硬要求：我们借力的每个 DeerFlow 表面
要在**自己源码树里有一份肉眼可见的拷贝**（契约镜像）。元原则：能借 DeerFlow 多少就借多少；
v2 拿得过来就拿，拿不过来就算了。证据底座：`_reference/deerflow-runtime-and-persistence.md`
（接线路事实）、`deerflow-cognition-engine.md`（旋钮表）、`deerflow-harness-architecture.md`
（结构标本）。

## 决策 / 方案

1. **embedded 接线**（runtime 层）：`DeerFlowClient` 封装——构造参数（model_name /
   subagent_enabled=True / available_skills / checkpointer=Bundle 的 **sync SqliteSaver**）；
   stream 事件流消费入口（三消费者分发给 bundle-contract 与 entry-surface plan）。
   （2026-10-02 修正：原写 AsyncSqliteSaver——client.stream() 是同步驱动（内部
   `agent.stream()`，docstring 明言不做 asyncio 桥接），LangGraph async-only saver 只实现
   异步接口；框架自己的同步工厂即配 SqliteSaver（`runtime/checkpointer/provider.py:120`）。
   v2 能用 async saver 是因为 v2 自己 `await graph.ainvoke` 异步驱动。冒烟钉死见落地关联。）
2. **契约镜像层** `runtime/contracts/`：我们消费的每个 DeerFlow 接口形状用自己的 typed
   定义复述一份——client.py（构造签名 + 事件类型 values/messages-tuple/custom/end）、
   subagents.py（CustomSubagentConfig 字段 + 治理旋钮）、checkpoint.py（checkpointer 接口）。
   **锁漂移**：contract test 比对镜像 vs 真身（v2 `test_deerflow_public_api.py` 模式 +
   CURRENT_DEERFLOW_PIN 锚——Q4 已确认守则）；镜像的是接口形状，不是实现（实现永远只有
   框架一份，不整文件拷贝）。
3. **结构定案**：外层编排 = 普通 Python 状态机（生命周期动作见 bundle-contract plan）；
   `graph/` 层与 NODE_SPEC 语法去留 → **撤**（第 7 轮查证：目录空、语法从未用），随之
   治理合同小改（project-structure.toml `[node_packages]` 段 + guide 再渲染，量级同
   add-doc-budget-gate）。
4. **middleware 只配置**：用框架现成实现（错误处理/输入消毒/compaction/循环熔断/token
   预算/委派限额——旋钮表引 `_reference/deerflow-cognition-engine.md` §6）；逃生口：
   真需要框架没有的行为时写标准 AgentMiddleware 插头，不碰框架。
5. **(b) 层旋钮声明**（agents 层）：研究 subagent 类型定义 + 预算参数；**一层深度自校验**
   （框架 schema 不强制 disallowed_tools 含 task——harness 必须断言，C 线警告）。
6. **凭证单路线**：embedded `.env`（模型 selector + key + TAVILY_API_KEY），不做 profile 体系。
7. **UNVERIFIED 验证项**（入线前必须落实）：① ask_clarification 在我们 run 里的处置
   （禁用可配置性 or 超时默认继续——HITL 暂缓裁决的尾巴）；② ~~Langfuse/tracing 在
   embedded 模式下是否可用~~ **已关闭（2026-10-02，digest+源码双证）**：可用——
   `client.stream()` 在图调用根注入 `build_tracing_callbacks()` + `inject_langfuse_metadata()`
   （client.py:933-942），`chat()` 包装 `stream()` 同覆盖；开启 = 环境变量
   `LANGFUSE_TRACING` + `LANGFUSE_PUBLIC_KEY/SECRET_KEY`，构造参数 `environment` 打
   env 标签，session_id=thread_id，`deerflow_trace_id` 恒写入；例外：Monocle 仅 Gateway
   lifespan 初始化，embedded 不覆盖。第一版不依赖，保持记录备查。

## 风险 / 取舍

- [deerflow.* 无 API 稳定性契约] → 契约镜像 + contract test + submodule 锁三重缓解；升级时
  测试红 = 有意识更新镜像。
- [撤 graph 层与治理预声明冲突] → 预留合同从未被用，撤除无既成现实可破坏；改动随本 plan 的
  change 一起走。

## 落地关联

成熟后**经用户拍板**入线（HITL 闸门）。change 候选：撤节点语法（治理小改）与 embedded 接线 +
契约镜像（产品首笔）可分可合，入线时定。接线首笔的红绿冒烟项：**embedded client + sync
SqliteSaver 跑通多轮对话且 `checkpoint.sqlite` 落盘可读**——当前证据 ~90% 指 sync 正确
（决策 1 修正注），此冒烟把剩余不确定性钉死（async saver + 同步 client 若意外可行也在此
实验中显形）。
