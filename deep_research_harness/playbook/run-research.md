# Playbook: run-research — 被使唤「跑起来 / 跑一个研究」时按此执行

> 受众：执行 agent。动词清单只认 `../COMMANDS.md` 的入口面，本文件不复制——这里缓存
> 的只有：执行序列、退出码级完成判据、environment 招供不了的坑、回执纪律。
> 治理门禁属于仓库根的治理目录（读其 README 的 Checker 命令一节）。

## 快速 lane（日常使唤走这条）

前置：`cd deep_research_harness`；real 梯需要 `.env`（见坑节），fixture 梯零凭证。

1. **单元门禁**（离线，零依赖）：

   ```bash
   make verify
   ```

   完成判据：exit 0，打印 `[verify] harness unittest gate passed.`

2. **fixture 研究 run**（零凭证）：

   ```bash
   make create PROBLEM="研究问题"
   ```

   完成判据：exit 0，打印 `state: completed (generation 1, …)` 并给出 bundle id；留存 id。

3. **展示 run**（被要求更多输出时；动词细节问 `../COMMANDS.md`）：

   ```bash
   python3 cli.py status <bundle_id>
   python3 cli.py watch <bundle_id>        # 终态 run：渲染历史后退出
   python3 cli.py inspect <bundle_id>
   python3 cli.py refine <bundle_id> "补充方向"   # 创建 generation+1 并前台跑完该代（按需）
   python3 cli.py cancel <bundle_id>       # 协作终止（按需）
   ```

   完成判据：exit 0；status 打印状态与 journal 摘要；watch 对已终态 run 渲染历史后
   退出；inspect 打印 journal 时间线与已采证据计数；refine 创建新 generation 并当场跑完该代，落到类型化终态。

4. **交回回执**：命令 + 退出码 + 终态行。只报本会话实际执行过的 run——没跑过的命令
   不得当作结果报告。

## 冷启动 lane（发布证明，慢速；RLF-001——ID 已退役，沿革归档 change `2026-10-04-remove-requirement-id-tracking`，在仓库根治理目录——的 on-demand 全量证据）

全新两件套 checkout（harness + deerflow submodule）从零跑通全链路，证明发布面自足：

```bash
git clone --recursive <repo-url> /tmp/release-face-proof
cd /tmp/release-face-proof/deep_research_harness
uv sync
make verify
make create PROBLEM="发布面冷启动证明"
```

完成判据：五条命令全部 exit 0，最后一步打印 `state: completed (…)`。
环境不允许任何一步时，显式标注 UNVERIFIED 并说明是哪一步——不许伪造结果。
（真实路径回执见文末「最近回执」。）

## 坑（environment 招供不了的）

- `make create` 里裸写 `--config` 会被 make 本身吃掉（`unrecognized option`）。
  换梯走变量：`CONFIG=base`；`fixture` 是默认值。
- real 梯（`CONFIG=base`）需要本目录 `.env` 凭证。凭证属用户保留区：缺了就问，绝不代建。
- `make smoke` 需先 `uv sync`；`../.uv-cache` 一旦暖过，sync 只需毫秒级。
- smoke 里以 `RuntimeError: deliberate fixture failure` 收尾的 traceback 是响亮失败
  测试在通过——看退出码，别看噪音。
- 常驻告警：`langgraph` 实装版本新于 InMemorySaver delta-history patch 验证过的版本；
  平时忽略，升级 langgraph 前先复查该 patch。
- 冷启动 red 的第一类原因：clone 漏了 `--recursive`（或漏
  `git submodule update --init`）。守卫 `check_release_face.py` 会点名这一项。

## 回执纪律

上面的完成判据每条都要有新鲜回执背书（回执新于最后一次相关改动）。本文件事实过期
时，与发现过期的同一轮修掉本文件——过期的缓存比没有缓存更糟。

### 最近回执

- 2026-10-04（本 change apply 时）：`UV_OFFLINE=1 make verify` exit 0（112 tests）·
  `make create PROBLEM="发布面冷启动随行回执"` exit 0
  （`state: completed (generation 1, revision 2)`）。
- 全动词旅程回执（2026-10-04）：create exit 0（bundle `fe3f0fcf-…`，completed g1）→
  watch exit 0（历史渲染后退出）→ refine exit 0（generation 2 completed，报告 admit）→
  cancel exit 0（cancellation requested, generation 2）。
- 冷启动 lane 回执（2026-10-04，本 change apply 时）：本仓库 `git clone -q --recursive .`
  至 /tmp → `uv sync` exit 0 → `UV_OFFLINE=1 make verify` exit 0（unittest gate passed）→
  `make create` exit 0（`state: completed (generation 1, revision 2)`）；
  `check_release_face.py` 对该 checkout exit 0。
