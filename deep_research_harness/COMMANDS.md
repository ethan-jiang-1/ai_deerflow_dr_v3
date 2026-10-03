# COMMANDS — 命令速查

> v3 的入口面（六子命令 CLI）由 entry-surface plan 的 owning change 定义后在此扩充；
> 当前已落地的目标如下。

## Harness（`cd deep_research_harness`）

```bash
make install    # 诚实 no-op：无外部依赖可装（deerflow-harness editable 源随接线 change 进入）
make test       # unittest 套件（stdlib，离线可跑）
make verify     # 应用单元门禁 = make test 的 gate 形态；任一测试失败即非零退出
```

`make verify` 只承载 harness 自身测试，不读、不引、不执行任何 OpenSpec 内容。

## 治理（repo 根，非 harness 命令）

治理门禁属于仓库根的治理目录（读其 README 的 Checker 命令一节）；本文件只登记
harness 自身的命令。

其余 CLI 子命令随各自 owning change 落地后在此登记。
