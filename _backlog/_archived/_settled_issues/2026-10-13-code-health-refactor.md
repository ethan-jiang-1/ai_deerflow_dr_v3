# Issue: 代码健康度收敛——结构性债的分阶段清偿

> 立卡: 2026-10-13 ｜ 状态: 已结 ｜ 类型: Task ｜ 毕业门: 已过 → extract-doc-hygiene-test-battery ｜ 可关闭: 是

**问题与期望结果：** 2026-10-13 的三路深挖审计（harness src / governance checkers /
tests 各一路，AST 实测 + 逐文件阅读）发现：应用侧分层与纯度故事很强，但存在三座超大
治理脚本、一个 442 行内联测试函数、一批跨模块重复与死码，以及治理脚本**自身无人看守**
（没有机器物检查它们的体积与结构）。期望结果：每一处"要改就得改 4~7 个地方"收敛为
"改一处"；长函数与巨型文件进入**棘轮**（只降不升）；全过程零行为回归、逐阶段可回滚。

**当前情况：** 全部结论有实测支撑，基线已固化（见下）。**没有任何一处是"感觉不好"**——
每个数字都可由本文档末尾的命令重放。

**未决问题：** 阶段 1 的规划工件是否被接受（Change Focus 选择的三条 policy 是否齐、
31 条负例的迁移边界是否为 owner 认可）。

**下一步：** 阶段 1 规划工件已落树并过 plan 门禁（见「落地关联」），停在 **propose 接受
边界**等 owner 拍板。拍板后开 apply；本卡继续留在活跃区（尚未归档，按章程不打毕业门孔）。

## 已知与未决

### 基线（2026-10-13，rev ca748d8；命令与退出码见「落地关联」）

| 度量（AST 实测） | governance (12 文件) | harness src | harness tests |
|---|---|---|---|
| LOC | 5,677 | 4,128 | 5,335 |
| 函数 >50 行 | **16** | 8 | 2 |
| 函数 >100 行 | **6** | 3 | 1 |
| 最长函数 | **442** | 131 | 108 |
| 测试数 | 99 methods | — | 251 (unit 217 + contract 34) |

六条门禁全绿：governance 套件 exit 0；`check_doc_hygiene.py --self-test` exit 0；plain
exit 0；`check_project_gate.py --phase closeout` exit 0；`check_project_architecture.py`
exit 0；harness `UV_OFFLINE=1 make verify` exit 0（251 tests / 0.748s）。

### 已确证的结构性事实（每条都有 file:line）

1. **三座大山**：`check_change_guidance.py` 1473 行 / 68 模块常量 / ~40 函数；
   `check_doc_hygiene.py` 1196 行；`check_project_architecture.py` 1024 行
   （`load_manifest:139` 269 行 = 解析+校验+构造三段揉一起）。
2. **442 行单函数** `check_doc_hygiene.py:727` `_self_test()` 内含 **31 条负例控制**
   （`errors.append("self-test: …")` 计数 = 31），正是 `test-evidence-policy` 要求的
   "守卫必须能变红"；但它内联在模块里 → 该 1196 行模块**没有 unittest 文件**，
   只能靠 `--self-test` 跑。
3. **CI 路径硬契约**：只有一条命令字符串出现在 CI 与 hook 中——
   `python3 openspec/governance/check_doc_hygiene.py`（`.github/workflows/governance.yml:54`、
   `.githooks/pre-commit:10`）。它必须永远是那个可执行入口。
4. **治理脚本无人看守**：`check_project_architecture.py` 的逐行导入矩阵只遍历 harness
   源码根；`DOC_BUDGETS` 只管常驻指令文档（字符单位）。**没有任何机器物看着
   `openspec/governance/*.py` 的体积/结构**——这是它们长到 1473 行的机制原因。
5. **`change_guidance_kernel.py` 是空壳**：214 行里 10 个导出零外部引用
   （`ValidationIssue`/`ReviewSchema`/`ProfileSchema`/`CompositionSchema`/`missing_fields`/
   `selected_policies`/`validate_review_table`/`neutrality_issues`/
   `profile_completeness_issues`/`section_after_level2_heading` 全部 grep 计数 = 0），
   ~157 行死码；真在用的只有 `table_cells`(1)、`deviation_register_issues`(7)、
   `delivery_record_issues`(5)。11 个 checker 只有 1 个 import 它。
6. **6 份 git/subprocess 包装**（`check_project_architecture.py:587`、`check_release_face.py:53`、
   `selected-change-closeout.py:80/88/93`、`check_proof_receipts.py:34`、
   `test_upstream_pin_agreement.py:35`），错误处理互不一致；全目录唯一可注入接缝是
   `check_project_gate.py:109` 的 `runner=`。
7. **3 套互不兼容的 finding 通道**：`list[str]`（7 文件）、4 键 dict
   （`check_project_specs.py:132`）、抛出 `ContractViolation`。
8. **`check_change_guidance.py` 的 OCP 违规是可量化的**：加一条 review policy = 同一文件
   ≥7 处联动编辑（常量 :86/:89-115、`:175-187`、`LOCAL_POLICY_REGISTRY:192`、
   `PROFILE_DEFINITIONS:211-226`、3 个并行 if 块 `:1123-1162`）。
9. **应用侧唯一胖点**：`runtime/pump.py` 450 行实为 4 个模块（`_drive:320` 131 行 /
   `_consume_turn:84` 112 行 / 计划与澄清策略 / 交付提交 + watch 工具）；8 个位置参数、
   5 元组返回、`thread_id` 形参根本没用到。
10. **终端事件名是未注册字符串协议**，散在 4 处：写方 `pump.py:381,391,396,400,449`、
    分类器 `diagnosis.py:95-179`、渲染 `render.py:69-78`、状态→事件映射 `cli.py:95-101`。
    加一个结局 = 改 4 个文件（`classify:74` 因此 129 行 7 分支）。
11. **4 张并行注册表**：`domain/bundle.py:36`（`fixture|mixed|all_real`）、
    `assembly.py:71`（`fixture|all_real`，`mixed` 抛错）、`adapters/client.py:16`
    （`base|fixture|record`）、`cli.py:278`（`fixture|base|record`）。
12. **CAS 空转（行为问题，非卫生问题）**：`pump.py:420,431` 把刚读出的 state 传回
    `write_state`，而 `bundle_state.py:106` 内部又重读一次 → 那里的 revision 检查
    **永远不触发**（看起来有并发保护、实际没有）。
13. **死码与重复**：`bundle_actions.py:170` `write_unanswered_questions` **零调用者**，
    而 pump 在 `pump.py:432-442` 内联手写了同一件事（且未走 atomic）；
    `_now_iso` ×4、`_journal` ×2、`_msg_field` ×2、liveness ×2；
    `recording.py:76-97` 与 `scripted/replay_model.py:148-165` 各写一遍 journal 行格式。
14. **测试面**：临时 run-bundle 脚手架在 11 个文件各抄一遍；`_PIN = "c"*40` ×8；
    固定时间戳 ×6（+3 处裸字面量）；`_event` 构造器 ×2；journal 读取包装 4 个变体；
    `test_run_engine.py` 674 行 / 31 测试 / 1 个类（杂物袋）；唯一共享物是 25 行的
    `tests/fixture_reports.py`。
15. **政策缺口**：`test_collection_guard.py:64-82` 没有已知违规负例，
    而 `openspec/governance/test-evidence-policy.md:44-48` 要求"守卫必须能变红"。

### 三条决定计划形态的约束

- **约束 A（路径契约）**：CI/hook 按精确路径调用 `check_doc_hygiene.py` → 子目录分割的
  形态只能是「薄入口 + 真代码进包」，不能把入口搬走。
- **约束 B（无人看守）**：治理脚本无体积守卫 → 只重构不设守卫，必然长回来；守卫是计划
  的一部分，不是附加项。
- **约束 C（安全网）**：442 行函数是 31 条负例控制，不是垃圾 → 抽取的验收判据只能是
  「31 条断言标识在 diff 两侧一一对应」，少一条即回归。

### 未决（等待确认，不阻塞阶段 1）

- 阶段 3 新增 `code-budgets` capability 会把 specs 主干从 13 个提到 14 个，需同步
  根 `README.md:85` 计数钉死与 doc-hygiene 的 root-count 规则靶子（已在此登记，避免
  到阶段 3 才发现）。
- 阶段 2 会把 `selected-change-closeout.py` 改名为 `selected_change_closeout.py`
  （连字符文件名使其**无法 import、只能 subprocess 测**），涉及 ~6 处引用含
  `required-paths.toml`。

## 方案与取舍

### 已裁决（owner 2026-10-13）

- **D1｜`--self-test` 保留为薄委托**：命令、stdout、退出码全不变。理由：它已被
  `openspec/specs/doc-truthfulness/spec.md:171`（Scenario: The rule proves it can fail）、
  `openspec/governance/README.md:69` 与
  `deep_research_harness/docs/skills/deep-research/verification-receipt.json:18-21`
  引用为守卫变红的证据入口；退役它是可见的政策变更，不该由重构顺手做出。
- **D2｜体积守卫新建 `code-budgets` capability**：代码行数/函数长度预算独立成 capability，
  可独立演进；不复用 `doc-budgets`（其单位是"字符/常驻指令文档"，扩到"行数/代码"会污染
  既有语义）。
- **D3｜严格串行，一阶段一 change**：每阶段独立可归档、独立可回滚，符合本仓
  「一次放行一把」。

### 分阶段计划（每阶段 = 一个独立 change）

| 阶段 | 目标 | 规范归属 | 风险 | 机器回滚探针 |
|---|---|---|---|---|
| **0** | 基线固化 + 人工棘轮（本卡） | 无 spec 变更 | 无 | 六条门禁退出码 |
| **1** | 抽出 442 行内联套件 + 规则注册表化 | 无 spec 变更 | 极低 | ①`--self-test` exit 0 ②31 条负例计数不变 ③套件 ≥99 通过 |
| **2** | 三座大山拆为包（薄入口不变） | 无 spec 变更；registry 登记新目录 | 低 | ①closeout gate 全绿 ②各 checker CLI 文本+退出码逐字比对 |
| **3** | 去重收敛 + 删 ~157 行死码 + **加体积守卫** | **新建 `code-budgets`** + `project-structure` delta | 中 | ①全部 checker exit 0 ②`--imports-only` 不变 ③删死码后全绿 |
| **4** | 拆 pump + 统一注册表/终端协议 | **真行为 spec**：run-bundle / run-admission / entry-surface / deerflow-wiring | **高** | `make verify` + `make smoke` **不改一行测试**而全绿 |
| **5** | 测试共享支撑 + 导航改名 + 补负例 | 无 spec 变更 | 低 | 测试数只增不减；guard 负例能变红 |

阶段 1 的关键顺序（`Scope` 值对象 + `Rule` 注册表先行）：30 个模块级常量被 9 条规则共享，
`MARKER_ALLOWLIST` 还被 self-test 就地改写；不先做这个，抽出去的测试无法与规则同址。

阶段 2 的拆分形态（入口文件名全部不变）：

```
check_change_guidance.py 1473 → 入口 ≤120 + guidance/{intro_tree,focus_card,proposals,active_changes,registry}.py
                                              + guidance/reviews/{workflow_outcome,node_agent,control_placement}.py
check_doc_hygiene.py     1196 → 入口 ≤120 + doc_hygiene/{scope.py,rules/*.py}
check_project_architecture.py 1024 → 入口 ≤120 + architecture/{manifest,guide,paths,imports,gitlink}.py
```

### 考虑过的备选与风险

| 备选 | 为什么否决 |
|---|---|
| A1 一把大 change 全做完 | 阶段 4 触行为语义、阶段 1–3 是纯机械；绑在一起时阶段 4 一旦在证据面发难，整包卡在未归档状态。与 D3 同向。 |
| A2 把入口脚本搬进子目录当"整齐" | 直接撞约束 A：CI 与 hook 的精确路径断裂，且 `governance.yml`/`pre-commit`/spec 三处文案需同步——成本在契约面而非代码面。 |
| A3 用 `tests/governance/test_doc_hygiene.py` 取代 `--self-test` | 撞 D1：doc-truthfulness 的 Scenario 与既有 verification receipt 都以该命令为守卫变红的证据入口。 |
| A4 顺手修 CAS 空转（事实 12） | 它是**行为正确性**问题（"看起来有保护、实际没有"），走 bug 轨：症状→根因证据→`修好判据`→授权。夹在重构里改等于悄悄改状态机语义。 |
| A5 先不设守卫，靠人工棘轮 | 撞约束 B：1473 行就是这么长出来的。 |
| A6 重写而非重构（换更"现代"的 checker 框架） | 31 条负例 + 99 method 全是绿的既有资产，重写等于把它们全部降级为"未验证"。 |
| A7 只做应用侧、放过治理脚本 | 放过最大的一处债（5,677 行里 16 个超长函数）。 |

**风险与缓解：**

- [阶段 4 改可观察行为] → 不变量写成 tasks 验收行：journal 事件名集合与顺序逐字不变、
  终端转移结果不变、**本阶段不得改任何测试**（改测试即判该阶段失败）。
- [`--self-test` 双轨漂移] → 委托必须调**测试模块里的同一批负例函数**，不在模块内留第二份
  断言代码（单一事实家）。
- [阶段 2 拆包后入口与内部漂移] → 入口只做 argparse + 调包，并加契约测试钉住
  "入口不承载规则逻辑"。
- [阶段 3 加 guard 自身无负例] → 新守卫必须自带已知违规负例（`test-evidence-policy` 要求）。

## 落地关联

按 D3，一段一 change，串行推进；每段走 `propose → 红绿 → gate → archive`。

- **阶段 1（已落树，2026-10-13，状态：propose 待拍板）**：
  `openspec/changes/extract-doc-hygiene-test-battery`（`.openspec.yaml` 标注
  `skip_specs: true` —— 纯机械重构，零可观察行为变化，故零 spec delta）。
  plan 门禁 `check_project_gate.py --phase plan --change extract-doc-hygiene-test-battery`
  退出码 0；`openspec validate --strict` 退出码 0。拍板后开 apply。
- 阶段 2（拟）：`split-governance-checkers`
- 阶段 3（拟）：`establish-code-budgets`（含去重与死码清偿）
- 阶段 4（拟）：`decompose-run-pump`
- 阶段 5（拟）：`share-test-support-and-rename`

基线重放命令（本卡所有数字的来源，退出码直测）：

```bash
python3 -m unittest discover -s openspec/tests/governance -q
python3 openspec/governance/check_doc_hygiene.py --self-test
python3 openspec/governance/check_doc_hygiene.py
python3 openspec/governance/check_project_gate.py --phase closeout
python3 openspec/governance/check_project_architecture.py
cd deep_research_harness && UV_OFFLINE=1 make verify
```

## 关闭条件

**做**（已选）：结论 = 上述六阶段表 + D1–D3 裁决；验收 = 每阶段自身 change 的
Delivery Record 达标且六条门禁不回退。结论被阶段 1 的 change 吸收后按 ritual 关闭
（`git mv` → `_settled_issues/`，分配 CLS-025）。

---

## 结案记录（2026-10-16）

**verdict**：结论被阶段 1 的 change 吸收并归档 → `extract-doc-hygiene-test-battery`
（archived as `openspec/changes/archive/2026-10-16-extract-doc-hygiene-test-battery`）。

**已交付**：`check_doc_hygiene.py` 1196 → 863 行（内联 450 行电池体移除；`Scope` 冻结值对象
+ `RULES` 注册表取代 30 个模块全局量与手列调度）；负例电池落 `_battery.py`（39 条控制：
30 负例 + 9 绿控制）并由治理套件逐例跑成独立用例（套件 99 → 145 用例）；`--self-test` 保留为
薄委托，命令/stdout/退出码逐字不变。六条门禁全绿；harness 面零改动；9 条规则新旧产出
逐规则 IDENTICAL。

**阶段推进记录**（同一卡，逐段追加；本卡为长期收敛主卡，不因单个阶段归档而重开）：

- 阶段 1 `extract-doc-hygiene-test-battery` —— 已归档（2026-10-16）。
- 阶段 2 `split-governance-checkers` —— **已归档（2026-10-16）**：arch checker 1024 → 39 行
  （新包 `project_architecture_check/`）、guidance checker 1473 → 36 行（新包
  `change_guidance_check/`，三审阅策略改注册表驱动）、doc-hygiene 账本规则 182 → 20 行
  （三个子规则 73/35/39）；六 checker stdout 逐字不变、套件 145 不减、八条偏差在案。
- 阶段 4 `decompose-run-pump` —— **已归档（2026-10-16）**：pump.py 450 → 228 行；四职责各有
  其模块（turn 302 / gates 111 / deliver 38）；终端结局协议与四张组合注册表各自收敛为一张声明
  （`domain/outcomes.py`、`bundle.COMPOSITION_LADDERS`）；核心不变量达成——`make verify`（251）
  与 `make smoke`（30）在 **tests/ 一行未改**的前提下全绿，journal 序列/公共签名/注册表逐字
  等于基线。唯一未完成项：`_drive` 参数收窄 ≤4（行数 131 → 51 已达标），按偏差 1 显式留开。
  **教训（写给后续阶段）**：本地收口只跑了 verify/smoke，漏跑 `make lint`（ruff）车道，
  33 项违规由远端 CI 抓出（run 38867472817）。**harness 面每次收口必须跑齐
  verify + smoke + lint 三条**。
- 阶段 3 `establish-code-budgets`、阶段 5
  `share-test-support-and-rename` —— 未开工，各自需要独立 change；批准沿用本卡阶段表与
  D1–D3 裁决即可，无需重新推敲。

**落地关联**：`openspec/changes/archive/2026-10-16-extract-doc-hygiene-test-battery`
（2026-10-16，已归档）。
