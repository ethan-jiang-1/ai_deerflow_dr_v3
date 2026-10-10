# BUG-002: check_doc_hygiene 的账本 Next-ID 校验读不到活跃 README 的声明——同一文件两个 Next-ID 漂移全绿通过

> 严重级别: P2 | 发现: 2026-10-10 | 状态: 已修（harden-backlog-next-id-guard，archive 2026-10-10-harden-backlog-next-id-guard：Next-ID 声明唯一性/一致性双门禁 + self-test 负例×2 + ∪ 推导单源化 `_allocated_numbers`；红先回执与门禁退出码见 change Delivery Record）

## 症状

`_backlog/issues/README.md` 同一文件出现两个 "Next available issue ID" 声明（头注滞留
CLS-021，活跃列表末行 CLS-022）；CLS-021 已被占用（`_archived/_settled_issues/` 台账
CLS-021 行在案），照头注取号会撞号。期间
`python3 openspec/governance/check_doc_hygiene.py` 退出码 0——治理 README 宣称校验
"计数与 Next-ID"，此漂移未被抓住。2026-10-10 全库文档审计发现。

## 根因

`check_doc_hygiene.py` 的账本一致性校验只解析 `_backlog/_archived/README.md`
（`BACKLOG_COUNTERS_FILE`，模块 :270 在案）的表格行做计数/Next-ID 断言；Next-ID 推导
只读台账 index（`_settled_issues/README.md` 表格行）与磁盘文件名。活跃/归档各 README
里**人读的 Next-ID 声明行不在任何校验路径上**。同一事实声明多份拷贝（本例 4 份：
头注、正文末行、counters 表、台账权威行）而只有 1 份被机器盯住，漂移是时间问题。

## 复现

修复前版本：`git show 2d9a3f8:_backlog/issues/README.md`——头注 `Next available issue ID: CLS-021`
vs 末行 `Next available issue ID: CLS-022`；同树执行
`python3 openspec/governance/check_doc_hygiene.py` → exit 0（doc-layer hygiene passed）。

## 修复关联

**2026-10-10 同日已做（发现当日实作，红绿在案）**：立本卡过程中，把活跃 BUG-002 计入
号池后 counters 行改 BUG-003，门禁随即红（`next-ID mismatch … allocation implies
BUG-002`）——暴露推导模型缺陷的第二个实例：checker 只扫归档目录，无视账本成文法则
"已修复目录 ∪ 活跃目录"（bugs/README 与 _fixed_bugs/README 均明文）。已修
`check_doc_hygiene.py`：Next-ID 推导扩为 ∪ 模型（`BACKLOG_ARCHIVE_TO_ACTIVE`）+
`--self-test` 负例（archive-only 声明看红、∪ 一致声明保持绿）。

**仍开放（本卡保持活跃的原因）**：①各 README 内 Next-ID 声明行的**唯一性**校验未实现
（多声明点仍无门禁，本次手工去重只是临时防线）；②change `harden-backlog-next-id-guard`
仍未入线——剩余硬化随该 change 走正式红绿。
