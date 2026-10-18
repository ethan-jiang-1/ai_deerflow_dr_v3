# Proposal: anchor-public-api-contract

## Why

全仓**唯一**的测试 skip 一直挂着一条明确的激活条件（它的 skip 消息自己写着）：

> *harness contract test not established yet (v3 skeleton); the pin agreement activates when
> `test_deerflow_public_api.py` lands*

而账本 `2026-10-02-digest-deerflow-native-deep-research.md:73` 记着计划："harness 侧契约测试锚
（`test_deerflow_public_api.py` 模式）**随 change ④ 建立**——`test_upstream_pin_agreement` 已预留
激活点"。**锚没建立**，于是治理侧那条"声明锁 == 契约测试里的 `CURRENT_DEERFLOW_PIN`"的双锚一致
检查**一直没跑**。

**而且镜像早就在等它的测试**：`runtime/adapters/contracts/client_surface.py` 的 docstring 原文是
"**The contract test compares these declarations against the real framework surface**; a drift
fails naming the surface"——声明齐了（构造参数 10 项含 placement、四个事件族、values 载荷四字段、
消费的默认值、checkpointer seam、stream 的两个 kwarg），**比对者缺席**。

## What Changes

- **新增 `deep_research_harness/tests/contract/test_deerflow_public_api.py`**：
  - `CURRENT_DEERFLOW_PIN`（与结构 registry 的 `[upstream_gitlink] commit` 一致）——**这一行的存在
    就让治理侧那条检查激活**；
  - **镜像 vs 真身**（框架可用时）：构造参数**逐项逐序逐 placement 相等** · 事件族**相等** ·
    stream 接受每个被消费的 kwarg（含 `thread_id` 显式 / `recursion_limit` 走 `**kwargs` 的**区别**）·
    被继承的模型类仍是类 · checkpointer seam 两个成员都在；
  - **镜像 vs 我们自己的用法**（**不需要框架**）：被判定的默认值仍是那些字面量，且
    `available_skills` **保持透传而非硬编码**（镜像原话"never hard-coded here"）· 声明的 values 载荷
    字段在**真实录制**里都出现过（正向证据）。
- **把契约套件接进框架车道**：`make smoke` 目前只 discover `tests/integration`；补上 `tests/contract`
  ——否则那 5 条要真框架的检查**在 CI 里永远只 skip**（车道问题，不是测试问题）。
- **逐条如实标注可验证边界**：真身**没有**公开 state schema，故 `VALUES_PAYLOAD_FIELDS` 只能给
  **正向证据**（声明的字段在真实录制里出现过），**证不了完备性**——写进测试 docstring，不假装。

**不变量**：产品行为零改动（只加测试 + 车道）· 镜像文件不动 · 框架**只读**（契约测试只 import 与
`inspect`，从不改 `deerflow/`）· 治理侧与产品侧既有车道全绿 · 无框架环境下按既有 `_FRAMEWORK_AVAILABLE`
模式**跳过而非失败**（与仓内 integration 测试同姿态）。

## Capabilities

### New Capabilities

<!-- none: 建立一条既有计划中的契约锚，不改任何 requirement。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **新增**：`deep_research_harness/tests/contract/test_deerflow_public_api.py`。
- **改**：`deep_research_harness/Makefile` 的 `smoke` 车道（discover 补 `tests/contract`）。
- **不动**：`contracts/client_surface.py`（镜像）· 任何产品代码 · 治理侧 · 工作流（CI 只调 `make smoke`）。
- **触发车道**：`make verify`（2 条无框架用例在此实跑）· `make smoke`（7 条全跑）· 治理套件（那条 skip
  应归零）· 七 checker。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/contract/test_deerflow_public_api.py`
  —— 它拥有"应用声明的框架面 == 真身"这一判定；此前该判定**不存在**（只有镜像）。
- **Seam classification:** deterministic-guardrail —— 纯静态比对（`inspect` + AST + 录制），无模型参与。
- **Question:** 一份早已写好、并在 docstring 里点名要"被契约测试比对"的镜像，能否在不改框架、不改产品
  行为的前提下被真正比对——且**故意抽掉镜像里的一项会红**、而治理侧那条唯一的 skip **归零**？
- **Necessary adjacent/external contracts:** `contracts/client_surface.py`（answers: 镜像的六组声明，
  含那条"`setup` 是裸成员而非点号路径"的形状）· `test_upstream_pin_agreement`（answers: 它要的正则
  与路径，以及"文件存在即激活"的判据）· `make smoke`（answers: 唯一带框架的车道，故契约套件必须接进去）
  · `_FRAMEWORK_AVAILABLE` 惯用法（answers: 无框架时跳过而非失败）。
- **Evidence seam:** venv 里 7/7 通过 · 默认车道 2 跑 5 跳 · **变异**（抽掉镜像一项 ⇒ 红；改我方
  默认值 ⇒ 红）· 治理套件 skip **1 → 0** · `make verify` / `make smoke` / lint / 七 checker / closeout。
- **Not in scope:** 改 `deerflow/`（只读铁律）· 改镜像的声明内容 · 把 `tests/contract` 全量搬进 smoke
  车道（只补契约套件这一处，integration 车道不动）· 工作流文件 · `VALUES_PAYLOAD_FIELDS` 的完备性
  证明（真身无公开 schema，如实标注）。
- **Triggered review policies:** local-context, change-admission
