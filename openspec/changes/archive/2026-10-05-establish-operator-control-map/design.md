# Design

## Context

现状四份文档的角色重叠：`repository-map.md`（目录树 + owner→证据路由表）、
`runtime-map.md`（336 行：主链结论、三层职责、11 步 create 路径、Bundle 内容、
易误解动作、配置两梯、发布形态、质量车道、改动路由、结构问题）、
`runtime-architecture.md`（21 行边界摘要，change-guidance 的 focused doc）、
`research-process.md`（skill/绑定/证据，结构良好）。治理面硬约束：
`check_doc_hygiene.py` 的 DOC_LAYER_DOCS 与 STALE_MARKER_FILES 闭集注册表
（docs 层每个 `*.md` 必须登记、每个登记必须存在）；`check_change_guidance.py`
的 FOCUSED_DOC_PATHS（focused doc 必须存在，应用 README 与 docs 索引必须链接）
与 INFORMATION_MAP_POLICY_ANCHORS（local policy 必须含文档名锚点）；
`AGENTS.md` 字符预算 6863/6863 正好顶线（棘轮只降不升）；
`test_project_gate.py` fixture 源表复制 runtime-architecture.md。文档无行数预算
（Line Budgets 只覆盖 AGENTS/CLAUDE/config.yaml/product README）。

2026-10-05 计划 Phase 1 完成判据：新 Agent 只读 README、控制地图和 tests/README
能找到 create、run loop、skill 证据、Bundle 状态和最小测试；链接检查通过；文档
不引入第二套业务规则。

## Goals / Non-Goals

**Goals:**

- 一份唯一总图（control-map）+ 一份 Bundle 持久化合同图（run-bundle）；其余文档
  首段声明专门角色并指回。
- 两种 loop 的职责表显性化（驱动者/决定什么/不决定什么/代码入口/证据）。
- skill 三列状态（声明/实际加载/质量）与"未实现清单"成文。
- 全部注册表与路由面同步，所有门禁绿；AGENTS 预算棘轮净负下调。
- 429 行三旧文档 + 95 行 research-process 的有效内容零丢失（按映射表逐节核对）。

**Non-Goals:**

- 不移动任何 `src/` 或 `tests/` 文件；不改六动词、命令、准入或任何 spec 语义。
- 不新增 proof lane、不改 verify/smoke 收集。
- 不重写 tests/README（Phase 3）。
- 不留旧文档的指针残壳（登记成本与复活风险都高于收益）。

## Decisions

1. **单图原则**。control-map.md 是唯一"总图"；run-bundle/research-process/
   testing-and-evaluation/local-operations 各自第一段声明专门角色并链接
   control-map。四图争总图的根因是 runtime-map 与 repository-map 职责界线不清，
   合并后由注册表与索引行状态描述固化分工。

2. **内容映射表（防丢失的核对依据）**：

   | 旧内容 | 去向 |
   | --- | --- |
   | runtime-map §1 先给结论 + spine 图 | control-map §1（压缩） |
   | runtime-map §2 三层职责 + coding agent 定位 + agents/ 空层 | control-map §3 |
   | runtime-map §3 11 步 create 路径 | control-map §4（压缩注释） |
   | runtime-map §3 Run Bundle 保存什么 | run-bundle §artifact 权属表 |
   | runtime-map §3 易误解动作 | control-map §5（六动词语义表） |
   | runtime-map §4 配置两梯 | control-map §6（压缩；配置细节仍归 research-process/local-operations） |
   | runtime-map §5 发布形态/冷启动/未实现清单 | control-map §9（压缩；§5.3 未来清单只保留一句话指向计划） |
   | runtime-map §6 质量车道表 + 三种对象 + 最小车道选择 | testing-and-evaluation（lane 表补冷启动行 + 三对象 + 选择图） |
   | runtime-map §7 改什么找哪里 | 并入 control-map §7 路由表 |
   | runtime-map §8 结构问题 | durable 部分进 control-map §2（workflow 词义三分）与 §9（单机非服务）；refine 决策状态保留原样引用 |
   | repository-map 目录树 + owner 表 + 按问题继续读 + 同轮维护 | control-map §3 树 + §7 表 + §10 + 尾注 |
   | runtime-architecture 全部（边界图、harness 保留清单、权威 spec 指针） | control-map §2 与 §8 |
   | research-process 的 Bundle 内对象表 | run-bundle 权属表（research-process 保留"判断 skill/委派/完成/质量"的操作指引并指链） |

3. **两种 loop 职责表（核心新增）**：列 = 驱动者 / 决定什么 / 不决定什么 / 代码
   入口 / 运行证据；行 = DeerFlow 宿主 agent loop、Harness run loop。表后紧跟
   四行不等式：agent stream 结束 ≠ state completed ≠ final admitted ≠ 研究
   质量达标（现有 run_engine 先写 terminal 再提交报告）。

4. **focused doc 更名而非扩张**：FOCUSED_DOC_PATHS 只把 runtime-architecture.md
   换成 control-map.md；run-bundle/research-process 不进 focused 集（应用 README
   与索引仍按惯例链接）。理由：focused 集是机器强制的最小核心面，扩张是治理
   面加宽，不属于本 change 的归并目的。

5. **AGENTS 预算净负 + 棘轮下调**：Information Map 两行合并改写（Repo map /
   Runtime map 两行 → Control map 一行 + Run bundle 一行的等价压缩），实测后把
   DOC_BUDGETS 的 6863 下调至新值。降棘轮是 ordinary edit，不需要 justification。

6. **红先行顺序**：新文档先落盘、注册表未更新 → `check_doc_hygiene.py` 必须红
   （unregistered docs-layer markdown，规则 4 已有自测负例）；随后注册表更新 →
   绿。这证明本 change 的注册表编辑是承重的，不是装饰。

7. **删除而非指针壳**：三份旧文档物理删除（git 历史保留可追溯）。一个只说"我
   搬走了"的 markdown 仍要过 docs-layer 注册、编码、marker 检查，且天然复活
   第二入口。

8. **markers 纪律**：新文档不得含 STALE_MARKERS（"骨架期"、"(skeleton)" 等）；
   "未实现"表述用"当前代码没有实现……"句式（runtime-map §5.2 先例），不是
   占位 marker。

## Risks / Trade-offs

- [429 行压缩到约 330 行丢失操作者价值] → 映射表逐节核对；链接与门禁兜底；
  git 历史可回查旧文。
- [引用面广，改漏链接] → 勘察已列出全部引用点（AGENTS×2、docs 索引×3、应用
  README×3、根 README×2、policy×1、checker×3、测试 fixture×1、旧文档互引）；
  doc hygiene 链接规则 + change-guidance focused 链机器验证。
- [AGENTS 编辑超 6863 顶线] → 净负改写；实测后下调棘轮；超线即 hygiene 红。
- [control-map 自己长成第二事实源] → 每节只保留路由 + 一句话事实声明；具体
  规则链接 owning code/spec；authority-and-projections 纪律约束。
- [删除后有人按旧路径深链进来] → git 历史可查；根/应用/AGENTS/索引四路由面
  同轮更新；无外部消费者（已 grep 验证 tests/COMMANDS/playbook 无引用）。
- [自测 fixture 名仍指旧文档名] → self-test 的 bad-bytes fixture 同步改名为
  control-map.md，保持语义一致。

## Migration Plan

一次前向切换，无运行时状态：

1. 新文档落盘（红证：未注册 → hygiene 红）；
2. 注册表与 fixture 名更新（hygiene 绿，此时新旧并存）；
3. research-process/testing-and-evaluation 定点补强；
4. 四路由面 + policy 行更新（AGENTS 净负 + 棘轮下调）；
5. 删除三份旧文档；全套门禁 + make verify 绿；
6. closeout 回执（新鲜、直测退出码、逐文件 digest）。

回滚：revert 提交即可恢复三份旧文档与全部注册表；无数据、无 schema、无上游
接触。

## Open Questions

无实质未决项。旧 runtime-map §5.3 的"未来发布前补齐清单"压缩为指向 2026-10-05
计划的一句话——若后续需要独立发布路线文档，属另行立项。
