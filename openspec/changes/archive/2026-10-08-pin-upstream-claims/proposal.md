# Proposal: Pin Upstream Claims

## Why

两处同病的钉定缺陷（plan C3，`_backlog/plans/2026-10-08-application-corpus-adoption.md`）：

1. **根 `AGENTS.md` 的 pin 等式失真**：第 8 行写"submodule 锁 `ceebf97f` = 上游
   v2.1.0"。实测 `git merge-base --is-ancestor 345f08be ceebf97f` 为真——`ceebf97f`
   是 v2.1.0（`345f08be`）的**后代**（digest 研究分支 `ethan-v2.1.0~1`），不是 tag
   本身。语料维护页的方法论（对上游论断必须钉定可核对）正是防这个病的，而我们的
   入口文件自己犯了。
2. **语料证据库活在仓外**：全部"上游参考"结论的证据源
   （DeerFlow 应用开发语料，三卷 19 页 + 维护层 + verify 脚本，38 文件 264K）住在
   机器本地路径 `/Users/bowhead/deer-flow/…`——fresh clone、换机器、未来会话都读
   不到，与本仓不变量"结论不得依赖某台机器的工作区现场"冲突。**裁决已做
   （2026-10-08，驾驭者选 A）**：原样复制进仓。

## What Changes

- **根 `AGENTS.md` 第 8 行 pin 等式修正**：改为表达"`ceebf97f` 是 v2.1.0 的后代
  （digest 研究分支），v2.1.0 为其祖先"的准确表述；净字符增量控制在现余量
  （2403/2425，+22）内，不动 `DOC_BUDGETS`，不 bump gitlink。
- **`_backlog/_reference/deerflow-application-corpus/` 原样复制语料**（38 文件，
  逐字不动——保住其自带 `verify.mjs` 的独立可验证性）；`_reference/README.md`
  目录表加一行 + 目录组织加一条，登记出处（源路径、钉定 `v2.1.0` = `345f08be`、
  复制日期）与**重审触发**（上游 re-pin 时重对语料 `_coverage` 的触发路径）。
- **`change-guidance/profiles/deerflow-downstream/deerflow-downstream.md` 补钉定
  纪律**：对上游（DeerFlow/任何 gitlink 依赖）的行为论断必须携带钉定引用
  （tag/commit）与核验方法；引用上游文档时默认其为发布时快照、以源码核验为准；
  gitlink 前进（re-pin）时重审全部在案上游论断。
- **同病排查结论**（实现期核实）：`project-structure.toml` 只声明裸 commit 无等式
  失真；`test_upstream_pin_agreement.py` 锁 toml↔gitlink 一致性、不涉及散文等式，
  均不需改。

## Capabilities

### New Capabilities

none: 事实修正、参考资料入库与指导纪律，无规范级行为变更。

### Modified Capabilities

none: doc-budgets 门槛不变（根 AGENTS 不超顶、预算表不动）；`skip_specs: true`
已声明。

## Impact

- 文件：`AGENTS.md`（一行内等价改写）、`_backlog/_reference/`（新增
  `deerflow-application-corpus/` 38 文件 + README.md 两处登记）、
  `openspec/change-guidance/profiles/deerflow-downstream/deerflow-downstream.md`
  （钉定纪律小节）。
- 既有守卫保持绿：doc-hygiene（入口链链接/预算/underscore 约定——嵌套
  `_coverage/` 已核验不触发只扫顶层的规则）、change-guidance、pin-agreement。
- `verify.mjs` 在复制品内可离线运行（本机 Node 22 在案），**不进 CI**——它是
  语料自身的结构自检，不是本仓守卫。
- 不触碰 `deerflow/` gitlink（既不修改也不深读；gitlink 证据照常记录）。

## Change Focus

- **Primary module / causal owner:** `AGENTS.md`（根入口，"submodule 锁什么"这一
  事实的散文 owner）与 `_backlog/_reference/`（外部参考资料 owner，`_backlog`
  README 约定在案）——钉定失真与证据库归所的最小 owner 组合。
- **Seam classification:** wiring — 事实修正、参考资料搬迁、指导纪律；无认知
  角色、无运行时状态、无准入语义。
- **Question:** 本仓对上游的每条论断是否钉定可核对（tag/commit + 核验方法），
  上游证据库是否活在仓内、换机器仍可复查？
- **Necessary adjacent/external contracts:** `check_doc_hygiene.py`（answers: 根
  AGENTS 字符预算 ≤2425 不涨、入口链链接解析、`_` 目录约定兼容）；`_backlog/
  README.md` 约定（answers: `_reference` 归属与索引格式，嵌套 `_coverage/` 相容
  ——underscore 规则只扫 `_backlog` 顶层，已核验源码）；C2 四类陈述规则
  （answers: 引用语料一律标"上游参考·卷·页·钉定 v2.1.0"，不冒充本仓要求）；
  `test_upstream_pin_agreement.py`（answers: toml↔gitlink 一致性不受散文修正影响）。
- **Evidence seam:** `git merge-base --is-ancestor` 取证记录（等式修正的依据）+
  复制品内 `node verify.mjs` 退出码 0 + doc-hygiene/change-guidance 退出码 0 +
  根 AGENTS 字符直测 ≤2425。
- **Not in scope:** gitlink 前进本身（只修等式与纪律，不 re-pin）；语料内容改写
  或删减（原样复制）；C6 产出质量；语料 verify 进 CI；上游文档快照问题的系统性
  修复（纪律先行，个案随各自 change 处理）。
- **Triggered review policies:** change-admission, local-context, deerflow-downstream-boundary
