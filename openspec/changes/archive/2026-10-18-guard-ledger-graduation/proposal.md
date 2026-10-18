# Proposal: guard-ledger-graduation

## Why

账本（`_backlog/`）的**状态机与计数**已有守卫：状态词表按面校验、名册（每张卡被索引、每行索引
可解析）、计数表与磁盘名册一致、编号声明唯一且与分配一致、表格行必须落在真表格块里。**唯一没有
守卫的是"毕业翻转必须与实现同一把落地"**——也就是本会话我手工做过四次（BUG-003/004/005/006）
的那条纪律：状态翻 `已修`、`git mv` 进 `_archived/_fixed_bugs/`、两处索引与计数同步，**这些都该
和修复代码在同一笔提交里**。

**实测取证**（这决定了规则形态）：
- `修复关联` 里点名的 change 是否存在：**零检查**（全库 grep 零命中）。
- **git 实测 6 张已修卡**：全部由"也动了 `_backlog/` 之外文件"的提交移入——**这条纪律今天成立，
  包括我这四把**。也就是说：现在做守卫是"把已经遵守的纪律钉住"，而不是"救一个已经烂掉的地方"。

## What Changes

- **新增 `project_architecture_check/graduation.py`**：一条**历史**规则（不是结构规则）——
  对 `_backlog/_archived/_fixed_bugs/` 下每张卡，用 git 找出**首次加入**它的提交，要求那笔提交
  **至少改动了 `_backlog/` 之外的一个路径**。一张"独自落地"的卡（只有移动、索引、计数，没有实现）
  正是它要找的形态。
- **接进 `validate_project()`**（与"源码结构"和"仓库历史"两条规则一起，**刻意不在 `--imports-only`
  里**——那个 flag 的语义是"只验证导入契约"）。
- **优雅降级**：没有 git、卡未被跟踪、git 二进制不可用 ⇒ **沉默跳过**，而不是失败。治理侧大量夹具
  建的是**没有历史的临时树**，一条在那里失败的规则等于把自己的盲区报成违规。
- **新增直接测试**：红例（卡片单独提交）· 绿例（卡片与实现同一笔提交）· 两个跳过（未跟踪、无 git）。

**不变量**：既有判定**只增不改** · 七个 checker + closeout gate + 治理套件（250）全绿 ·
真实历史（6 张卡）仍绿 · harness 面零改动 · 体积表按实测 + `required-paths.toml` 登记。

## Capabilities

### New Capabilities

<!-- none: 加的是架构守卫的一步，不改任何 requirement 或产品契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **新增**：`project_architecture_check/graduation.py` · 其直接测试。
- **改**：`facade.py`（追加一步）· `check_code_budgets.py`（新模块入表）· `required-paths.toml`。
- **不动**：账本的任何卡片、索引、计数 · `gitlink.py` 与其余既有规则 · 任何一个被检查的文件。
- **触发车道**：治理套件 · 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/project_architecture_check/graduation.py`
  —— 它拥有"毕业翻转是否与实现同一把落地"这一判定；此前该判定**不存在**。
- **Seam classification:** deterministic-guardrail —— 纯历史分析（git log + show），无模型参与。
- **Question:** 一条读**仓库历史**的规则，能否在真实历史（6 张卡）上绿、在"卡片独自提交"上红、
  而在**没有 git 的夹具树**上沉默跳过——且不改变任何既有判定？
- **Necessary adjacent/external contracts:** `gitio.run_git`（answers: 共享的 git 调用层，从不
  解释退出码，错误姿态归调用方）· `gitlink.py`（answers: 既有"用 git 元数据"的范例与 raise 姿态）·
  `contract.py` 的 `ContractViolation`（answers: 违规形状）· 治理夹具（answers: 大量临时树没有
  历史，规则必须能跳过）。
- **Evidence seam:** 先期 git 实测（6/6 合规）· 红例/绿例/两个跳过逐条实测 ·
  真实树绿 · 变异检查 · 七 checker + closeout · 治理套件 250。
- **Not in scope:** 校验"修复关联点名的 change 是否存在"（**取证显示零检查**，但那需要解析自由文本
  的 change 名，判据比本条弱；留作 follow-up——**追记（2026-10-18）：已由 change `machine-readable-fix-reference`（2026-10-18）落地**）· 校验 `已落修`/`已修` 的时序 · 改任何卡片 ·
  非 Python 或非 git 的场景 · CAS 空转。
- **Triggered review policies:** local-context, change-admission
