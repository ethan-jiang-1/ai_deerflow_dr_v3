# Design

## Context

动机见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 既有导入规则 | `imports.py`（332 行、顶格）：分层方向、外部名白名单、fixture 配方——**无环检测** |
| 编排 | `facade.validate_project()` 按序调 7 步；`--imports-only` 只跑 `validate_imports` |
| 违规形状 | `ContractViolation(code, detail)` → `main()` 打印 `ERROR [code] detail` 到 stderr、退出 1 |
| 本仓既有的"合法环断点" | 函数内延迟导入（`cli._self_test` → `_battery`）、`if TYPE_CHECKING:` 块（`turn.py`） |
| 真实树现状 | 本会话两把已把治理侧环清零——新规则在真实树上应为**绿** |

## Goals / Non-Goals

**Goals:** 规则落在新模块且接入既有编排 · 真实树绿 · 两模块环与三模块环都能红 · 合法形态不误报 ·
体积表与登记同步。

**Non-Goals:** 不动 `imports.py` 与任何既有规则 · 不扩到 harness · 不做自动修复。

## Decisions

### D-1｜只算"模块级"导入：直接位于 `Module.body` 的 `Import`/`ImportFrom`

- **选**：只要导入语句的父节点是模块体（不在 `if`/`try`/函数/类里），就算一条边。
- **为什么**：**延迟导入正是本仓断环的既定手法**。若把函数内导入也算边，`cli._self_test` →
  `_battery` 就会被判成环——而那恰恰是本会话用来**消除**环的手段。把 `if TYPE_CHECKING:` 内的
  导入也排除，同理（它在运行时根本不执行）。
- **代价**：一个"藏在 `try:` 里的模块级导入"不会被算作边（罕见，且那种写法本身也不该依赖）。
- **换来**：规则与仓库的既定断环手法一致，零误报。

### D-2｜强连通分量，而不是两两互导

- **选**：Tarjan/迭代式 SCC，报出所有 size > 1 的分量。
- **为什么**：三模块环（A→B→C→A）同样是环，但**没有任何一对**是互导的——只查两两互导会漏掉它。
- **代价**：实现稍复杂（但 ~30 行足够）。
- **换来**：任意长度的环都能抓，且报告能列出整条环路径。

### D-3｜两种导入形态都解析到具体文件

- **选**：相对导入（`from .fixtures import x`）按当前包的层级解析到兄弟模块；绝对导入
  （`from gitio import run_git`、`from doc_hygiene_check import X`）先看**同目录**是否存在该
  模块/包，存在才算边。包名解析到 `pkg/__init__.py`。
- **为什么**：治理脚本靠"目录在 `sys.path` 上"用绝对导入引兄弟模块（`gitio`、`roots`、
  `markdown_fences`），而这正是本会话两处环里出现过的一种边（`_battery` → 包的绝对导入）。
  只看相对导入会漏掉入口文件与包之间的边。
- **代价**：需要"同目录同名模块"的存在性判断。
- **换来**：覆盖本仓实际使用的两种形态。

### D-4｜范围先限治理目录树

- **选**：只检查 `openspec/governance/`（含其子包）。
- **为什么**：本会话两处环都在这里；harness 侧有自己的分层矩阵（`imports.py`）但**环检测同样缺失**
  ——那是 follow-up，不在本把扩大范围（一次放行一把）。
- **换来**：真实树绿的可控性；范围写在模块 docstring 里，后续扩展有明确落点。

### D-5｜报告形状沿用既有 `ContractViolation`

- **选**：`ContractViolation("import.cycle", "…->…")`，每个分量报一条，环路径按字典序稳定输出。
- **为什么**：既有 checker 的调用方（CI、closeout、测试）都按 `ERROR [code] detail` 读；新规则
  沿用同一形状，不改任何消费者。
- **换来**：零消费者改动；输出稳定（可断言）。

## Risks / Trade-offs

- [误报 facade 再导出] → 再导出是**单向**的（facade → 实现），不是环；实测确认（真实树绿）。
- [误报包的 `__init__` 与子模块] → `pkg/__init__.py` 导入子模块是单向；子模块**若**在模块级
  反向导入 `pkg`（即 `from pkg import x`）才会成环——那正是应当被报出的形态（本会话
  `fixtures ↔ registry` 就是它）。
- [规则自身顶格] → 新模块独立入表；若超 50 行的函数出现，表里会计数并在闸下。
- [真实树意外有环] → 那说明本会话漏看了第三处；规则先跑真实树，若红则**先报告再修**（不为了让
  规则变绿而放宽规则）。
- [SCC 实现有 bug 导致漏报] → 用临时树里的两模块环与三模块环做**正向**证明（必须被报出），
  再用"真实树绿"做反向证明。

## Migration Plan

1. 建 `cycles.py`：模块枚举 → 模块级导入解析 → 图 → SCC → 违规。
2. 接入 `facade.validate_project()` 与 `--imports-only`。
3. 直接测试：临时树里种两模块环、三模块环（必须红）；合法形态（延迟导入、`TYPE_CHECKING`、
   facade 再导出、单向依赖）必须绿；真实树必须绿。
4. 体积表 + 登记；门禁；收口。

**回滚**：撤销 diff（新模块删除、facade 撤掉一步）。
