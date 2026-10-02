# DeerFlow harness 包架构标本（解剖报告全文）

> 类型: 外部系统分析（消化材料） | 基线: submodule `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7`（= 上游 v2.1.0） | 更新: 2026-10-02
>
> 来源：只读调查。所有路径相对于 `deerflow/backend/packages/harness/deerflow/`（简写 `deerflow/`）；
> extension-api 相对于 `deerflow/backend/packages/extension-api/`。
> 本材料回答「一个成熟的 agent harness 长什么样」——我们自己 harness 结构推敲的标本。

---

## 1. 包的整体分层

### 顶层模块清单（`ls deerflow/` 实测）与一词角色

| 模块 | 角色 |
|---|---|
| `agents/` | **装配层**：lead agent 工厂、middleware 链、ThreadState、memory 提取、任务连续性 |
| `subagents/` | 委派系统：executor（后台执行引擎）、registry、capacity、durable batch |
| `tools/` | 工具组装面：`get_available_tools()` + `builtins/`（present_files、ask_clarification、task、view_image…） |
| `skills/` | 技能发现/解析/frontmatter/工具策略/投影/SkillScan |
| `mcp/` | MCP 集成：client、cache、session_pool、durable tasks |
| `sandbox/` | `Sandbox` ABC + 本地 provider + 沙箱工具 + 租约/审计 |
| `extensions/` | Python 插件 loader/registry/placement 锚点/ordering/stack 组合 |
| `models/` | 模型工厂（thinking/vision）+ 各 provider patch |
| `persistence/` | DeerFlow 自有 SQL ORM（runs/thread_meta/scheduled_tasks…），**与 LangGraph checkpointer 分离** |
| `runtime/` | 运行时宿主：RunManager + run_agent + StreamBridge + checkpointer/store 工厂 + journal |
| `config/` | ~45 个 pydantic 配置模型（每个域一个文件）+ 热重载边界 |
| `reflection/` | `resolve_variable`/`resolve_class` 动态类路径加载（唯一 importlib 汇点） |
| `community/` | 可选 provider 集合（搜索引擎、AIO/E2B/boxlite/tenki 沙箱、浏览器自动化） |
| `authz/` | 授权 principal/provider/RBAC |
| 其他 | `guardrails/`、`tracing/`（Langfuse/LangSmith）、`tui/`、`uploads/`、`workspace_changes/`、`projects/`、`scheduler/`、`integrations/`、`client.py`（嵌入式 DeerFlowClient）、`utils/`、`trace_context.py` |

### 依赖方向（grep 实测 `^from deerflow.`）

- **`config/` 几乎是叶子**：被 agents(28处)/mcp(9)/models(2)/persistence(8)/runtime(14)/sandbox(6)/skills(7)/subagents(8)/tools(8) 全员 import；它自己只有 3 处懒加载反向依赖（`config/agents_config.py:339` 懒 import `persistence.agents`；`config/app_config.py:57` import `extensions.loader.ExtensionSpec` 仅为类型）。
- **`agents/` 是装配顶点**：import config、tools、sandbox、skills、subagents、models、authz、extensions、runtime（checkpoint_mode/context_keys/events）、tracing（grep 输出全列表已验证）。
- **`runtime/` 在 agents 之上**：`runtime/runs/worker.py` 等 import `agents.thread_state`、`agents.middlewares.summarization_middleware`、`models.create_chat_model`、`sandbox.lease`、`tracing`、`workspace_changes` —— runtime 是"运行 agent 的宿主"，agents 是"造 agent 的工厂"。
- **tools ↔ agents 存在受控双向**：`tools/tools.py` 懒 import `agents.lead_agent.prompt`（技能缓存刷新）；靠函数内 lazy import 化解环。
- **包外铁律**：harness（`deerflow.*`）永不 import app（`app.*`），由 `backend/tests/test_harness_boundary.py` 在 CI 强制（`backend/AGENTS.md:199` 明文）。分层规则是文档化 + 测试锚定，不是 lint 工具。

结论：分层是「config 叶 → 功能子系统（tools/sandbox/skills/mcp/models/subagents）→ agents 装配 → runtime 宿主 → app(Gateway)」，仅一条显式强制边界（harness↔app），其余靠约定。

---

## 2. 装配机制（config.yaml → 运行时对象）

**核心模式：字符串类路径 + 反射解析 + 两级工厂。**

1. **配置解析**：`config.yaml` → pydantic `AppConfig`（`config/app_config.py`），`get_app_config()` 按文件内容签名缓存并热重载；基础设施字段 restart-only（`config/reload_boundary.py::STARTUP_ONLY_FIELDS` 注册表，测试 `test_reload_boundary.py` 锚定）。
2. **类路径声明**：`models[].use`、`tools[].use`、`sandbox.use`、`plugins[].use` 全是 `"module.path:ClassName"` 字符串（例：`config.example.yaml:153` `use: deerflow.models.patched_deepseek:PatchedChatDeepSeek`；`:1437` `sandbox.use: deerflow.sandbox.local:LocalSandboxProvider`）。统一由 `reflection/resolvers.py:25 resolve_variable` / `:73 resolve_class` 解析并做类型/基类校验。**这就是「config 声明 → 运行时对象」的映射模式：没有中央注册表，importlib 就是注册表。**
3. **两级工厂**：
   - SDK 级：`agents/factory.py:66 create_deerflow_agent(model, tools, middleware|features, ...)` —— **纯参数、不读 YAML**（docstring 明言），feature 用 `RuntimeFeatures` dataclass（`agents/features.py:16`，tri-state：`True`=内置默认实现 / `False`=关 / 实例=自定义替换）。
   - 应用级：`agents/lead_agent/agent.py:796 make_lead_agent(config: RunnableConfig)`（LangGraph Server ABI）→ `:801 assemble_lead_agent` → `:916 _assemble_lead_agent`：解析运行时选项（优先级 request > agent config > default，`_resolve_runtime_option` :167）→ 模型解析+授权（`_resolve_model_name`/`_authorize_model_name`）→ `get_available_tools()` → `apply_tool_authorization` → `assemble_deferred_tools`（tool_search 延迟目录）→ `build_middlewares`（:484）→ `apply_prompt_template`（`lead_agent/prompt.py:1070`）→ **最终调用 LangChain 的 `langchain.agents.create_agent`**（agent.py:1239），state_schema 用 `get_thread_state_schema(mode)`。
4. **装配结果自描述**：`LeadAgentAssembly(graph, descriptor)`（agent.py:91-101）—— descriptor 记录解析后的模型、渲染 prompt hash、授权后工具表、middleware 栈顺序；仅当有 observer 注册才构建（`_complete_assembly` :852，零 observer 快速路径）。
5. **extension 贡献最后合并**：`extensions/stack.py:134 compose_with_extensions` 在完整栈存在后一次性合并（agent.py:742-771）。
6. 另有 config 声明式 middleware 通道：`extensions.middlewares` 列表（class path 或 `{class, kwargs}`），`agents/middlewares/configured_extensions.py::load_configured_extension_middlewares` 经 `reflection.resolve_class` 加载（agent.py:715 调用）。

---

## 3. Agent 循环与 middleware 链

**循环本体不是 DeerFlow 写的**：`langchain.agents.create_agent`（LangGraph prebuilt，agent.py:33 import、:1239 调用）提供 model→tools→model 循环；DeerFlow 的全部行为通过 **middleware** 注入。

**接口形状**（基于 `langchain.agents.middleware.AgentMiddleware`，DeerFlow 中间件普遍 `AgentMiddleware[AgentState]`，如 `agents/middlewares/tool_error_handling_middleware.py:50`）：
- 生命周期钩子：`before_agent/after_agent(state, runtime)`、`before_model/after_model(state, ...)`
- 包装钩子（瀑布/洋葱）：`wrap_model_call(self, request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelCallResult`（实例签名见 `dynamic_context_middleware.py:751`）、`wrap_tool_call(self, request: ToolCallRequest, handler) -> Any`；各有 async 孪生 `awrap_*`。
- 注册方式：**列表顺序即注册**——`build_middlewares()`（agent.py:484）顺序 append；顺序契约文档化于 `agents/middlewares/AGENTS.md`（36 条编号），关键不变量「ClarificationMiddleware 必须最后」在代码里强制（agent.py:740 注释 + factory.py:419-423 把被挤走的它移回尾部）。
- 局部插入：`@Next(AnchorClass)/@Prev(AnchorClass)` 装饰器（`agents/features.py:49,61`，写 `_next_anchor/_prev_anchor` 类属性），插入算法 `factory.py:433 _insert_extra`（冲突检测 + 迭代解析 + 环检测）。

**现有 middleware 清单**（`agents/middlewares/` 47 个文件；AGENTS.md 编号职责，摘要）：
- 共享运行时基座（`build_lead_runtime_middlewares`，subagent 复用）：InputSanitization(1) / ToolOutputBudget(2) / ToolResultSanitization(3) / ThreadData(4) / Uploads(5) / Sandbox(6) / DanglingToolCall(7) / LLMErrorHandling(8) / Authorization+Guardrail(9) / SandboxAudit(10) / ReadBeforeWrite(11) / ToolProgress(12) / ToolReceipt+ToolErrorHandling(13)
- lead-only（`build_middlewares` 追加）：DynamicContext(14) / SkillActivation(15) / SkillToolPolicy(16) / DurableContext(17) / Summarization(18) / Todo(19) / TokenUsage(20) / Title(21) / Memory(22) / ViewImage(23) / McpRouting(24) / DeferredToolPromotionAudit(25) / DeferredToolFilter(26) / SystemMessageCoalescing(27) / SubagentLimit(28) / LoopDetection(29) / TokenBudget(30) / custom(31) / configured extensions(32) / TerminalResponse(33) / ModelLengthFinishReason(34) / SafetyFinishReason(35) / Clarification(36, 必须最后)

**LLM 调用**：graph 的 model 节点内，被 `wrap_model_call` 链包裹；模型实例由 `models/factory.py::create_chat_model` 按 `config.models[].use` 造（含 thinking/vision 分支、request_admission 限流、各家 patch）。
**工具执行**：tool 节点被 `wrap_tool_call` 链包裹；工具通过 `runtime: Runtime` 参数注入获得 LangGraph runtime（`tools/types.py:8` `Runtime = ToolRuntime[dict[str,Any], ThreadState]`，例 `sandbox/tools.py:2118 bash_tool(runtime: Runtime, command, ...)`）。
**流式输出**：`runtime/` 的 `RunManager` + `run_agent()` + `StreamBridge`（`runtime/__init__.py` re-export；memory/redis 两实现）；流模式 values / messages-tuple / custom / end（`client.py` 嵌入式消费同一契约）。自定义事件走 `utils/custom_events.emit_custom_event` 双发（writer + astream_events）。

---

## 4. extension-api 公共契约面

包：`backend/packages/extension-api/deerflow_extension_api/`（`API_VERSION = "0.2.1"`，`__init__.py:80`）。**铁律：本包绝不 import `deerflow`**（`__init__.py:3-6` docstring）——extension 可独立于 host 发布。

**能贡献什么**（`contracts.py:183-217 ExtensionRegistry` Protocol，全部方法带默认实现保证 additive）：
1. `middlewares(contributor)` — `MiddlewareContributor.contribute_middlewares(app_store, ctx) -> Sequence[MiddlewarePlacement]`（:149）
2. `task_lifecycle(contributor)` — `on_task_start/on_task_stop(app_store, task_store, info, outcome)`（:71-87）
3. `system_model_observer(observer)` — 观察非 middleware 包裹的系统级模型调用（title/summarization/memory/goal，`SystemOperationKind` :93）
4. `agent_assembly_observer(observer)` — 收到装配 descriptor
5. `context_compaction_observer(observer)` — 压缩事件
6. `service(service)` — `ExtensionService.start(deps: ExtensionRuntimeDeps)/stop()`，deps 含 app_store、`HostPolicySnapshot`、session_factory、run_evidence_reader（:161-176）
7. `routers(routers)` — FastAPI APIRouter 序列（类型保持 Any，host 校验后挂载，:210-217）

**placement 语义化**（`placement.py`）：`Placement` 枚举 `MODEL_LOGICAL/MODEL_PHYSICAL/TOOL_VISIBLE/TOOL_RAW/STANDARD`（按「轴+端」的语义保证定位，而非「第 3 层」的结构位置）+ `AgentScope` LEAD/SUBAGENT/BOTH + `order`。host 侧唯一知道栈形状的模块是 `extensions/anchors.py`（锚点表把语义 placement 翻译成具体索引）。

**最小 extension**（`examples/deerflow-extension-example/deerflow_extension_example/__init__.py:21-32`）：
```python
@extension(api="0.2.0", name="example")
def install(registry: ExtensionRegistry, config: Mapping[str, Any]) -> None:
    if config.get("enabled", True) is False: return
    service = ExampleService()
    registry.middlewares(ExampleMiddlewareContributor())
    registry.task_lifecycle(ExampleTaskLifecycle())
    registry.system_model_observer(ExampleSystemObserver())
    registry.service(service)
    registry.routers((build_router(service),))
```
加载：config.yaml 顶层 `plugins:` 列表（operator 控制，startup-only），`ExtensionSpec`（`extensions/loader.py:31`，含 enabled/name/use/config/required），config 顺序即加载顺序（loader docstring：栈位置敏感所以顺序要显式可复现）。`HostPolicySnapshot`（contracts.py:31-46）是对 host 限额的**窄投影**而非整个 AppConfig——刻意解耦发布节奏。

---

## 5. Skills 系统

- **发现/加载**：`skills/storage` + `load_skills()` 递归扫描 4 类根（`skills/public/` 全局公共、`{DEER_FLOW_HOME}/users/{uid}/skills/custom/` 用户自建、`{DEER_FLOW_HOME}/integrations/skills/{provider}/` 托管、legacy custom），每次调用全量扫描不缓存目录；enabled 状态读 `extensions_config.json`。
- **frontmatter schema**（`skills/frontmatter.py:15-27`）：`ALLOWED_FRONTMATTER_PROPERTIES = {name, description, license, allowed-tools, argument-hint, required-secrets, secrets-autonomous, metadata, compatibility, version, author}`；`split_skill_markdown`（:41）用正则 `^---\n(.*?)\n---` + `yaml.safe_load` 切分 metadata/body。`allowed-tools` 支持 spec 字符串或 YAML list，可移植拼写映射（`Bash`→`bash`、`Read`→`read_file` 等）。
- **目录/检索**：`skills/catalog.py::SkillCatalog`（不可变目录；查询形态 `select:a,b` / `+prefix` / 自由文本；`MAX_RESULTS=5`）；`skills/describe.py::build_skill_search_setup(skills, enabled, ...)` 产出 `describe_skill` 工具 + 名称表。
- **注入到模型可见面**（`agents/lead_agent/prompt.py`）：
  - 默认（`skills.deferred_discovery: false`）：`<available_skills>` 块带全量元数据进系统提示（:846）；
  - 延迟发现（true）：紧凑 `<skill_index>` 仅名称（:893），运行时 `describe_skill` 工具按需取元数据，再 `read_file` 加载正文——保 prompt 前缀缓存；
  - 显式激活：`/skill-name task` 由 `SkillActivationMiddleware` 检测，注入 SKILL.md 正文为隐藏当轮上下文；`SkillToolPolicyMiddleware` 在真实激活后才应用 `allowed-tools`（过滤 schema + 阻断执行）；`DurableContextMiddleware` 把已读技能引用记入 `ThreadState.skill_context`（只存 name/path/description，不存正文），压缩后仍可见。
- 沙箱文件投影：`skills/projection.py` 把 enabled 技能物化到 `skills_view/{public,custom,legacy,integrations}` 虚拟树（`/mnt/skills`）。

---

## 6. Sandbox 与工具

**Sandbox 抽象**（`sandbox/sandbox.py:44 class Sandbox(ABC)`）方法面：
- `execute_command(command, env=None, timeout=None) -> str`（env 键过 POSIX 名校验 :17，值用于注入请求级 secret）
- `execute_command_in_scope(..., scope_id=)` / `release_command_scope(scope_id)`（additive，默认直通）
- `read_file(path, start_line, end_line)` / `download_file(path) -> bytes` / `write_file(path, content, append)` / `update_file(path, bytes)`
- `list_dir(path, max_depth=2)`（missing→FileNotFoundError，失败→OSError，绝不 `[]`）
- `glob(path, pattern, ...) -> (matches, truncated)` / `grep(path, pattern, ...) -> (matches, truncated)`（truncated=「可能不完整」语义）
- 类属性 `persistent_shell_sessions: bool|None` 三态 fail-closed（:64，证据消费者据此把 bash 证据降级 UNVERIFIED）

**Provider 模式**：`SandboxProvider` 暴露 `acquire/acquire_async/get/release`（`sandbox/sandbox_provider.py`）；由 config `sandbox.use` 类路径选择。实现：`sandbox/local/`（每 user/thread PathMapping，虚拟路径 `/mnt/user-data/{workspace,uploads,outputs}`）+ `community/` 下 aio(Docker)/e2b/boxlite/tenki。`SandboxMiddleware`（`sandbox/middleware.py`）负责获取沙箱并把 `sandbox_id` 写入 state。

**工具注册——没有注册表/decorator 扫描**，是**组装函数 + 列表**：
- `tools/tools.py:73 get_available_tools(groups, include_mcp, model_name, subagent_enabled, ...)` 组装：config `tools[]`（`resolve_variable(cfg.use, BaseTool)` :113）+ `BUILTIN_TOOLS` 列表（:31-35）+ 条件附加（MCP task 工具、upload 工具、skill_evolution 工具、subagent 的 task/batch 工具、vision 才加 view_image :154-157、ACP）+ MCP 缓存工具（`mcp/cache.py::get_cached_mcp_tools`，带 `deerflow_mcp` 元数据标签）+ ACP 工具；最后按名去重（:207-221，防 LLM 收到歧义 schema，issue #1803）。
- 工具定义风格：`@tool("bash", parse_docstring=True)` + `runtime: Runtime` 参数注入（`sandbox/tools.py:2117`）——docstring 即模型可见 description，LangChain 从 docstring/签名生成 args schema。
- **schema 进模型请求**：交给 LangChain `bind_tools`（create_agent 内部）；DeerFlow 的增量是**延迟 schema**：`DeferredToolFilterMiddleware` 隐藏 MCP 工具 schema 直到 `tool_search` 或 `McpRoutingMiddleware` 晋升（`ThreadState.promoted` 按 catalog-hash 作用域）——省 prompt token + 保前缀缓存。

---

## 7. Persistence

**两套彻底分离的持久化**（`persistence/__init__.py` docstring 直言）：
1. **LangGraph checkpointer**（graph 执行状态/checkpoint，即消息历史所在）：`runtime/checkpointer/provider.py`（sync 工厂）+ `async_provider.py`，后端 memory/sqlite/postgres，由 config 的 legacy `checkpointer` 段或统一 `database` 段驱动（provider.py:62-80 `_resolve_checkpointer_config`）。另有 `cached_saver.py`（checkpoint cache）。Delta checkpoint 模式是 DeerFlow 自己的 channel 表示优化（`runtime/checkpoint_mode.py` + `checkpoint_patches.py`），带 fail-closed 兼容门。
2. **DeerFlow 应用 SQL**（`persistence/`，SQLAlchemy 2.0 async ORM）：`base.py::Base(DeclarativeBase)`（自动 to_dict）；**按聚合一分目录**的模式：`persistence/<aggregate>/{base.py, model.py, memory.py, sql.py}`（实测 `thread_meta/`、`run/` 等 17 个聚合目录：agents、channel_connections、feedback、managed_subagents、mcp_tasks、personal_access_tokens、projects、run、scheduled_task_runs、scheduled_tasks、subagent_batches、thread_meta、user、webhook_delivery…），memory.py/sql.py 双实现同一 base 接口（与 LangGraph store 的多后端语义对齐，如 `ThreadMetaStore.search()` 三后端 JSON 过滤语义一致）。Alembic 迁移在 `persistence/migrations/`。

**线程/消息持久化模型**：消息 = LangGraph checkpoint 里的 `messages` channel（由 checkpointer 落盘）；线程元数据（标题、显示名、filter）= `thread_meta` store；运行记录 = `persistence/run/model.py::RunRow`（run_id/thread_id/status/operation_kind/idempotency_key/model_name/metadata_json/kwargs_json/token 计数/`owner_worker_id`+`lease_expires_at`+`cancel_action` 多 worker 租约字段）；运行事件流 = RunJournal（`runtime/journal.py`）→ run_events。摘要/委派台账/技能上下文不进 messages，存 `ThreadState` 的独立 channel（`summary_text`、`delegations`、`skill_context`，自定义 reducer）。

---

## 8. 可借鉴模式 vs 复杂度包袱（判断，标注为判断）

### 值得照搬的结构模式
1. **两级工厂**（判断：直接抄）：`create_deerflow_agent`（纯参数 SDK 层，可测）在 `make_lead_agent`（config 驱动应用层）之下——我们 harness 的「组装函数」与「配置入口」应该同样分层。
2. **类路径 + 反射解析作插件机制**（判断：抄）：`use: module:Class` + `resolve_class(path, base_class)` 统一模型/工具/沙箱/middleware/plugin 五个扩展点，无需自建注册表。
3. **middleware 瀑布 + 语义 placement**（判断：抄思想）：挂在标准 `AgentMiddleware` 钩子上；顺序契约文档化编号 + 关键不变量代码强制（Clarification 最后）；扩展用「轴+端」语义 placement 而非索引号；`@Next/@Prev` 锚点做局部插入。
4. **tri-state feature flag**（`RuntimeFeatures`：True/False/实例）——声明式组装 + 每点可替换自定义实现。
5. **extension-api 独立契约包**（判断：若我们做插件面则抄）：不 import host；Protocol 全带默认实现（additive 演进）；host 只暴露 `HostPolicySnapshot` 窄投影而非全配置；semantic placement 的锚点翻译表是 host 内唯一知道栈形状的模块。
6. **装配自描述 + observer**（`LeadAgentAssembly(graph, descriptor)`，零 observer 快速路径）——可观测「这次 run 到底用什么拼出来的」。
7. **热重载边界注册表**（`STARTUP_ONLY_FIELDS` + 测试锚定 + config 签名缓存）——配置可变性与进程冻结的冲突显式管理。
8. **durable context channel 模式**（判断：对 deep research 尤其重要）：摘要、委派台账、已读技能引用走 `ThreadState` 独立 reducer channel，不塞 messages——压缩后不丢。我们的 research plan/finding ledger 同构。
9. **延迟工具 schema**（tool_search + catalog hash 作用域晋升）——工具多时省 token。
10. **双持久化分离**（checkpointer 管 graph 状态 / 自有 SQL 管运行记录，每聚合 memory+sql 双实现）+ **RunRow 的幂等键/租约字段**。
11. **嵌入式 client 与 Gateway 同构**（`client.py`，Gateway conformance 测试用 Pydantic 模型校验 client 输出）——我们若做控制底座，同一契约多入口。
12. **信任边界纪律**（判断：抄原则）：system 通道只放框架权威文本，不可信值走消毒过的 HumanMessage data 通道；注入消息盖 server-owned provenance 章；runtime context `__`-键服务端独占。

### 复杂度包袱（为它的规模/场景服务，deep research 单机 harness 大多不需要）
1. **36 条 lead middleware 链的大半**（判断）：title 生成、clarification 表单卡（v2 form 协议/字段校验数百行）、uploads、IM channel 相关、TokenUsage 归并——服务多入口聊天产品；我们大概只需：input sanitization、tool error handling、summarization、durable context、loop/token budget、terminal response ≈ 6-8 条。
2. **多实例协调全套**（判断：不要）：scheduled task 的 Postgres advisory lock/lease 预算、run ownership heartbeat、Redis StreamBridge、沙箱 cross-instance ownership store（take/claim/del: 状态机、TTL、心跳线程）——单实例研究底座完全不需要。
3. **技能物化投影**（`skills/projection.py` skills_view 树、E2B mount 上传预算/签名清单）——为沙箱内技能隔离服务；prompt 级技能注入足够。
4. **AuthZ/RBAC provider 框架 + guardrails 双层门**——多租户才需要。
5. **MCP durable task runtime**（mcp_tasks 表、lease、重试、死信）——只有长时 MCP 任务才需要。
6. **配置面规模**（45 个 config 模块、config_version=45、每字段 reload 语义标注）——热重载语义的维护成本本身；我们底座可以直接 startup-only 全量。
7. **subagent durable batch / warm pool / IM channels / Windows 编码兼容**——产品面特性。
8. LangChain AgentMiddleware 的隐式语义（after_model 反序分发等）是外部依赖行为，DeerFlow 靠文档+测试锚定——依赖它的同时要接受这份隐式性（判断：可接受，但我们的 harness 应把顺序不变量写成自己的测试）。

### 不确定/未深入（如实声明）
- `runtime/runs/manager.py`（RunManager，>2000 行）与 `worker.py` 只做了结构性 grep + AGENTS.md 交叉引用，未逐行读；run admission/lease 细节引自信任的模块内 AGENTS.md 文档。
- LangChain `AgentMiddleware` 钩子分发语义（如 after_model 反序）来自 DeerFlow 文档与 LangChain 惯例，未对照 langchain 源码验证。
- `app/`（Gateway FastAPI 层）超出 harness 范围，未调查（另见 runtime-and-persistence 材料）；`tui/`、`guardrails/`、`tracing/` 仅确认存在与角色。
- langgraph.json 只知其声明 `deerflow.agents:make_lead_agent` 入口（backend/AGENTS.md 与 agents/AGENTS.md 记载），未读文件本体。
