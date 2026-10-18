# Proposal: retire-portable-export

## Why

父卡裁决 #4，本轮取证确认：`openspec/governance/portable_change_guidance_export.py`
（**140 行**，"Verify a digest-bound portable Change Guidance candidate"——把引导系统**导出给别的
项目**的候选包校验器）**没有任何调用者**：

| 可能的使用者 | 实测 |
|---|---|
| CI（`.github/workflows/*.yml`） | 零引用 |
| Makefile / `make verify` | 零引用 |
| `check_project_gate.py` 与七个 checker | 零引用 |
| 任何测试 | 零引用 |
| 仅有的引用 | 它自己的 `required-paths.toml` 登记 · `governance/README.md` 一行描述 · 父卡 · 一个归档 change 的历史 tasks |

也就是说：它**占着"必需路径"的名分、出现在治理组件清单里、却不为本仓任何检查提供服务**。
它的用途（把引导系统可移植地导出）属于**别的项目**，本仓没有这个需求。

## 本轮同时更正一条父卡判断（第 3 项：program/workstream 模式）

上一轮我在父卡里写"**没有任何真实 change 用过**"program/workstream 模式——**这是错的**。
本轮实测：`openspec/changes/archive/2026-10-07-surface-runtime-structure/proposal.md` **真的用过**
（`## Program Focus` + **三个** `### Workstream Focus:`：chain-lock / vocabulary-fix / skill-slot）。

按判定程序重新裁决，**改为保留**：

| 问题 | 证据 |
|---|---|
| 守护什么 | 一个**多工作流 program** 提案必须登记每个工作流（否则 program 与普通 change 无从区分） |
| 属产品还是装置 | 装置（提案形态）——但那不等于不必要 |
| 抓到过/用过真问题 | **被真实使用过一次**（上述 3 工作流 program） |
| 代价 | 约 **99 行**（6 个模块）+ config 3 行；**且未使用时零成本**——校验只在 `if program_count or workstream_count:` 时激活 |
| 可推导 | 不适用 |

**1 个真实用户 + 对非用户零成本 + 唯一的多工作流承载机制 ⇒ 必要，保留。**
（同时记一条**已知缺口**：该分支**没有电池控制**；它是被保留的能力而非待退役对象，缺口留在父卡跟踪。）

## What Changes

- **删除** `openspec/governance/portable_change_guidance_export.py`（140 行）。
- **删除**它在 `required-paths.toml` 的登记与 `governance/README.md` 的组件表行（**不留悬挂引用**）。
- **更新父卡**：第 4 项标记为已执行（写明理由：无调用者）；第 3 项由"退役候选"更正为**保留**
  （附更正的证据与那条已知缺口）——父卡是权威记录，错的地方必须改。

**不变量**：七个 checker + closeout gate + 治理套件全绿 · `--self-test` 契约不变 ·
**program/workstream 模式一点不动** · 其余治理组件一个不删 · 产品代码与 harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 删除一个未被调用的导出校验器，不改任何产品 requirement。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **删**：`portable_change_guidance_export.py`（140 行）· `required-paths.toml` 一行 ·
  `governance/README.md` 一行。
- **改**：父卡（裁决 #3 更正 + #4 执行）· `check_code_budgets.py`（若该文件在表内则删行；预期**下降**）·
  可能需同步 `test_split_manifest.py` 的清单 pin（它按 owner 分组钉 required-paths 内容）。
- **不动**：program/workstream 模式的任何代码、文档、config · 其余治理组件 · 产品代码。
- **触发车道**：治理套件（含架构 checker 的 required-paths 校验）· 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/portable_change_guidance_export.py` ——
  一个"必需路径"级别的治理组件，其唯一作用是服务**别的项目**的导出需求。
- **Seam classification:** deterministic-guardrail —— 组件退役；无模型参与。
- **Question:** 一个被登记为必需、却没有**任何**调用者的 140 行组件，能否连同它的登记与文档行一起
  退役而不留悬挂引用——而 program/workstream 模式（**有一个真实用户**）被有据地保留？
- **Necessary adjacent/external contracts:** `required-paths.toml` + 架构 checker 的存在性校验
  （answers: 删文件必须同时删登记，否则 checker 红）· `test_split_manifest.py` 的清单 pin
  （answers: 它钉 owner 分组的条目，可能需要同步）· `governance/README.md` 的组件表
  （answers: 文档行必须同步，否则文档指向已删文件）· 父卡（answers: 它是裁决的权威记录）。
- **Evidence seam:** 无调用者的取证（CI/Makefile/gate/checker/测试五处零引用）· 删除后架构 checker 与
  doc-hygiene 绿 · required-paths 无悬挂 · 治理套件 · 七 checker + closeout · 受管行数下降。
- **Not in scope:** program/workstream 模式的任何改动（**本轮判为保留**）· 给它补电池控制（记为已知
  缺口，另开一把）· 父卡其余裁决项（计数器表数量列 · suspend 面 · 毕业门/可关闭）· 产品代码。
- **Triggered review policies:** local-context, change-admission
