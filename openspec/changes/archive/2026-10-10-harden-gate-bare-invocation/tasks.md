# Tasks: harden-gate-bare-invocation

## 1. 红：治理 unittest 负例先行

- [x] 1.1 `openspec/tests/governance/test_project_gate.py` 新增负例：子进程裸跑
      `python3 openspec/governance/check_project_gate.py` → 断言 exit 2 且
      stderr/stdout 同时含 `--phase` 与 `openspec/governance/README.md` 两个锚点。
      Verify: `python3 -m unittest discover -s openspec/tests/governance -q` 该例红。

## 2. 绿：使用面落地

- [x] 2.1 `check_project_gate.py` argparse 加 `epilog`（两 phase 一行语义 + README
      指引）；缺参错误路径打印同一指引（`parser.error` 消息）。
      Verify: 1.1 转绿。
- [x] 2.2 语义回归：`--phase closeout` exit 0（六 checker 全绿）、`--phase plan`
      按既有语义退出——既有调用字节不变。Verify: 实测两回执。

## 3. 收口

- [x] 3.1 治理 unittest 套件全绿；closeout gate exit 0；
      `openspec validate harden-gate-bare-invocation --strict` 0。
- [x] 3.2 `openspec archive harden-gate-bare-invocation`（strict validate）；
      归档后复跑 closeout gate 0。

## Deviation Register

- none：apply 与 design 一致，无偏离。

## Delivery Record

- **外部行为**: 裸跑 `check_project_gate.py` 仍 exit 2，但错误输出携带 phase 契约指引（`--phase plan|closeout` + 治理 README）；`--help` 常驻同指引。判定语义零变化、`--phase` 无默认值（显式契约不放宽）。
- **影响面**: `openspec/governance/check_project_gate.py`（argparse 子类 error 钩子 + epilog）、`openspec/tests/governance/test_project_gate.py`（+2 负例/正例）。
- **实际跑了什么**: （退出码直读）红：治理套件 → 1（恰 2 条新例失败，Ran 94）；绿：同套件 → 0；裸跑 → 2 且双锚点在场；`--phase closeout` 回归 → 0；`--help` → 0 含指引。
- **未执行的检查**: none。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）。
