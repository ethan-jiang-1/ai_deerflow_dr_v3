# Design

## Context

根 `AGENTS.md` 2403/2425 字符（+22 余量），第 8 行是唯一等式失真点（toml 声明裸
commit 无病，已核验）。语料 38 文件 264K，自带 `verify.mjs`（Node 22 可跑，按
文件自身位置定位语料、只用内置模块）。`_reference/README.md` 有目录表 + 目录组织
两处索引格式。doc-hygiene 的 underscore 规则只扫 `_backlog` 顶层（`_reference/
_coverage/` 嵌套不触发，已核验源码 `_rule_backlog_underscore`）。驾驭者裁决
（2026-10-08）：原样复制进仓（Option A）。

## Goals / Non-Goals

**Goals:**

- 入口文件的 pin 表述与 git 事实一致，且可被一句话核验；
- 语料证据库进仓、自包含、可离线验证，出处与重审触发登记在案；
- "对上游论断必须钉定可核对"成为 deerflow-downstream 的成文纪律。

**Non-Goals:**

- 不 re-pin gitlink（`ceebf97f` 原地不动）；
- 不改语料任何内容（原样复制，出处登记放 `_reference/README.md` 而非改语料文件）；
- 不把语料 verify 纳入 CI 或任何 gate（它是语料自身结构自检）。

## Decisions

**D1 等式修正在一行内完成，净增量 ≤ +22 字符。**
现文："submodule 锁 \`ceebf97f\` = 上游 v2.1.0"；改为表达后代关系的紧凑形式
（如"submodule 锁 \`ceebf97f\`（v2.1.0 后代，digest 分支；v2.1.0=345f08be 为
祖先）"——最终措辞在 apply 时逐字计数，保证 ≤2425）。完整考古记录
（merge-base 命令、digest 分支名）不进入口文件，登记在 `_reference/README.md`
的语料条目与 plan 里。
备选落败：展开成多行说明（预算装不下，入口文件也不是考古现场）；只删等号不
说明关系（读者会继续猜）。

**D2 语料逐字复制，出处与重审触发住 `_reference/README.md`。**
语料 README 自述"复制全部内容并保留相对目录结构，即可独立阅读和验证"——动一个
字就破坏其 `verify.mjs` 与锚点体系。出处、钉定版本（v2.1.0 = `345f08be`）、复制
日期、源路径、重审触发全部登记在 `_reference/README.md` 的条目行，语料自身
`_coverage/` 维护页保持原貌（它的重审触发表继续有效，仓库侧触发器指向它）。
备选落败：摘编进仓（破坏证据链自包含性）；改写语料头部加仓内声明（动内容）。

**D3 钉定纪律三句话进 deerflow-downstream profile。**
①行为论断必须携带钉定引用（tag/commit）+ 核验方法；②上游文档默认为发布时
快照，引用以对源码的核验为准（语料 round-10 的手册快照实证为依据：integration-
guide 三处与 v2.1.0 源码不符）；③gitlink 前进（re-pin）时重审全部在案上游论断。
备选落败：纪律进根 AGENTS（预算不够且层次不对——upstream 事务属 profile）；
进 change-practice（C2 四类陈述已管"标注"，钉定方法属 deerflow-downstream 的
trigger 范围）。

**D4 验证矩阵**：复制品 `node verify.mjs` → 0；doc-hygiene/change-guidance → 0；
根 AGENTS 字符直测 ≤2425；`git merge-base --is-ancestor 345f08be ceebf97f` 取证
记入 Delivery Record；pin-agreement 测试随治理套件跑绿。

## Alternatives

- **语料只复制正文三卷、丢弃 `_coverage`/verify 脚本**：落败——维护层是钉定
  纪律的方法论本体（重审触发表、排除项、历史轮次），verify 是自包含性的保证；
  砍掉它们就是把语料降级为散文。
- **软链（symlink）代替复制**：落败——git 对 symlink 的跨平台行为脆弱，且
  本质仍是仓外依赖，没解决自包含问题。
- **把等式修正扩成独立"上游事实登记表"**：落败——超出 C3 规模；散布在案的上游
  论断清点属后续按需（C2 四类陈述规则已在 change 层面强制标注）。
- **顺手 re-pin gitlink 到 v2.1.0 tag 本身**：落败——digest 分支包含在用的研究
  材料，re-pin 是独立决策（会丢祖先内容），与本修等式 change 无关，明示不做。

## Risks / Trade-offs

- [语料与源头漂移] → 接受并管理：源头更新频率低（10 轮/生命周期），重审触发
  登记在案（上游 re-pin 或语料大版本更新时重对）；漂移不影响本仓运行时。
- [+22 字符装不下理想表述] → 措辞压缩到事实最小集（后代/非 tag/祖先 commit）；
  细节引用 plan 与 `_reference` 登记——入口文件保持路由密度。
- [38 文件稀释 `_backlog` 索引注意力] → 语料是 `_reference` 的下级目录（agent
  按任务按需读），`_reference/README.md` 一个条目行即可定位；不进任何活跃队列。
- [verify.mjs 对 Node 版本敏感] → 其 README 自述需 ESM+Unicode 正则的 Node（本轮
  Node 22 实测）；不进 CI 故不构成环境约束，复制时登记实测版本。

## Migration Plan

纯增量 + 一行改写，无运行时迁移。回滚 = revert AGENTS 一行 + 删除复制品目录 +
revert profile 小节。

## Open Questions

none: 处置已由驾驭者裁决（Option A），措辞与登记格式已定。
