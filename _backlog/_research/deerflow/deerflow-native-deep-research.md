# DeerFlow v2.1.0 原生 Deep Research 能力盘点

> 类型: 外部系统分析（消化材料） | 盘点基线: submodule `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7`（ethan-v2.1.0~1，= 上游 v2.1.0） | 更新: 2026-10-02
>
> 来源：直接阅读 `deerflow/` submodule 源码（只读）。本文只登记"框架有什么"，不下"v3 怎么用"的结论——方案见 [`../plans/2026-10-02-digest-deerflow-native-deep-research.md`](../plans/2026-10-02-digest-deerflow-native-deep-research.md)。

## 结论先行

DeerFlow v2.1.0 **没有**一个写死的 deep research 图。它的"Deep Research 能力"由三件东西拼出来：

1. 一份**方法论 skill**（`deep-research`）
2. 一套**subagent 委派系统**（lead agent 通过 `task` 工具派生隔离子代理）
3. **宿主工具与运行时**（web 搜索/抓取、沙箱、checkpointer、Gateway）

研究流程是动态涌现的：lead agent 加载 skill 方法论 → 按需派生 subagent 做多角度研究 → 汇总产出。这与 v2 的"静态 StateGraph 逐节点流水线"是两种范式。

## 1. deep-research skill（方法论层）

位置：`deerflow/skills/public/deep-research/SKILL.md`（公开 skill，随框架提交）。

- 纯提示词文档，无代码。触发条件写明："任何需要 web 研究的问题，代替单次 WebSearch"。
- 四阶段方法论：
  1. **Broad Exploration** — 广度搜索，识别维度/视角/利益相关方
  2. **Deep Dive** — 每个重要维度定向搜索 + `web_fetch` 读全文 + 顺引用追查
  3. **Diversity & Validation** — 事实数据/案例/专家观点/趋势/对比/挑战六类信息互补
  4. **Synthesis Check** — 综合前核对：≥3-5 个角度、多源交叉、关键数字有出处
- 核心原则："Never generate content based solely on general knowledge."

## 2. subagent 委派系统（执行层）

位置：`deerflow/backend/packages/harness/deerflow/subagents/`（registry / executor / builtins / config）。

- **内置类型只有两个**（`builtins/`）：`general-purpose`、`bash`。
- **类型可经 config.yaml 自定义**（`CustomSubagentConfig`）：description + system_prompt + tools 白名单 + skills 白名单 + model + max_turns + timeout + token_budget。
- executor 注释提到 "deep-research subagents" 用 `max_turns=150`——即**通过自定义类型**声明一个长跑研究子代理，不是内置。
- 委派治理是框架级中间件：并发钳制（`clamp_subagent_concurrency`，1–64）、每 run 总数上限（默认 6，可配 1–50）、token 预算（默认开 summarization 时 1M / 不开时 2M，per-agent 可覆盖）、超时覆盖。
- 子代理禁再派生（`disallowed_tools` 默认含 `task`）——**委派深度固定为一层**。

## 3. 宿主工具与运行时（底座层）

- 工具：`web_search`、`web_fetch`、沙箱内 `bash`/文件读写等（`deerflow.tools`）。
- 运行时：Gateway（FastAPI `app.gateway.app:app`，端口 8001）内嵌 LangGraph 兼容 runtime（RunManager + run_agent + StreamBridge）；checkpointer 可插拔；sandbox 可插拔。
- 可观察性：每个 Gateway 响应带 `X-Trace-Id`；有 trace/tracing、persistence、workspace_changes 等模块。
- agent 侧：`agents/factory.create_deerflow_agent`、middleware 链（含 tool error handling、context compaction）、skills catalog（`select:data-analysis,deep-research` 语法）、guardrails、reflection、scheduler。

## 4. 对 v3 的直接含义（事实，非方案）

| 事实 | 含义 |
|------|------|
| 框架无固定研究图 | v2 那种 "bootstrap → wave0/1/2 → …" 的静态图在 v3 不必也不该照搬 |
| deep research = skill + 动态委派 | 研究质量的核心杠杆变成：方法论提示词 × subagent 配置 × 委派治理参数 |
| 委派只一层、预算/并发框架管 | harness 若要更强的准入控制，得想清楚在哪一层插（skill 内容 / subagent 类型声明 / 外层图 / Gateway 之外） |
| Run Bundle / 证据账本 / gate 框架没有 | 这些仍是 v3 harness 的差异化职责（v2 思想的保留区） |

## 5. 历史注脚

v2 仓库在 2026-07 曾开过 plan `deerflow-native-deep-research-graph.md`（CLS-009，2026-07-19 归档），结论是"imported workflow isomorphic mapping，00–18 roadmap 逐节点自建"——即 v2 当时评估过原生能力后仍选择手搓节点。v3 重新开题，方向相反：**以原生能力为主，harness 做底座**。两份材料的时代背景不同（v2.1.0 发布于 2026-09-24，v2 开题时框架还没到这个形态），对照读有信息量。
