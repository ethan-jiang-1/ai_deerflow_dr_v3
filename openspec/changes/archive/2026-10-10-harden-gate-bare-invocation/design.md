# Design: harden-gate-bare-invocation

See proposal.md — Why. The gate's judgment surface (phase dispatch, checker set,
exit codes) is pinned by ci-governance and its unittest suite; this change touches
only how a failed invocation explains itself.

## Decisions

1. **指引不加默认**：`--phase` 保持 required。默认 `closeout` 的诱惑被否——plan
   阶段（在途 change 的轻量 gate）与 closeout（归档前全量）语义不同，静默默认会把
   "跑错了 phase"变成"跑对了别的什么"。
2. **epilog + error 双落点**：argparse 的 `epilog=` 常驻 help；缺参错误走
   `parser.error()` 自定义消息（argparse 原生 exit 2 保留），两个落点都写
   `--phase plan|closeout` 语义一行 + `openspec/governance/README.md` 指引。
3. **负例断言文本锚点用稳定短语**：断言 `"--phase"` 与 `"openspec/governance/README.md"`
   同时在场（不锁整句措辞，留文案演进空间）。

## Alternatives Rejected

- **`--phase` 默认 `closeout`**：否——见决策 1。
- **裸跑改为打印 help 后 exit 0**：否——exit 0 会把"没跑成 gate"伪装成"跑过了"；
  失败必须非零（本仓退出码直测纪律）。
- **改 CI 调用方式或 wrapper 脚本**：否——canonical 序列的调用字节被
  `check_ci_governance` 钉死，为提示语去动声明面是反向的复杂度。

## Verification

治理 unittest 红（裸跑断言缺指引）→ epilog/error 落地绿 →
`check_project_gate.py --phase closeout` exit 0（语义回归）→ 裸跑 exit 2 且双锚点
在场 → 治理 unittest 套件全绿 → closeout gate 0 → strict validate → archive。
