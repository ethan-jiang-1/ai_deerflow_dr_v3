# Runtime Architecture

> 运行时与权威边界的摘要面；每个事实的权威是其 owning spec 与代码（`src/deerflow_deep_research/`）。
> 这里只缓存跨文件的边界图，不复制细节。面向操作者的完整解释见
> [`runtime-map.md`](runtime-map.md)。

## 边界图

- **研究认知引擎 = DeerFlow 原生能力**：lead agent 可读取 `deep-research` skill，按需派生
  subagent；框架侧没有静态研究图。harness 经 `runtime/client.py` 的显式绑定进入框架公共
  面（`make_stream_fn` 是唯一 stream 缝，per-call recursion limit）。
- **Harness 保留**：Run Bundle 生命周期（create/status/watch/cancel/refine/inspect 六动词，
  `cli.py` → `runtime/interaction/cli.py`；装配在 `runtime/entry.py`）、确定性控制边界（`engine/` validator / gate + `runtime/admission.py` / `runtime/ledger.py`）、
  journal 与 final report 投影、显式组成记录（`domain/bundle.py`：`fixture` / `mixed` /
  `all_real`；base 真实梯记录 `all_real`，fixture 配方如实报 `fixture`，`mixed` 为声明未接线的
  枚举成员——去留见其 owning change）。
- **DeerFlow 是宿主运行时，不 import 本包**；接线形态（embedded binding）由
  establish-embedded-wiring 定案，受 `check_harness_dependency_direction.py` 守护。
- **权威事实源**：Run Bundle 合同 = `run-bundle` spec；验收收口 = `run-admission` spec；
  入口面 = `entry-surface` spec。boundary 决策的历史推敲见
  [`_backlog/_done/_closed_plans/`](../../_backlog/_done/_closed_plans/README.md)。
