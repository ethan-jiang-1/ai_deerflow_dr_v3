# Design

## Context

证据见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 全仓唯一 skip | 它的消息点名激活条件：`test_deerflow_public_api.py` lands |
| 镜像 | `contracts/client_surface.py` 六组声明（构造参数 10 项含 placement · 4 事件族 · 4 个 values 字段 · 消费的默认值 · checkpointer seam · stream 两 kwarg） |
| 真身可静态验证 | `DeerFlowClient.__init__` 逐项逐序逐 placement 一致 ✓ · `StreamEventType.__args__` 四族一致 ✓ · `PatchedChatDeepSeek` 是类 ✓ · `SqliteSaver.from_conn_string`/`setup` 在 ✓ |
| `recursion_limit` 的形状 | **不是**显式参数，走 `stream(self, message, *, thread_id=None, **kwargs)` 的 `**kwargs` |
| values 载荷 | 真身**无公开 state schema**；录制里观察到的并集**正好**是声明的四个字段 |
| 车道 | `make verify` 是**框架无关**单元车道；`make smoke` 才是带框架的那条（原本只 discover `tests/integration`） |

## Goals / Non-Goals

**Goals:** 建立锚（`CURRENT_DEERFLOW_PIN` + 镜像 vs 真身）· 治理侧那条 skip **归零** ·
框架无关的部分在默认车道也跑 · 框架相关的部分**在 CI 里真跑**（接进 smoke 车道）· 变异能双红。

**Non-Goals:** 改 `deerflow/`（只读）· 改镜像声明 · 动工作流 · 证明 values 字段的完备性。

## Decisions

### D-1｜锚就是那一行常量：双锚由**治理侧**比对

- **选**：本文件只声明 `CURRENT_DEERFLOW_PIN`；它与结构 registry 的一致由
  `test_upstream_pin_agreement`（治理侧，读两份文件）断言。
- **为什么**：**依赖方向**要求应用不得知道治理层的路径（见偏差 4，我的第一版 docstring 就被自家
  守卫抓了）。锚点与比对者分居两侧，是那个方向的正确体现。
- **换来**：skip 归零，且两侧的职责干净。

### D-2｜与框架无关的检查**不**带框架门槛

- **选**：`DeclaredSurfaceVersusOurUsageTest`（默认值 vs 我方调用点 · 录制里的载荷字段）**不加**
  `skipUnless`；只有真正要 import 真身的四条才加。
- **为什么**：我第一版把两个类都 gated，结果默认车道 **7 条全 skip**——那等于"锚建立了但没人看"。
  拆开之后：**2 条在框架无关车道恒跑**（它们在 CI 的 `make verify` 里就生效），5 条在框架车道跑。
- **换来**：skip 数从 7 降到 5，且这 5 条在 CI 里**真的执行**（见 D-3）。

### D-3｜把契约套件接进**框架车道**（否则那 5 条永远只 skip）

- **选**：`make smoke` 的 discover 补 `tests/contract`。
- **为什么**：契约测试的意义就是"比对真身"；在框架无关车道里它只能 skip。仓内唯一的带框架车道是
  `make smoke`，而 CI 正好调它（`governance.yml` 的 "Harness integration smoke" 步骤）——**不动工作流**
  就让它进 CI。
- **代价**：smoke 车道多跑 41 条契约测试（实测 0.02 秒）。
- **换来**：5 条真身比对**在 CI 里执行**，不是"存在但从不运行"。

### D-4｜`recursion_limit` 的 `**kwargs` 形状要被**显式**断言

- **选**：`test_stream_accepts_every_consumed_kwarg` 既断言"每个被消费的 kwarg 可传"，也**单独断言
  `**kwargs` 仍在**。
- **为什么**：这是镜像注释里记着的**区别**（`thread_id` 显式、`recursion_limit` 走 catch-all）。只断言
  "名字在里面"会漏掉"框架把 catch-all 去掉"这种破坏——那时名字消失了但破坏点不同。
- **换来**：形状级别的漂移也能红。

### D-5｜values 字段只给**正向证据**，并把边界写进 docstring

- **选**：断言"声明的四个字段都在真实录制里出现过"，**并写明证不了完备性**。
- **为什么**：真身没有公开 state schema（实测 `deerflow.client` 只暴露 `StreamEventType`/`StreamEvent`/
  `CheckpointStateAccessor`）。假装能证完备，就是造一个"看起来更强"的守卫。
- **换来**：能证明"声明不是虚构"，且不越界宣称。

## Risks / Trade-offs

- [镜像与真身都改却对不上] → 变异双红已证（抽镜像一项 ⇒ 红；改我方默认值 ⇒ 红）。
- [把契约测试塞进框架车道算"改车道迁就测试"] → D-3 的理由是**语义**：契约测试只能在有真身的环境里
  成立；车道选择由被测对象决定，不是由方便决定。
- [手搓形状] → 偏差 1、2：checkpointer seam 的"点号 vs 裸成员"我先解析错了；`_FRAMEWORK_AVAILABLE`
  的门槛范围我先设错了。两处都由**真跑**（venv 与默认车道各跑一遍）暴露。
- [测试里引用治理层路径] → 偏差 4：自家依赖方向守卫当场红。修措辞，不改守卫。

## Migration Plan

1. 写锚（pin + 镜像 vs 真身 + 镜像 vs 我方用法）。
2. venv 跑通（7/7）；默认车道确认 2 跑 5 跳。
3. 接进 `make smoke`；确认契约套件 41 条在框架车道全过。
4. 变异双红；恢复字节一致。
5. 门禁（含 skip 归零）；收口。

**回滚**：撤销 diff（删测试文件 + Makefile 两行 + 治理侧 skip 回归）。
