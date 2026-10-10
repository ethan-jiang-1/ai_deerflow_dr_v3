# Tasks: add-workflow-dispatch-trigger

## 1. 红先

- [x] 1.1 `check_ci_governance.py` 的 `WORKFLOW_REQUIRED_MARKERS` 增加
      `"workflow_dispatch:"`
- [x] 1.2 真树 `check_ci_governance.py` → 红（退出码直测）
- [x] 1.3 governance 套件 → fixture 缺 dispatch 致红（退出码直测）

## 2. 转绿

- [x] 2.1 `.github/workflows/governance.yml` 的 `on:` 块增加 `workflow_dispatch:`
- [x] 2.2 `test_ci_governance.py` fixture 同步 + 新负例（移除 dispatch 必须失败）
- [x] 2.3 真树 checker + governance 套件全绿（退出码直测）

## 3. 门禁与收口

- [x] 3.1 `openspec validate add-workflow-dispatch-trigger --strict` 退出码直测
- [x] 3.2 `check_project_gate.py --phase closeout` 退出码直测
- [ ] 3.3 `openspec archive add-workflow-dispatch-trigger -y`；核对主 spec 吸收
      dispatch 场景
- [ ] 3.4 push 后 `gh workflow run` 或直接以新 push 触发，观测远端 run：canonical
      六步 + 1.14.0 首跑 + lint 首跑的结论（这一步同时关闭 establish-lint-lane 与
      align-ci-openspec-pin 的 UNVERIFIED-remotely）

## Deviation Register

- none: 尚未开始 apply；触发语义与同步面以 design 为准，偏离就地登记。

## Delivery Record

- **外部行为**: CI 触发面在 push/PR 之外增加手动 `workflow_dispatch`（写权限者对 HEAD
  显式重跑同一 canonical 六步序列，无新增权限、无跳步）；触发器被 checker marker 钉死，
  无声摘除即红。ci-governance 主 spec 吸收 dispatch 语义（新增 "Manual dispatch
  re-runs the gate on HEAD" 场景）。
- **影响面**: `.github/workflows/governance.yml`（on: +1 触发器）、
  `openspec/governance/check_ci_governance.py`（+1 marker）、
  `openspec/tests/governance/test_ci_governance.py`（fixture +2 行、+1 gut 负例，
  10→11 tests）、`openspec/specs/ci-governance/spec.md`（MODIFIED 吸收）。
- **实际跑了什么**: （退出码直读，apply 工作树）红先：加 marker 后真树 checker → 1、
  governance 套件 → 1；转绿后：真树 checker → 0、test_ci_governance 11 tests OK、
  governance 套件 → 0、strict validate → 0、closeout gate → 0。
- **未执行的检查**: 远端 dispatch 首跑（任务 3.4：push 后观测 canonical 六步 +
  1.14.0 首跑 + lint 首跑——同时关闭 establish-lint-lane 与 align-ci-openspec-pin
  的 UNVERIFIED-remotely）。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）；
  触发器语义的规范语义拍板由驾驭者以"留下来的事儿都处理了"授权（2026-10-10）。
