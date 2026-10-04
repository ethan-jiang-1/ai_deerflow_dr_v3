# COMMANDS — 入口面（能处理什么，一行一条）

> 人与 agent 的入口菜单：这里只回答「能处理多少事情」，不写过程——每个需要过程的
> 条目给出指向 playbook 的路由，细节一律在路由目标里。动词语义与封闭命令集的 owner
> 是 entry-surface 能力（ENS-001）；治理门禁属于仓库根的治理目录。

## 研究 run（`cd deep_research_harness`）

```bash
python3 cli.py create "研究问题…" --config fixture   # 建束 + 前台运行（默认 fixture 梯：零凭证）
python3 cli.py create "研究问题…" --config base      # real 梯（$VAR 凭证由框架解析）
python3 cli.py watch <bundle_id>    # journal 投影，终态即退出
python3 cli.py status <bundle_id>   # 状态 + journal 摘要 + owner PID 活性
python3 cli.py cancel <bundle_id>   # 记录取消请求（泵协作终止）
python3 cli.py refine <bundle_id> "方向文本"   # generation+1 重跑
python3 cli.py inspect <bundle_id>  # journal 时间线 + 已采证据 + 装配快照
```

- 跑一个研究 / 展示结果 / 重跑：过程、完成判据与坑 → [playbook/run-research.md](playbook/run-research.md)

## 测试 lane

```bash
make install   # 依赖环境准备（可编辑 deerflow-harness 的接线随 wiring change 落地）
make test      # unittest 套件（stdlib，离线可跑）
make verify    # 应用单元门禁 = make test 的 gate 形态；任一测试失败即非零退出
make smoke     # 集成 lane（需先 uv sync：框架依赖环境）
make record-stream PROBLEM="…"   # 集成 fixture 录制（真实 API，显式 opt-in）
```

`make verify` 只承载 harness 自身测试，不读、不引、不执行任何 OpenSpec 内容。

## 能干什么（一段话答「HELP」）

跑项目并出新鲜回执（上面两个 lane）；建 harness 四层（domain / engine / agents /
runtime）；走 OpenSpec propose → apply → polish → sync → archive；诊断 / 评审 / TDD。
边界：`deerflow/` 只读；`.env`、`.agents/skills/`、gitignored 便利件是用户保留区；
规范语义的裁决交给人。
