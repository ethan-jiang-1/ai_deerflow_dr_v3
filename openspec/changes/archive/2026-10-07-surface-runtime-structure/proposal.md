# Proposal: Surface Runtime Structure

## Why

入口链（cli.py → interaction → bundle → entry → client → run_engine → admission）目前只存在于
五份散文文档的重复叙述中（README/control-map/research-process/run-bundle/tests README 各讲一遍），
没有任何机器锁：链条换 owner、被绕过或文件改名都不会红。同时两个核心模块名在撒谎——
`entry.py` 不是入口（入口是 cli.py），它是装配；`run_engine.py` 与顶层 `engine/` 裁决层撞名，
实际是运行泵。这正是操作者与 coding agent「要探索半天才看清逻辑怎么串」的机械根源。
skill 绑定同样只有隐式事实：`available_skills=None` 写死在 client.py，没有声明面可下手。

## What Changes

- **新增锁链 contract 测试**（`tests/contract/test_entry_chain.py`，离线 stdlib，进 `make verify`）：
  用源码/AST 断言锁住入口链六环的调用关系（cli.py 只委托 interaction.cli.main；cmd_create/cmd_refine
  经 bundle_actions.start + entry.run_foreground；run_foreground 经 bundle_checkpointer/build_client/
  make_stream_fn/run_research；终态交付经 bundle.admission.submit_artifact）。锁调用签名，不锁行号。
- **词汇修正（模块改名，行为零变化）**：`runtime/entry.py` → `runtime/assembly.py`（消除与
  entry-surface 入口面的撞名）；`runtime/run_engine.py` → `runtime/pump.py`（消除与 `engine/`
  裁决层的撞名）。实测 12 个外部消费者文件（9 个测试文件 + `interaction/cli.py` +
  `runtime/__init__.py` docstring + `tools/record_stream.py`）直接 cutover，无兼容 shim；
  `@impl` 标签随代码移动。
- **skill 声明槽（声明面 only，激活不在范围）**：config（base/fixture.yaml）新增 skills 声明段，
  装配时经 `build_client` 传入 `available_skills`；**默认值保持 `None`（现行为不变）**，contract
  guard 钉住 declared-none 姿态。skill 激活语义（框架侧实际加载什么、质量如何）是认知变更，另立项。
- **文档瘦身**：链条的权威移交给锁链测试；control-map §4 等四处降为路由，不再各自复述链条全文。
- **manifest 登记**：`required-paths.toml` 增删对应路径（新测试文件、两个改名），架构 checker 保持绿。

## Capabilities

### New Capabilities

<!-- none: 全部落在既有 capability；结构改名走 manifest 登记协议，不改 spec 文本 -->

### Modified Capabilities

- `entry-surface`: 新增 requirement——create/refine 必须沿声明链路由，且链条由离线 contract
  测试机械锁定（链断即红）。
- `deerflow-wiring`: 新增 requirement——skill 选择是显式声明而非隐式写死：config 声明、装配传递、
  默认 none、guard 钉住；激活语义不在本 capability 承诺范围。

## Impact

- 新增：`deep_research_harness/tests/contract/test_entry_chain.py`。
- 改名（git mv + import cutover）：`src/deerflow_deep_research/runtime/entry.py` → `assembly.py`、
  `runtime/run_engine.py` → `pump.py`；消费者（实测 12 文件）= `runtime/interaction/cli.py`、
  `runtime/__init__.py` docstring、9 个测试文件（见 tasks 2.2/2.5 显式清单）、
  `tools/record_stream.py`。
- config：`config/base.yaml`、`config/fixture.yaml` 增 skills 声明段（默认空/none）；
  `runtime/adapters/client.py::build_client` 读声明传参。
- 文档：`docs/control-map.md` §4 瘦身为路由；README 链条图改为指向锁链测试；`tests/README.md`
  登记新资产。
- 登记：`openspec/governance/required-paths.toml`。
- 触发 lane：`make verify`（src/**、tests/** 变更）与 `make smoke`（interaction/assembly/pump
  变更）。
- **边界声明**：本 change 不修改、不深读 `deerflow/` gitlink；skill 声明槽只使用已在
  contract mirror 里登记的框架构造参数（`available_skills`），不需要新的上游边界授权。
  所述行为均为本 change 范围（proposed scope），非现状。

## Program Focus

- **Program outcome:** 操作者与 coding agent 从目录名 + 一张图 + 一条会红的锁链测试即可重建
  「逻辑怎么串」的全貌；入口链、模块词汇、skill 选择全部显性，散文降为路由。
- **Candidate / obligation budget:** CHAIN-001, VOC-001, VOC-002, SKL-001, SKL-002
- **Declared workstream order:** chain-lock, vocabulary-fix, skill-slot
- **Program decision authority:** 规范语义（entry-surface / deerflow-wiring delta 的验收线）由人
  拍板；wiring 实现细节（AST 断言形态、docstring 措辞、cutover 顺序）由 apply agent 在本
  Program 范围内自主决定。
- **Shared archive invariant:** 三个 workstream 共享同一条不变量——`make verify` 全绿 +
  `make smoke` 全绿 + 架构/doc 卫生 checker 全绿，且 test ID 集合相对基线只增不改（锁链测试
  新增；改名零 test ID 变化）。三个 workstream 全部达标才整体 archive，不许部分归档。
- **Program failure / recovery:** 任一 workstream 红证后停留原地修复：vocabulary-fix 失败回滚
  该 workstream 的 git mv（chain-lock 测试立即变红指出断环，天然回滚探针）；skill-slot 失败
  回滚 config 段与 build_client 透传（默认姿态由 SKL-002 guard 钉住，回滚后 guard 仍绿）。
  计划级 re-scope 需人工拍板，回滚不静默。
- **Split / expansion rule:** 新消费点在 cutover 中现身的，纳入所属 workstream，不扩预算；
  skill 激活语义、操作者快车道（rehearse）、`.deer-flow/` 归置均超出本 Program，出现触发即
  拆独立 change，不在本 Program 内膨胀。
- **Not in scope:** skill 激活语义与质量评估；操作者 rehearse/replay 入口；`.deer-flow/` 运行态
  归置；tests/ 目录重排；任何 CLI 动词语义、domain/engine 规则、Bundle schema 变更。

### Workstream Focus: chain-lock

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/` 的组合面 +
  `tests/contract/` 离线证据面——锁的是「谁调用谁」这条组合事实。
- **Seam classification:** wiring — 断言既有调用关系的组合签名，不改认知、不改状态规则、
  不改任何可观察行为。
- **Question:** 入口链六环的调用关系能否被一个离线 contract 测试机械锁定，使换 owner、
  绕环、改名三种漂移都变红，而重构内部实现不误伤？
- **Necessary adjacent/external contracts:** entry-surface（answers: create/refine 旅程的声明
  路由是链条的需求权威）；delivery-lanes（answers: contract 测试进 verify 车道的收集合同，
  collection guard 需同步）；doc-truthfulness（answers: 文档降为路由后不得残留第二套链条叙述）。
- **Evidence seam:** 先写断言对现状红（如锁 entry.py 而链走别处即红）证咬合，再校准绿；
  最终 `make verify` 全绿、断言覆盖六环；`git diff --stat` 证明零 src 行为变更。
- **Not in scope:** 运行时行为变更；integration 车道新增；链条语义重设计。
- **Triggered review policies:** local-context, agent-information-map, authority-and-projections, change-admission
- **Candidate / obligation IDs:** CHAIN-001
- **Target / retirement:** CHAIN-001 = 锁链 contract 测试落地并进 verify 默认收集；随本
  workstream 交付即 retire，后续链条演进由该测试守护。
- **Surface grade:** internal——无 CLI/UX 变化；可观察面仅为测试红绿与文档路由。
- **Decision authority:** 断言形态（AST vs import 反射 vs 源码正则）由 apply agent 决定；
  「六环调用关系不可绕过」这一验收线由人确认。
- **Negative path / recovery:** 红证任务先行：人为断开一环（如把 run_foreground 改为直调
  client）必须红；红证后恢复原状再校准。若 AST 断言过脆（重构即误报），降级为 import 级
  断言并记录取舍，不得为绿灯放松覆盖。

### Workstream Focus: vocabulary-fix

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/` 的模块命名——
  entry.py 与 run_engine.py 两个名字的语义纠正及其 12 个外部消费者文件。
- **Seam classification:** wiring — git mv + import cutover，函数体零改动；行为由既有
  125+ 测试与 chain-lock 断言守护。
- **Question:** 在 chain-lock 测试已锁调用关系的前提下，两个撞名模块能否在零 test ID 变化、
  零行为变化下完成改名，使 runtime 目录名直接拼出链条职责（interaction → assembly → adapters
  → pump → bundle）？
- **Necessary adjacent/external contracts:** project-structure manifest（answers: required-paths
  增删按登记协议，架构 checker 判定改名合法）；chain-lock workstream（answers: 改名后的链条
  调用关系仍被锁定，改名不构成绕环）；deerflow-wiring spec（answers: 绑定与泵行为语义不变，
  仅路径变）。
- **Evidence seam:** 改名中途的 ImportError 红证（证明测试咬合结构）；修复后 `make verify`
  全绿 + test ID 清单逐项相同 + `make smoke` 全绿。
- **Not in scope:** 并入子包或目录重排（单文件不建目录——沿用 2026-10-05 split 原则）；
  `interaction/`、`scripted/`、`bundle/`、`adapters/` 的任何位置变化。
- **Triggered review policies:** local-context, agent-information-map, change-admission
- **Candidate / obligation IDs:** VOC-001, VOC-002
- **Target / retirement:** VOC-001 = entry.py → assembly.py（含 14 消费点 cutover + manifest
  登记）；VOC-002 = run_engine.py → pump.py（同上）。两者随本 workstream 交付即 retire。
- **Surface grade:** internal——模块路径变化对操作者不可见（CLI 入口不变）；可观察面为
  import 路径与文档链接。
- **Decision authority:** 新名字 assembly/pump 由本 proposal 提案、人拍板后冻结；cutover
  顺序与 docstring 措辞由 apply agent 决定。
- **Negative path / recovery:** 分两步红证：mv 后不修 import → ImportError；修一半 →
  chain-lock 或收集错误红。全程可 `git mv` 反向回滚，chain-lock 测试作回滚探针。

### Workstream Focus: skill-slot

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/adapters/` 的绑定
  装配（build_client 的 available_skills 参数来源）——声明面归 config，传递归 adapter。
- **Seam classification:** wiring — 声明解析与参数透传；默认值 None 保持现行为逐字节不变；
  不制造 prompt、不定义认知角色。
- **Question:** skill 选择能否从写死的 `available_skills=None` 变为 config 声明 + 装配透传 +
  guard 钉住默认姿态，使未来激活 skill 时只填声明槽而不再动绑定代码？
- **Necessary adjacent/external contracts:** deerflow-wiring spec（answers: 构造参数
  available_skills 已在 contract mirror 登记，透传不引入新框架面）；config 两梯合同
  （answers: base/fixture 的梯语义与零凭证保证不因新增声明段破坏）。
- **Evidence seam:** SKL-002 guard 对「声明缺省 = None 透传」做离线断言（FakeClient 记录
  构造参数，不 import 框架）；`make verify` 全绿；真实梯下 skill 实际加载行为不在本
  workstream 证明范围，显式标注 UNVERIFIED。
- **Not in scope:** skill 激活语义、skill 内容评审、认知评估；`agent_name`/`environment` 等
  其余未透传参数的激活；deerflow/ gitlink 的任何触碰。
- **Triggered review policies:** local-context, change-admission, deerflow-downstream-boundary
- **Candidate / obligation IDs:** SKL-001, SKL-002
- **Target / retirement:** SKL-001 = config skills 声明段 + build_client 透传（默认 None）；
  SKL-002 = contract guard 钉住 declared-none 姿态与声明解析规则。随本 workstream 交付即
  retire；激活语义立项时在此槽上扩展，不改槽位合同。
- **Surface grade:** internal——默认姿态下无任何模型可见行为变化；激活后（未来 change）才
  影响 agent 上下文，届时走 node-agent 门。
- **Decision authority:** 声明段 YAML 形态由 apply agent 在「声明缺省必须解析为 None」约束
  下决定；「激活语义另立项、本槽只声明不激活」由人拍板。
- **Negative path / recovery:** guard 先红后绿：把 build_client 改回硬编码非 None 值或让声明
  解析吞掉错误类型，guard 必须红。失败回滚 config 段与透传，guard 与既有 mirror 测试保证
  回滚后仍绿。
