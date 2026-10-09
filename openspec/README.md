# Deep Research OpenSpec

## Reading Map

- [config.yaml](config.yaml) is the native authoring context and operation route.
- [specs/](specs/) holds approved capability behavior; [changes/](changes/) holds
  proposed deltas currently under development, and completed changes live under
  `changes/archive/`.
- [Deep Research product context](product/README.md) is the concise reading
  map for product-specific orientation; it routes detail to its existing owners.
- [Change Guidance](change-guidance/README.md) routes local design and admission
  policies without becoming runtime authority.
- [Governance](governance/README.md) owns project registries, deterministic
  checkers, and the bounded closeout-evidence command.

## 开发闭环（一页走通）

一笔变更从意图到归位按序六步；本页只路由，正文留在各 owner：

1. **意图** — 分析与设计推敲进 [_backlog/issues/](../_backlog/README.md)；「决策/方案」
   与「落地关联」填实即毕业（能写出一张 [Change Focus](change-guidance/core/change-practice.md)）。
2. **权威归属** — 按 [Policy Route](change-guidance/README.md) 选齐触发的 canonical
   policy；应用面 owner 看 [app 指南 Information Map](../deep_research_harness/AGENTS.md)；
   精确路径只认 project-structure manifest。
3. **slice 交付** — propose 停在拍板边界（规范语义由人裁决）；红绿测试先行；
   实现与文档随 owning slice 同落。
4. **证据分层** — 按问题选最小车道，别从最贵的证据起步；见下节"四件不同的事"。
5. **验证形态** — `make verify`（应用单元门禁）/ `make smoke`（集成，需 `uv sync`）/
   [治理 checker 序列](governance/README.md)；退出码一律直测——管道会吞掉真实结果。
6. **交付记录与归位** — 回执（runner 写下命令/退出码/revision）+ [closeout 义务](governance/selected-change-closeout.md)
   → `openspec archive` → 知识归位（specs/ 主干、代码、测试、`_backlog` 回写）。

## 证据分层：四件不同的事

"单元绿"不是行为证据。四层各证其是，一层通过不代表下一层成立：

| 层 | 证明什么 | 不证明什么 |
|---|---|---|
| 离线单元与契约 mirror | 纯规则、接口镜像、收集合同 | 真实框架组合行为 |
| 装配 smoke | 真框架组装与 CLI 全旅程（脚本模型） | 真实模型的研究质量 |
| 真实梯观察（显式 opt-in） | 真模型下的行为侧写 | 统计意义的质量结论 |
| 冷启动发布 | 全新环境按发布说明跑通 | 真实 API 质量、多用户服务 |

完整车道表、替身阶梯与各 lane 的"不证明什么"列：[testing-and-evaluation](../deep_research_harness/docs/testing-and-evaluation.md)。

## 门禁等级（读规则先问在哪层）

- **成文标准** — AGENTS.md、本页、车道表：靠评审与人执行，不是机器挡住；
- **机器门禁** — 治理 checker、closeout gate、CI canonical 序列：真的会红；
- **自我声明** — Change Focus 自报、回执的语义内容（checker 只验在场与结构）；
- **仓库外不可核实** — 远端 required-checks 配置等：仓库文件里查不到，别假设其存在。

> 该分级词汇是上游参考（DeerFlow 应用开发语料·卷二组织立场，钉定 v2.1.0）按本仓
> 实例化的综合，不是 DeerFlow 官方规定，也不替代任何 owning spec。

This map is navigation only. Exact project topology remains owned by the
project-structure manifest: `governance/project-structure.toml` (contract) and
`governance/required-paths.toml` (inventory).
