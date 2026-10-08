# Tasks

## 1. 回放测试扩充（`tests/unit/runtime/test_event_stream_replay.py`）

- [x] 1.1 新增 `test_replayed_stream_materializes_every_search_result`：回放后
  断言 `diagnostics/searches/` 恰好 11 条（web_search×6 + web_fetch×5，探针
  2026-10-08 实证）、每条 JSON 含 generation/seq/tool/arguments/content/call_id
  键、content 非空。
- [x] 1.2 新增篡改负例 `test_unpaired_search_result_is_not_materialized`：把一
  条搜索结果的 call_id 改为未配对值 → 断言总数 10（"未配对不物化"是规则，
  红先于绿：先跑确认当前实现对篡改的正确行为，再钉住）。

## 2. 验证与回执

- [x] 2.1 `make verify` 退出码直测（新测试进默认离线门禁）；篡改负例红证：
  临时把物化断言计数改为错误值确认测试红，再还原（守卫可红的直接演示）。

## 3. 归档前义务

- [x] 3.1 repo 根 closeout gate；`UV_OFFLINE=1 make verify`；`openspec validate
  assert-replay-materialization --strict`；`git diff HEAD --check`（退出码直测）。
- [x] 3.2 gitlink 取证四件套 + skill 版本对齐。

## 4. 归档与回写

- [x] 4.1 archive → `openspec/changes/archive/<date>-assert-replay-materialization/`。
- [x] 4.2 回写 plan C6 批次表（C 面落判）。

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记。

## Delivery Record

- **外部行为**: 真实录制流回放契约补全——物化计数（11=6+5）与记录形状成为
  红绿事实；"未配对结果不物化"被篡改负例钉为规则；research-process 的"已物化
  可直读复核"承诺获得机器事实支撑。
- **影响面**: 仅 `tests/unit/runtime/test_event_stream_replay.py`（+2 测试方法、
  collections 导入）；实现零改动（SearchLog/pump 未动）；DECLARED_MACHINES/
  quality-register/spec 均不变。
- **实际跑了什么**: 新测试文件 4/4 绿（PYTHONPATH=src 直测）；红证：断言改 12
  → FAILED exit 1 → 还原 11 → OK exit 0（中途一次"恢复后仍红"为 stale pyc
  假象——12/11 等长同秒致字节码缓存未失效，清缓存后消除，已如实记录）；
  `UV_OFFLINE=1 make verify` → exit 0。
- **未执行的检查**: smoke 旅程的 create 物化断言未强化（smoke 已覆盖，本面
  专注真实流钉样）；fixture 报告的 URL 可溯性探针属 A 面取证（已做：6/6 命中），
  本 change 不落任何 A 面断言。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者授权全程推进，对交付负最终责任。
