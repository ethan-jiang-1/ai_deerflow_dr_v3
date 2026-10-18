# Design

## Context

动机见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 电池规模 | 724 行 · 57 函数 · 1 类 · 46 声明 · **104 顶层名** |
| 控制清单 | 43 条（31 负例 + 12 绿色），`NEGATIVE_CASES` 顺序 = CLI 报告顺序 = 测试用例顺序 |
| 上一把的成果 | 入口 901 → 87 行、环已断（电池改从包导入） |
| 本把发现 | `_battery.py` **此前从未在 `required-paths.toml` 登记**——它一直被"名字稳定"的假设保护着，但没有守卫 |

## Goals / Non-Goals

**Goals:** `_battery.py` 变薄且文件名不变 · 包内是干净 DAG · 43 条控制与清单 pin 不变 ·
104 个名零缺失 · `--self-test` 逐字不变 · 棘轮按实测重测 · 首次登记入册。

**Non-Goals:** 不改任何控制 · 不重构 `NegativeCase` · 不加"治理模块不得互导"的新守卫（记为 follow-up）。

## Decisions

### D-1｜两个模块 + 门面：按"夹具 vs 注册表"切

- **选**：`fixtures.py`（56 个构造器 + 其私用片段常量）· `registry.py`（`NegativeCase` · `_c` ·
  45 个用例 ID · `NEGATIVE_CASES` · 4 个运行器）· `__init__.py` 门面。
- **为什么**：电池的两半职责本就清楚——**造树**与**判定**。注册表引用构造器（`CONTROLS` 里每个
  条目带一个 `build`），反向不需要；这给出 `registry → fixtures` 的单向边。
- **代价**：两个模块 + 门面。
- **换来**：依赖方向可陈述；`fixtures.py` 可以独立被新用例复用（不必导入整张注册表）。

### D-2｜用例 ID 常量留在 `registry.py`

- **选**：45 个 ID 常量与 `NEGATIVE_CASES` 同处 registry。
- **为什么**：它们是**注册表的键**，测试既用它们取控制、也用它们断言存在。放一起可让"改了 ID
  却忘了注册表"这类漂移在同一文件里暴露。
- **代价**：registry 略大（378 行）。
- **换来**：注册表的自洽性在一个文件里。

### D-3｜两个片段常量归 `fixtures.py`（本把踩过的环）

- **选**：`_FENCE_ORPHAN_ROW` / `_FENCE_LEDGER_README` 放 fixtures（**不是** registry）。
- **为什么**：抽取器按"顶层赋值归 registry"的规则把它们放进了 registry，而 fixtures 里的围栏
  构造器要用它们 ⇒ **包内立刻出现环**（`fixtures ↔ registry`），导入即 `ImportError`。
  按**使用者**而非**语法形态**归属，环就没了。
- **代价**：归属规则不是纯语法的，需要看引用。
- **换来**：DAG 干净（`registry → fixtures` 单边）。

### D-4｜棘轮按实测重测 + 首次登记

- **选**：`_battery.py` 724 → **118**；3 个新模块入表；`_battery.py`、包目录与 3 个模块一并登记。
- **为什么**：`test_table_declares_the_largest_scripts` 会抓"最大脚本未入表"——本把第一次跑就
  被它抓到（`unmanaged top-five scripts: ['doc_hygiene_battery/fixtures.py']`）。
- **换来**：拆分永久锁定；且"名字稳定"的面第一次有了守卫。

## Risks / Trade-offs

- [包内再次出现环] → 本把已踩过一次（D-3）并由导入错误当场抓出；`registry → fixtures` 单边现在
  可陈述；后续若要加"禁止治理模块顶层互导"的自动化守卫，是 follow-up——**追记（2026-10-18）：已由 change `guard-import-cycles`（2026-10-17）落地**。
- [104 个名漏列] → 门面与 `__all__` 由脚本按最终归属生成，并逐个核对可达性（本把核到 104/104）。
- [清单 pin 或 `NEGATIVE_CASES` 顺序变了] → pin 由测试钉死（31/12/43），顺序即 CLI 报告顺序，
  测试逐条断言；本把未改动任何条目内容。
- [`--self-test` 依赖 `_battery` 的名字] → `_battery.py` 保留且再导出全部 104 个名。
- [棘轮漏改] → 闸与三条预算测试会报。

## Migration Plan

1. 按"夹具 vs 注册表"抽取两个模块（含 D-3 的归属修正）。
2. 门面 + 薄 `_battery.py`；套件绿。
3. 棘轮重测 + 登记；登记变红实测。
4. 行为零变化逐项对照；收口。

**回滚**：撤销 diff（包目录删除、`_battery.py` 恢复）。
