# Proposal: rename-closeout-tool

## Why

`openspec/governance/selected-change-closeout.py` 的文件名带连字符，**因此无法被 `import`**——
Python 的模块名不允许连字符。后果是它的逻辑只能靠 subprocess 调用（按路径）来测，任何针对
它内部函数的单元测试都写不出来；现有治理测试之所以一律用 `importlib.util.spec_from_file_location`
按路径加载，正是被这类文件名逼出来的。

它同时**顶在体积闸的上限**：`check_code_budgets.py:58` 给它设的上限是
`FileBudget(max_lines=256, max_long_functions=1)`，而它现在**正好 256 行**——再写一行就红。
要拆它（把某个函数提出来降低行数）就得先能测它，而要能测它就得先能 import 它。

这是 CLS-025 卡"未决"一节里记着、并预期在阶段 2 处理、但**五个阶段都没做**的一条。

## What Changes

- `git mv openspec/governance/selected-change-closeout.py openspec/governance/selected_change_closeout.py`。
- **同步全部活引用（8 处）**：`openspec/config.yaml`（政策文本里的路径）·
  `change_guidance_check/constants.py`（与该政策配对的**声明字符串**——两者必须同时改，否则
  guidance checker 会报声明漂移）· `required-paths.toml`（登记条目）· `check_code_budgets.py`
  （体积上限的键，否则预算不再作用于该文件）· `governance/README.md`（组件表）·
  `selected-change-closeout.md`（文档里的两条命令示例）。
- **补一条"可 import"的证明**：新增治理测试，用**真 import**（把 governance 目录放进
  `sys.path` 后 `import selected_change_closeout`）加载该模块并断言它暴露自己的 CLI 入口——
  这正是改名要解锁的能力，用测试把它钉住。

**不变量**：脚本的命令行契约（`verify-boundary` / `record-review` 子命令、stdout、退出码）
逐字不变 · `SCHEMA_VERSION = "selected-change-closeout/v1"` **保持原样**（它是**已记录证据的
数据模式标识**，不是路径；改名它会让既有回执失效）· 文档 `.md` **不改名**（文档不受 import
约束，改它只会多动两处登记）· 门禁组件集不变（它本就不是门禁组件——`check_project_gate.py`
只注册 4 个：change-guidance / harness-dependency-direction / ci-governance / proof-receipts）。

## Capabilities

### New Capabilities

<!-- none: 文件名与可测性不是 capability 的 requirement；脚本的命令行契约不变。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改名**：`openspec/governance/selected-change-closeout.py` → `selected_change_closeout.py`。
- **改**：`openspec/config.yaml` · `change_guidance_check/constants.py` ·
  `required-paths.toml` · `check_code_budgets.py` · `governance/README.md` ·
  `selected-change-closeout.md` · 新增一条治理测试。
- **不动**：脚本内任何逻辑与命令行契约 · `SCHEMA_VERSION` · 历史归档与 `_backlog/_archived`
  里的旧路径（那是当时的快照）· `deerflow/`。
- **触发车道**：`make verify`（harness 面，确认零影响）· 治理套件 · 六个门禁组件 ·
  `make smoke` 不涉及（改名不碰 harness 运行时）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/selected_change_closeout.py`
  —— 它拥有"选中 change 的 closeout 证据如何被记录与校验"这一决定；本 change 只改它的**名字**。
- **Seam classification:** deterministic-guardrail —— 一个操作者工具的可寻址性；无模型参与。
- **Question:** 一个被连字符挡住 `import`、因而只能 subprocess 测、又顶在体积闸上限的工具，
  能否改名到可 import、并让全部 8 处引用与声明字符串同步跟上——而它的命令行契约、证据数据
  模式与历史记录都不变？
- **Necessary adjacent/external contracts:** `openspec/config.yaml` 与
  `change_guidance_check/constants.py`（answers: 政策文本与 checker 声明是一对，必须同改，
  否则 guidance checker 报漂移）· `required-paths.toml`（answers: 登记路径必须存在，否则
  `path.missing`）· `check_code_budgets.py`（answers: 体积上限按文件名索引，键不改则失守）·
  `selected-change-closeout.md`（answers: 文档是操作者的入口，命令示例必须可复制粘贴运行）。
- **Evidence seam:** `python3 -m unittest discover -s openspec/tests/governance`（含新增的
  import 测试）· 六个门禁组件逐一退出码 · 脚本自身的 `--help` 与子命令退出码对照 ·
  `python3 openspec/governance/check_project_architecture.py`（登记面）。
- **Not in scope:** 拆分该脚本以降低行数（改名解锁了这件事，但那是下一把）· 把治理目录里
  其他连字符文件一并改名 · `.md` 改名 · CAS 空转 · 任何脚本逻辑改动。
- **Triggered review policies:** local-context, change-admission
