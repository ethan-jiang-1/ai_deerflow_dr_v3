# Plan: 三连击——报告落 final/、refine 轻装重启、集成 lane 进 CI（queued-triple)

> 类型: 设计 | 更新: 2026-10-04
> 执行方式: 一个 ongoing goal 顺序落三把 change，每把独立走全 OpenSpec 管道（plan→propose→红绿 apply 带证据回执→archive→账本→commit），静默推进、终态一次汇报。

## 背景 / 现状

v3 已真跑验证（EASA 深研究 gen-5 完成并产出实质简报）。三件挂账候选均有真实场景支撑：
① 简报还躺在 checkpoint 里，没走验收收口——QC 闭环（模型提议、代码裁决）没在真实
报告上转过一圈；② refine 同线程续跑在 209 条消息的重上下文上撞了五次上限才完成——
轻装重启是正路；③ 集成/旅程测试只在本地跑，CI 无依赖安装步。

## 决策 / 方案（三把 change 的次序与设计草案）

**第一把 `land-final-report`（QC 闭环收口，最优先）**
- run engine 在 run_completed 时把终答（末条 AI 消息全文）经 `submit_artifact`
  （kind=`final_report`，filename 按 generation 命名）走 hold point：validator 裁决 →
  ledger admit → 内容落位。admission 的落位规则补上既有声明（RUB-001："最终报告 →
  final/"）：final_report 类 admitted 内容路由到 `final/`（admission 模块落位处小改，
  spec 层 MODIFIED run-admission 的落位句 + MODIFIED deerflow-wiring 的终态需求加
  "engine submits the final answer through the hold point"）。
- 证据：单测（admitted final_report 落 final/、reject 不落）红绿 + 真跑复验
  （一个小真问题 → run completed → final/ 出现报告文件 + ledger admit 条目）。

**第二把 `refine-slim-restart`（轻装重启）**
- refine 语义升级：generation+1 时**换新 thread_id**，并把上一代的关键上下文以
  **结构化摘要**（已答内容要点 + 已收集材料清单 + 未决问题）写进
  `request/generation-N-context.md`，作为新一代的初始消息组成部分；旧 thread 保留在
  state.json 新字段 `prior_thread_ids`（可追溯，checkpoint 回放仍可达）。
- 证据：单测（新 thread、摘要文件、prior_thread_ids 记账、旧 checkpoint 不动）+
  真跑复验（对 EASA bundle refine → 新线程轻上下文一次完成简报，对照旧路径五次
  触顶）。
- 风险：摘要本身是确定性代码写的（材料清单/要点抽取自 checkpoint 消息的机械
  投影，不是模型生成）——不引入认知权威。

**第三把 `ci-integration-lane`（CI 接线）**
- `.github/workflows/governance.yml` 增 uv 安装步（astral-sh/setup-uv + 缓存
  deep_research_harness/uv.lock）+ `make smoke` 步；`check_ci_governance.py` 的
  声明同步（checker 钉死每条 CI 声明——加步必须同步 checker，CIG-001 符合性）。
- 证据：checker 本地绿 + --self-test；CI 真跑由 push 验证（本地只能声明一致性），
  如实标注 UNVERIFIED-until-push。

## 风险 / 取舍

- [三把串行的上下文消耗] → 每把独立小 change，前把失败不挡后把（账本各自记账）。
- [摘要质量决定新一代起点] → 摘要是机械投影（标题/工具结果计数/末答节选），
  宁可保守不可编造；模型自己会在新线程里决定怎么用。
- [CI 步与 checker 声明的耦合] → checker 的 self-test 先行红绿。

## 落地关联

三把 change 依次 `land-final-report` → `refine-slim-restart` → `ci-integration-lane`；
各自 archive 后本 plan 关闭（CLS-009）。
