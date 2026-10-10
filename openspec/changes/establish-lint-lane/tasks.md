# Tasks: establish-lint-lane

## 1. 取证与基线

- [ ] 1.1 存档红基线：`uv run ruff check src tests tools cli.py --output-format concise`
      全量输出入 issue 卡附录（108 条逐条对照批次的凭据）
- [ ] 1.2 `cd deep_research_harness && UV_OFFLINE=1 make verify` 取修改前绿回执

## 2. 批 A：纯机械/局部类

- [ ] 2.1 修 UP012/UP017/UP037/UP035（`datetime.UTC` 别名、去引号注解、
      collections.abc 导入、encode 参数）
- [ ] 2.2 改写 E501 超长行（22 处，语义不变）；E741 `l` 具名化；E731 lambda→def；
      B007 循环变量 `_` 前缀
- [ ] 2.3 批 A 后 `UV_OFFLINE=1 make verify` 红→绿确认（exit 0 直测）

## 3. 批 B：I001 import 排序

- [ ] 3.1 `--fix` 排序后逐文件核对：注释语义被重排损伤的（`recording_deepseek.py`
      层位理由等）就地 `# noqa: I001 — <理由>`
- [ ] 3.2 批 B 后 `UV_OFFLINE=1 make verify`（`test_entry_chain` AST 锁链专项确认）

## 4. 批 C/D：F401 判定 + 语义修复

- [ ] 4.1 F401 逐条判定：seam 保留 → 带理由 noqa（与 `extract_plan` 同式）；
      真无用 → 删；`PLAN_MARKER_*` 以 grep 消费者 + `test_entry_chain` 断言为准
- [ ] 4.2 F821 注解名 → `TYPE_CHECKING` 条件导入；F841 刻意赋值 → 带理由 noqa、
      真冗余 → 删；E402 sys.path 既定模式 → 带理由 noqa
- [ ] 4.3 批 C/D 后 `UV_OFFLINE=1 make verify` exit 0

## 5. 命令位与接线

- [ ] 5.1 `Makefile` 增 `lint:`（`UV_CACHE_DIR=… uv run --no-sync ruff check src tests
      tools cli.py`）+ `.PHONY` 同步
- [ ] 5.2 红演示：临时违例文件使 `make lint` 非零 → 移除 → 复绿（退出码直测，
      证明 lane 能变红）
- [ ] 5.3 `COMMANDS.md` 测试 lane 增 `make lint` 行（含"需 uv sync"前提说明）
- [ ] 5.4 `pyproject.toml` dev 组注释更新为现役事实；`change-practice.md` 措辞恢复
      "run lint and tests"

## 6. 门禁与收口

- [ ] 6.1 全树 `make lint` exit 0；`UV_OFFLINE=1 make verify` exit 0；
      `make smoke` exit 0（旅程 lane，操作者可见面未变仍须绿）
- [ ] 6.2 `python3 openspec/governance/check_doc_hygiene.py` exit 0（COMMANDS 行进
      入口预算面）；`openspec validate establish-lint-lane --strict` 退出码直测
- [ ] 6.3 `python3 openspec/governance/check_project_gate.py --phase closeout` 退出码直测
- [ ] 6.4 issue 关闭 ritual：`git mv _backlog/issues/2026-10-10-lint-lane-establishment.md
      _backlog/_archived/_settled_issues/`（文件名不变）；`_settled_issues/README.md`
      加行（CLS-022）+ Next ID → CLS-023；`issues/README.md` 删活跃行 + Next ID →
      CLS-023；`_archived/README.md` 计数 21→22、Next ID → CLS-023；卡头状态改
      `已结（establish-lint-lane）`

## Delivery Record

- **外部行为**: （closeout 时填写——本 change 无产品运行时行为：lint lane 命令位、
  COMMANDS 菜单行、全树 `ruff check` exit 0。）
- **影响面**: （closeout 时填写——预计约 20 个 src/tests/tools 文件 + Makefile /
  COMMANDS / pyproject / change-practice。）
- **实际跑了什么**: （closeout 时填写——命令与退出码直读。）
- **未执行的检查**: （closeout 时填写——如 CI 远端序列 UNVERIFIED-until-push。）
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）。

## Deviation Register

- none: 尚未开始 apply；批次划分与处置策略以 design 为准，apply 中若出现需要偏离
  design 的决定（如某 F401 的 seam 判定与预期相反），就地登记于此并给出裁决依据。
