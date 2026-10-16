# Design

## Context

动机见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 被测模块 | `openspec/governance/selected_change_closeout.py`（256 行，**本 change 一行不改**） |
| 待覆盖函数 | 7 个，改造前在测试中引用**各 0 次** |
| 端到端盲区 | 治理侧 12 个测试文件里 8 个用 subprocess——**拒绝路径在端到端里不可见** |
| `_active_change_root` 的确定性 | 它用 `resolve_root(None, default=Path.cwd())`（`roots.py`：显式值优先、否则调用方默认）⇒ **cwd 可控即可确定性测试** |
| git 依赖函数 | `_resolved_commit` / `_verify_boundary` 需要**临时 git 仓库**（不碰真实仓库） |

**`_verify_boundary` 的完整契约（实读 103-152 行后写下）**：change 名可解析 → 声明的仓库身份必须是**绝对路径** → cwd 与声明仓库的 `--show-toplevel` 必须同源 → base/head 必须是**可解析的 commit** → base 必须是 head 的祖先 → **HEAD 必须等于 head_commit**（防漂移）→ **worktree 必须干净** → 返回 `boundary-verified` + `diff_summary`（改动文件数 + diff 的 sha256）。

**两条硬约束**

1. **工具文件一行不改**：本 change 只加测试。wrong decision 要记录，不要就地修。
2. **测试只在临时目录里跑**：临时规划根、临时 git 仓库，绝不写真实仓库。

## Goals / Non-Goals

**Goals:** 7 个函数各有直接覆盖，且**每个都有拒绝路径**；每条守卫证明能变红；工具文件与 harness 面零改动。

**Non-Goals:** 修任何缺陷；拆 256 行；其他治理脚本的同类缺口（先做这一个当样板）；CAS 空转。

## Decisions

### D-1｜用真 import，不用 importlib 按路径加载

- **选**：`sys.path` 插入 governance 目录后 `import selected_change_closeout`（`finally` 复原）。
- **为什么**：既有的治理测试一律 `importlib.util.spec_from_file_location` **按路径**加载——那对连字符文件也管用，因此**证明不了改名解锁的能力**。要测的是"真 import 之后逻辑可直接驱动"，测试就必须真 import。
- **换来**：谁把名字改回连字符，这批测试立刻红（沿上一把的守卫）。

### D-2｜cwd 可控即确定性：`os.chdir` + `addCleanup`

- **选**：需要"当前仓库/规划根"的用例，在临时目录里 `os.chdir`，并用 `addCleanup` 复原。
- **为什么**：`_active_change_root` 与 `_verify_boundary` 都以 `Path.cwd()` 为"当前仓库"的事实源。控制 cwd 是**对被测函数的真实依赖**下手，而不是给它打桩——打桩会测到我自己的替身。
- **代价**：测试之间共享进程 cwd，必须保证复原。
- **换来**：测的是真实现，且不触碰真实仓库。

### D-3｜发现缺陷时**锁定**而非修复

- **选**：围栏代码块里的 checkbox 被当成真任务——写成两条**锁定当前行为**的测试，注释里写明这是已记录的缺陷、后果是什么、以及"修好后应当反转这条断言"。
- **为什么**：本 change 的授权是**加覆盖**，不是改工具；工具文件的 owner 是 closeout 语义，改它需要裁决。仓规第 4 条正是这个形态："决定不修的'看似 bug'，在原位留理由 + 一条锁定它的测试。"
- **换来**：缺陷有**可复现的失败优先点**，而套件保持绿。

### D-4｜`_verify_boundary` 走真 git，不打桩 git

- **选**：临时 `git init` + 一次提交 + `git config`，用真实 `rev-parse`/`merge-base`/`status`。
- **为什么**：该函数的判定**全部**建立在这几个 git 查询的结果上；打桩 git 等于把被测逻辑替换掉。
- **换来**：成功路径与四种拒绝路径（仓库不匹配 / commit 未知 / HEAD 漂移 / worktree 脏）都被真实驱动。

## Risks / Trade-offs

- [共享进程 cwd 泄漏到其他测试] → 每次 `os.chdir` 都配 `addCleanup(os.chdir, previous)`；且治理套件整体通过（190 条）。
- [临时 git 仓库受宿主 git 配置影响] → 显式 `git config user.*` 与 `commit.gpgsign false`；不依赖全局配置。
- [锁定缺陷被误读为"认可该行为"] → 测试名与注释都写明是 RECORDED DEFECT、后果、以及修好后如何反转。
- [测试写太宽反而变成实现复述] → 断言选取**输入-输出契约与拒绝条件**（record 的 `condition` 值），不断言内部实现细节。

## Migration Plan

1. 真 import 加载模块，按函数分 7 个用例类。
2. 围栏探针 → 确认缺陷 → 写成锁定测试。
3. `_verify_boundary` 成功路径 + 四种拒绝。
4. 变异检查（三处）证明测试承重。
5. 门禁 + 归档。

**回滚**：纯新增测试文件，删除即可。
