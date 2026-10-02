# DeerFlow 运行时与持久化面（Run 驱动 / resume / 边界）

> 类型: 外部系统分析（消化材料） | 基线: submodule `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7`（= 上游 v2.1.0） | 更新: 2026-10-02
>
> 来源：只读调查 DeerFlow submodule。所有路径相对 `deerflow/`。本材料回答「harness 到底怎么驱动一次
> agent run、过程状态存在哪、resume 靠什么」——Q2 接线路与 Q3 持久化边界的全部事实输入。

---

## 1a. 进程内驱动一次 run

**核心组件**（`backend/packages/harness/deerflow/runtime/`，包 `deerflow-harness` v2.1.0，import 前缀 `deerflow.*`）：

- `run_agent()` — `runtime/runs/worker.py:807`：
  `async def run_agent(bridge: StreamBridge, run_manager: RunManager, record: RunRecord, *, ctx: RunContext, agent_factory: Any, graph_input: dict, config: dict, stream_modes: list[str] | None = None, stream_subgraphs: bool = False, interrupt_before=None, interrupt_after=None) -> None`。执行 agent 后台任务，事件发布到 bridge。
- `RunContext`（frozen dataclass，worker.py:606-629）——一次 run 的基础设施依赖束：`checkpointer, store, event_store, run_events_config, thread_store, mcp_task_repo, app_config, extensions, checkpoint_channel_mode("full"|"delta"), checkpoint_snapshot_frequency, on_run_completed, conversation_reader`。
- `RunManager`（`runtime/runs/manager.py:248`，2424 行）——内存 run 注册表 + 可选持久 RunStore。关键方法：`create()`(manager.py:605，uuid4 run_id)、`create_or_reject()`(1498，admission，multitask_strategy=reject|rollback|interrupt，同 thread 活跃 run 冲突抛 `ConflictError`)、`get()/aget()`(662/706，内存优先、store 兜底水合)、`list_by_thread()`(723)、`cancel()`(1309，返回 `CancelOutcome` 枚举)、`try_start()`、`reserve_thread_operation()`、`reconcile_orphaned_inflight_runs()`(1861，租约/孤儿恢复)、`cleanup()`(1952，默认 300s 保留窗口)、`start_heartbeat()/shutdown()`。`RunRecord` dataclass（manager.py:184-231）：run_id/thread_id/assistant_id/status/on_disconnect/operation_kind/metadata/kwargs/user_id/token 统计/lease/idempotency_key 等。
- `RunStatus`/`DisconnectMode`/`ThreadOperationKind` — `runtime/runs/schemas.py`：pending|running|success|error|timeout|interrupted；cancel|continue；run|checkpoint_write|artifact_write|artifact_archive|branch|delete。
- `StreamBridge`（`runtime/stream_bridge/base.py:57`）抽象协议：`publish(run_id, event, data)` / `publish_end(run_id)` / `subscribe(run_id, last_event_id=None, heartbeat_interval=None) -> AsyncIterator[StreamEvent | StreamGap]` / `cleanup(run_id, delay)`。实现：`MemoryStreamBridge`（asyncio.Queue，进程内）与 `RedisStreamBridge`（可选 extra `deerflow-harness[redis]`，跨进程，故意不从 `__init__` 导出）。哨兵：`END_SENTINEL`、`HEARTBEAT_SENTINEL`；`StreamGap`(requested/earliest/latest_event_id) 表示回放窗口越界。
- 公开导出面：`deerflow/runtime/__init__.py:19-61` 的 `__all__`（RunManager/RunRecord/run_agent/RunContext/StreamBridge 族/checkpointer 工厂/CheckpointStateAccessor/serialize 族）。顶层 `deerflow/__init__.py` 是**空文件**——没有统一门面，公开面是各子包 `__init__`。

**下游在进程内怎么发起 run —— 两条真路**：

1. **`DeerFlowClient`（`deerflow/client.py:145`，嵌入式客户端，官方文档化入口）**：`__init__(config_path=None, checkpointer=None, *, model_name, thinking_enabled, subagent_enabled, plan_mode, agent_name, available_skills, middlewares, environment)`；`chat(message, thread_id=...) -> str`（client.py:1193）与 `stream(message, thread_id=...) -> Generator[StreamEvent]`（client.py:770，事件类型 `"values" | "messages-tuple" | "custom" | "end"`，client.py:124）。**它不经过 RunManager/run_agent/StreamBridge**——client.py:859-889 明确说明这是同一 `create_agent()` 工厂的并行 sync 消费者，不是 Gateway 的包装。**多轮必须传 checkpointer**（client.py:151-154），否则每次调用无状态。
2. **自组装 RunManager + StreamBridge + run_agent**：框架只提供零件；组装逻辑（admission、trace 绑定、config 构建、checkpoint 校验、metadata 任务、`asyncio.create_task` 挂 worker）全部住在 **app 层** `backend/app/gateway/services.py::start_run`（services.py:1459-1796）——这是参考组合方式，但 `app.*` 是未发布代码（backend/AGENTS.md Harness/App split：app imports deerflow，deerflow never imports app，`tests/test_harness_boundary.py` CI 强制）。下游要复刻这套组装只能 import `deerflow.runtime` 零件自己拼。

公共/内部边界的事实：`backend/AGENTS.md:194-199` 声明 harness 是 "Publishable agent framework package"、app 是 "Unpublished"。`make_lead_agent` 的签名/返回类型被称为 "published ABI"（agents/AGENTS.md，仅对 LangGraph Server 而言）。**未找到**对 `deerflow.*` 其余导入的正式稳定性/弃用政策文档——`deerflow.runtime.__all__` 是事实上的导出面，但没有版本化承诺。

## 1b. Gateway REST

FastAPI app：`backend/app/gateway/app.py`（端口 8001；nginx 2026 统一入口，`/api/langgraph/*` 重写为 `/api/*`）。Routers 挂载见 app.py:880-961。

**thread-scoped runs**（`app/gateway/routers/thread_runs.py`，prefix `/api/threads`）：
- `POST /{thread_id}/runs`（:923）后台 run，立即返回 RunResponse
- `POST /{thread_id}/runs/stream`（:941）create+SSE；响应头 `Content-Location: /api/threads/{thread_id}/runs/{run_id}`（LangGraph SDK 依赖它拿 run_id）
- `POST /{thread_id}/runs/wait`（:996）create+阻塞；完成后返回 serialize 的 thread state，复用/跨 worker 场景返回 `{status, error}`
- `POST /{thread_id}/runs/regenerate/prepare`、`/edit-regenerate/prepare`（:901/:912）
- `GET /{thread_id}/runs`（:1091，最新 100 条）、`GET /runs/page`（:1101 keyset 分页）、`GET /{run_id}`（:1143）
- `POST /{run_id}/cancel`（:1155）、`GET /{run_id}/join`（:1215 观察者 SSE）、`POST /{run_id}/stream`（:1331）
- `GET /{run_id}/messages`（:1528）、`GET /{run_id}/events`（:1710 完整事件流）、`GET /{run_id}/workspace-changes`（:1747）、`GET/POST /{run_id}/artifacts/archive`（:1637/:1652）、`GET /../messages`、`/messages/page`、`/token-usage`（:1361/:1500/:1767）

**threads**（`app/gateway/routers/threads.py`）：`POST /api/threads`（:866 创建）、`GET/PATCH /{id}`、`POST /{id}/branches`、`POST /search`、`POST /{id}/move`、`DELETE /{id}`、`GET/POST /{id}/state`（:1446/:1495）、`POST /{id}/history`（:1699）、`POST /{id}/compact`、`GET/PUT/DELETE /{id}/goal`。

**stateless runs**（`app/gateway/routers/runs.py`）：`POST /api/runs/stream`（:33）、`/wait`（:59）——无需预建 thread，自动建临时 thread；`GET /{run_id}/messages|feedback`。

**关键 schema**：`RunCreateRequest`（`app/gateway/run_models.py:29-58`，`extra="forbid"`）：`input, command, metadata, config, context, conversation_references, checkpoint_id, checkpoint, stream_mode, stream_subgraphs, on_disconnect("cancel"|"continue"), multitask_strategy("reject"|"rollback"|"interrupt"), if_not_exists("create")` + 兼容占位（webhook/on_completion/after_seconds/feedback_keys 必须为 None，`stream_resumable` 只接受 false/null——非默认值 422）。stream_mode 合法集合（`deerflow/runtime/stream_modes.py:7-15`）：`values, messages-tuple, updates, debug, tasks, checkpoints, custom`；`messages`/`events`/`tools` 等 422。可选 `Idempotency-Key` 头（thread-scoped create/stream/wait，按 owner+thread+key 做 sha256 域化）。

**认证**（`docs/API.md:1221-1274` + app/gateway/auth_middleware.py）：四种身份源——浏览器 session cookie（`access_token` HttpOnly + CSRF double-submit `X-CSRF-Token`）、OIDC/SSO、PAT（`Authorization: Bearer dfp_...`，scope 收窄到 threads/runs/projects 路由）、**Internal Auth（服务对服务）**：`X-DeerFlow-Internal-Token`（=env `DEER_FLOW_INTERNAL_AUTH_TOKEN`）+ `X-DeerFlow-Owner-User-Id`（owner 隔离键，不建 users 行）——这是下游 harness 走 REST 的最直接方式。非公开路径 fail-closed。

## 2. 持久化

**BaseCheckpointer：DeerFlow 自己不定义**。接口即 LangGraph 的 `langgraph.types.Checkpointer`（`runtime/checkpointer/provider.py:27`、`async_provider.py:25` import）。可插拔实现全部来自 LangGraph 官方包，由工厂选择：
- `memory` → `InMemorySaver`（默认，无 config 时）
- `sqlite` → `SqliteSaver` / `AsyncSqliteSaver`（extra `langgraph-checkpoint-sqlite`）
- `postgres` → `PostgresSaver` / `AsyncPostgresSaver` + psycopg AsyncConnectionPool（extra `deerflow-harness[postgres]`；pyproject.toml:73-78）
- 选择优先级：legacy `checkpointer:` 节 > 统一 `database:` 节 > 默认 InMemory（`async_provider.py:187-212`）。工厂：sync `get_checkpointer()/checkpointer_context()/reset_checkpointer()`（provider.py:196/267/243，单例）；async `make_checkpointer()` asynccontextmanager（async_provider.py:216，Gateway lifespan 用）。delta 模式下再包一层 `CachedHistorySaver`（`runtime/checkpointer/cached_saver.py`）。

**run 元数据持久化**（与 checkpoint 分离）：`RunStore` 抽象（`runtime/runs/store/base.py:112`）→ `MemoryRunStore`（`runs/store/memory.py:21`，database.backend=memory 时）与 `RunRepository`（`persistence/run/sql.py:35`，SQL）。run 事件持久化：`RunEventStore`（`runtime/events/store/`：memory/jsonl/db 三后端）。

**ThreadState**（`deerflow/agents/thread_state.py:280-295`，LangGraph thread state 的 schema）：extends langchain `AgentState`（messages 等）+ `sandbox, thread_data, title, artifacts, todos, goal, uploaded_files, viewed_images, promoted, delegations, skill_context, task_notes, task_history, summary_text, background_tasks`，各带自定义 reducer（merge_artifacts/merge_goal/merge_delegations/merge_skill_context 等）。实际存在 LangGraph checkpoint 里，按 `thread_id` 键控；channel 模式 `full`（全量 messages）或 `delta`（`checkpoint_channel_mode`，默认 full，进程冻结、重启切换；`runtime/AGENTS.md` Checkpoint Channel Modes 节）。

**resume 需要什么**：
- 核心事实：**框架没有"重启同一个 run"**——resume = 在同一 `thread_id` 上创建新 run，状态连续性来自 checkpointer（checkpoint 按 thread_id 累积）。
- 指定 checkpoint 分叉：`RunCreateRequest.checkpoint_id` / `checkpoint` → Gateway 校验属主 thread（不匹配 400）并 `checkpointer.aget_tuple` 验证存在性，**不存在 → 404 "Checkpoint {id} not found"**（services.py:1338-1392），然后写进 `config.configurable.checkpoint_id` 交给 LangGraph。
- Human-in-the-loop：`command: {"resume": value}` → `Command(resume=...)`（services.py:1569-1573）。
- `multitask_strategy=interrupt` 的取消保留 checkpoint；`rollback` 恢复 pre-run checkpoint（worker.py `_capture_rollback_point`/`_rollback_to_pre_run_checkpoint`）。
- **delta 模式不能分叉**：worker 在图启动前把 fork 线性化为当前 head 的整写（`_linearize_delta_checkpoint_resume`，worker.py:2246；runtime/AGENTS.md "A delta-mode run cannot fork"）。
- **checkpoint 丢失/不存在的行为**：(a) 新 thread 无 checkpoint → 静默从零开始（`if_not_exists="create"`，thread 自动创建）；(b) 显式 `checkpoint_id` 不存在 → 404 fail-closed；(c) checkpoint 通道模式不匹配（full 进程读 delta thread）→ threads router 409 `CheckpointModeMismatchError`（runtime/AGENTS.md，`checkpoint_mode.py`）；(d) Gateway 重启时未终态的 run 被孤儿恢复标记 error（`STARTUP_ORPHAN_RECOVERY_ERROR`，manager.py:40，deps.py:608-623）——run 记录还在 RunStore，但执行不续，需新 run。

## 3. run 与 trace 身份

- `X-Trace-Id`：`TraceMiddleware`（`app/gateway/trace_middleware.py:11`）对每个 HTTP 请求绑定；接受 caller 传入的 header（规范化：可打印 ASCII、≤512 字符，`trace_context.py:57-77`），否则 `uuid4().hex` 新铸（`generate_trace_id`，trace_context.py:52）。写入响应头（SSE 也覆盖）。
- **唯一事实源是 ContextVar** `_current_trace_id`（`deerflow/trace_context.py:49`）；其余一切载体（响应头、runtime.context、run record metadata、日志）都是派生输出、绝不回读。caller 在 `body.metadata`/`body.config.context` 里发的 `deerflow_trace_id` 会被**替换**而非采纳（services.py:1574-1583；worker `_bind_trace_id` worker.py:751-774）。下游要 pin 关联 id 就发 `X-Trace-Id`。
- 非 HTTP 入口各自绑定：scheduled/MCP 通知/IM/embedded（`DeerFlowClient.stream()` 每步 bind，client.py:784-822）。辅助函数：`ensure_trace_id()` / `resolve_trace_id(*carriers)` / `bind_trace_id()` / `request_trace_context()`（不继承上一请求）。
- 一个 run 的稳定 id：`run_id`（uuid4，RunManager.create）、`thread_id`（`^[A-Za-z0-9_-]{1,64}$`，`deerflow/utils/thread_id`）、`assistant_id`、每步 `checkpoint_id`。trace id 会写进 run record 的 `metadata.deerflow_trace_id`（runs 表持久）和 checkpoint `config["metadata"]`（持久、事后可查）。
- **下游关联手法**：REST 下游从 `Content-Location` 头与 SSE 首帧 `metadata` 事件（worker.py:1057-1065，`{run_id, thread_id}`）拿到框架 id；发自己的 `X-Trace-Id` 让它贯穿 run record/checkpoint/日志/Langfuse。注意 thread metadata 故意不含 trace id（一个 thread 跨多个 run）。

## 4. 框架对下游的官方边界

- `backend/AGENTS.md:194-199`（Harness/App split）：harness = `packages/harness/`，"Publishable agent framework package"，import `deerflow.*`；app = `app/`，未发布；依赖方向 CI 强制。**没有一份明说"下游应用从哪里接入"的文档**。
- 事实上的接入面有三层：(1) **`deerflow-harness` 包**（pyproject.toml：deerflow-harness 2.1.0，Python ≥3.12，hatchling 打包 `deerflow`；console script `deerflow` = TUI CLI；extras：postgres/redis/tui/browser/ollama/monocle 等）——`deerflow.runtime.__all__`、`deerflow.client.DeerFlowClient`、`make_lead_agent`、`deerflow.config.get_app_config` 等是事实导出面；(2) **Gateway REST**（docs/API.md 是完整参考，含 SDK 用法示例 API.md:1345-1463）；(3) **extension 契约** `packages/extension-api`（`deerflow_extension_api` 0.2.1，零依赖、禁止 import deerflow；贡献 middleware/lifecycle observer/Gateway service/FastAPI router；`examples/deerflow-extension-example/` 演示五种贡献）。harness pyproject 精确 pin `deerflow-extension-api==0.2.1`（版本契约）。
- **未找到**：`deerflow.*` 导出的正式 stability/deprecation 政策。下游若 import harness 内部路径（如 `deerflow.runtime.runs.worker`）没有契约保护。

## 5. 流式输出消费（事件清单）

**SSE 线上事件**（worker 发布 + `services.sse_consumer` services.py:1954-2047 透传）：
- `metadata` — 首帧 `{run_id, thread_id}`
- `values` — 全量 state 快照（serialize 后；带 `deerflow_seq` 消息排序戳）
- `messages` — token 增量/tool call/tool result（公共请求名 `messages-tuple`，SSE 事件名 `messages`；`write_file`/`str_replace` 参数增量有界批处理）
- `updates` / `tasks` / `debug` / `checkpoints` — LangGraph 模式 1:1
- `custom` — 自定义事件（含子代理 `task_*` 生命周期，root namespace）
- 子图帧带命名空间：`values|<ns>` 等（stream_subgraphs=true 时）
- `error` — `{message, name}`（worker.py:1453-1460，run 异常时）
- `end` — 终帧（END_SENTINEL）
- `gap` — `{"code":"stream_replay_gap", run_id, requested/earliest/latest_event_id, "recovery":"reload_durable_state"}`（回放游标越界或 idempotent 复用无流时）
- 心跳：SSE 注释 `: heartbeat`（不是事件）
- 重连：`Last-Event-ID` 头，回放窗口 = `stream_bridge.queue_maxsize`（默认 256）。
- `on_disconnect: cancel|continue` 只作用于创建者自己的流；join 观察者断开不取消。

**持久 run_events feed**（独立于 SSE，`runtime/events/catalog.py:58-94` + `contracts/run_event_stream_contract.json`）：`run.start, run.end, run.error, run.delivery, llm.human.input, llm.ai.response, llm.tool.result, llm.error, context:memory, subagent.start/step/end, workspace_changes, middleware:{guardrail|loop_detection|safety_termination|skill_activation|skill_secrets|tool_promotion|tool_progress}`。经 `GET /threads/{id}/runs/{rid}/events`、`/messages`、`/messages/page` 消费——run 结束后仍可读。

嵌入式路径（DeerFlowClient.stream）事件：`values / messages-tuple / custom / end`（end 带累计 usage）。

## 6. 对下游 harness 的含义

1. **两条驱动路的适用条件**：
   - **Gateway REST**（推荐给独立部署的 harness）：进程隔离、完整 admission/idempotency/cancel/lease/多 worker 语义、SSE + 持久事件双通道；用 Internal Auth（internal token + owner header）即服务对服务接入，无需 users 行；`Content-Location` + `metadata` 帧给全 run/thread id。代价：必须跑起 Gateway（含 config.yaml），认证/CSRF/CORS 要配对。
   - **进程内 `DeerFlowClient`**：适合同进程轻量驱动，sync 生成器即用；但它**没有 RunManager 语义**——无 run 记录、无 cancel/lease/idempotency、无 RunStore/run_events 持久化、trace/run 身份体系是简化版（每 turn 新 run_id 塞进 HumanMessage kwargs）。多轮必须自带 checkpointer。
   - **自组装 RunManager+run_agent**（复刻 `services.start_run`）：能力最全但参考实现住在未发布的 `app.*` 层，等于下游要自己维护一套 admission 组装，且无稳定性契约——最贵的一条路。
2. **持久化边界的硬事实**：
   - 框架持久化三块：checkpointer（thread state，LangGraph 表）、RunStore（run 元数据行）、RunEventStore（事件 feed）——后两块在 `database.backend=memory` 时是进程内的、重启即失。下游 Run Bundle 若要跨重启，必须配 sqlite/postgres。
   - **resume 语义 = 同 thread 新 run**；"接续对话"只需 thread_id（checkpoint 自动累积），"从特定点重放"需 checkpoint_id（丢失即 404，fail-closed）。孤儿 run 重启后标记 error 不复活——下游不要指望"继续那个 run"，只能重发新 run。
   - delta 模式（若启用）禁止 checkpoint 分叉，worker 会线性化——下游做 branch/regenerate 语义时要意识到模式差异。
   - trace id 是请求级的、server-owned：下游用 `X-Trace-Id` pin、从响应头/run metadata 读回；不要试图通过 body 传 `deerflow_trace_id`（会被替换）。
3. **不确定/未找到**：`deerflow.*` 导出的正式 API 稳定性政策文档（不存在或未找到）；`deerflow` 顶层无 `__init__` 门面（空文件）。
