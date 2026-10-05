# Tasks

## 1. 守卫红先行

- [x] 1.1 Write `tests/unit/runtime/test_binding_doc_guard.py`: import
  `DEEP_RESEARCH_RECURSION_LIMIT` from
  `deerflow_deep_research.runtime.adapters.client` and `CONSUMED_DEFAULTS`
  from `deerflow_deep_research.runtime.adapters.contracts.client_surface`;
  assert `docs/research-process.md` contains every `f"{key}={value}"` pair plus
  `recursion_limit={limit}` verbatim, and `docs/run-bundle.md` contains the
  heading `## 一次 run 的证据关联`. Verify: the guard FAILS red naming the
  missing pairs/heading (capture for the receipt).

## 2. 文档内容

- [x] 2.1 Add the binding knob table to `docs/research-process.md`
  (config_path 显式解析+env 钉 / checkpointer 工厂 seam / model_name /
  thinking_enabled / subagent_enabled / plan_mode / available_skills /
  middlewares 注入 / thread_id / recursion_limit per-call；每行含 owner 与
  测试证据；recursion 行含 AppConfig 顶层 300 疤痕说明). Verify: guard green
  and `check_doc_hygiene.py` exits 0.
- [x] 2.2 Add the `## 一次 run 的证据关联` section to `docs/run-bundle.md`
  (thread_id → checkpoint / snapshot → journal / submissions 链 / final 的
  走法，每步能推出与不能推出什么，inspect 入口). Verify: guard green and
  hygiene green.

## 3. 双 lane 与 closeout

- [x] 3.1 Run `make verify` (all green incl. the new guard) and `make smoke`
  (not owed — no smoke surface touched — but run as belt-and-braces); direct
  exit codes only.
- [x] 3.2 Run the full closeout set (governance suite, closeout gate,
  doc hygiene + self-test, architecture, project specs, release face,
  dependency checker, plan gate for this change, git diff --check,
  git diff --exit-code HEAD -- deerflow) with directly-read exit codes, then
  write the fresh verification receipt (argv/cwd/exit/stdout/stderr, HEAD
  revision, dirty status, per-file digests, the task-1.1 red output quoted,
  UNVERIFIED notes). Verify: receipt newer than last edit, every exit matches
  expectation.
