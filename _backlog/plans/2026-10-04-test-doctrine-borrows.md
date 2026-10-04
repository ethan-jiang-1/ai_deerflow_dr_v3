# Plan: 测试战略采纳路线图（test-strategy adoption roadmap，v3 全量版）

> 类型: 设计 | 更新: 2026-10-04（v3 全量版：十篇 digest 全部消化后重写，取代同名 v1/v2 草案）
> 来源: digest `/Users/bowhead/deer-flow/_digest/test-strategy/`（940 行，10 篇）逐篇消化。
> 定位: 本卡是 v3 测试战略的**路线图与长期参照**——当前能补足的列了 change，将来能指导的列了触发条件。

## 一、总判断（消化后的结论）

DeerFlow 自测体系的一句话策略：**"离线确定性是默认，真实边界是显式 opt-in；测契约不测智能；每条架构规矩都有一个钉住它的测试；门禁自身也要被测试。"**

对照结论：**v3 的骨架与这套思想高度同源**（两边吃的是同一套 agent 测试教训），距离不在思想，在三层——机制件没建齐（本卡 Tier A）、纪律没挂钩成文（Tier B）、规模没到（Tier C 触发条件全部写明）。digest 最有价值的模式不是某段代码，而是三个"元姿势"：**每层显式声明自己不证明什么**；**执法者自己也要被测试**；**文档写了什么=交付物是什么，一致性由测试执行**。

## 二、采纳矩阵（digest 十域 × v3 现状，2026-10-04 全量盘点）

✓=已对齐（维持即可）｜🟡=部分（补齐项列明）｜✗=缺（Tier A/B 承载）｜⏸=规模门槛（触发条件写明）

| digest 域 | v3 现状 | 处置 |
|---|---|---|
| 00 全景地图 + 每层"不证明什么" | 🟡 lane 表有，缺"不证明什么"列与执行路由表 | **B2**：doctrine 文档已升级（本轮），路由表随后续 lane 增补 |
| 01 TDD 强制 + 红绿回执 | ✓ tasks 回执制度在案（两处偏离已披露） | 维持 |
| 01 offline-first 三分法 + live 三重门 | ✓ stdlib gate / smoke / real 梯三层；**缺：门策略自身的元测试** | **A6**（CI 执行预算一起） |
| 01 确定性纪律（事件不用 sleep、teardown 无泄漏） | ✓ temp dirs + addCleanup 全覆盖 | 维持 |
| 01 真一切只换模型 | ✓✓ smoke 即此形态（真 client/图/skill/checkpointer，只换模型） | 维持 |
| 01 no-unpinned-invariant（规矩有钉子测试） | 🟡 质量注册处有同步测试；AGENTS.md/doctrine 内容未钉 | **B2** |
| 01 scar-tissue（事故留疤） | ✓ error-fallback 守卫、澄清回声排除均由此而来 | 维持 |
| 01 设计文档自带 Testing Strategy（实现前成文） | 🟡 tasks 有红绿计划，无成文节 | **B1** |
| 01 docs-as-contract（文档=交付物） | ✗ COMMANDS/Makefile/cli 三处命令面无一致性测试 | **A4** |
| 02 替身阶梯级 1（剧本模型） | ✓ ScriptedChatModel（含 raise 动作、真图真中间件） | 维持 |
| 02 级 2 内容寻址录制回放 | ✗ 完全没有——**最贵证据（EASA 真跑）无法变永久 fixture** | **A1+A2**（最大借鉴项） |
| 02 归一化纪律 + miss 响亮清单 | ✗（随 A2 落地；我们已有同族解法：fallback 标记守卫） | A2 |
| 03 反 fake-green（真录制×真栈） | 🟡 smoke 是真栈+剧本；无真录制回放 | A1/A2 覆盖 |
| 03 真 SDK payload 钉住 | ✗ stream kwargs 的 per-call 语义刚踩坑（recursion 链） | **A3** |
| 03 跨语言契约 JSON / 跨栈 Playwright | n/a（无前端） | ⏸ 有前端时 |
| 04 部署配置即测试 | ✓ .gitignore/ignored_paths、requirement_ids 等已由 checker 钉住 | 维持 |
| 04 import 防火墙（AST 扫描） | ✓ architecture checker 的 import.external/boundary 同机制 | 维持 |
| 04 CI pinning CI（工具链版本=被测契约） | 🟡 openspec CLI 钉住了；**uv 版本与 uv.lock 的一致性没有钉**（delta patch 警告正是版本漂移症状） | **A6** |
| 04 AGENTS.md 治理（预算+结构+被测试） | ✗ 无预算/结构门禁（我们只有 4 个 AGENTS.md，规模未到） | ⏸ 文件数/预算超限时 |
| 04 豁免清单信任边界（不能自授权） | ✓ 无豁免机制即无此问题；将来引入时按 digest 先例设计 | ⏸ |
| 04 "evidence over a green check" | ✗ 哲学未成文 | **B5** |
| 05 时长基线分片 | ✗ 90 测试未到规模 | ⏸ 测试 >500 |
| 05 collection 也是回归面 | ✓ 我们的 gate 本身就跑发现+收集（import 断裂=红） | 维持 |
| 05 单测入口文档化（单文件/单函数命令承诺） | ✗ COMMANDS.md 无单测命令 | **B4**（并入 A4） |
| 07 崩溃模拟离线习语（不杀进程） | 🟡 死子进程+直构状态在用；"同 store 重建 as-if-restarted"未成文 | **B3** |
| 07 竞态显式成测（窗口期竞态单独成测） | ✓ CAS 冲突用例即此（scan/claim 竞态同型） | 维持 |
| 07 唯一活跃约束做最后防线 | 🟡 CAS 是我们的对应物；DB 级唯一约束暂无（单写者模型） | 维持（多写者出现时再议） |
| 07 追加式事件日志=历史重建真理源 | ✓ journal 即此（#3352 同型守卫=我们的回放 fixture） | 维持 |
| 08 技能测试面（四测试面+SkillScan+waiver 信任边界） | ✗ 完全没接——技能定制的前置机制 | **A5'**（第二把借鉴，独立 change） |
| 08 迁移契约（逐 revision 回滚契约） | ⏸ state schema v2 出现时 | 触发条件写明 |
| 09 dev 依赖治理（每个测试依赖带"为什么在这"） | ✗ dev 组 pytest/ruff 无 why-注释 | **B4** |
| 09 无覆盖率门禁的取舍 | ✓ 同立场（结构性门禁优于代理指标）——**但理由未成文** | **B5** |
| 09 CI 执行预算（concurrency 取消 + timeout 成文） | ✗ workflow 无 concurrency/timeout——新 smoke lane 可能挂死 CI | **A6** |
| 09 跨平台精确 skip（镜像生产守卫） | ✓ smoke 的 skipUnless 镜像 config 解析 | 维持 |
| 09 静态发现→运行时证明的工作流 | 🟡 在用未成文（扁平 chunk 的发现→守卫即此循环） | **B5** |

## 三、落地路线（Tier A/B 每件一 change 或合并，全管道；Tier C 只记触发条件）

### Tier A——机制件（红绿先行，真跑复验）

| # | change | 内容 | 证据 |
|---|---|---|---|
| **A6** | `harden-ci-budget`（小，先行——保护后续所有 CI 时间） | governance.yml 加 `concurrency`（按 PR 取消旧 run）与 `timeout-minutes`；`check_ci_governance` markers 同步；gov fixture 同步 | trio 绿 + closeout 0 |
| **A4** | `pin-command-surface`（小） | docs-as-contract 守卫：COMMANDS.md 提及的 make targets 必须存在于 Makefile、cli.py 子命令必须在 COMMANDS.md 登记（双向） | 单测红绿：删一个 target→红；补 B4 单测命令进 COMMANDS.md |
| **A5** | `guard-unit-lane-network`（小，digest 自评缺口 #1 的预防性补齐） | unit gate 结构性禁外联：socket guard（unittest 基类/conftest 级），负例控制（故意联网→红） | 单测红绿 + verify 仍 0 |
| **A1** | `add-replay-model`（最重） | 内容寻址回放模型（caller+归一化输入哈希、system prompt 剔键、miss 响亮清单）+ EASA 简报真跑录制 + 回放断言（报告落位/澄清/fallback 全在真实形状上回归） | 单测红绿 + 录制/回放双真跑 |
| **A5'** | `adopt-skill-review-surface`（第二把借鉴，独立） | 技能测试面最小借鉴：定制技能落位→确定性 review（零 LLM analyzer）→waiver 边界先例；服务"拎出 deep-research 换名换 trigger" | review 冒烟红绿 |

### Tier B——纪律挂钩（文档/约定/轻测试，可两把合并）

- **B2** doctrine 文档钉住（lane 表 targets ↔ Makefile 一致性、守卫清单 ↔ machines.py 一致性——后者已有，前者随 A4 顺带）。
- **B1** change 指导补"Testing Strategy 实现前成文"条（进 change-guidance 或 proposal 模板约定）。
- **B4** dev 依赖 why-注释（pyproject dev 组）。
- **B5** doctrine 补三段哲学：evidence over a green check；无覆盖率门禁的取舍理由；静态发现→运行时证明的工作流命名。
- **B3** as-if-restarted 习语成文进 doctrine（崩溃模拟不杀进程）。

### Tier C——规模门槛（触发条件写明，届时按证据启动）

| 项 | 触发条件 |
|---|---|
| 时长基线分片 | 单元测试数 >500 或 gate 时长 >3 分钟 |
| 迁移契约（逐 revision 回滚） | state schema 升 v2 |
| AGENTS.md 预算治理 | 指令文件 >8 个或单文件超 32KB |
| 跨栈契约 JSON / Playwright | 出现前端 |
| 行为断言 eval 栈 | 需要断言"研究质量"本身时（real 梯多次之后） |
| 集成真服务（Postgres/Redis 语义） | 持久化后端多样化时 |

## 四、演变指导（将来如何使用这张图）

1. **每个新 feature 的 change**：proposal 的 Evidence seam 回答"哪个 lane 证明它"；设计工件带 Testing Strategy 节（B1 生效后成文）；新守卫负例控制是硬要求（已有纪律）。
2. **每次真实事故**：按 scar-tissue 循环——发现 → 人工评审 → runtime anchor/守卫 → 变异验证（红→绿）→ 质量注册处登记。
3. **规模增长时**：Tier C 按触发条件启动，触发前不预支复杂度。
4. **框架升级时**：契约镜像 + stream 缝镜像（A3 后）先红，再有意识更新——digest 的 uv-pinning 案例就是我们的镜子。

## 风险 / 取舍

- [借鉴过度超前于规模] → 每件都有真实触发事件（扁平 chunk、recursion 链、命令面三处、digest 自评缺口）；Tier C 全部带触发条件。
- [纪律文档腐化] → A4/B2 把"文档说的"钉进测试——文档漂移即红。
- [digest 基线漂移] → 引用带路径与版本锚（fb6334b2），上游演进走 _upstream-sync。

## 落地关联

执行顺序：A6 → A4 → A5 → A1（最重）→ A2 → A5' → B 类合并收尾。每把 archive 后在本卡登记；全部完成后本 plan 关闭（CLS-010），doctrine 文档同步最终态。
