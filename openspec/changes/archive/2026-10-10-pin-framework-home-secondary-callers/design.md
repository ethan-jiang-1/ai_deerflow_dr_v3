# Design: pin-framework-home-secondary-callers

See proposal.md — Why. Mechanically, the framework resolves its home as
`$DEER_FLOW_HOME` else `Path.cwd()/.deer-flow`（`deerflow/backend/packages/harness/
deerflow/config/runtime_paths.py`）；`assembly.pin_framework_home()`（`FRAMEWORK_HOME =
REPO_ROOT / ".deer-flow"`，REPO_ROOT 自 `__file__` 推导、cwd 无关）只被
`run_foreground` 调用（assembly.py:144，AST 锁在 `test_framework_home.py`）。
smoke 两个文件与 record 工具绕过 `run_foreground` 直连 `build_client`，于是 cwd 兜底
把运行态写进应用子树。

## Decisions

1. **复用 `pin_framework_home()`，不新造机制**：三处调用点在构造 client 前显式调用。
   pin 函数已带子树内拒绝（响亮失败）与 REPO_ROOT 推导，本 change 零语义增量。
2. **锁用 AST contract，不锁行号**：沿用 `test_run_foreground_pins_before_client_construction`
   的模式，新增一个测试方法遍历三个目标文件的 AST：凡函数体内出现 `build_client`
   调用，则同函数体内必须存在更早的 `pin_framework_home` 调用（按 AST 出现顺序）。
   阶段内重构不误伤，漏 pin 即红。
3. **文档与实现同轮**：应用 README「注意 pin 只在 create/refine 的前台装配路径生效…」
   与控制地图目录树注（清扫轮 1bb28b2 写入的临时 caveat）同轮改为"全部入口已 pin"，
   并保留一句"框架运行态只落仓库根 `.deer-flow/`"。
4. **删本地第二家放在 green 之后**：`deep_research_harness/.deer-flow/` 是 gitignored
   运行态（15 thread 无 bundle 对应、memory sqlite、skill 投影锁），pin 落地后删除，
   并以 smoke 复跑 + 目录不存在断言收口——先删后 pin 会立刻再生，顺序不可反。

## Alternatives Rejected

- **Makefile 给 smoke/record-stream 设 `DEER_FLOW_HOME` env**：否——env 只覆盖 make
  入口，直接 `uv run python tools/record_stream.py` / IDE 直跑测试仍漏；且 AST contract
  锁不住 env 面。代码级调用是可锁定、可 greps 的接线点。
- **tests/integration 加 conftest 自动 pin**：否——unittest 无 conftest 机制（那是
  pytest 习语），引入隐式自动行为反而脱离本仓"显式接线 + 机械锁"的惯例。
- **只改文档承认第二家合法**：否——主干 requirement 明文"application tree holds
  product code, tests, docs, config, and tools only"，承认即违已批规范。

## Verification

红（AST 断言 3 文件全红）→ 绿（接线 + contract 全绿）→ `make verify` 0 →
`make lint` 0 → 删目录 → `make smoke` exit 0 且 `test ! -d deep_research_harness/.deer-flow`
→ 全套治理 checker 0 → 归档。
