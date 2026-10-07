# Design

## Context

入口链现状（已通读六环源码核实）：`cli.py`(17 行纯转发) → `runtime/interaction/cli.py`
（六动词 presentation）→ `runtime/bundle/bundle_actions.py`（原子建 Bundle）→
`runtime/entry.py::run_foreground`（装配：`bundle_checkpointer` → `build_client` →
`make_stream_fn`）→ `run_engine.run_research`（消费流/计划闸/澄清/取消/终态）→
`bundle.admission.submit_artifact`（validator 先裁决）。链条散文分布于 README、control-map §4、
research-process、run-bundle、tests README 五处；`test_wiring_mirror` 只锁绑定面（构造参数/
事件族/defaults），`test_entry_composition` 用替身锁装配行为——链条组合关系本身零锁定。

- **已核实的现状事实**：`client.py:106` 写死 `available_skills=None`；
  `contracts/client_surface.py` 已把该参数登记为 mirror 的第十个构造参数（默认 None 是
  CONSUMED_DEFAULTS 的一部分）；config/base.yaml 与 fixture.yaml 无 skills 声明段。
- **已核实的消费面（写本设计后 grep 实测）**：entry.py 消费者 = interaction/cli.py、
  tools/record_stream.py、5 个 unit 测试、runtime/__init__.py docstring；run_engine.py 消费者
  = entry.py、interaction/cli.py、tools/record_stream.py、3 个 unit 测试、1 个 integration
  测试。并集 = **12 个外部消费者文件**（9 测试 + interaction/cli.py + runtime/__init__.py +
  record_stream.py），另加两改名文件自身与新增 chain-lock 测试。
- 2026-10-05 split change 确立的原则继续适用：目录为职责群而设，不为每个文件设；改名属
  单文件语义纠正，不建新子包。
- `make verify` 基线（写本设计后实测直测）：188 项 unit/contract 全绿，退出码 0；`make smoke`
  同轮实测：14 项全绿，退出码 0（注意 smoke 计数较历史归档的 9 项已涨——clarification/
  plan journey 已并入，改名零 test ID 变化的对照基数以实测 188 + 14 为准）。
  AST 可行性已探针验证：六环断言目标（含函数级懒 import 的 `submit_artifact`）
  在 stdlib `ast.walk` 下全部可见。Collection guard 核实：`tests/contract/` 已有包标记，
  新 contract 文件自动进入 verify 收集，无需改 guard。

## Goals / Non-Goals

**Goals:**

- 链条组合关系获得可执行权威：一个离线 contract 测试，断环/换 owner/改名漏切三种漂移必红。
- runtime 目录名直接承载链条词汇：`interaction/ → assembly.py → adapters/ → pump.py →
  bundle/`。
- skill 选择获得声明槽：config 声明、装配透传、默认 None 逐字节保持、guard 钉住。
- 文档从「第二套链条叙述」降为「指向锁链测试的路由」。

**Non-Goals:**

- 不激活 skill（认知变更，另立项走 node-agent 门）；不动 `.deer-flow/`；不做 rehearse 入口；
  不重排 tests/；不改六动词语义、domain/engine 规则、Bundle schema。

## Decisions

1. **锁链测试 = 断言调用签名，不锁行号**。实现形态：对链条各环源文件做 stdlib `ast`
   解析，断言（a）`cli.py` 仅委托 `interaction.cli.main`；（b）`cmd_create`/`cmd_refine`
   调用 `bundle_actions.start`/`refine` 与 `entrypoint.run_foreground`（改名后为
   `entrypoint` = assembly）；（c）`run_foreground` 函数体内出现 `bundle_checkpointer`、
   `build_client`、`make_stream_fn`、`run_engine.run_research`（改名后 `pump.run_research`）
   的调用名；（d）`_record_delivery`/`_submit_final_report` 路径上出现
   `submit_artifact`。每条断言失败信息命名断环。选 AST 而非 import 反射：contract 车道
   禁止 import interaction/cli（会连带 import run_engine，其中 `from .bundle...` 可 import，
   但保持零产品 import 更干净且与「行为保持性」场景一致——重构函数内部不误伤）。
2. **改名顺序在 chain-lock 之后**：锁链测试先落地并对现状绿，随后改名在同一 workstream
   内同步更新测试中的模块路径引用——改名后立即跑锁链测试 + 全量 verify，test ID 逐项
   相同即证明改名行为中性。`@impl DEW-001` 等标签随代码移动，不新增 ID。
3. **`assembly.py` / `pump.py` 命名**：`entry.py` 撞 entry-surface（spec 词汇），`run_engine.py`
   撞 `engine/` 裁决层。control-map 已用「运行泵」补救，`pump.py` 是把既成词汇落进代码；
   `assembly.py` 直述其装配职责（docstring 已自述 "foreground assembly"）。
4. **skill 槽走声明透传，不走激活**：config 增顶层 `skills:` 段（缺省 = 未声明），assembly
   解析后传 `build_client(available_skills=...)`；缺省解析结果严格为 `None`（不是 `[]`——
   两者在框架语义上可能不同，保持现状值最诚实）。guard 用 FakeClient 记录构造参数 +
   mirror 常量比对，零框架 import。激活语义另立项时只填槽，不动槽位合同。
5. **文档权威移交**：链条的机械权威 = 锁链测试；README 链条图保留一张（人读），control-map
   §4 从 11 步复述改为「链条六环 + 指向锁链测试」，research-process/run-bundle/tests README
   的链条叙述降为链接。不新增任何文档文件（受 doc-budgets 约束，control-map 在预算内
   瘦身）。

## Alternatives

- **只做锁链测试、不改名**（原最小方案）：被否——`entry.py`/`run_engine.py` 的词汇碰撞是
  「看不清」的机械成因之一，且消费者只增不减，拖后改名成本单调上升；用户明确要求长期
  正确优先。
- **把 interaction/ 提为顶层（与 runtime 平级）**：否——四层 ownership（runtime/domain/
  engine/agents）是 manifest 冻结的 canonical 集合，提层需 project-structure spec change，
  且 interaction 是 runtime 组合职责的一部分（六动词 delegation 属 presentation，不是独立
  ownership 层）；收益不抵治理面重开。
- **run_engine.py 并入子包 `runtime/pump/`**：否——单文件不建目录（2026-10-05 原则），
  平铺改名同样达成词汇目标。
- **skill 槽同时实现激活**：否——激活是认知变更（框架加载什么、质量如何、失败如何降级），
  需 node-agent 契约与真实梯证据；混入 wiring change 会把「声明面存在」与「激活有效」两个
  不同证据等级的问题搅在一起。
- **锁链测试用运行时 import 反射**：否——contract 车道 import 产品 CLI 会把 presentation
  模块拉进离线门禁的依赖图，且反射断言的是 import 成功而非调用关系；AST 直接断言调用
  签名，重构不误伤。

## Unresolved Questions

- `skills:` 声明段的确切 YAML 形态（list of names vs map with per-skill options）：apply
  期按「缺省解析必须严格为 None」约束定，形态本身不进 spec。
- 锁链测试对 `_submit_final_report` 懒 import 的断言粒度（函数级 vs 模块级）：apply 期以
  「断环必红、重构不误伤」双场景校准。
- control-map §4 瘦身后保留的最低叙述量：apply 期按 doc 预算与 doc-truthfulness 校准。
