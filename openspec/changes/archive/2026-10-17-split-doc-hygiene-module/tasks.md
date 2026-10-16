# Tasks

## 1. Break the cycle first

- [x] 1.1 Record the baseline: `--self-test` stdout and exit code, `failing_controls()` (must be empty), the inventory pin (31/12/43), the governance suite count (221) and the entry's public names (39)
- [x] 1.2 Create `openspec/governance/doc_hygiene_check/` with `constants.py` (the 16 declarations) and `scope.py` (`Scope`), moved verbatim
- [x] 1.3 Have `check_doc_hygiene.py` import those names from the package and re-export them; verify the governance suite passes and the battery still holds
- [x] 1.4 Switch `_battery.py`'s twelve names to the package (the cycle is now gone: both sides depend on the package, not on each other); verify the suite and all seven checkers pass

## 2. Move the rules

- [x] 2.1 Move the ledger/counter/hukou/placement helpers into `ledger.py` and the rule entry points plus `RULES`/`violations` into `rules.py`, verbatim
- [x] 2.2 Re-export the full public surface from the entry with an explicit block; verify all 39 public names are reachable and the suite passes
- [x] 2.3 Verify every violation message is byte-identical: run the seven checkers and compare their output against the baseline captures

## 3. Make the entry thin

- [x] 3.1 Move `main()` and the `--self-test` delegation into `cli.py`; the entry keeps only the facade, `__getattr__` fallback and the `__main__` call
- [x] 3.2 Compare `--self-test` stdout and exit code against the baseline from 1.1; verify byte-identical
- [x] 3.3 Verify the whole gate set: governance suite, seven checkers, closeout gate

## 4. Budget, registration, closeout

- [x] 4.1 Re-measure every file and update the budget table: lower the entry's ceiling to its measured value and add each new module at its own; verify the budget checker and its three tests pass
- [x] 4.2 Register the new package and its modules in `required-paths.toml`; verify the architecture checker exits 0 (with a mutation check: move one module away and confirm `path.missing`)
- [x] 4.3 Verify zero behaviour change as a set: `--self-test` line, `failing_controls()` empty, inventory pin 31/12/43, 39 public names reachable, suite count not reduced, harness untouched
- [x] 4.4 Fill this change's `## Delivery Record` with the four required labels and the raw receipts


- none: 本 change 只改实现位置与依赖方向；规则语义、消息文本、退出码、控制清单与公共面都不变。若搬移中发现某处**无法**在不改语义的前提下分离（例如某规则与 CLI 共享可变状态），按 core 原则记入本表并停下请裁决。

## Delivery Record

- **外部行为**: 零变化，逐项对照过：`--self-test` 输出**逐字**仍为 `doc-hygiene self-test passed.`、退出码 0 · **43 条电池控制全部成立**（`failing_controls()` 为空）· 清单 pin **31/12/43 不变** · 原始 **58 个顶层名在入口零缺失**（比提案承诺的 39 个更严：连私有名也一并核对）· 治理套件 **221 条不增不减**（含 46 条 doc-hygiene 测试与 CLI 契约测试）· 七 checker + closeout gate 全绿 · harness 面零改动。
- **影响面**: `check_doc_hygiene.py` **901 → 88 行**（薄入口：门面 + `__all__` + `__getattr__` 兜底 + `__main__` 调用）· 新增 `doc_hygiene_check/`：`constants.py` 230 · `ledger.py` 266 · `rules.py` 282 · `__init__.py` 143 · `scope.py` 67 · `cli.py` 47 · `_battery.py` 的 12 个名字改从包导入（**断环**）· `check_code_budgets.py` 入口上限 901 → **88** + 6 个新模块入表 · `required-paths.toml` 登记包目录（目录区）与 6 个模块（文件区）。
- **实际跑了什么**: 治理套件 exit 0（221）· 七个 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· `--self-test` 直跑：输出与退出码对照 · `failing_controls()` 直跑：空 · 58 个顶层名可达性脚本：零缺失 · **登记变红实测**：移走 `doc_hygiene_check/rules.py` → `ERROR [path.missing]` exit 1 → 恢复 exit 0 · **体积表按实测重测**（入口 88、六个模块各按实测）且闸与三条预算测试全过 · harness 改动行数 0。
- **未执行的检查**: `_battery.py`（724 行、仍顶格）**未拆**——本 change 只改它的导入来源（断环），其拆分是同一目标的第二把 · `Scope` 的冻结值对象**未重构** · 环形导入的**残留风险未用自动化守卫锁定**（没有任何 checker 检查"治理模块之间不得顶层互导"；本 change 消除了这一处环，但没有加守卫防止它再次出现）· 真实模型梯未跑。


## Deviation Register

- 偏差 1（AST 装饰器跨度，我第二次犯）：抽取器用 `node.lineno` 取定义文本，而**装饰器行在它之前**——`Scope` 因此丢了 `@dataclass(frozen=True)`，症状是 `TypeError: Scope() takes no arguments`，由治理套件当场抓红。阶段 4 已记录过同一坑，这次我仍踩了，故在生成器里写明注释（`start = min([node.lineno] + [d.lineno for d in decorator_list])`）。
- 偏差 2（登记表分区，被门禁抓出）：新包目录我一开始放进了**文件区**，架构 checker 报 `ERROR [path.kind] required file is not a file`。该表区分文件与目录两区，包目录须与另两个包并列。
- 正面记录（打破连续四把的偏差）：本 change **先写 propose/design/tasks、后实施**，没有再犯前四把"文档留到最后"的顺序问题——证明预算紧时也能按 ritual 顺序走，只要不把工件写成大部头。
