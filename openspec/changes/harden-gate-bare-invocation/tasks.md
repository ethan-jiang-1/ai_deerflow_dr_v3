# Tasks: harden-gate-bare-invocation

## 1. 红：治理 unittest 负例先行

- [ ] 1.1 `openspec/tests/governance/test_project_gate.py` 新增负例：子进程裸跑
      `python3 openspec/governance/check_project_gate.py` → 断言 exit 2 且
      stderr/stdout 同时含 `--phase` 与 `openspec/governance/README.md` 两个锚点。
      Verify: `python3 -m unittest discover -s openspec/tests/governance -q` 该例红。

## 2. 绿：使用面落地

- [ ] 2.1 `check_project_gate.py` argparse 加 `epilog`（两 phase 一行语义 + README
      指引）；缺参错误路径打印同一指引（`parser.error` 消息）。
      Verify: 1.1 转绿。
- [ ] 2.2 语义回归：`--phase closeout` exit 0（六 checker 全绿）、`--phase plan`
      按既有语义退出——既有调用字节不变。Verify: 实测两回执。

## 3. 收口

- [ ] 3.1 治理 unittest 套件全绿；closeout gate exit 0；
      `openspec validate harden-gate-bare-invocation --strict` 0。
- [ ] 3.2 `openspec archive harden-gate-bare-invocation`（strict validate）；
      归档后复跑 closeout gate 0。

## Deviation Register

- none: 尚未开始 apply；批次与判定以 design 为准，apply 中若出现偏离就地登记。
