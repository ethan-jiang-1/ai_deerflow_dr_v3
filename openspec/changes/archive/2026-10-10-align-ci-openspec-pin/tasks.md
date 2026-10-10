# Tasks: align-ci-openspec-pin

## 1. 红先（常量先行，workflow/fixture 缺同步必红）

- [x] 1.1 `check_ci_governance.py` 钉定 `@fission-ai/openspec@1.13.1` →
      `@fission-ai/openspec@1.14.0`（WORKFLOW_REQUIRED_MARKERS 及文件内其它声明处）
- [x] 1.2 真树 `check_ci_governance.py` → 红点名 1.14.0 marker 缺失（退出码直测）
- [x] 1.3 governance 套件 → fixture 缺同步致红（退出码直测，不用管道）

## 2. 转绿（workflow + fixture）

- [x] 2.1 `.github/workflows/governance.yml` npm pin → 1.14.0；确认
      "generation-aligned (same as .agents/skills frontmatter)" 注释恢复为真
- [x] 2.2 `test_ci_governance.py` fixture 同步 1.14.0
- [x] 2.3 真树 checker 转绿 + 套件全绿（退出码直测）

## 3. 门禁与收口

- [x] 3.1 `openspec validate align-ci-openspec-pin --strict` 退出码直测
- [x] 3.2 `python3 openspec/governance/check_project_gate.py --phase closeout` 退出码直测
- [x] 3.3 `openspec archive align-ci-openspec-pin -y`（skip_specs）；归档后
      `git push origin master`，以 gh 观测远端 Governance Gate（1.14.0 首跑 +
      make lint 首跑）结论
      （push 后补录：archive+push 均完成；远端 run 38019200855 在更早的 doc hygiene
      步失败（上一提交的计数漂移），1.14.0 与 make lint 步未执行到——UNVERIFIED-
      remotely，待下一次治理路径 push 验证。）

## Deviation Register

- none: 尚未开始 apply；单方向单目标（升 1.14.0），偏离就地登记。

## Delivery Record

- **外部行为**: CI 的 OpenSpec CLI 代际 1.13.1 → **1.14.0**（workflow npm pin、checker
  钉定常量、测试 fixture 三处同步）——与本地 CLI 及 `.agents/skills` frontmatter 恢复
  代际一致；workflow 注释 "generation-aligned (same as .agents/skills frontmatter)"
  由失真恢复为真。CI strict-validation owner 从此与本地归档产物同代际。
- **影响面**: `openspec/governance/check_ci_governance.py`（marker 常量）、
  `.github/workflows/governance.yml`（npm pin）、
  `openspec/tests/governance/test_ci_governance.py`（fixture）。
- **实际跑了什么**: （退出码直读，apply 工作树）红先：改常量后真树 checker → 1
  （点名缺失 1.14.0 marker）、governance 套件 → 1；同步后：真树 checker → 0、
  套件 → 0、strict validate → 0、closeout gate → 0。
- **未执行的检查**: CI 上 1.14.0 首跑（strict-validation owner 与 npm 拉取）——push 后
  以 gh 观测；checker 对 frontmatter 的机器交叉核对未做（design Non-Goal，另立卡）。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）。
