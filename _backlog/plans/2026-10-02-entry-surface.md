# Plan: 入口面（entry-surface）

> 类型: 设计 | 更新: 2026-10-02 | 来源: digest 边界 plan 六裁决推敲（裁决 #4 + debugger 硬需求）

## 背景 / 现状

裁决：**最小 CLI**——六子命令镜像状态机动作集与观察面（refine 入口 2026-10-02 定案
补齐，见决策 1）。**debugger 为用户一级硬需求**（v2 之痛：
可调试性糟糕 → 工具堆失控；v3 必须根治）。元原则：v2 剧场（12 子命令/TUI 三形态/调试工作台/
9 runbook/双凭证路线）整体不抄——阶梯概念留精神、砍厚度。证据底座：
`_reference/v2-harness-app-shape.md`（剧场全貌）、`deerflow-runtime-and-persistence.md` §5
（事件清单）。项目级准绳（透明可见优先 / 交付质量给非 AI 接手者 / QC 研究定位）见
wiring plan 背景节，先序于本 plan 一切裁决。

## 决策 / 方案

1. **六子命令 CLI**（2026-10-02 定案补 refine 入口，CLI 镜像状态机动作集；工具入口形态
   随 change 细化——`python -m` 或独立脚本；运行进程模型 = 前台单进程 + 文件交互，
   见决策 6）：
   - `create "研究问题…"` → 建 Bundle + **前台发起并默认本终端直播**（wiring plan 的
     embedded client，单泵三汇见决策 6）
   - `status <id>` → 状态 + journal 摘要 + **owner PID 活性检查**（PID 死而状态 active
     → failed-resume，fail-loud 不装活）
   - `watch <id>` → **journal tail 近实时渲染**（与 create 共享同一渲染器，数据源 =
     journal 投影；工具级粒度，人话摘要层无感）
   - `cancel <id>` → 写取消标记（状态机转移请求），create 进程的泵协作检查 → 优雅终止
     ——复用 v2 外部取消纪律
   - `refine <id> "方向文本"` → 同一 bundle generation+1 重跑（**一个动词一个动作**，
     可审计好学；实现倾向方向文本 + 同 thread 续跑——checkpoint 连续性让模型看得到
     上一代报告；generation 上限继承 v2 纪律，随 change 验证）
   - `inspect <id>` → 验收后看报告/证据/**全程回放**
   外加 make 环境目标（install/verify/fixture 演跑）。
2. **watch = 渲染器，不是调试器**：消费 stream 事件流（messages-tuple 的 token/工具调用、
   custom 的 subagent 生命周期、values 快照、end 用量）三消费者设计之一；**默认人话摘要，
   `--verbose` 切原始事件**。单向观察（HITL 暂缓，与 6/6 裁决自洽）。
3. **inspect 的事后三面（2026-10-02 补写关闭线索③⑥）**：journal 时间线（谁何时
   admit/reject）+ **checkpoint 全程回放**（复用 `client.get_thread()` /
   `CheckpointStateAccessor` 的 checkpoint 历史量化机器——不自造 sqlite 解析；配合
   bundle 装配快照可完整重建「模型当时看到什么」）+ **质量报告页**（一页「验收结论 +
   证据链」人话呈现——交付给不懂 AI 的接手人，QC 映射的「竣工资料移交」形态）。
4. **两级阶梯**：fixture 演跑（零凭证——落地形态 = wiring 决策 6 的 checked-in
   fixture config，`use:` 类路径缝换假模型/假 web_search，跑完整真实 client 链路，
   2026-10-02 关闭线索④）→ real 跑（base config）；不做 001-031 八级。
5. **验收标准（硬需求落条款；2026-10-02 EV2 机制级化，关闭线索⑤）**：三层观察
   （watch 直播/journal 时间线/checkpoint 回放）第一天全部可用且好用——closeout 证据
   两件套：① 每层红绿测试，且每个新守卫过一次**负例控制**（引入违规→看红→还原→看绿，
   记录在案——「从不红的守卫≈不存在」；gate smoke 元测试形态：一条测试专门证明 gate
   自己会拦，它不拦即 gate 坏）；② 一次真实排障演练，CI 化形态 = record/replay golden
   （录一次真实排障、永久零凭证回放，验形状漂移而非 volatile 值）。
6. **运行进程模型（2026-10-02 用户定案选项 A；关闭打磨线索⑦②）**：run 活在 create 的
   前台进程——**单泵三汇**（一次 stream 迭代分发三汇：本终端渲染 / journal 落账 / 终态
   检测——wiring「三消费者」在泵层原样成立）；`watch <id>` attach = journal tail（渲染器
   共享、数据源切换）；`cancel` = 状态标记 + 泵协作检查；崩溃检测 = owner PID 记入
   state.json（bundle plan）+ status 活性检查。**零新增传输机制**——journal 一个介质
   两用（直播载体 + 时间线，正是三层观察里 journal 的双重身份）；`nohup create &` +
   `watch <id>` 免费获得后台形态，不建后台 worker 路线。续答轮（wiring 决策 8）在两种
   数据源下都渲染为显式事件。弃选：后台 worker（进程管理新机器、发起终端失直播，违背
   透明准绳）、砍独立 watch attach（违背裁决 #4 的最小 CLI 形态）。

## 风险 / 取舍

- [渲染器的实时性] → stream 天生直播（B 线事实），渲染器是纯展示组件，复杂度低；
  性能风险可忽略。
- [checkpoint 回放依赖框架格式] → 与 bundle-contract 的 fail-loud 语义共用；回放失败
  如实报，不静默。

## 打磨线索（全部关闭，2026-10-02）

① ~~refine 的 CLI 入口~~ → 用户定案：第六子命令（见决策 1）。② ~~watch 对齐~~ →
随进程模型定案（见决策 6：渲染器共享双数据源，续答轮显式渲染）。③ ~~inspect 复用
内建机器~~ → 已并入决策 3（get_thread / CheckpointStateAccessor）。④ ~~两级阶梯落地
形态~~ → 已并入决策 4（指向 wiring 决策 6）。⑤ ~~EV2 机制级化~~ → 已并入决策 5
（负例控制 + gate smoke + replay golden）。⑥ ~~inspect 质量报告面~~ → 已并入决策 3
（事后三面）。⑦ ~~运行进程模型~~ → 用户定案选项 A（见决策 6）。

## 落地关联

成熟后**经用户拍板**入线（HITL 闸门）。依赖 wiring-structure（client 封装）与
bundle-contract（journal/checkpoint）先定合同；CLI 壳本身薄，随其后。
