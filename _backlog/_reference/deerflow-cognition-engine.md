# DeerFlow 认知引擎与治理参数面（deep-research skill + subagent 委派）

> 类型: 外部系统分析（消化材料） | 基线: submodule `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7`（= 上游 v2.1.0） | 更新: 2026-10-02
>
> 来源：只读调查 DeerFlow submodule（文件路径相对 `deerflow/`，行号来自当前 checkout）。
> 本材料是「harness 事前约束层」的完整旋钮底账——Q2 答案 (b) 层的全部事实输入。

---

## 1. deep-research skill 全文结构

文件：`skills/public/deep-research/SKILL.md`（198 行，纯方法论文本，无脚本/资源文件）。

**Frontmatter（触发条件原文，L1-4）**：
```yaml
name: deep-research
description: Use this skill instead of WebSearch for ANY question requiring web research. Trigger on queries like "what is X", "explain X", "compare X and Y", "research X", or before content generation tasks. Provides systematic multi-angle research methodology instead of single superficial searches. Use this proactively when the user's question needs online information.
```

**核心原则（L29-31）**："Never generate content based solely on general knowledge. … A single search query is NEVER enough."；要求"Load this skill BEFORE starting any content generation task"（L10）。

**四阶段（Research Methodology，L33-106）**：
- **Phase 1: Broad Exploration**（L35-58）：Initial Survey（先搜主话题建立整体认知）→ Identify Dimensions（从初始结果识别需深挖的子主题/角度）→ Map the Territory（记录不同视角/利益相关方）。
- **Phase 2: Deep Dive**（L60-81）：对每个 dimension 做 Specific Queries（精确关键词）、Multiple Phrasings（多种措辞组合）、**Fetch Full Content**（用 `web_fetch` 读全文而非 snippet）、Follow References（追踪来源引用的其它资源）。
- **Phase 3: Diversity & Validation**（L83-94）：六类信息覆盖表——Facts & Data / Examples & Cases / Expert Opinions / Trends & Predictions / Comparisons / Challenges & Criticisms（每类给了示例搜索词）。
- **Phase 4: Synthesis Check**（L96-106）：五项 checklist——≥3-5 个角度、fetched 并通读过最重要来源、有具体数据/例子/专家观点、正反两面都覆盖、信息时效与权威性；**"If any answer is NO, continue researching before generating content."**

**工具用法约束**：
- `web_search`：查询要具体加上下文（"enterprise AI adoption trends 2024" 而非 "AI trends"，L110-131）；**Temporal Awareness（L133-152）**：每次查询前读 `<current_date>`，按用户意图选时间精度（today→月+日+年、this week→周区间、recently→月、this year→年），多措辞尝试数值/文字/相对形式。
- `web_fetch`（L154-160）：四种情况读全文——结果高度相关且权威、需要 snippet 之外的信息、来源含数据/案例/专家分析、需要理解发现的完整上下文。

**注意**：skill 本身不含任何 subagent/委派指令——"派 subagent 做研究"完全是框架层（lead prompt 的 `<subagent_system>` + `task` 工具）行为，skill 只约束研究方法论本身。

**其它相关公开 skill**（`skills/public/`，28 个）：
- `github-deep-research/SKILL.md`（L3）：GitHub 仓库多轮深研（GitHub API + web_search + web_fetch，四轮 workflow，产出结构化 markdown 报告）。
- `systematic-literature-review/SKILL.md`（L3）：跨多篇 arXiv 论文的系统性文献综述（与单篇的 `academic-paper-review` 明确分流）。
- 其余（consulting-analysis、data-analysis 等）为内容生成型，非 deep research 方法论。

## 2. CustomSubagentConfig 精确形状

**Schema 定义**：`backend/packages/harness/deerflow/config/subagents_config.py:102-136`（Pydantic）：

| 字段 | 类型 | 默认 | 说明（Field description 原义） |
|---|---|---|---|
| `description` | str | **必填** | "When the lead agent should delegate to this subagent" |
| `system_prompt` | str | **必填** | 行为指引 |
| `tools` | list[str]\|None | None | 工具白名单；None = 继承父 agent 全部工具 |
| `disallowed_tools` | list[str]\|None | `["task","ask_clarification","present_files"]` | 拒绝名单（**默认禁 task = 一层深度限制**；可被覆盖） |
| `skills` | list[str]\|None | None | skill 白名单；None = 全部启用 skill，`[]` = 禁用 skill |
| `model` | str | `"inherit"` | inherit = 用父模型 |
| `max_turns` | int | 50（≥1） | 最大 agent 轮次（一次模型调用+其工具执行） |
| `timeout_seconds` | int | 900（≥1） | 执行时长上限 |

内部运行时 dataclass `SubagentConfig`（`subagents/config.py:11-46`）同字段，但 `disallowed_tools` 默认只有 `["task"]`。model 解析顺序（config.py:55-67）：显式 model > 父 run 模型 > `models[0]`。

**config.yaml 声明位置**：顶层 `subagents.custom_agents.<name>`。例子原文（`config.example.yaml:1754-1774`）：
```yaml
#   custom_agents:
#     analysis:
#       description: "Data analysis specialist for processing datasets and generating insights"
#       system_prompt: |
#         You are a data analysis subagent. Focus on: ...
#       tools:                  # Tool whitelist (null = inherit all)
#         - bash
#         - read_file
#         - write_file
#       skills:                 # Skill discovery/activation allowlist (null = all, [] = none)
#         - data-analysis
#         - visualization
#       model: inherit          # 'inherit' uses parent's model
#       max_turns: 80
#       timeout_seconds: 600
```

**Per-agent 覆盖**（对 built-in 和 custom 都生效）：`subagents.agents.<name>`，字段 `SubagentOverrideConfig`（subagents_config.py:74-99）：`timeout_seconds` / `max_turns` / `model` / `skills` / `token_budget`（全可选，None=继承）。

**发现与选用机制**（`subagents/registry.py`）：
- 解析顺序（`get_subagent_config` docstring，L109-113）：① built-in（general-purpose, bash）→ ② config.yaml `custom_agents` → ③ 已启用的 admin-managed 定义（同名冲突时被排除出 runtime，L209-215）→ ④ `subagents.agents.<name>` 覆盖。
- **选用是 LLM 按 description 匹配，非自动路由**：lead prompt 的 `_build_available_subagents_description`（`agents/lead_agent/prompt.py:303-340`）把每个类型渲染成 `- **name**: description首行(HTML转义)` 放进 `<subagent_system>` 块；模型调用 `task` 工具时显式传 `subagent_type` 参数（`tools/builtins/task_tool.py`，参数：`prompt`、`subagent_type`、可选 `acceptance_criteria`、可选 `description` 仅作进度标签）。
- 过滤：custom agent 的 `allowed_subagents`（None=全部 / []=硬禁 / list=白名单）同时过滤 prompt 发现和 task 执行；host bash 不可用时 `bash` 类型被隐藏（registry.py:224-238）。

**Built-ins 原样**：
- `general-purpose`（`subagents/builtins/general_purpose.py:5-70`）：`tools=None`（继承全部），`disallowed_tools=["task","ask_clarification","present_files"]`，`model="inherit"`，`max_turns=150`。description 强调"clear delegation benefit"（specialist tools / 独立并行 / context 隔离），"Do NOT use merely because work is complex"。system_prompt 含 tool_restrictions（禁止再派 task）、file_editing_workflow（str_replace 优先）、output_format（要求 `[citation:Title](URL)` 引用格式）。
- `bash`（`subagents/builtins/bash_agent.py:5-50`）：`tools=["bash","ls","read_file","write_file","str_replace"]`（仅沙箱工具），`max_turns=60`，同样禁 task/ask_clarification/present_files。

## 3. 委派治理参数全表

**进程容量（startup-only，重启生效）** `subagent_runtime`（`config/subagent_runtime_config.py`；例 `config.example.yaml:1701-1705`；restart-required，见 `config/reload_boundary.py::STARTUP_ONLY_FIELDS`）：
- `max_running: 3`（1-64）：进程内并发执行的 native subagent 上限（Gateway/embedded 启动时装一个进程级 FIFO admission controller）。
- `max_queued: 64`（0-10000）、`admission_policy: queue|reject`、`queue_timeout_seconds: 300`。

**每响应并发钳制**（`subagents_config.py:18-36`）：`clamp_subagent_concurrency` = clamp 到 [1, min(64, subagent_runtime.max_running)]；`effective_subagent_concurrency` 把「per-run 请求值（configurable `max_concurrent_subagents`）」与启动时 `max_running`、安全上限取最小，**同一个值同时喂给 lead prompt、SubagentLimitMiddleware 和进程执行容量**——热改 YAML 不能让已创建的 controller 超卖。

**每 run 总数**：`subagents.max_total_per_run`，默认 **6**（schema 1-50，`DEFAULT_MAX_TOTAL_SUBAGENTS_PER_RUN`，subagents_config.py:11-13,152-157）；运行时覆盖 `configurable.max_total_subagents`（clamp 到同区间）。由 `SubagentLimitMiddleware` 对 durable delegation ledger 中**当前 run_id** 的条目计数（跨 run 的历史委派不占预算）；耗尽时剥离剩余 task 调用、强制 `finish_reason="stop"`、附可见 limit note。

**Token 预算（两档）**（subagents_config.py:44-71, 236-264）：`subagents.token_budget`（TokenBudgetConfig：`enabled`/`max_tokens`/`max_input_tokens`/`max_output_tokens`/`warn_threshold`/`hard_stop_threshold`，见 `config/token_budget_config.py`）。默认 `enabled=True`，`max_tokens` **与 `summarization.enabled` 耦合：summarization 开=1,000,000，关=2,000,000**（注释明说 1M 档"still covers legitimate deep research"），warn 0.7，hard-stop 1.0。用户显式设置的 budget（全局或 per-agent）永远优先于耦合重算。硬停行为：剥离当轮 tool_calls、强制 stop、正常收尾并打 `stop_reason=token_capped`（不抛异常）。Per-agent 覆盖：`subagents.agents.<name>.token_budget`（对 built-in 和 custom 都生效——注释明确 token budget 是"must engage for every subagent"的 backstop，与 timeout/max_turns 只作用于 built-in 不同）。

**超时**：`subagents.timeout_seconds` 默认 **1800s**（仅作为 built-in 的全局默认；custom agent 用自己的 900 除非覆盖），per-agent `agents.<name>.timeout_seconds` > 全局 > 自带值（registry.py:142-149）。执行超时产生 `task_timed_out`。

**Max turns**：built-in 默认 general-purpose=150 / bash=60；`subagents.max_turns`（全局，仅覆盖 built-in）与 `agents.<name>.max_turns`（per-agent，built-in+custom）可改。`turn_budget.py::resolve_recursion_limit` 把 turn 数按组装的 middleware 链深度换算成 LangGraph recursion_limit（逐字透传会损失 ~18/150 turn）。耗尽 → GraphRecursionError → `stop_reason=turn_capped`。

**一层深度限制**：`disallowed_tools` 默认含 `task`（`SubagentConfig` 默认 `["task"]`；CustomSubagentConfig 与两个 built-in 默认 `["task","ask_clarification","present_files"]`），且 general-purpose system_prompt 明文禁止调用 task。**注意：custom agent 的 disallowed_tools 是可配置字段——下游若要硬保证一层深度，应在 harness 侧校验自定义类型没有把 task 从 disallowed_tools 拿掉（框架 schema 不强制）。**

**其它护栏**：`LoopDetectionMiddleware`（`loop_detection.enabled`，factory 默认 True；重复同工具调用集 → 剥 tool_calls 强制收尾，`loop_capped`）；`verification.receipts_enabled`（默认 on，receipt 引用 `[rN]` 校验）；`subagent_batches.*`（durable batch，默认 `enabled: false`，与普通 task 的限额互相独立）。

**覆盖方式总结**：全局=`subagents.*`（timeout/max_turns 只落 built-in；token_budget 落所有）；per-agent=`subagents.agents.<name>`；per-request=`configurable.{max_concurrent_subagents, max_total_subagents}`；进程级=`subagent_runtime.*`（重启才生效）。

## 4. lead agent 侧可配置面

**`create_deerflow_agent`**（`agents/factory.py:66-81`，纯参数 SDK 工厂，不读 YAML）：
参数：`model`、`tools`、`system_prompt`、`middleware`（**全接管**，与 features/extra_middleware 互斥）、`features: RuntimeFeatures`、`extra_middleware`（经 `@Next/@Prev` 锚点插入，features.py:49-69）、`plan_mode`、`state_schema`、`checkpoint_channel_mode`（"full"|"delta"，delta+checkpointer 被拒绝）、`checkpoint_snapshot_frequency`、`checkpointer`、`name`、`subagent_runtime: SubagentRuntime`（直连 SDK 时显式注入容量/batch worker；要求 features.subagent=True；batch worker 需先 `await runtime.start()`）。

**RuntimeFeatures**（`agents/features.py:30-41`）：`sandbox=True`、`memory=False`、`memory_config=None`、`summarization=False|middleware实例`（**无内置默认**，SummarizationMiddleware 需要 model 参数）、`subagent=False`、`vision=False`、`auto_title=False`、`guardrail=False|实例`（**无内置 GuardrailMiddleware**，True 会 raise）、`loop_detection=True`、`token_budget=False`（lead 级）。

**`make_lead_agent`/`assemble_lead_agent` 的 runtime configurable**（`agents/lead_agent/agent.py:937-962`）：`model_name`、`thinking_enabled`、`is_plan_mode`、`subagent_enabled`（**默认 False**）、`max_concurrent_subagents`、`max_total_subagents`、`agent_name`（custom agent）。

**对下游有用的 middleware 开关**（完整 36 条链见 `agents/middlewares/AGENTS.md`，装配点 `tool_error_handling_middleware.py::_build_runtime_middlewares` + `lead_agent/agent.py::build_middlewares`）：
- **Context compaction**（`DeerFlowSummarizationMiddleware`，config `summarization.*`，`config/summarization_config.py`）：`enabled`（pydantic 默认 False；**config.example.yaml:1922-1923 默认写了 `enabled: true` + trigger tokens 32000**）、`model_name`（null=用 run 实际模型做摘要，非 models[0]）、`trigger`（tokens/messages/fraction 三种，OR 逻辑，至少一条；fraction 需要模型的 `context_window` 声明否则弃用告警）、`keep`（默认 `messages: 20`）、`trim_tokens_to_summarize: 4000`、`skill_file_read_tool_names`。**lead 与 subagent 共用同一开关**（subagent 经 `build_subagent_runtime_middlewares` 继承，与 token budget 1M/2M 档耦合）。
- **Tool error handling**（`ToolErrorHandlingMiddleware`）：把工具异常转成 error `ToolMessage` 让 run 继续（错误详情截 500 字符 + "Continue with available context, or choose an alternative tool"），并给所有结果打 `deerflow_tool_meta`（status/recoverable_by_model/recommended_next_action）。`LLMErrorHandlingMiddleware` 把 provider 失败转成带 `deerflow_error_fallback` 的 AIMessage；subagent 侧被 executor 映射为 `task_failed`。
- **Guardrails**（`middlewares/AGENTS.md` 条目 9 + `docs/GUARDRAILS.md`）：`GuardrailMiddleware` 是 pre-tool-call 双闸——`authorization.enabled`（AuthorizationProvider，Layer1 能力过滤复用为 Layer2 执行检查）+ `guardrails.enabled`（显式 GuardrailProvider，例 `deerflow.guardrails.builtin:AllowlistProvider`，config.example.yaml:2763-2780）；fail-closed、审计、拒绝为 error ToolMessage。
- **Reflection**：`deerflow/reflection/` 只是**动态模块加载工具**（`resolve_variable`/`resolve_class`），支撑 `tools[].use:` 类路径与 `extensions.middlewares` 的 `module:Class` 字符串——不是行为反思机制，命名易误解。
- **Skills catalog select 语法**：`SkillActivationMiddleware`（`agents/middlewares/skill_activation_middleware.py`）识别**最新真实用户消息开头的严格 `/skill-name task` 斜杠语法**（run 级绑定、权威、触发 `SkillToolPolicyMiddleware` 应用该 skill 的 allowed-tools）；无斜杠时 skill 仅作为 `<available_skills>` 元数据块被发现（`skills.deferred_discovery: true` 可换成紧凑 `<skill_index>` + `describe_skill` 工具）。skill 的 allowed-tools 只在真实激活后钳制 lead 工具集。per-agent skill 白名单：custom agent config.yaml 的 `skills` 列表、subagent 的 `skills` 字段、`DeerFlowClient(available_skills=...)`。
- 其它相关：`InputSanitizationMiddleware`（外层净化用户输入）、`ToolResultSanitizationMiddleware`（对 `web_fetch`/`web_search`/`image_search`/`web_capture` 结果中和框架标签——对 deep research 直接相关）、`ToolOutputBudgetMiddleware`（工具输出预算/外置）、`ReadBeforeWriteMiddleware`（默认 on）、`SubagentLimitMiddleware`（见 §3）、`TokenBudgetMiddleware`（lead 级 `token_budget.enabled` 默认 false）。

## 5. 跑一次 deep research run 的最小配置

**没有现成的"deep research 一页文档"**；相关文档散在：`backend/docs/CONFIGURATION.md`、`backend/docs/summarization.md`、`backend/docs/GUARDRAILS.md`，以及前端用户手册 `frontend/src/content/en/harness/subagents/*.mdx`（quick-start 明确：**UI 的 Ultra 模式 = `subagent_enabled=true` + plan mode + reasoning effort high**；limits/catalog/delegation/reference 各一页）。

**config.yaml 最小声明**（`config.example.yaml` 为模板，`make config` 生成）：
1. `models[]`：至少一个模型（无模型启动直接失败，`subagents/config.py:49-52`）。必须。
2. `tools[]`：`web_search`（默认示例 = DDG：`deerflow.community.ddg_search.tools:web_search_tool`，L802-804）+ `web_fetch`（默认示例 = Jina：`deerflow.community.jina_ai.tools:web_fetch_tool`，L1059-1061；同一时刻只允许一个 web_fetch provider）。deep-research skill 的可用性依赖这两个工具。
3. `skills:` 默认即可——`skills/public/` 自动扫描，**skill 未在 `extensions_config.json` 的 `skills` map 中显式登记时默认 enabled**（`config/extensions_config.py:567-586`），所以 deep-research 开箱可用；`container_path: /mnt/skills`。
4. `sandbox.use:` 默认 local provider。
5. `subagents:` 可整段留空（quick-start.mdx L14 原话："The `subagents:` section in `config.yaml` can stay empty; the built-in defaults work"）。
6. 推荐给 deep research 加（example 注释里就是这么建议的，L1740-1748）：`subagents.agents.general-purpose.{timeout_seconds: 2700, max_turns: 250}`、`summarization.enabled: true`。

**关键事实：委派不是 config.yaml 开关**。`SubagentsAppConfig`（subagents_config.py:139-169）**没有 `enabled` 字段**；backend/AGENTS.md 里"`subagents.enabled` master switch"的说法与 schema 不符（未找到该 key）。启用方式是**每请求** runtime configurable `subagent_enabled: true`（默认 False；UI=Ultra 模式；API=`body.context`/`config.configurable`；`DeerFlowClient(subagent_enabled=True)`，client.py:186）。

**程序化最小路径**（embedded，无 HTTP）：`DeerFlowClient(model_name=..., subagent_enabled=True, available_skills={"deep-research"} 或 None=全部)` → `chat()/stream()`（`packages/harness/deerflow/client.py:179-239`）；或在请求 configurable 里带 `{"subagent_enabled": true, "max_concurrent_subagents": N, "max_total_subagents": M}`。显式钉死 skill 可用斜杠激活 `/deep-research <query>`（SkillActivationMiddleware 严格语法）。直接 `create_deerflow_agent` 用户需自传 `SubagentRuntime` + `features.subagent=True`，且**工厂不渲染系统提示词、不装 Gateway API/UI**（agent.py Direct subagent runtime 段）。

## 6. harness 事前约束层可用旋钮清单

| Config key / 旋钮 | 作用 | 默认值 | 覆盖层级 |
|---|---|---|---|
| `subagent_runtime.max_running` | 进程内并发执行 subagent 数（并发钳制的真实槽位） | 3（1-64） | 全局，**startup-only** |
| `subagent_runtime.max_queued` / `admission_policy` / `queue_timeout_seconds` | 排队上限 / queue\|reject / 排队超时 | 64 / queue / 300s | 全局，startup-only |
| configurable `max_concurrent_subagents` | 每响应 task 并发（被 clamp 到 min(64, max_running)） | 取 max_running | per-request |
| `subagents.max_total_per_run` | 每 run 委派总数（对 ledger 当前 run 计数） | 6（1-50） | 全局 |
| configurable `max_total_subagents` | 同上的 per-request 覆盖（clamp 1-50） | 落 max_total_per_run | per-request |
| `subagents.token_budget.enabled/max_tokens/warn_threshold/hard_stop_threshold` | 每 subagent-run token 硬顶（硬停剥 tool_calls 强制收尾，token_capped） | enabled=True；max_tokens **1M（summarization on）/ 2M（off）**；warn 0.7；hard 1.0 | 全局（显式设置永远赢过耦合档） |
| `subagents.agents.<name>.token_budget` | per-agent token 预算覆盖（built-in+custom 都生效） | None | per-agent |
| `subagents.timeout_seconds` | 超时默认（**仅 built-in**） | 1800s | 全局 |
| `subagents.agents.<name>.timeout_seconds` | per-agent 超时（built-in+custom） | None | per-agent |
| `subagents.agents.<name>.max_turns` / `subagents.max_turns` | 轮次上限（后者仅 built-in；turn→recursion_limit 按链深换算） | gp=150 / bash=60 / custom=50 | per-agent / 全局 |
| `custom_agents.<name>.disallowed_tools` | 工具拒绝名单（默认含 task = 一层深度；**可被去掉，harness 需自校验**） | `["task","ask_clarification","present_files"]` | per-type |
| `custom_agents.<name>.tools` / `.skills` / `.model` / `.system_prompt` / `.description` | 自定义 subagent 类型全定义 | tools=None(全继承) / skills=None(全) / model="inherit" | per-type |
| `subagents.agents.<name>.skills` | skill 白名单（None=全，[]=无） | None | per-agent |
| configurable `subagent_enabled` | task 工具是否出现（委派总开关） | **False** | per-request |
| `summarization.enabled/.trigger/.keep/.model_name` | lead+subagent 共用的 compaction（也决定 token 预算档位） | pydantic False（example yaml 写 true, trigger tokens 32000, keep messages 20） | 全局，热重载 |
| `loop_detection.enabled` | 重复工具调用循环熔断（loop_capped） | True（factory 默认） | 全局 |
| `verification.receipts_enabled` | subagent 报告 `[rN]` receipt 引用校验 | on | 全局 |
| `guardrails.enabled` + provider / `authorization.enabled` | pre-tool-call 执行闸（AllowlistProvider 等） | 关 | 全局 |
| `read_before_write.enabled` / `tool_progress.enabled` | 写前读校验 / 工具停滞状态机 | on / off | 全局 |
| `token_budget.enabled`（顶层） | **lead** run 的 token 硬顶 | false（max_tokens 200000, warn 0.8, hard 1.0） | 全局 |
| `recursion_limit` / `max_recursion_limit` | LangGraph 超步预算及不可信上限 | 100 / 1000 | 全局（热重载） |
| `skills.deferred_discovery` | `<available_skills>`↔`<skill_index>`+describe_skill | false | 全局 |
| extensions `skills: {name: {enabled}}` | 单 skill 启停（未登记=默认启用） | 启用 | per-skill |
| custom agent `allowed_subagents` | 委派类型白名单（None=全 / []=硬禁） | None | per-agent（snapshotted 进 run metadata） |
| configurable `model_name` / `thinking_enabled` / `is_plan_mode` | lead 模型/思考/plan 模式 | models[0] / True / False | per-request |

## 7. 调查中的未找到/不确定项（如实记录）

1. `subagents.enabled` 作为 config.yaml key——不存在于 schema（backend/AGENTS.md 的表述与代码不符）。
2. 没有 deep-research 专用文档页或端到端示例配置。
3. `custom_agents` 的 disallowed_tools 理论上可移除 `task`（schema 不强制一层深度）——下游 harness 若要硬保证需自行断言。以上均已给代码证据。
