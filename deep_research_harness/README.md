# DeerFlow Deep Research Harness (v3)

这是基于 DeerFlow 2.1 的研究运行与控制底座。DeerFlow 的 lead agent、skill 和工具驱动动态研究；Harness 管理每次研究的 Run Bundle、状态、journal、checkpoint 和最终报告准入。当前运行形态是单机前台 CLI。

## 从问题到报告

```text
cli.py（稳定启动入口）
  -> runtime/interaction/cli.py（参数、交互、输出）
  -> bundle_actions.start（创建 Bundle）
  -> runtime/assembly.run_foreground（配置、client、SQLite 装配）
  -> DeerFlow lead agent <-> 模型 / 工具 / 按需 subagent
  -> runtime/pump.py（消费事件、有限续答、取消、终态）
  -> validator + admission + ledger（最终回答准入）
  -> ../runs/d_YYYYMMDD/<bundle-id>/final/report-genN.md   （仓库根 runs/，应用子树之外）
```

链条的组合关系由 [锁链契约测试](tests/contract/test_entry_chain.py) 机械锁定（离线、
AST 级、零产品 import）：任何一环被替换、绕过或改名漏切，`make verify` 即红。

交互上下文（TTY 或 `DEEP_RESEARCH_INTERACTIVE=1`）中 `create` 先经**计划确认闸门**（agent 交计划 → 操作者确认/修订/跳过 → 注入续跑，确认计划物化于 `request/plan-gen1.md`）；模型判断含糊时可先反问（答案原样续跑）。状态、checkpoint、journal 和已接纳产物持久保存在各自 Bundle 中，没有额外的集中式运行状态库。删除一个 Bundle 会永久失去该运行，其余运行仍可使用。`completed` 还需结合准入结果和报告文件判断产物是否交付；validator 检查产物合同，不验证研究事实质量。

## Reading Map

| 你要驾驭什么 | 放在哪里 / 直接入口 |
| --- | --- |
| 交互：七动词、直播输出、journal 投影 | [CLI 实现](src/deerflow_deep_research/runtime/interaction/cli.py)、[共享渲染](src/deerflow_deep_research/runtime/interaction/render.py) |
| 运行：装配、流、可信 I/O、持久化 | [assembly](src/deerflow_deep_research/runtime/assembly.py)、[控制地图](docs/control-map.md) |
| 规则：状态合同、validator、gate | [state_machine](src/deerflow_deep_research/domain/state_machine.py)、[validator](src/deerflow_deep_research/engine/validator.py) |
| 研究认知：skill、模型、工具、委派 | [研究过程地图](docs/research-process.md)、[base 配置](config/base.yaml) |
| 验证：离线规则/合同、框架 smoke、输入样本 | [tests](tests/README.md)、[fixtures](tests/fixtures/README.md) |
| 开发操作：显式录制与诊断 | [tools](tools/README.md) |
| 运行数据：每次研究的状态、证据和报告 | [Run Bundle 地图](docs/run-bundle.md)、[Bundle 路径合同](src/deerflow_deep_research/domain/bundle.py)；仓库根 `runs/`（gitignored，`DEEP_RESEARCH_RUNS_ROOT` 可覆盖） |
| 开发治理：设计准入、结构登记、任务账本 | 仓库根 OpenSpec / backlog；不参与产品运行 |
| 权威边界与策略参考 | [控制地图](docs/control-map.md)、[local operations](docs/local-operations.md)、[testing](docs/testing-and-evaluation.md)、[词汇](CONTEXT.md) |

源码仍有 `domain / engine / agents / runtime` 四个所有权层；`agents` 当前仅包入口。上游 `deerflow/`（包括它的 scripts）是锁定的只读框架。我们自己的可执行开发工具放 tools，不把它们混进产品入口或测试 runner。

## 运行与观察

在本目录执行。离线验证只需 stdlib；运行与集成需 Python 3.12+、uv、兄弟目录的 DeerFlow submodule 和首次 `uv sync`。`make install` 是提示环境准备方法的 no-op。

```bash
make verify                              # 离线 unit + contract 门禁
uv sync                                  # 准备 DeerFlow 运行依赖
make create PROBLEM="研究问题"            # 默认 fixture，零凭证
make create PROBLEM="研究问题" CONFIG=base # 真实模型/外部工具，需凭证
python3 cli.py status <bundle_id>         # 当前状态和近期 journal
python3 cli.py watch <bundle_id>          # 观察 journal，终态退出
python3 cli.py inspect <bundle_id>        # 时间线、已采证据、装配快照
```

`cancel` 只记录取消请求，由运行泵协作终止。`refine` 创建下一代并**前台跑完该代**（方向文本即该代方向文档）。完整命令见 [COMMANDS](COMMANDS.md)，操作旅程见 [playbook](docs/playbook/run-research.md)。

框架运行态（memory 库、skill 投影、用户数据）由 binding 钉在仓库根 `.deer-flow/`（gitignored，应用子树外）。fixture 配置加载 [runtime scripted providers](src/deerflow_deep_research/runtime/scripted/__init__.py)，base 记录 `all_real`，fixture 记录 `fixture`；`mixed` 是尚未接线的枚举。provider 代码随当前 Python package 打包，wheel 仍不包含完整 CLI/config/兄弟布局，发布面是源码 checkout + 锁定 submodule。

## 改一处，先证明哪一层

| 改动对象 | 最小起点 | 扩大验证 |
| --- | --- | --- |
| 纯规则 / 准入 / 本地落盘 / stream 适配 | tests/unit 中对应 owner 文件 | `make verify` |
| 配置 / 接口镜像 / thread 与递归上限转发 | `tests.contract.test_wiring_mirror` | `make verify`，真实绑定加 smoke |
| CLI / client / checkpoint 接线 | `tests.unit.test_entry_composition` 或对应 integration 文件 | `make smoke`（脚本模型 + 真框架） |
| 真实研究策略与质量 | 明确认知 owner 和评审标准 | 显式 base 运行；不进入默认 CI |

不要把端到端当唯一定位手段。逐文件选择见 [测试资产地图](tests/README.md)，主链、两种 loop、发布形态及未实现清单见 [控制地图](docs/control-map.md)。Coding Agent 从 [AGENTS](AGENTS.md) 选择 owner，其余参考见 [文档索引](docs/README.md)。
