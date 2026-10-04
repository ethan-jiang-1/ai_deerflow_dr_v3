# v2 Harness 应用骨架全貌（非 Bundle 部分）

> 类型: 外部系统分析（消化材料） | 基线: /Users/bowhead/ai_deerflow_deep_research_v2（v2 参考仓库，只读） | 更新: 2026-10-02
>
> 来源：直接阅读 v2 仓库（只读）。本材料覆盖 v2 **应用骨架**（分层 / 静态图节点 / 入口面 / runbooks）——
> Bundle 内部实现由另一份材料覆盖（v2-run-bundle-implementation.md，调查中）。所有事实带源路径；
> 判断单独标注。

## 1. 分层结构（v3 骨架的祖先）

```
deep_research_harness/src/deerflow_deep_research/
├── agents/  domain/  engine/  graph/  runtime/   ← 五层：v3 骨架原样继承
├── resources/                                    ← v3 骨架【未】照搬（推敲议题：有意扔还是未到）
└── tool.py                                       ← v3 骨架【未】照搬（同上）
```

证据：`ls /Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/src/deerflow_deep_research/`；
v3 对照 `openspec/governance/required-paths.toml` 的 source-root 清单（五层，无 resources/tool.py）。

## 2. 静态研究图节点全貌（v2 范式：手搓 StateGraph 逐节点流水线）

12 个节点（`src/deerflow_deep_research/graph/nodes/`，每行 docstring 原文首行）：

| 节点 | 职责（docstring 首行原文） |
|------|------------------------------|
| `bootstrap` | Real bootstrap node factory. |
| `topic_planning` | Real topic planning node. |
| `wave0` | Real Wave0 source-intake node. |
| `wave1` | Real Wave1 evidence extraction node. |
| `wave2_synthesis` | Real Wave2 synthesis node — cross-topic synthesis from accepted evidence. |
| `targeted_evidence` | Real targeted_evidence node — critic dispatch + gap worker fan-out. |
| `hitl1` | Real HITL1 structured-profile node. |
| `hitl2` | Real HITL2 autonomous decision node. |
| `readiness` | Real readiness node — hard checks, critic, report plan, route determination. |
| `rerun` | Real rerun node — scoped invalidation, generation increment, back-edge routing. |
| `final_delivery` | Real bounded final-delivery composition and publication handoff. |
| `gate_adapter.py` | Thin adapter so the graph layer can invoke gate evaluation without importing …（验收收口 = 图上一个适配点） |

流程骨架（据节点名与职责推断的顺序，**判断**）：bootstrap → topic_planning → wave0/1/2
（源摄入→证据抽取→跨题综合）+ targeted_evidence（critic 派发 + gap worker 扇出）→ hitl1/hitl2
（两段人机交互）→ readiness（硬检查+路由）→ rerun（范围化失效+回边）→ final_delivery。

## 3. 入口面：「操作剧场」形态

来源：`deep_research_harness/COMMANDS.md`（读至 L70；该文件自称「索引非权威——权威是 Makefile
与 runbooks」）+ `docs/runbooks/` 目录清单。**注意本节只覆盖已读范围**，完整阶梯以 v2 原文为准。

### 两条凭证路线（互斥，COMMANDS 明文「别混」）

| 路线 | 适用目标 | 凭证 |
|------|---------|------|
| **embedded / soft-bundle**（001~004、010、020、031 等，不带 `PROFILE=`） | CLI/TUI 全部内嵌跑法 | harness 侧 `.env` 三要素（模型 selector + 模型 key + TAVILY_API_KEY） |
| **Gateway 观察**（仅 `demo-real PROFILE=` / `demo-tui PROFILE=` 两个目标） | 起真实框架 Gateway 做观察 | profile 体系：`make profile-setup`（装 sibling 框架）→ `profile-init` → `profile-dev`；observer 门含 JSON enhanced logging |

### 跑法阶梯（命名轴：001~004 CLI 全自动；01x 自动简化 / 02x 手动）

001 fixture 图 smoke（零凭证）→ 002 scripted 真实链路 → 003/004 真实全自动（两级意图）→
010 TUI 自动全跑 → 020 TUI 手动 HITL1；另有 TUI fixture 预演、嵌入式校准裸入口、调试工作台
（030/031：节点边界 step/continue + `--attach`/`--replay`，经 lifecycle 校验）。

soft-bundle CLI 子命令族（12 个）：create / run / bind / clean / verify / status / path /
inspect / phases / list / workspace-report / workspace-clean。

### Runbook 体系

`docs/runbooks/`：README + 001/002/003/004/010/020/030/031 各一份（每级阶梯一份操作单）。

## 4. 对 v3 的含义（判断，非事实）

1. **「可观察可操作」在 v2 是重资产**：两条凭证路线 + 12 个 CLI 子命令 + TUI 三形态 + 调试工作台
   + 9 份 runbook。v3 的 Q1 把「可观察可操作」列为「留」项——v2 的实际形态提示 v3 第一版必须
   **决定要多薄**；这可能是独立的一份衍生 plan（入口面阶梯）。
2. **v3 骨架未照搬 `resources/` 与 `tool.py`**：起骨架时的取舍未记录在案（当时无决策记录纪律）。
   推敲议题：有意扔（补理由）还是未到（补规划）。
3. **验收收口在 v2 是图上的 `gate_adapter`**：支持我们 Q2 (c) 答案的「admission owner 在外层图」，
   但 v2 形态是「节点内适配器」——v3 的收口形态（图节点 / 独立模块 / 边）待与 v2 Bundle 材料
   对照后裁决。
4. **HITL 两个节点（hitl1/hitl2）是 v2 的一等公民**：v3 的 Q1 答案里没有显式提 HITL——推敲议题：
   v3 的 run 生命周期（start/resume/status/cancel/refine）要不要为 HITL 留一等位置（框架侧有
   ask_clarification 内建工具，形态会不同）。
