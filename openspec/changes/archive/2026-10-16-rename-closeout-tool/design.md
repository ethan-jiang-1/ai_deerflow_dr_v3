# Design

## Context

动机见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 该脚本是否门禁组件 | **否**——`check_project_gate.py` 只注册 4 个组件（change-guidance / harness-dependency-direction / ci-governance / proof-receipts） |
| 谁调用它 | **无人以代码调用**；它是操作者手动工具（`verify-boundary` / `record-review` 子命令） |
| 活引用 | **8 处**（含 1 对"政策文本 ↔ checker 声明"、1 个体积上限键、1 条登记、1 张文档表、2 条文档命令示例） |
| 行数 / 体积上限 | **256 / 256**（正好顶格） |
| 治理套件用例数是否被 pin | **否**（无计数规则盯着它，故新增一条测试不会撞计数） |

**三条硬约束**

1. **命令行契约逐字不变**：子命令名、stdout、退出码——它是操作者工具，回执里会引用。
2. **`SCHEMA_VERSION` 保持原样**：`"selected-change-closeout/v1"` 是**已记录证据的数据模式标识**，
   不是路径。改名它会让既有回执与记录失效。
3. **政策文本与 checker 声明必须同改**：`openspec/config.yaml` 里那句政策文本与
   `change_guidance_check/constants.py` 里的声明字符串是**一对**，只改一边会让 guidance checker
   报声明漂移（那正是它的职责）。

## Goals / Non-Goals

**Goals:** 文件可被真 `import`；8 处引用与那对声明同步；命令行契约与数据模式不变；
新增一条测试把"可 import"钉住。

**Non-Goals:** 不拆脚本（改名只是解锁拆的前提）；不动 `.md` 的名字；不碰其他连字符文件。

## Decisions

### D-1｜只改 `.py`，`.md` 保持连字符

- **选**：`git mv` 只动 `.py`；`selected-change-closeout.md` 名字不变（但文档里引用该脚本的
  两条命令示例要改成新名）。
- **为什么**：连字符的问题只对 **Python 模块名**成立——文档不受 import 约束。改 `.md` 会多动
  两处登记（`required-paths.toml` 的 `.md` 条目 + `openspec/README.md` 的链接），零收益。
- **代价**：一对文件名字风格不一致。
- **换来**：改动面最小；`.md` 与它的历史链接全部继续有效。
- 备选：两个都改——否决：纯churn，且 `README.md` 的链接、登记条目、doc-hygiene 的
  文件存在性检查都要跟着动。

### D-2｜`SCHEMA_VERSION` 不改

- **选**：保持 `"selected-change-closeout/v1"`。
- **为什么**：它是**记录进回执的数据模式标识**（`@impl` 与 schema 字段），不是文件路径。改名它
  等于宣布"旧记录是另一个模式"，会让既有证据无法解读。
- **代价**：字符串里留着旧词。
- **换来**：历史回执继续可读；未来若真要改模式，走版本号（v2），而不是跟着文件名走。
- 备选：同步改成 `selected_change_closeout/v1`——否决：**混淆了"文件叫什么"与"记录是什么模式"**。

### D-3｜用**真 import** 而非 importlib 按路径加载来证明

- **选**：新增治理测试，把 `openspec/governance` 放进 `sys.path` 后
  `import selected_change_closeout`，断言模块暴露其 CLI 入口（如 `main`）且 `SCHEMA_VERSION`
  仍是 v1。
- **为什么**：既有治理测试一律用 `importlib.util.spec_from_file_location` **按路径**加载——
  那对连字符文件也管用，因此**证明不了改名要解锁的能力**。要证明"现在可以真 import"，测试就
  必须真的用 `import`。
- **代价**：测试里要临时操纵 `sys.path`（用 `addCleanup` 复原）。
- **换来**：改名这件事从此有**回归守卫**——谁把名字改回连字符，这条测试立刻红。
- 备选：不加测试，只靠人工验证一次——否决：那正是本仓库一直反对的"未钉住的保证"。

### D-4｜体积上限的键必须跟着改

- **选**：`check_code_budgets.py` 的 `"selected-change-closeout.py"` 键改为新名。
- **为什么**：该预算表按**文件名**索引；键不改，体积守卫对它就**静默失守**（不再度量），
  而它现在正好顶格 256 行——最不能失去守卫的时刻。
- **换来**：改名后仍被度量；顺带这次改名本身不该改变行数，所以上限值不变（256/1）。

## Risks / Trade-offs

- [漏改某一处引用 → 登记 `path.missing` 或文档命令跑不通] → 任务里逐处列出并逐一验证；登记面
  用架构 checker 的**变红实测**证明它真的在看这个文件。
- [政策文本与声明字符串只改一边 → guidance checker 报漂移] → 两者在同一提交内同改，并用
  `check_change_guidance.py` 的退出码验证。
- [体积上限键失守而无人察觉] → 任务里显式断言：改后 `check_code_budgets.py` 仍**度量**该文件
  （用一个临时超限探针或直接读表确认键存在）。
- [新增测试污染 sys.path] → 测试内 `sys.path.insert` + `addCleanup` 复原；并断言模块来自
  预期路径。
- [改到历史归档里的旧路径] → 明确不动 `openspec/changes/archive/**` 与 `_backlog/_archived/**`
  （那是当时的快照）。

## Migration Plan

1. `git mv` 改名。
2. 同步 8 处引用（其中 config.yaml 与 constants.py 必须同改）。
3. 新增"可 import"测试。
4. 跑：治理套件 · 六个门禁组件 · 脚本自身 `--help`/子命令 · 架构 checker（含变红实测）·
   体积闸（确认仍度量）。
5. 登记与文档同步；归档。

**回滚**：无运行时状态；回滚 = `git mv` 回原名 + 撤销引用同步。
