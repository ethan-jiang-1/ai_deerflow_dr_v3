# Design: promote-lint-to-ci

## Context

`make lint` 本地全绿（establish-lint-lane），但 CI canonical 序列五步不含它。检查器以
`WORKFLOW_REQUIRED_MARKERS` 封闭清单校验 workflow，测试以 `VALID_WORKFLOW` fixture +
gut 型负例锁声明。另见既有漂移：ci-governance spec 的序列清单漏 `make smoke`
（2026-10-04 ci-integration-lane 以 skip_specs 入 CI）——本 delta 一并修正。

## Goals / Non-Goals

- Goals：canonical 序列六步化（+`make lint`）；checker marker、fixture、负例、
  spec delta、README 段五处同轮同步。
- Non-Goals：pre-commit hook 扩员（lint 属 CI）；lint 规则集；多 job/矩阵；
  OpenSpec CLI pin 对齐（独立 change）。

## Approach

1. **顺序**：`make lint` 放 `make smoke` 之后——`uv run --no-sync ruff` 依赖
   smoke 步 `uv sync` 建好的环境；改动最小且无需提前 sync。
2. **marker 同步三处**：checker `WORKFLOW_REQUIRED_MARKERS` + workflow 步骤 +
   `VALID_WORKFLOW` fixture（gut 型负例沿用既有形状：摘 `make lint` 必须失败）。
3. **红先**：先加 checker marker → 真树 `check_ci_governance.py` 红（workflow 缺步）
   + governance 套件红（fixture 缺步）→ 加 workflow/fixture 步骤转绿。

## Alternatives

- **lint 放 smoke 之前**——输在：`make lint` 的 `uv run --no-sync ruff` 需要已 sync
  的环境，提前则 CI 必须显式加 `uv sync` 步（多一步、慢）。
- **只加 workflow 步骤不改 checker**——输在：canonical 序列的封闭清单是漂移防护的
  本体，不进 marker 表的步骤随时可被摘掉。
- **顺带做 CLI pin 对齐**——输在：两个独立裁决混一个 change；pin 对齐单独成 change
  （随本 change 归档后立即立项）。

## Open Questions

none: 顺序、同步面、红先路径均定案；pin 对齐独立立项。
