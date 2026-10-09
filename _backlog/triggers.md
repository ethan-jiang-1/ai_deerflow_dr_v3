# triggers.md · 活触发器索引

> 性质：**账本**（随行更新，非章程）。借鉴 `ai_dsh_assitant/_backlog/triggers.md`
> 的两个核心件——**索引行**与**扫一眼的义务**，不借其池。
>
> 延后不自动加行。延后的句子写在拥有该决定的已关闭卡或记录上，这里只收一件事：
> 不在这张表上，后来的人会把已经否掉的做法再做一遍，而且那条条件是**工作里自己会
> 撞上的一次观察**（一次跑、一份文件、一次审计、一次 change 入线）。一行一个观察，
> 并写明它出现的地方。「以后」「有空」「用户点名」不收——点名的动作本身就是触发。
> 常设指令或常设机制（如 DOC_BUDGETS 棘轮）已经在盯的，不收第二份。
>
> **扫描义务**：change 归档收口时、立新卡前的取代检查时、阶段收口时，扫一眼本表。
> **写行**：同一次改动里，那个错误真的会发生、观察也只有一个。
> **删行**：触发到场、按 owner 卡的写回规则重进后删行；裁决被推翻，改指向或删行；
> 下次扫的时候，如果必须先想起这张表才知道要看什么，这行就不是触发——删行，
> 句子留在 owner 卡上。

| 对象 | 裁决 | 触发条件（一次观察，出现在哪） | 家 |
|---|---|---|---|
| A5' 技能 review 面（adopt-skill-review-surface） | 降级为触发式，不预造 | 技能定制 change 入线时（该 change 的 proposal 阶段就会撞上） | [CLS-010](_done/_settled_issues/2026-10-04-test-doctrine-borrows.md) |
| 时长基线分片 | 规模门槛，触发前不预支复杂度 | `make verify` 常规跑中单元测试 >500 或 gate 时长 >3 分钟 | [CLS-010](_done/_settled_issues/2026-10-04-test-doctrine-borrows.md) |
| 迁移契约（逐 revision 回滚） | 规模门槛 | state schema 升 v2 的 change 入线时 | [CLS-010](_done/_settled_issues/2026-10-04-test-doctrine-borrows.md) |
| 行为断言 eval 栈 | 规模门槛 | 需要断言"研究质量"本身时；CLS-020 已判条件满足、工作仍未立项——首轮收割即抓到的沉底实证 | [CLS-010](_done/_settled_issues/2026-10-04-test-doctrine-borrows.md) |
| 跨栈契约 JSON / Playwright | 规模门槛 | 仓库出现前端目录/页面时 | [CLS-010](_done/_settled_issues/2026-10-04-test-doctrine-borrows.md) |
| 集成真服务（Postgres/Redis 语义） | 规模门槛 | 第二个持久化后端入线时 | [CLS-010](_done/_settled_issues/2026-10-04-test-doctrine-borrows.md) |
| playbook 预算化 | 刻意不做 | 文档审计发现 playbook 同类失控（一场景一文件/三类内容上限被冲破）再犯 | [CLS-011](_done/_settled_issues/2026-10-04-agent-playbook-and-minimal-release.md) |
| 回执机器守卫 | 刻意不做 | 发现回执被绕过或造假的实例 | [CLS-011](_done/_settled_issues/2026-10-04-agent-playbook-and-minimal-release.md) |
