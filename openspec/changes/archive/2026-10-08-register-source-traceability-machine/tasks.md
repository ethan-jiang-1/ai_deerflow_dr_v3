# Tasks

## 1. 纯判定器（`engine/traceability.py`）

- [x] 1.1 新增 `SourceTraceReport`（frozen dataclass：`urls`/`traceable`/
  `untraceable` 三元组字段）与 `trace_source_urls(report_text: str,
  search_corpus_texts: Iterable[str]) -> SourceTraceReport`：D1 抽取/归一/子串
  判定；docstring 声明"证有记录支撑、不证记录为真"与已知边界（无 decode/
  变体归一）；`@impl` 标签登记。

## 2. 机器注册与 register 同步

- [x] 2.1 `engine/machines.py` 的 `DECLARED_MACHINES` 增加
  `source-traceability` 条目（不变量文本含"不证明记录为真"）。
- [x] 2.2 `docs/quality-register.md` 增加对应行（三列格式，证据 seam 指向
  新测试文件）。
- [x] 2.3 红证：临时删 register 行 → 漂移测试红（点名 source-traceability）
  → 还原 → 绿（守卫可红演示，退出码直测记录）。

## 3. 测试四件套（`tests/unit/engine/test_traceability.py`）

- [x] 3.1 fixture 钉样：回放 real-small-stream（现场驱动真实泵）→ 报告 6 URL
  全 traceable（探针实证值）。
- [x] 3.2 合成负例：引用 `https://example.invalid/never-searched` 的报告 →
  URL 进 untraceable。
- [x] 3.3 空语料 smoke（collector 惯例）：空语料 → 全部 URL untraceable。
- [x] 3.4 篡改语料：移除一条记录 → 该记录支撑的 URL 变 untraceable。

## 4. 验证与归档

- [x] 4.1 `UV_OFFLINE=1 make verify` 退出码直测；closeout gate；
  `openspec validate register-source-traceability-machine --strict`；
  `git diff HEAD --check`；gitlink 四件套 + skill 对齐。
- [x] 4.2 交付记录四段填实 + Deviation Register 终值。
- [ ] 4.3 archive → 回写 plan A 面落判（含"admission 化被探针否决"记录）。

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记。

## Delivery Record

- **外部行为**: "报告 URL 有无同 run 搜索记录支撑"从人肉复核变成注册在案的
  纯函数质量机器（source-traceability）；fixture 报告 6/6 可溯被钉为金样本；
  空语料/篡改语料/未知 URL 三类假绿路径全部被负例封死；register 漂移守卫对
  新机器名生效（红证在案）。
- **影响面**: `engine/traceability.py`（新增纯模块）、`engine/machines.py`
  （+1 机器）、`docs/quality-register.md`（+1 行）、`tests/unit/engine/
  test_traceability.py`（新增 4 测）；validator 闭集/runtime 零触碰；gitlink
  未动。
- **实际跑了什么**: 新测试 4/4 绿（0.021s）；漂移红证（删 register 行 →
  test_register_names_every_declared_machine FAIL 点名 → 还原 → OK）；
  `UV_OFFLINE=1 make verify` → 0；closeout gate → 0；validate --strict → 0；
  `git diff HEAD --check` → 0；skill 对齐 1.14.0。
- **未执行的检查**: admission 阻断化未做（探针证据否决，Alternatives 在案，
  未来需独立规范语义裁决）；URL 变体归一（decode/短链/重定向）未做（D1 明示
  边界，真实样本 c7f0d36f 的 jina.ai 疑似 fetch 截断类漏配，属该边界）；
  Sources 节结构解析未做（B 面及后续裁决面）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者授权全程推进，对交付负最终责任。
