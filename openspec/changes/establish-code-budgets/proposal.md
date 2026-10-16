# Proposal: establish-code-budgets

## Why

阶段 2 把三个千行 checker 拆成薄入口与职责子包之后，`openspec/governance/` 从 13 个文件变成
30 个、6,639 行。拆开暴露了两件原先被"文件太大"掩盖的事：

1. **重复的基础设施各自为政**。git 调用有 **6 份独立包装**，行为互不一致——
   `project_architecture_check/gitlink.py:14` 有 `OSError` 护栏并抛 `ContractViolation`；
   `check_release_face.py:53` 自己吞掉 `OSError` 返回 `None`；`check_proof_receipts.py:34`
   无任何护栏；`selected-change-closeout.py:80` 返回 bytes 而非 str；另有测试侧一份。
   仓库根解析同样有 **5 个变体**（`parents[2]` / `parents[3]` / `Path.cwd()` / argv 优先 /
   `__file__` 派生）。想给"git 不可用"加一条统一行为，得同时改六处。
2. **没有任何东西看着这些脚本自己的体积**。`check_project_architecture.py` 的逐行导入矩阵
   只遍历 harness 源码根；`DOC_BUDGETS` 只管常驻指令文档（字符单位）。**治理脚本长到 1473 行
   却无人报警**，正是这条盲区造成的——阶段 1/2 是人工发现并偿还，不是机器拦住。

现在做，是因为阶段 2 刚建立的子包结构给了共享模块一个明确落点（`governance/` 顶层），
且这两件事必须同一轮做：**没有守卫，去重省下的行数会被无意识地重新长回来**。

## What Changes

- **新增 `code-budgets` capability 与其 checker**：声明式表（每个受管文件 = 总行数上限 +
  超长函数个数上限），超限失败时**点名文件、实测值、上限、违规函数**；受管文件缺失按
  "missing managed path"失败；棘轮纪律（只降不升，升需在表旁写一行理由）写进声明表注释。
  checker 自带 `--self-test` 负例（种一个超限文件 + 一个超长函数，两者都必须被报出）。
- **共享 git 调用层 `gitio.py`**：一份 `run_git()`（`cwd` 显式、`text` 可切、返回
  `CompletedProcess` 且**不抛**），供 6 处调用点复用；**各调用点保留自己现有的错误处理与
  返回类型**（`gitio` 只共享"怎么调 subprocess"，不强行统一"出错怎么办"——那会改变失败
  路径的可观察行为）。
- **共享根解析层**：一份 `resolve_root(argv_value, default_parents)` 供 5 个变体复用，
  **每个调用点保持自身的默认值**（argv 优先、parents 层级、`Path.cwd()` 各自不同，属各自
  CLI 契约的一部分）。
- **死码清偿**：`change_guidance_kernel.py` 214 行里有 **8 个定义、88 行**在活跃代码中零引用
  （`CompositionSchema` / `ProfileSchema` / `ReviewSchema` / `missing_fields` /
  `neutrality_issues` / `profile_completeness_issues` / `selected_policies` /
  `validate_review_table`）——按可达性分析确认（从 5 个真实使用者出发的闭包之外），
  全树活跃代码与测试引用计数为 0。删除后 kernel 只留真正被使用的原语。
- **`manifest.py:load_manifest` 三段式拆分**（171 行，全库最长函数）：阶段 2 只提取了两个
  天然子块；本次按 `_parse_manifest_document` / `_validate_manifest_contract` /
  `_build_manifest` 补完，用一个中间值对象承载 19 个校验产物。
- **登记与计数同步**：`required-paths.toml` 增 `code-budgets` checker 与其测试；根 README
  的 specs 计数 13 → 14（新建 capability 的必然结果）；`openspec/governance/README.md`
  组件表与独立检查段增该 checker；CI canonical 序列增一步（由 ci-governance 的声明表钉住）。

**不变量（本 change 的验收核心）**：六个既有 checker 的 stdout 与退出码**逐字不变**（含
**失败路径**——去重动的是基础设施，成功路径的逐字比对覆盖不到失败的形状）；治理套件用例数
不减（基线 145）；棘轮只降不升；新守卫必须"能变红"（自带负例 + 一次真实的移走-恢复证明）。

## Capabilities

### New Capabilities

- `code-budgets`: 治理脚本自身的代码体积预算闸——声明式上限、超限点名失败、缺失受管文件
  失败、棘轮纪律、自带可失败的负例自检。

### Modified Capabilities

<!-- none: 六个既有 checker 的行为零变化；去重只改实现共用的地方，不改任何判定语义、
     违规文本或退出码。ci-governance 的 canonical 序列增一步属其既有声明表的值变更，
     该决定记在 tasks 与 design 里并在 apply 时同步其 checker 的声明面。 -->

## Impact

- **新增**：`openspec/governance/check_code_budgets.py`、`openspec/tests/governance/test_code_budgets.py`、
  `openspec/specs/code-budgets/spec.md`（归档时由 delta 生成）。
- **新增（共享层）**：`openspec/governance/gitio.py`、`openspec/governance/roots.py`。
- **改**：6 个 checker 的 git 调用点与根解析点改为复用共享层（各自默认值与错误处理不变）；
  `change_guidance_kernel.py`（删 88 行死码）；`project_architecture_check/manifest.py`
  （`load_manifest` 三段式）；`required-paths.toml`；`openspec/governance/README.md`；
  `.github/workflows/governance.yml` 与 `.githooks/pre-commit`（新增守卫步，由 ci-governance
  声明表钉住）；根 `README.md`（specs 计数 13 → 14）。
- **不动**：六个 checker 的任何判定语义、违规文本、退出码；`deerflow/` gitlink；
  `deep_research_harness/` 的任何源码与测试；`_battery.py` 的 39 条控制。
- **触发车道**：治理套件、`check_project_gate.py --phase closeout`、CI canonical 序列；
  harness 的 `make verify` / `make smoke` 不受影响（不含 harness 文件）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/` —— 治理检查器目录自身：
  它拥有"共享基础设施放在哪、脚本自己的体积由谁看着"这两个决定。
- **Seam classification:** deterministic-guardrail —— 纯机械的代码卫生与体积闸；无模型参与，
  既有判定语义零变化。
- **Question:** 6 份 git 包装与 5 个根解析变体能否收敛到共享层、kernel 的 88 行零引用定义
  能否安全删除、并新增一个真能变红的体积闸——而六个既有 checker 的 stdout 与退出码在
  **成功路径与失败路径上都逐字不变**？
- **Necessary adjacent/external contracts:** `.github/workflows/governance.yml` 与
  `.githooks/pre-commit`（answers: 新增守卫步会不会破坏 ci-governance 已钉住的 canonical
  命令集？答：该 checker 的声明表就是为"改序列必须同改声明"而存在，属受控同步）；
  `openspec/governance/required-paths.toml`（answers: 新增路径如何登记？答：按既有协议增
  files/directories 条目）；根 `README.md`（answers: 新建 capability 会让 specs 计数从 13
  变 14，doc-hygiene 的 root-count 规则正在盯着该行）；`openspec/governance/README.md`
  （answers: 组件表与独立检查段如何自述新 checker？答：按既有表格形态增行）。
- **Evidence seam:** 六个既有 checker 的 stdout 逐字比对（**成功路径 + 种植违规的失败路径
  各一轮**）· 治理套件用例数不减 · 新守卫的 `--self-test` 负例 + 一次移走-恢复的真实变红
  证明 · 改 `load_manifest` 前后的绿地对照 · `git diff` 确认 harness 零改动。
- **Not in scope:** 任何判定语义或违规文本的修改；finding 形状的强制统一（见 design
  Alternatives：把三种形状强行归一为一种会改变失败路径与退出码，与本 change 的"逐字不变"
  边界冲突，只共享底层不改变形状）；`check_doc_hygiene.py` 的包级拆分（阶段 2 已裁定不做）；
  harness 侧任何改动（阶段 4 的 `decompose-run-pump` 才碰）；`_battery.py` 拆分。
- **Triggered review policies:** local-context, change-admission
