# Design

## Context

tests/unit/ 13 文件扁平；tests/README 的 owner 表是当前唯一的 owner 来源。
Makefile `test` 从 `tests` 顶层 discovery（integration 因无 `__init__.py` 被跳过
——注释明示 deliberate）。required-paths 登记
`tests/unit/test_entry_composition.py`（entry-surface 组）与四个 tests 子目录。
7 个 unit 文件用 `Path(__file__).resolve().parents[N]` 锚定 harness root 或
fixtures（N=1 或 2）；contract 的 parents[3] 不动。文档引用测试路径 5 处
（quality-register、testing-and-evaluation）+ tests/README 全文 + control-map §7 +
research-process + run-bundle。计划 §3.4 给出目标结构与 owner 划分（含
"entry composition 归 interaction"）。

## Goals / Non-Goals

**Goals:**

- 目录即 owner：domain / engine / runtime / interaction 四包，每文件一个归属。
- 收集合同机器锁定：新 guard 证明 unit+contract 被默认发现、integration 默认
  排除，并能 planted-failure 变红。
- test ID 变化仅为登记过的前缀变化，before/after 清单入回执。

**Non-Goals:**

- 不动 contract/integration/fixtures 的文件位置与收集语义；不改 Makefile 命令
  与 proof-lanes registry；不改任何断言；不做 tests/README 的"验证菜单"全量
  重写（路径同步即可，菜单化留给后续按需 change）。

## Decisions

1. **owner 划分沿 tests/README 既有 owner 表**（不新造判定）：domain 规则 →
   domain/；engine 纯裁决 → engine/；Bundle 落盘、状态读取、准入落盘、运行泵、
   事件回放、posture → runtime/；渲染、命令面、playbook、entry 组合 →
   interaction/（计划 §3.4 明示）。
2. **guard 的断言集合**（新文件 `unit/test_collection_guard.py`，guard 自身留在
   unit 顶层——它守护的是**树形**而非某个 owner）：
   - `unit/{domain,engine,runtime,interaction}/__init__.py` 与 `unit/__init__.py`、
     `contract/__init__.py` 在场；
   - `tests/integration/` 递归无任何 `__init__.py`（隔离不变量，planted 红点）；
   - `unittest.defaultTestLoader.discover("tests")`（进程内，verify 环境已含
     PYTHONPATH=src）结果：每个 id 以 `tests.unit.` 或 `tests.contract.` 开头、
     零 `tests.integration.`、四个 owner 命名空间与 contract 各至少一个测试
     （不冻结文件清单，避免新增测试文件即碎）。
3. **parents[] 修正**：迁移文件统一 +1（`parents[2]`→`[3]`；
   test_event_stream_replay 的 `parents[1]`→`[2]`）；不做更聪明的锚点重写——
   最小 diff，且 guard/verify 全量兜底。
4. **红先行两段**：① guard 先落盘而 owner 包未建 → 红（缺包标记）；② 迁移完成
   后 planted `tests/integration/__init__.py` → guard 红 → 删除 → 绿。两段红证
   均入回执。
5. **ID 映射证明**：迁移前后全量 test ID 清单 diff，输出恰为
   `tests.unit.test_X` → `tests.unit.{owner}.test_X` 的成对替换；计数不变
   （125 + guard 自身）。
6. **文档同轮**：quality-register（5 处）、testing-and-evaluation（1 处）、
   control-map §7（12 处）、research-process（3 处 unit 引用）、run-bundle
   （2 处）、tests/README（目录图、owner 表路径、单文件命令示例）；required-
   paths 的 1 条路径更新。AGENTS/README/COMMANDS 无测试路径引用（已勘察）。

## Risks / Trade-offs

- [漏 bump 一个 parents[] 索引] → 文件读取 FileNotFoundError → 对应测试红；
  verify 全量兜底；逐文件 grep `parents\[` 复查。
- [文档漏改一条测试链接] → doc-hygiene 链接规则 + 迁移后全仓 grep
  `unit/test_` 复查。
- [guard 误冻结文件清单] → 断言只用命名空间覆盖与不变量，不用显式文件列表。
- [planted 标记忘删] → guard 在 verify 里持续红，不可能带病归档。
- [ID 前缀变化破坏外部消费者] → 勘察确认无 CI/脚本硬编码单测试路径；tests/
  README 命令示例同轮更新。

## Migration Plan

1. 捕获 before ID 清单；
2. 写 guard（红：owner 包未建）；
3. git mv 12 文件 + 4 个 `__init__.py` + parents[] 修正；
4. guard 绿 + verify 绿；捕获 after ID 清单与映射；
5. 文档/登记同轮；planted 红证；
6. closeout 双 lane + 回执。
回滚：revert 提交。

## Open Questions

无。
