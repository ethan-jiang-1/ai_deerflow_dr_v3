# Tasks

## 1. 码集与裁决（`engine/verdicts.py` + `engine/validator.py`）

- [x] 1.1 `verdicts.py` RESULT_CODES：删除 `hash_mismatch`、新增
  `report_structure_violation`；docstring 同步。
- [x] 1.2 `validator.py` 新增结构常量（`REPORT_MIN_CHARS=200`/
  `REPORT_MAX_CHARS=200_000`、Sources 标题正则）与
  `_report_structure_problem(content) -> str | None`（UTF-8 解码 → 标题 →
  Sources → 长度，逐一命名违反面）；有序规则尾部、仅 `kind="final_report"`
  生效，渲染 `report_structure_violation`。

## 2. spec delta（已在 propose 落笔，apply 期核对）

- [x] 2.1 `specs/run-admission/spec.md` MODIFIED requirement 与
  `verdicts.py` 逐字一致；strict validate 绿。

## 3. 引擎测试（`tests/unit/engine/test_admission_engine.py`）

- [x] 3.1 闭集断言更新（新六码，`hash_mismatch` 出局）。
- [x] 3.2 结构红绿：合规 final_report → ok；四方面各一红（非 UTF-8 / 无标题 /
  无 Sources / 超下限），reason 点名对应面；超上限红。
- [x] 3.3 scoping 负例：同内容作为 `evidence` 提交 → ok（结构仅管 final_report）。

## 4. fixture 拟真升级（共享构造器 + 六处消费点）

- [x] 4.1 `runtime/scripted/__init__.py` 新增 `fixture_report(body: str) -> str`
  （D4 骨架；docstring 声明"仅供 fixture 模拟"）。
- [x] 4.2 `test_cli_journey.py`（create/refine 两脚本，保 "cost-side"）、
  `test_clarification_journey.py`（两脚本）、`test_plan_journey.py`
  （`_FINAL`/`_FINAL_UNMARKED`，相等断言随常量）、`test_wiring_smoke.py`
  （`_SCRIPT_CONTINUATION`）升级为 `fixture_report(...)`。
- [x] 4.3 `test_admission_runtime.py`（:198/:207 两处 final_report 内容）、
  `test_run_engine.py`（:491 AI 消息 content，保 "最终简报全文内容"）升级。

## 5. 验证与归档

- [x] 5.1 `UV_OFFLINE=1 make verify`（退出码直测）；`make smoke`（journey 全
  绿为契约可行证明）；closeout gate；validate --strict；`git diff HEAD --check`。
- [x] 5.2 gitlink 四件套 + skill 对齐；负例红证记录（结构断言任一违反面 → 红）。
- [x] 5.3 交付记录四段填实 + Deviation Register 终值。
- [ ] 5.4 archive（**含 spec sync**：MODIFIED delta 合入 run-admission 主规范）
  → 回写 plan B 面落判。

## Deviation Register

- D4 修正：`fixture_report` 的住处由 `runtime/scripted/__init__.py`（design D4）
  改为 `tests/fixture_reports.py`——scripted 模块 import langchain_core，unit
  离线车道不可依赖框架（import 链实测证据：unit 测试导入即 ModuleNotFoundError
  路径）。语义不变（仍是 fixture-only 构造器，stdlib 纯函数）；plan 旅程断言
  追加 `.strip()` 归一（真实 agent 链对最终消息做 strip 的实测行为）。裁决依据：
  离线门禁不可破；落在工件：`tests/fixture_reports.py` + 六处 import。

## Delivery Record

- **外部行为**: 结构空壳的 final_report 从此进不了 bundle——validator 渲染
  `report_structure_violation` 并点名违反面（编码/标题/Sources/长度包络）；
  死码 `hash_mismatch` 退役，封闭码集保持六码；journey/脚本 fixture 全部升级
  为拟真报告（旅程断言原文保留）。
- **影响面**: `engine/verdicts.py` + `engine/validator.py`（码集与结构规则）、
  run-admission 主规范（MODIFIED 已同步）、`tests/fixture_reports.py`（新增
  共享构造器，D4 修正后住处）、六个测试消费点升级、`tests/unit/engine/
  test_admission_engine.py`（闭集断言 + 结构红绿 + scoping 负例）。
- **实际跑了什么**: `UV_OFFLINE=1 make verify` → 0（含新结构测试）；`make
  smoke` → 0（15 tests，journey 升级后全绿）；红证：旁路结构规则 →
  test_headingless_final_report_is_rejected FAILED → 还原 → OK；closeout gate
  → 0；validate --strict → 0；gitlink `ceebf97f` 未动；skill 对齐 1.14.0。
- **未执行的检查**: 真实梯（base 真模型）未跑——真实报告对契约的合规性由
  replay 真实流（探针合规）与现存 runs 报告（探针合规）佐证，非统计结论；
  Sources 节内容语义未验（A 面机器管支撑，本面只管结构存在）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者授权全程推进（码集二选一裁决 D2 已在案），对交付负最终责任。
