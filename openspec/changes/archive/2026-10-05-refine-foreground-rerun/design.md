# Design

## Context

现状事实链（全部代码级核实）：`cmd_refine` 只调 `bundle_actions.refine`（打印
"generation N started: …" 与 "state: active"）后返回；`run_foreground` 仅被
`cmd_create` 调用；`run_research` 首条消息固定读 `request/problem.txt`
（bundle.refine_request_relative 生成的 refine-N.txt 无人消费）；`rule_refine`
经 `replace()` 继承旧 owner_pid（已死）；`observe`（status）发现 active + 死
owner → `rule_crash_transfer` → failed-resume + journal "crash_detected"。
composition 由 create 从 config 推导（fixture→fixture，else→all_real），state
经 replace 继承到下一代。旅程测试 refine 段只断言 "generation 2" 与
"state: active"。ScriptedChatModel 按 cursor 重放脚本（不按输入区分），但
旅程测试逐子进程调用，可给 refine 子进程注入不同的 `DEERFLOW_FAKE_SCRIPT`。

## Goals / Non-Goals

**Goals:**

- "generation N started" 全真：创建 + 当场跑完 + 类型化终态 + 报告经既有准入。
- 消息 = 该代方向文档；owner = 活进程；梯 = bundle 自声明延续。
- 六动词集合、状态机规则、准入语义零变化；fresh_context API 变体行为不变。

**Non-Goals:**

- 不做 refine 的 `--config` 覆盖（梯延续即合同）；不做 fresh_context seed
  document 的运行侧消费（slim-restart 的既有未接线状态，另行立项）；不做
  worker/后台（第 5 轮裁决）；不接 `mixed` 梯。

## Decisions

1. **消息选择放 run_engine 而非 CLI**：`run_research` 读 state 后按
   `state.generation` 选文档（gen 1 → problem.txt；gen>1 →
   refine-{generation}.txt）。理由：消息语义是 run 的事实，未来任何调用方
   （工具、worker）自动获得正确消息；CLI 只做委托。缺文件 → read_text 响亮
   失败（FileNotFoundError 自带路径）。
2. **owner_pid 放 bundle_actions.refine（action 层）**：与 `start` 的
   `owner_pid or os.getpid()` 模式一致——动作层拥有进程身份，domain 规则保持
   纯净。重跑期间 status 探活的对象就是正在跑的 refine 进程。
3. **梯延续映射放 entry.py**：`config_name_for_composition(composition)` —
   {"fixture": "fixture", "all_real": "base"}；其余值（含 `mixed`）ValueError
   响亮点名。放装配层（entry 拥有 config 解析），不放 CLI。
4. **cmd_refine 复用 create 的完整呈现契约**：started 行（refine 后）→
   run_foreground（live renderer、pin、thread_id=refined.thread_id、
   config_name=映射结果）→ ImportError remedy 文案（词为 refine）→ 终态行 +
   state 行。不新造输出格式。
5. **旅程测试的重复 hash 问题**：同一脚本会给 gen2 相同回答 → validator 重复
   hash 拒收。解法：`_cli` 增加可选 env 合并参数；refine 子进程注入
   `DEERFLOW_FAKE_SCRIPT=[{"content": "…refined answer…"}]`（与 create 的默认
   回答不同）→ gen2 报告 admit。断言：returncode 0、"generation 2" 起始行、
   "state: completed"、report-gen2.md 存在、ledger admit 计数 ≥ gen2。
6. **测试布局**：新增 `tests/unit/interaction/test_refine_foreground.py`——
   cmd 接线（patch entrypoint.run_foreground 记录调用，断言 config/thread/pin
   传参）+ 映射函数表驱动；`test_run_engine.py` 加消息选择测试（gen2 handle，
   stream_fn 收到 refine-2 文本而非 problem）；`test_bundle_runtime.py` 加
   owner_pid 断言。全部红先行（现状分别因不调用/不发 refine 文本/继承死 pid
   而红）。

## Risks / Trade-offs

- [refine 变耗时命令（真实梯几十分钟）] → 裁决已接受（前台模型是第 5 轮
  合同）；playbook 同步说明。
- [重复 hash 让真实 refine 被拒] → 与 gen1 完全相同的回答本就该拒（validator
  既有语义）；旅程测试用不同回答覆盖健康路径。
- [gen>1 但 refine-N.txt 缺失] → 响亮 FileNotFoundError（带路径）；不静默回退
  problem.txt——回退才是谎言。
- [owner_pid 断言在测试里依赖 os.getpid 语义] → refine 在测试进程内调用，
  断言 refined.owner_pid == os.getpid()（同进程），确定性成立。
- [忘了从未实现清单移除 refine 项] → control-map 两处 + tests/README 两处 +
  playbook 两处均已列入任务清单逐一同步。

## Migration Plan

红先行（unit×4 组 + 旅程扩展跑 smoke 红）→ 四点实现 → verify+smoke 全绿 →
文档/spec 同步 → closeout 回执 → 归档。回滚 = revert（无 schema、无数据迁移）。

## Open Questions

无。fresh_context 的 seed document 消费是显式 not-in-scope（既有未接线状态，
如做需单独 change 并定义消息组装合同）。
