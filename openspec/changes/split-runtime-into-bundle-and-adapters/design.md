# Design

## Context

runtime/ 顶层 12 模块（1445 行）+ interaction/ + contracts/ + fixtures/。import graph
勘察结论：

- **持久化簇**（互 import 密集）：atomic ← {admission, bundle_actions,
  bundle_state, journal, ledger}；bundle_state ← {admission, bundle_actions,
  journal, ledger}；journal ← {admission, bundle_actions}；ledger ← {admission}；
  外部消费者 = run_engine、entry、interaction/cli（懒 admission）、9 个 unit
  测试、1 个 integration、tools。专属测试 seam：test_bundle_runtime、
  test_admission_runtime、test_state_read_diagnosis（+ test_bundle_domain 在
  domain 侧）。
- **binding 簇**：client ← {entry, 3 测试, tools}；client → contracts.client_surface
  （顶层 import）+ snapshot_middleware（函数内懒 import）；subagent_posture ←
  1 测试（独立 checker）。snapshot_middleware 仅 stdlib（叶）。
- **fixtures/ 被 config 机器引用**：`config/fixture.yaml` 写
  `deerflow_deep_research.runtime.fixtures:ScriptedChatModel` /
  `:fake_web_search` —— provider 字符串是配置合同，挪包即 cutover，零收益。
- required-paths 逐文件登记：deerflow-wiring 组（client/run_engine/snapshot +
  contracts、fixtures 目录）；entry-surface 组（entry + interaction + tools）。
- 架构守卫按 `src/<pkg>/<layer>/` 前缀判层：子目录继承 runtime 层，四层
  ownership 与 import 方向不受包内重排影响（interaction/contracts/fixtures
  嵌套即为既有实证）。
- 基线（本 change 前直测）：`make verify` 125 绿；`make smoke` 9 绿；125 个
  test ID 已存档 `/tmp`（回执随附清单）。

## Goals / Non-Goals

**Goals:**

- runtime 目录名直接表达六种职责：interaction/、entry.py（assembly）、
  run_engine.py（execution）、bundle/（persistence）、adapters/、fixtures/。
- 零行为变化：test ID 逐项相同、verify/smoke 全绿、CLI 与 Bundle schema 不变。
- 簇内相对 import 保留（迁移面最小化），外部直接 cutover 无 shim。

**Non-Goals:**

- 不动 tests/ 文件位置（Phase 3）；不改 entry.py / run_engine.py 名字或内容
  语义；不动 config/ 与 provider 路径；不动 domain/engine；不新增 spec。

## Decisions

1. **簇划分以 import 证据为准**（迁移原则：两个以上消费者或独立测试 seam）：
   bundle/ 六件套（5×atomic 内部消费 + 4 个专属测试文件）与 adapters/ 四件套
   （client 消费 contracts+snapshot；posture 有独立测试）满足原则；
   entry.py（单文件、名字自说明、计划明示可保留）与 run_engine.py（单文件
   执行 seam、6 个外部消费者但迁移仅是改名收益）保留在顶层——这不是放弃
   而是原则的直接应用：**目录为职责群而设，不为每个文件设**。
2. **fixtures/ 不动**：config 机器引用是发布面合同，cutover 收益为零、风险
   为配置断裂。`mixed` 未接线枚举与本 change 无关。
3. **迁移顺序**（单次原子完成，不留中间态）：
   a. `git mv` 六件套 → bundle/、四件套 → adapters/，创建两个 `__init__.py`
   （一行职责 docstring，不复制地图）；
   b. 簇内 import 不动（`.atomic`/`.contracts` 等相对引用在包内继续成立），
   `..domain`/`..engine` → `...domain`/`...engine`；
   c. 外部消费者直接 cutover：run_engine（`from . import bundle_state` →
   `from .bundle import bundle_state`；journal 同理；懒 admission 两处）、
   entry、interaction/cli（顶层与懒 import）、测试与 tools；
   d. `runtime/__init__.py` docstring 更新为六职责路由。
   迁移中途运行一次测试捕获 **ImportError 红**（证明 seam 咬合），随后修复
   转绿——红证入回执。
4. **required-paths 更新**：deerflow-wiring 组 client/snapshot/contracts 三条
   路径加 `adapters/` 前缀（run_engine 留在原组原路径）；repo-skeleton 在
   runtime/__init__.py 旁补 bundle/ 与 adapters/ 的 `__init__.py` 两条（删除
   会响亮失败；与 interaction/__init__.py 登记先例一致）。entry-surface 组
   不动。
5. **文档同轮**：control-map §4 步骤 3/8/11 与 §7 表中
   bundle_actions/bundle_state/admission/ledger/journal/client/snapshot/
   posture 的链接加前缀；research-process 的 client/contracts/snapshot/
   posture 链接同步。entry/run_engine/interaction 链接不变。
6. **模块 docstring**：迁移文件现有 docstring 保留；两个新 `__init__.py`
   一句话声明职责边界（"state authority stays in domain; deterministic
   verdicts stay in engine"式），不写第二套地图。

## Risks / Trade-offs

- [漏改一处 import → ImportError] → 迁移中途红证正是 seam 证明；verify+smoke
  全量兜底；grep 复查旧路径零残留。
- [test ID 意外变化] → before/after 清单逐项 diff，必须零差异。
- [config provider 断裂] → fixtures 不动，provider 字符串零变化；contract
  mirror 测试锁配置解析。
- [注册表漂移] → required-paths 更新后 architecture checker 直测；删除旧路径
  条目避免幽灵登记。
- [懒 import 漏改] → 逐文件 grep `from .admission\|from .snapshot\|runtime.admission`
  等旧全路径，确认零残留后再跑门禁。
- [smoke 环境差异] → 基线已在本机直测绿（9 项）；迁移后同命令复测。

## Migration Plan

见决策 3 的顺序；回滚 = revert 提交（git mv 可逆，无数据/schema）。

## Open Questions

无。`runtime.research.ResearchGraphRecipe` 出现在架构 checker 的条件分支中
（当前树未触发、本 change 不触碰该面）；若未来 wiring change 落地该 recipe，
包路径再按其 owning change 处理。
