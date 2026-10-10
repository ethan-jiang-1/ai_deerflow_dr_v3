# Design: establish-lint-lane

## Context

基线（2026-10-10，`uv run ruff check src tests tools cli.py`，concise 口径计数）：
E501×22、I001×15、UP017×14、UP037×13、F401×10、E741×9、F821×7、UP012×5、UP035×4、
F841×3、E731×3、E402×2、B007×1（合计 108，61 条 `--fix` 可自动修）。
敏感点：`pump.py` 的 `PLAN_MARKER_*` 导入被标 F401——近邻 `extract_plan` 导入即带
`# noqa: F401 — domain owns the vocabulary; seam name preserved` 注释，同族导入的
去留必须按 seam 保留约定逐条判定；`test_entry_chain` 以 AST 锁 import 关系，任何
import 重排后必须 `make verify` 复绿。

## Goals / Non-Goals

- Goals：全树 `ruff check` exit 0；`make lint` 命令位 + COMMANDS 行 +
  change-practice 措辞恢复；无永久性整体豁免（个别例外用带理由的就地 noqa）。
- Non-Goals：CI canonical 序列、pre-commit 扩员、ruff 升级、select 规则集调整、
  任何运行时行为变更。

## Approach

1. **分级批次**（每批以 `UV_OFFLINE=1 make verify` 收口，红即停）：
   - 批 A（纯机械/局部）：UP012、UP017、UP037、UP035、E501（>120 行改写）、
     E741（`l` → 具名）、E731（lambda → def）、B007；
   - 批 B（import 排序 I001）：`--fix` 后逐文件核对——凡注释会被重排损伤语义的
     （如 `recording_deepseek.py` 的层位理由注释），就地 `# noqa: I001 — <理由>`；
   - 批 C（F401 逐条判定）：seam 保留 → 补 `# noqa: F401 — <理由>`（与
     `extract_plan` 同式）；确认无消费者且非 seam → 删；
   - 批 D（语义修复）：F821（future-annotations 下注解名未导入 → `TYPE_CHECKING`
     条件导入）、F841（刻意保留 → noqa 带理由；真冗余 → 删）、E402（sys.path
     注入既定模式 → noqa 带理由）。
2. **命令位**：Makefile `lint:` 目标 + `.PHONY`；红演示（临时违例文件 → lint 红 →
   移除 → 复绿，证明 lane 能变红）；COMMANDS 测试 lane 增行。
3. **措辞恢复**：`pyproject.toml` dev 组注释改为陈述现役事实；`change-practice.md`
   恢复 "run lint and tests"。

## Alternatives

- **`ruff --fix` 一把梭**——输在：批次边界失控；import 重排横越 AST 锁链与 seam 保留
  注释，红了无法归因到单批。
- **per-file-ignores 按文件类整体豁免**——输在：豁免面失去逐条理由，同文件新违规
  静默通过，违背"新守卫必须能变红"与信噪比初衷。
- **基线棘轮（钉住 108 只降不升）**——输在：把 108 条噪音永久化；绿是可达的，
  棘轮是为不可达绿准备的工具。

## Open Questions

none: CI 归属（本次不进）、基线策略（修绿而非棘轮）、敏感类处置（就地 noqa 带理由）
均已在 issue 卡与本设计定案。
