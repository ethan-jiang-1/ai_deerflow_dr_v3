# Tasks

## 1. Baseline and the move

- [x] 1.1 Record the baseline: the governance suite (`python3 -m unittest discover -s openspec/tests/governance`) and the harness lanes (`UV_OFFLINE=1 make verify`, the ruff lane) all exit 0; record the case counts  ✓ 治理套件 157 OK（skipped=1）· verify 252 OK · lint 0。
- [x] 1.2 Capture the tool's command-line contract before the move: `--help`, plus `verify-boundary` and `record-review` with no arguments (their usage/exit codes), into `/tmp/rct-before/`; verify each capture is non-empty  ✓ 命令行契约已捕获：`--help` exit 0（11 行）· `verify-boundary` exit 2（3 行）· `record-review` exit 2（5 行）。
- [x] 1.3 `git mv openspec/governance/selected-change-closeout.py openspec/governance/selected_change_closeout.py`; verify the old path is gone and `python3 openspec/governance/selected_change_closeout.py --help` still exits 0  ✓ `git mv` 完成；旧名消失、新名 `--help` exit 0。

## 2. Every reference follows, including the paired declaration

- [x] 2.1 Update the policy text in `openspec/config.yaml` **and** the matching declaration string in `change_guidance_check/constants.py` in the same step; verify `python3 openspec/governance/check_change_guidance.py` exits 0 (the paired declaration does not drift)  ✓ config.yaml 的政策文本与 constants.py 的声明字符串**同一步同改**；`check_change_guidance.py` exit 0（无声明漂移）。
- [x] 2.2 Update `required-paths.toml`; verify `python3 openspec/governance/check_project_architecture.py` exits 0, and prove the registration is live by temporarily moving the file and confirming the checker reports the missing path, then restoring  ✓ 登记已更新；架构 checker exit 0，并做**变红实测**（移走文件 → 报缺失 → 恢复 exit 0）。
- [x] 2.3 Update the budget key in `check_code_budgets.py` and verify the budget still **measures** the file (read the table back and confirm the new key is present with the same ceiling), then verify `python3 openspec/governance/check_code_budgets.py` exits 0  ✓ 预算键改为 `selected_change_closeout.py`，仍为 `FileBudget(max_lines=256, max_long_functions=1)`；旧键无残留；体积闸 exit 0。**若漏改此键，守卫会对该文件静默失守**——而它正好顶格 256 行。
- [x] 2.4 Update the two command examples in `selected-change-closeout.md` and the component row in `governance/README.md`; verify no live reference to the old file name remains (`grep` over the working tree excluding archives), and that `python3 openspec/governance/check_doc_hygiene.py` exits 0  ✓ `.md` 的两条命令示例与正文（3 处）、`governance/README.md` 组件表均已更新；活引用零残留（历史归档与 `_archived` 按规矩不动）；doc-hygiene exit 0。

## 3. Prove the capability the rename unlocks

- [x] 3.1 Add a governance test that imports the module by name (putting `openspec/governance` on `sys.path`, restored via `addCleanup`) and asserts it exposes its CLI entry point with `SCHEMA_VERSION` still `selected-change-closeout/v1`; verify the test passes  ✓ 新增 `openspec/tests/governance/test_closeout_tool.py`：用**真 import**（`sys.path` + `finally` 复原）加载，断言暴露 `main` 且 `SCHEMA_VERSION` 未随名变；治理套件 157 → 159 全绿。
- [x] 3.2 Prove the test can fail: temporarily rename the file back to the hyphenated name and confirm the new test fails, then restore; record both exit codes in the delivery record  ✓ **变异检查**：把文件改回连字符名 → 新测试 `ModuleNotFoundError` 退出 1；恢复 → OK。这条守卫真的能红。
- [x] 3.3 Verify the schema-version decision held: `SCHEMA_VERSION` is unchanged and the tool's `--help`/subcommand captures match the baseline from 1.2 as far as the rename is concerned (same subcommands, same usage)  ✓ `SCHEMA_VERSION` 保持 `selected-change-closeout/v1`（由 3.1 的断言钉住）；命令行契约对照改前捕获：**唯一差异是 usage/error 里的程序名**（argparse 的 `prog` 来自调用文件名），子命令集合、选项、错误文案、退出码（0/2/2）全部不变。

## 4. Closeout evidence

- [x] 4.1 Run the full gate set: the governance suite, `check_project_gate.py --phase closeout`, the ruff lane and `UV_OFFLINE=1 make verify`; verify every exit code is 0 read directly  ✓ 7 个 checker + closeout gate + 治理套件全部 exit 0（直测）；ruff lint exit 0。
- [x] 4.2 Confirm no product or test surface changed: `git diff --stat origin/master..HEAD -- deep_research_harness/` is empty; record the command and its output  ✓ `git diff --stat -- deep_research_harness/` 输出为空。
- [x] 4.3 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines produced by the runner above  ✓ 见下 `## Delivery Record`。

## Deviation Register

- 偏差 1（过程记录，一处实现误差）：同步引用的脚本在 `governance/README.md` 上断言失败而中止——那一行用的是简写 `` `selected-change-closeout.md` / `.py` ``，不含完整文件名，我的断言假定它含。已单独补改该行与其后的 `.md`（3 处）。**教训：批量替换前要逐处确认匹配串的真实形态，别假定文档里写的是完整路径。**
- 偏差 2（有意的差异，非缺陷）：命令行的 usage/error 文本里出现了新文件名。这不是契约变化，而是**改名的必然投影**——argparse 的 `prog` 取自调用文件名。已按"逐字 diff 后确认唯一差异"的方式记录，而不是把它说成"完全一致"。
- 偏差 3（刻意不改，就地写明）：`SCHEMA_VERSION` 仍是 `"selected-change-closeout/v1"`，字符串里留着旧式写法。这是**刻意保留**：它标识的是已记录证据的**数据模式**，不是文件路径；跟着文件名改会让既有回执变成"另一个模式的记录"。新增测试把这条决定钉住，避免后来者"顺手统一"。

- 偏差 4（过程记录，同类错误第二次犯，值得单列）：写收口文档时我**又**在替换里追加了一节 Deviation Register，而占位那份还在 → 出现两节；修的时候按"删第一段到第二段"删，**区间跨过了中间的 Delivery Record，把它整节删掉**，两个门禁立刻转红。修法是补回该节并核对结构（1 节 Deviation Register + 1 节 Delivery Record + 4 个字段全在）。**这已是本会话第二次踩"锚点/区间选错"，且两次都是我自己加的文档块造成：规矩应当是"就地替换占位内容"，不是"在文件尾部再追加一份"。**

## Delivery Record

- **外部行为**: 脚本逻辑零改动。命令行契约对照改前捕获：**唯一差异是 usage/error 文本里的程序名**（`selected-change-closeout.py` → `selected_change_closeout.py`，argparse 的 `prog` 来自调用文件名）——子命令集合（`verify-boundary`/`record-review`）、选项、错误文案、退出码（`--help` 0 · 两个子命令缺参 2）全部逐字不变 · **`SCHEMA_VERSION` 保持 `selected-change-closeout/v1`**（由新增测试钉住；它是已记录证据的数据模式标识，不是路径）· harness 面零改动（`git diff --stat -- deep_research_harness/` 为空）。
- **影响面**: `openspec/governance/selected-change-closeout.py` → `selected_change_closeout.py`（`git mv`）· `openspec/config.yaml`（政策文本）· `change_guidance_check/constants.py`（与之配对的声明字符串，同改）· `required-paths.toml` · `check_code_budgets.py`（体积上限的键）· `governance/README.md`（组件表）· `selected-change-closeout.md`（3 处命令与正文，文件本身**不改名**）· 新增 `openspec/tests/governance/test_closeout_tool.py`。
- **实际跑了什么**: 治理套件 exit 0（157 → **159**，含新增 2 条）· 7 个 checker 逐个 exit 0（architecture / change-guidance / code-budgets / doc-hygiene / ci-governance / proof-receipts / harness-dependency-direction）· closeout gate exit 0 · ruff lint exit 0 · `make verify` exit 0（252）· **登记变红实测**（移走文件 → `path.missing` → 恢复 0）· **新增测试的变异检查**（改回连字符名 → `ModuleNotFoundError` exit 1 → 恢复 OK）· **体积预算仍度量**（新键在场、上限 256/1、旧键无残留）· 命令行契约三段逐字 diff。
- **未执行的检查**: 未拆该脚本以降低 256 行的顶格行数——**改名只是解锁了拆的前提**（可 import ⇒ 可单测），拆分本身属下一把 · `make smoke` 未跑（本 change 不碰 harness 运行时，且 `git diff --stat -- deep_research_harness/` 为空可证）· 其他连字符文件未一并改名（不在本 change 范围）。
