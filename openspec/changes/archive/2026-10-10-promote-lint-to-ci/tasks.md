# Tasks: promote-lint-to-ci

## 1. 红先（marker 先行，workflow/fixture 缺步必红）

- [x] 1.1 `check_ci_governance.py` 的 `WORKFLOW_REQUIRED_MARKERS` 增加 `"make lint"`
- [x] 1.2 真树运行 `python3 openspec/governance/check_ci_governance.py` → 红点名缺失
      marker（退出码直测，记录红回执）
- [x] 1.3 `python3 -m unittest discover -s openspec/tests/governance -q` → fixture
      缺步致红（记录红回执）

## 2. 转绿（workflow + fixture + 负例）

- [x] 2.1 `.github/workflows/governance.yml` 在 `make smoke` 步后增 `make lint` 步
- [x] 2.2 `test_ci_governance.py` 的 `VALID_WORKFLOW` fixture 增对应步骤；新增负例
      "gut 掉 make lint 必须失败"（沿用既有 gut 形状）
- [x] 2.3 真树 checker 转绿 + governance 套件全绿（退出码直测）

## 3. 成文标准同步与门禁

- [x] 3.1 `openspec/governance/README.md` CI 段落序列描述同步（六步）
- [ ] 3.2 `openspec validate promote-lint-to-ci --strict` 退出码直测
- [ ] 3.3 `python3 openspec/governance/check_project_gate.py --phase plan --change
      promote-lint-to-ci` 退出码直测
- [x] 3.4 plan-review（control-placement 义务）：Control Placement Review 表与实现对照
- [x] 3.5 `python3 openspec/governance/check_project_gate.py --phase closeout` 退出码直测

## 4. 归档与远端

- [x] 4.1 `openspec archive promote-lint-to-ci -y`；核对 ci-governance 主 spec 已吸收
      六步序列
- [ ] 4.2 `git push origin master`；以 gh 观测远端 Governance Gate 新 run 的结论

## Deviation Register

- none: 尚未开始 apply；批次与判定以 design 为准，apply 中若出现偏离就地登记。

## Delivery Record

- **外部行为**: CI canonical 序列五步 → 六步（+`make lint`，置于 smoke 之后）——lint
  回归从此 push 即红，不再依赖本地自觉。ci-governance 主 spec 修正既有漂移
  （序列清单补记 make smoke）并吸收 make lint。
- **影响面**: `.github/workflows/governance.yml`（+1 步）、
  `openspec/governance/check_ci_governance.py`（+1 marker）、
  `openspec/tests/governance/test_ci_governance.py`（fixture +1 步、+1 gut 负例，
  9→10 tests）、`openspec/specs/ci-governance/spec.md`（MODIFIED 吸收）、
  `openspec/governance/README.md`（CI 段六步）。
- **实际跑了什么**: （退出码直读，apply 工作树）红先：加 marker 后真树
  `check_ci_governance.py` → 1（点名缺失 marker）、`test_ci_governance` 单跑 →
  FAILED (failures=1)——曾被我方管道 tail 吃掉退出码误读为绿，verbose 单跑实锤
  （本仓"退出码直测"教训的第三次现身，已记录）；转绿后：真树 checker → 0、
  governance 套件 → 0（10 tests 直测）、strict validate → 0、plan/closeout gate → 0。
- **未执行的检查**: 远端 Governance Gate 对本 change 提交的运行结果（push 后以 gh
  观测，见任务 4.2）；CI 上 `make lint` 首跑时长 UNVERIFIED-until-push。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）。

> 记录补录说明：本 Delivery Record 于 archive 之后、首次 commit 之前补实——补录原因
> 是 closeout 编辑竞争（python 批处理勾任务与记录填写竞争同一文件，与 establish-lint-lane
> 同型）；以上事实均为 archive 前已发生的 apply 回执，非事后构造。任务 3.5 于 archive
> 前已绿、4.1（archive 本身）随归档完成，勾选于此。
