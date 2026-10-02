# Plan: 接线与结构定案（wiring-structure）

> 类型: 设计 | 更新: 2026-10-02 | 来源: digest 边界 plan 六裁决推敲（裁决 #1/#3/#5 + 用户契约镜像要求）

## 背景 / 现状

六项裁决已定（见 digest plan 修订节）：接线路 = **embedded DeerFlowClient**；外层编排 = **普通状态机**
（非 LangGraph 图）；middleware = **只配置不编写**。用户硬要求：我们借力的每个 DeerFlow 表面
要在**自己源码树里有一份肉眼可见的拷贝**（契约镜像）。元原则：能借 DeerFlow 多少就借多少；
v2 拿得过来就拿，拿不过来就算了。证据底座：`_reference/deerflow-runtime-and-persistence.md`
（接线路事实）、`deerflow-cognition-engine.md`（旋钮表）、`deerflow-harness-architecture.md`
（结构标本）。

**项目级准绳（2026-10-02 用户确立，先序于一切技术裁决）**：① 这是一个研究与练习项目，
工程化渐进推进——**透明可见、可调试优先**于机制精巧与省轮次；② 最终交付给不懂 AI 的
人——workflow 质量必须让非 AI 接手者可依赖（宁可响亮失败、不可安静烂掉；一切失败路径
人话可读）；③ 项目的研究本体 = **「带质量控制的 agentic workflow 研发怎么做合理」**，
参照建筑施工质量监控体系（监理独立性/隐蔽验收/试块/竣工资料），DeerFlow 为实验环境——
质量控制体系映射表见 bundle-contract plan 的设计理由节。

## 决策 / 方案

1. **embedded 接线**（runtime 层）：`DeerFlowClient` 封装——构造参数全集（model_name /
   subagent_enabled=True / available_skills〔构造期参数，不能 per-call 切换〕/
   checkpointer=Bundle 的 **sync SqliteSaver** / config_path〔决策 6：显式传 base 或
   fixture〕/ environment〔tracing 标签，见决策 7②〕/ middlewares〔逃生口，注入语义见
   决策 4〕）；stream 事件流消费入口。**「三消费者」定义（2026-10-02 定）**：同一条
   embedded stream 的三个消费方——① watch 渲染器（直播展示，entry-surface 承载）、
   ② journal 落账器（model_tool 事件写 diagnostics，bundle-contract 承载）、③ 状态机
   终态检测器（终态判定：正常完成 / 澄清中断〔决策 8 检测谓词〕/ stop_reason 识别，
   wiring+bundle 联合承载）。与观察「三层」（watch/journal/checkpoint 回放）是两个
   概念——回放不消费实时流。
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
   真需要框架没有的行为时写标准 AgentMiddleware 插头，不碰框架。**注入语义（2026-10-02
   digest 补课）**：client 的 `middlewares=[...]` 参数是**插入**（lead 链 #32 槽位，
   SafetyFinishReason/Clarification 之前），不是接管，无移除内置项的机制；middleware 间
   **无错误隔离**（一个抛异常后续全跳过）——逃生口中间件必须自防异常。**默认值矩阵**
   （base config 写旋钮时的基线）：默认/强制已开 = 输入消毒、远程内容消毒（web 结果
   中性化）、ToolErrorHandling、LLMErrorHandling（含断路器 5 次/60s）、loop_detection、
   read_before_write、verification.receipts；默认关 = summarization（决策 6 已定显式开）、
   lead 级 token_budget（v1 保持默认关——subagent 级 token 预算默认已开，1M/2M 档够用；
   证据说话再开）、tool_progress、guardrails、authorization。
5. **(b) 层旋钮声明**（agents 层）：研究 subagent 类型定义 + 预算参数——**物理落点 =
   deerflow config.yaml 的 `subagents.custom_agents.<name>` + `subagents.agents.<name>`
   段**（即决策 6 的 base config，不是代码）；**一层深度自校验**（框架 schema 不强制
   disallowed_tools 含 task——harness 必须断言，C 线警告）。
6. **配置面设计**（2026-10-02 定案，用户拍板选项 A；取代原「凭证单路线」表述）：
   - **三个 config 面，命名区分死**：`openspec/config.yaml`（治理上下文，≤12500 字符
     预算闸）/ harness `.env`（秘密）/ **deerflow config.yaml**（框架装配面：models /
     tools / sandbox / `subagents.*` / summarization 等旋钮）。「config.yaml」一词在本仓
     一律带前缀使用。
   - **harness 持有两份 checked-in 配置**：`base`（real 跑）与 `fixture`（零凭证演跑）；
     构造 client 时**显式传 `config_path`** 二选一（框架会从 cwd / `DEER_FLOW_PROJECT_ROOT`
     自动发现 config.yaml——必须杜绝误拾）。生效配置即 checked-in 文件，「实际生效的是
     什么」永远可答（digest harness/09 的 ST3/RT1 判据，连 dump 机制都不需要）。
   - **形状与秘密分离**：config.yaml 持形状，`api_key: $VAR` 引用 `.env`（框架 `$VAR` →
     `os.getenv`）；`.env`（模型 selector + key + TAVILY_API_KEY）由 harness 入口层在
     构造 client 前装载进进程环境。不做 profile 体系（原裁决保持）。
   - **fixture 档 = 框架自己的 `use:` 类路径缝**：fixture config 的 `models[].use` /
     `tools[].use` 指向假模型（FakeToolCallingModel 式）/ 假 web_search 类路径——零凭证
     跑完整真实 client 链路（供 entry-surface 两级阶梯消费）。
   - **base config 必须显式开 `summarization.enabled: true`**：pydantic 层默认关、上游
     example 模板写 true，两处默认态不一致——以我们自己的 checked-in 文件为准（长跑
     deep research 需要 compaction 保护，这不是可选项）。
7. **UNVERIFIED 验证项**（入线前必须落实）：① ~~ask_clarification 在我们 run 里的处置~~
   **已关闭（2026-10-02 定案，处置设计见决策 8）**——事实查证：embedded 模式无禁用开关
   （原拟的两个选项「禁用可配置性/超时默认继续」均不存在于 embedded 路径）；② ~~Langfuse/tracing 在
   embedded 模式下是否可用~~ **已关闭（2026-10-02，digest+源码双证）**：可用——
   `client.stream()` 在图调用根注入 `build_tracing_callbacks()` + `inject_langfuse_metadata()`
   （client.py:933-942），`chat()` 包装 `stream()` 同覆盖；开启 = 环境变量
   `LANGFUSE_TRACING` + `LANGFUSE_PUBLIC_KEY/SECRET_KEY`，构造参数 `environment` 打
   env 标签，session_id=thread_id，`deerflow_trace_id` 恒写入；例外：Monocle 仅 Gateway
   lifespan 初始化，embedded 不覆盖。第一版不依赖，保持记录备查。
8. **ask_clarification 处置 = (a) harness 自动续答 + (c) prompt 减频**（2026-10-02
   用户定案；透明与质量两准绳同向选择）。事实底座（源码查证）：embedded 模式无法从工具
   集剔除该工具——剔除机制 `non_interactive` 是 Gateway 内部认证路径的 configurable 键，
   client 的 configurable 写死 5 键（client.py:282-294）；框架自带的抑制机制
   `disable_clarification`（转 proceed ToolMessage）是 runtime context 键，client kwargs
   白名单（8 个授权键）传不进；链尾 ClarificationMiddleware 无条件在位，调用时
   `Command(goto=END)`——本轮优雅终止、问题入 checkpoint、stream 正常走到 end。处置：
   - **(c) 第一道（减频）**：任务消息自带「非交互环境，不要请求澄清，按最佳判断继续并
     说明假设」；
   - **(a) 承重**：检测谓词为纯函数（stream 终态末条 AI 消息带未应答的 ask_clarification
     调用）→ 有界自动续答（同 thread_id 发续答轮，最多 N 次，N 初定 2）→ 续答消息带
     来源戳「[非交互模式·系统自动应答] …」（框架 provenance 纪律，回放永远诚实）→
     耗尽 → fail-loud 终态，**未回答的问题原文保留进 bundle**；
   - **检测机器复用**：同一套「读 stream 终态判原因」能力承担 stop_reason 识别
     （token_capped/loop_capped/model_length_capped）——wiring 层的通用观察底座；
   - **联动**：状态机转移（auto_proceed 有界、耗尽终态）落 bundle-contract plan 决策 2；
     watch 把续答轮呈现为显式事件（透明准绳）；
   - **弃选 (b)**（#32 槽中间件抑制）：机制埋进框架 hook 隐式语义（after_model 反序分发、
     混合批次丢兄弟调用），与透明/质量准绳相悖；将来工程化期可换路线，(a) 的检测机器
     不白写。

## 风险 / 取舍

- [deerflow.* 无 API 稳定性契约] → 契约镜像 + contract test + submodule 锁三重缓解；升级时
  测试红 = 有意识更新镜像。
- [撤 graph 层与治理预声明冲突] → 预留合同从未被用，撤除无既成现实可破坏；改动随本 plan 的
  change 一起走。
- [终态检测误判（漏检澄清 → run 假完成）] → 检测谓词纯函数 + 红绿测试钉死；journal 记录
  终态判定依据；status 面展示判定原因——误判本身可见（透明准绳）。

## 落地关联

成熟后**经用户拍板**入线（HITL 闸门）。change 候选：撤节点语法（治理小改）与 embedded 接线 +
契约镜像（产品首笔）可分可合，入线时定。接线首笔的红绿冒烟项：**embedded client + sync
SqliteSaver 跑通多轮对话且 `checkpoint.sqlite` 落盘可读**——当前证据 ~90% 指 sync 正确
（决策 1 修正注），此冒烟把剩余不确定性钉死（async saver + 同步 client 若意外可行也在此
实验中显形）。
