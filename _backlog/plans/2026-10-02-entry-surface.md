# Plan: 入口面（entry-surface）

> 类型: 设计 | 更新: 2026-10-02 | 来源: digest 边界 plan 六裁决推敲（裁决 #4 + debugger 硬需求）

## 背景 / 现状

裁决：**最小 CLI**——五子命令承载生命周期动作与观察面（refine 的 CLI 入口待裁决，见
打磨线索①）。**debugger 为用户一级硬需求**（v2 之痛：
可调试性糟糕 → 工具堆失控；v3 必须根治）。元原则：v2 剧场（12 子命令/TUI 三形态/调试工作台/
9 runbook/双凭证路线）整体不抄——阶梯概念留精神、砍厚度。证据底座：
`_reference/v2-harness-app-shape.md`（剧场全貌）、`deerflow-runtime-and-persistence.md` §5
（事件清单）。项目级准绳（透明可见优先 / 交付质量给非 AI 接手者 / QC 研究定位）见
wiring plan 背景节，先序于本 plan 一切裁决。

## 决策 / 方案

1. **五子命令 CLI**（工具入口形态随 change 细化——`python -m` 或独立脚本）：
   - `create "研究问题…"` → 建 Bundle + 发起（wiring plan 的 embedded client）
   - `status <id>` → 状态 + journal 摘要
   - `watch <id>` → **直播渲染器**（见下）
   - `cancel <id>`
   - `inspect <id>` → 验收后看报告/证据/**全程回放**
   外加 make 环境目标（install/verify/fixture 演跑）。
2. **watch = 渲染器，不是调试器**：消费 stream 事件流（messages-tuple 的 token/工具调用、
   custom 的 subagent 生命周期、values 快照、end 用量）三消费者设计之一；**默认人话摘要，
   `--verbose` 切原始事件**。单向观察（HITL 暂缓，与 6/6 裁决自洽）。
3. **inspect 的两层事后排障**：journal 时间线（谁何时 admit/reject）+ **checkpoint 全程回放**
   （从 checkpoint.sqlite 重渲染完整消息历史/工具调用——debugger 硬需求的第三层）。
4. **两级阶梯**：fixture 演跑（零凭证，provider 替换）→ real 跑；不做 001-031 八级。
5. **验收标准（硬需求落条款）**：三层观察（watch 直播/journal 时间线/checkpoint 回放）
   第一天全部可用且好用——每层的红绿测试 + 一次真实排障演练作为 closeout 证据。

## 风险 / 取舍

- [渲染器的实时性] → stream 天生直播（B 线事实），渲染器是纯展示组件，复杂度低；
  性能风险可忽略。
- [checkpoint 回放依赖框架格式] → 与 bundle-contract 的 fail-loud 语义共用；回放失败
  如实报，不静默。

## 打磨线索（2026-10-02 系统审计登记，随本 plan 打磨轮逐个过）

① **refine 的 CLI 入口裁决**：bundle-contract 决策 2 的 v1 动作集含 refine，本 plan 五子
命令无其入口——补第六子命令/参数形态，或明确 v1 状态机支持而 CLI 延后（后者须答
「谁触发」）。
② **watch 对齐**：消费 wiring 决策 8 的续答轮显式事件；「三消费者」定义对齐 wiring
决策 1（watch 是其一）。
③ **inspect 回放复用内建机器**：`client.get_thread()` / `CheckpointStateAccessor` 已
提供 checkpoint 历史量化 + 消息序列化——不自造 sqlite 解析；RT2/RT7 影像盲区裁决联动
bundle 打磨线索②（回放重建得了对话、重建不了「模型当时看到什么」）。
④ **两级阶梯落地形态** = wiring 决策 6 的 checked-in fixture config（`use:` 类路径缝，
零凭证跑完整真实 client 链路）。
⑤ **EV2 负例控制机制级化**：验收条款（决策 5）的「红绿测试」落为「引入违规→看红→还原
→看绿并记录」+ gate smoke 元测试形态（「从不红的守卫≈不存在」）。
⑥ **inspect 质量报告面**（联动 bundle 打磨线索③）：一页「验收结论 + 证据链」人话呈现，
交付给不懂 AI 的接手人。

## 落地关联

成熟后**经用户拍板**入线（HITL 闸门）。依赖 wiring-structure（client 封装）与
bundle-contract（journal/checkpoint）先定合同；CLI 壳本身薄，随其后。
