# Quality Register（检查注册处，RT10）

> 质量由哪些机器保证——单一清单面。清单的代码事实源 = `src/deerflow_deep_research/engine/machines.py`
> 的 `DECLARED_MACHINES`；单元测试在两者漂移时失败。接手者从这里一眼看到每台机器
> 保证什么、在哪验证。

| 机器 | 保证的不变量 | 证据 seam |
| --- | --- | --- |
| validator | 任何 artifact 内容未过裁决不得进入 bundle；拒绝携带封闭结果码与人话理由（hold point，模型提议、代码裁决） | `tests/unit/test_admission_engine.py`（每个结果码可达）+ `test_admission_runtime.py`（reject 不落内容） |
| gate | 阶段只渲染 pass / blocked，纯推导自声明需求 vs 已 admit 事实；blocked 点名未满足项 | `tests/unit/test_admission_engine.py`（blocked 精确点名） |
| ledger-chain-verification | `evidence/submissions.jsonl` 是 sha256 哈希链：任何字段篡改、插入、删除都在首个断链处响亮失败；单一 commit owner | `tests/unit/test_admission_runtime.py`（篡改/插入/verdict-less commit 负例） |
| subagent-posture-guard | 两份 checked-in 配置声明无自定义 subagent；未来任何声明必须把 `task` 排除在 `disallowed_tools` 外（深度自校验 fail-closed，报错点名配置文件/违规者/remedy） | `tests/unit/test_subagent_posture.py`（含违反声明→红的负例控制） |
| command-surface-guard | `COMMANDS.md` 登记的 make targets / cli 子命令与 Makefile、`cli.py` 三处互相一致；漂移即红 | `tests/unit/test_command_surface.py`（双向一致性 + 负例控制） |
| application-unit-gate | `make verify` 跑 stdlib unittest 套件，任一失败非零退出；不读不引任何 OpenSpec 内容 | `Makefile` + gate 自身的红证明回执（红 → 绿） |
| repository-governance-gates | 聚合 closeout 门禁及其组件 checker（结构/需求/specs/指导/依赖方向）在归档前全部 exit 0 | 仓库根治理目录（其 README 登记确切命令；governance-owned，非 harness lane） |

## 纪律

- 加/删机器 = owning change 的决定，不顺手改；`DECLARED_MACHINES` 与本表同步漂移会红。
- 每台新守卫落地须过一次负例控制（引入违规 → 看红 → 还原 → 看绿）。
- 本表是索引不是第二权威：每台机器的语义由其 owning 代码与 spec 拥有。
