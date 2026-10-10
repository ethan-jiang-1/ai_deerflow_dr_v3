# Issue: lint lane 缺位——ruff 已配置、基线 108 违规、无命令位

> 立卡: 2026-10-10 ｜ 状态: 已结（establish-lint-lane，archive 2026-10-10-establish-lint-lane：全树 ruff 108 → 0、make lint 命令位 + 红演示、COMMANDS 行、change-practice 措辞恢复）｜ 类型: Task ｜ 毕业门: 未过 ｜ 可关闭: 否

**问题与期望结果：** `pyproject.toml` dev 组已配 ruff（select E/F/I/UP/B/ASYNC、
line-length 120，注释自认 "CI does not enforce it"），但仓库内不存在 lint 命令位
（Makefile/COMMANDS 均无），而 `change-practice.md` 曾要求每个 slice 收口
"run lint and tests"。期望：`make lint` 命令位存在且全绿、进 COMMANDS 菜单、
change-practice 的 lint 措辞恢复成立。

**当前情况：** 2026-10-10 基线实测 `uv run ruff check src tests tools cli.py` = 108 违规
（61 条可 `--fix` 自动修）。风险点：部分 F401 是**有意的 seam 名保留**（`pump.py` 的
`PLAN_MARKER_*` 导入，近邻 import 即带 `# noqa: F401 — seam name preserved` 注释；
`test_entry_chain` 以 AST 锁 import 关系，任何 import 重排/删除必须红绿验证）；
F821 均为 future-annotations 下注解名未导入（运行时无害，类型检查破）；
个别 F841 是带"kept for introspection"注释的刻意赋值。直接加 `make lint` 等于交付
一条长期红的 lane——本次审计选择立卡而非上红门禁，change-practice 措辞先对齐为
"run the tests"。

**未决问题：** 基线处置策略（全量修绿 vs per-file-ignores 棘轮豁免刻意模式）；
lint 是否进 CI canonical 序列（`check_ci_governance.py` 声明面需同步）；函数内 import
带理由注释的 quirk 用 noqa 还是重构上移。

**下一步：** propose change `establish-lint-lane`：先钉基线快照与负例，再分级修复
（纯机械类 --fix 逐批红绿；敏感类手工 + 就地理由），最后 `make lint` target +
COMMANDS 行 + change-practice 恢复 "lint and tests" 措辞，本卡按 ritual 关闭。

## 已知与未决

已知：ruff 版本下限 `>=0.14.11`；`.ruff_cache/` 已在仓库根存在（说明曾跑过但未收口）。
未决：见上。

## 方案与取舍

全量 `--fix`（快；但 import 重排有撞 AST 锁链测试与 seam 保留约定的风险）vs 分级手工
（慢；可控、每批可红绿）vs 豁免棘轮（诚实保留刻意模式；扩大豁免面需逐条理由）。
倾向：分级手工 + 带理由的 noqa + 必要处 per-file-ignores；自动修复仅限无争议类
（I001 排序中不含 seam 保留注释的、UP012/UP017/UP037）。

## 落地关联

待 propose `establish-lint-lane`；修绿并接线后本卡关闭。

## 关闭条件

四态之一——默认"做"：`make lint` 全绿 + COMMANDS 登记 + change-practice 恢复措辞 +
新鲜回执（命令/退出码/revision）。

## 附录：红基线取证（2026-10-10）

- 基线 revision：`868d4f0`（审计修复 + change① 归档后的树）
- 复现命令：`cd deep_research_harness && UV_CACHE_DIR=../.uv-cache uv run --no-sync ruff check src tests tools cli.py --output-format concise`
- 结果：exit 1，**108 violations**（rule census：E501×22、I001×15、UP017×14、UP037×13、
  F401×10、F821×7、UP012×5、F841×3、E731×3、E402×2、B007×1、UP035×4）
- 逐条凭据：由上命令于该 revision 复现（避免 11KB 逐条清单永久入卡——信噪比裁定，
  见 change 的 Deviation Register）。
