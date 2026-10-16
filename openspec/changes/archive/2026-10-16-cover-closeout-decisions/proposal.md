# Proposal: cover-closeout-decisions

## Why

上一把 `rename-closeout-tool` 把 `selected-change-closeout.py` 改成可 import 的名字，理由是
"连字符挡住 import ⇒ 逻辑只能 subprocess 测 ⇒ 无法单测"。**但收益还没兑现**：改名后我只加了
一条"可 import + 暴露 main"的证明，那个工具真正的判定逻辑至今仍是零直接覆盖。

实测（`grep` 于 `openspec/tests/`）：

| 函数 | 职责 | 测试中引用 |
|---|---|---|
| `_parse_attestation` | 证据文件的结构校验 | **0** |
| `_planning_home` | 从起点向上找规划根 | **0** |
| `_active_change_root` | 按 change 名定位活跃 change | **0** |
| `_resolved_commit` | 把 commit 引用解析为完整哈希 | **0** |
| `_verify_boundary` | 校验 caller 声明的提交范围 | **0** |
| `_unchecked_task_labels` | 从 tasks.md 解析未勾任务标签 | **0** |
| `_validate_review` | 校验 review 文档与 change 树 | **0** |

它们此前只能通过 subprocess 端到端触及（治理侧 12 个测试文件里有 8 个用 subprocess）——而端到端
测不到**拒绝路径**：一个只对合法输入跑过的校验器，与一个真的会拒绝非法输入的校验器，在端到端
里看起来一样。这正是 `test-evidence-policy` 要求的"守卫必须能变红"所针对的缺口。

## What Changes

- **新增 `openspec/tests/governance/test_closeout_decisions.py`**：用**真 import**（上一把已解锁）
  直接驱动这 7 个函数，每个函数覆盖：合法输入的正常路径 + **至少一条拒绝路径**（非法结构、
  缺字段、标签不匹配、commit 解析失败等），并断言返回值形态而非仅断言不抛。
- **对纯文件系统/ git 依赖的函数**（`_planning_home` / `_active_change_root` / `_resolved_commit` /
  `_verify_boundary`）：在临时目录与**临时 git 仓库**里构造最小场景，不触碰真实仓库。
- **若测试暴露真实缺陷**：按 core 原则走 bug 轨——记入 Deviation Register、停下请裁决，
  **不静默改语义**来把测试变绿。

**不变量**：脚本自身逻辑与命令行契约零改动 · `SCHEMA_VERSION` 不变 · 既有 159 条治理用例全绿 ·
harness 面零改动 · 不新增对真实仓库的写操作（测试只在临时目录里跑）。

## Capabilities

### New Capabilities

<!-- none: 补的是既有工具的测试覆盖，不改任何 requirement 或契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **新增**：`openspec/tests/governance/test_closeout_decisions.py`。
- **改**：无（若发现缺陷则另行报告，不在本 change 内修）。
- **不动**：`selected_change_closeout.py` 的任何一行 · `SCHEMA_VERSION` · 历史归档 ·
  `deep_research_harness/` 全部 · CAS 空转（事实 12）。
- **触发车道**：治理套件（`python3 -m unittest discover -s openspec/tests/governance`）·
  六个门禁组件 · `make verify` 与 ruff（确认 harness 面零影响）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/selected_change_closeout.py`
  —— 它拥有"选中 change 的 closeout 证据如何被校验"这一决定；本 change 只**测**它，不改它。
- **Seam classification:** deterministic-guardrail —— 一个校验器的判定逻辑；无模型参与。
- **Question:** 这个工具的七个判定函数，能否在被直接驱动时证明**既接受合法输入、也拒绝非法
  输入**——而脚本一行不改、既有 159 条用例全绿、且不写真实仓库？
- **Necessary adjacent/external contracts:** `openspec/governance/selected-change-closeout.md`
  （answers: 证据文件与 review 文档的**形状**是什么——测试夹具按它构造）·
  `tests/contract`-style 的既有断言（answers: 不能重复或削弱既有端到端断言）·
  `check_code_budgets.py`（answers: 新增测试文件是否受预算管制——测试不在预算表内）。
- **Evidence seam:** 治理套件用例数与退出码 · 每条新增断言**能变红**的证明（对被测函数做局部
  变异或对夹具做已知违规构造）· `check_project_gate.py --phase closeout` ·
  `git diff --stat -- deep_research_harness/` 为空。
- **Not in scope:** 修任何缺陷（发现即报告）· 拆 `selected_change_closeout.py` 的 256 行（另一把）·
  其他治理脚本的同类覆盖缺口（先做这一个，作为样板）· CAS 空转 · 任何脚本改动。
- **Triggered review policies:** local-context, change-admission
