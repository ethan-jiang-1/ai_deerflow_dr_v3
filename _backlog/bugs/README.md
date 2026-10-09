# Active Bugs — 活跃 bug 列表

>
> **bug 编号权威在 `_archived/_fixed_bugs/`；新 bug = 已分配的最大编号 + 1（已修复目录 ∪ 活跃目录），避免与活跃 bug 撞号。** 本文件只列活跃 bug。

## 修完一个 bug 的步骤

1. `git mv bugs/BUG-<NNN>-<slug>.md _archived/_fixed_bugs/BUG-<NNN>-<slug>.md`
2. 更新 `_archived/_fixed_bugs/README.md`（加表格行 + 更新 Next available bug ID）
3. 更新本文件（删掉该 bug）
4. 更新 `../_archived/README.md`（计数 +1）

查明了、还没修的，用 `git mv` 进 [`../_archived/_suspended_bugs/`](../_archived/_suspended_bugs/README.md)——挂起不是修好，**挂起跟显式指示走**，agent 不得自行挂起。

## 状态词表（机器校验，`check_doc_hygiene.py` 强制）

| 字段 | 词 | 说明 |
|---|---|---|
| `状态` | `活跃`（本目录）/ `待修`（查明未修进挂起池）/ `已修`（修好进归档） | 状态行内写 `状态: 活跃` 等，词必须在词表内 |

---

## 活跃列表

| Bug | 标题 | 发现 | 状态 |
|-----|------|------|------|
| [BUG-001-degenerate-plan-as-report.md](BUG-001-degenerate-plan-as-report.md) | 真梯连续两跑"计划走私 + 计划冒充报告"退化（CLS-018 病状复发） | 2026-10-10 | 活跃 |

**Next available bug ID: BUG-002**

---

新建 bug 文件 `BUG-<NNN>-<slug>.md`，`<NNN>` 取 `_archived/_fixed_bugs/README.md` 的 Next available ID：

```markdown
# BUG-<NNN>: <一句话标题>

> 严重级别: P0 / P1 / P2 | 发现: 2026-MM-DD | 状态: 活跃

## 症状
观察到什么错误行为（现场、报错、复现路径）。

## 根因
定位到的机制层原因（越到"契约/结构"层越好，避免只描述表象）。

## 复现
最小复现步骤 / 命令 / 输入。

## 修复关联
落地的 OpenSpec change 名称 + 版本；或说明为何拆成更窄的 follow-up。
```

> 约定：严重级别用 `P0`（阻断）/ `P1`（重要）/ `P2`（次要）。把每个 bug 当作**契约探针**——一个具体缺陷往往牵出一整类失败，值得顺藤摸瓜做横切排查，而不是只打一个孤立补丁。
