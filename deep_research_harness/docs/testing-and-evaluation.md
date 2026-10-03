# Testing and Evaluation

> 应用侧测试政策的承接文档。lane 划分自首个 test-bearing change（establish-run-bundle）
> 起生效。

## Lanes

| Lane | Command | 覆盖 |
| --- | --- | --- |
| Application unit gate | `make verify`（= `PYTHONPATH=src python3 -m unittest discover -s tests`） | domain 纯规则（转移/检测/journal 策略）+ runtime 物化（CAS/lease/journal/删除语义） |
| Governance checks（governance-owned，非 harness lane） | 聚合治理门禁（repo 根治理目录的 README 登记确切命令） | 结构/需求/文档治理 |

## 原则（承接自 v3 方向）

红绿测试先行；每个新守卫过一次负例控制（引入违规 → 看红 → 还原 → 看绿——gate 本身也
要能变红）；测旅程不只测单元；零凭据确定性 seam 优先，凭据化 live 证据是补充且需显式
定界；本机无法验证的部分显式标注 UNVERIFIED。

交互/TUI/调试台/突变检查等 lane 随各自 owning change 落地后在此登记。
