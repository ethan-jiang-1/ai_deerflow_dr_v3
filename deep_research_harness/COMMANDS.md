# COMMANDS — 命令速查

> 六子命令入口面（establish-entry-surface）+ 测试 lane。治理门禁属于仓库根的治理目录
> （读其 README 的 Checker 命令一节）；本文件只登记 harness 自身的命令。

## 入口面（`cd deep_research_harness`）

```bash
python3 cli.py create "研究问题…" --config fixture   # 建束 + 前台运行（默认 fixture 梯：零凭证）
python3 cli.py create "研究问题…" --config base      # real 梯（$VAR 凭证由框架解析）
python3 cli.py watch <bundle_id>    # journal 投影，终态即退出
python3 cli.py status <bundle_id>   # 状态 + journal 摘要 + owner PID 活性
python3 cli.py cancel <bundle_id>   # 记录取消请求（泵协作终止）
python3 cli.py refine <bundle_id> "方向文本"   # generation+1 重跑
python3 cli.py inspect <bundle_id>  # journal 时间线 + 已采证据 + 装配快照
```

## 测试 lane

```bash
make test      # unittest 套件（stdlib，离线可跑）
make verify    # 应用单元门禁 = make test 的 gate 形态；任一测试失败即非零退出
make smoke     # 集成 lane（需先 uv sync：框架依赖环境）
```

`make verify` 只承载 harness 自身测试，不读、不引、不执行任何 OpenSpec 内容。
