# Tasks

## 1. 红先行

- [x] 1.1 Create `tests/unit/runtime/test_search_log.py`: unit tests for the
  recorder — note_call + note_result materializes a file with
  generation/seq/tool/arguments/content; duplicate call_id writes once;
  non-search tool names write nothing; orphan results (no paired call) write
  nothing; filename shape `gen{N}-{seq:03d}-{name}.json`. Verify: FAILS red
  (module absent — ImportError) — capture.
- [x] 1.2 Extend `tests/unit/runtime/test_run_engine.py`: a scripted search turn
  (AI chunk with a web_search tool_call, tool-result chunk with content, then
  the values snapshot + final answer) driven through `run_research` — assert
  `diagnostics/searches/gen1-001-web_search.json` exists with the query and
  content. Verify: FAILS red (no file written) — capture.
- [x] 1.3 Extend the journey test: the create call injects a script whose first
  item emits a `web_search` tool call (query: 无人机 认证壁垒) and whose second
  item is a distinct final answer; assert after the run that
  `diagnostics/searches/gen1-001-web_search.json` exists, carries the query in
  arguments and the canned fixture content. Run `make smoke` and verify the
  journey FAILS red at the searches assertion — capture.

## 2. 实现

- [x] 2.1 Create `runtime/bundle/search_log.py` per design decisions 1–3
  (SearchLog with note_call/note_result, SEARCH_TOOL_NAMES, atomic writes,
  call-id dedupe, gen-prefixed filenames). Verify: 1.1 turns green.
- [x] 2.2 Wire `run_engine`: construct the SearchLog in `run_research` (with the
  state's generation), pass into `_consume_turn`, feed note_call from AI-message
  tool_calls (both chunk and values branches) and note_result from tool messages
  (both branches, content included). Verify: 1.2 turns green; `make verify`
  fully green.
- [x] 2.3 Run `make verify` and `make smoke` — both green, the previously
  red steps green.

## 3. spec 与文档同轮

- [x] 3.1 Update docs: `docs/run-bundle.md` (artifact table gains the
  `diagnostics/searches/` row; traceability walk mentions it),
  `docs/research-process.md` (质量评估 column and 判断质量 paragraph name the
  readable materialization), `docs/control-map.md` (not-implemented list: the
  evidence line gains "搜索已物化到 diagnostics/searches/ 可直读，仍不自动进
  evidence/"), `tests/README.md` (journey description row). Verify: hygiene
  exits 0; no doc claims searches still live only in the checkpoint.

## 4. Closeout 证据

- [x] 4.1 Full closeout set with directly-read exit codes (governance suite,
  closeout gate, doc hygiene + self-test, architecture, project specs, release
  face, dependency checker, plan gate for this change, make verify, make smoke,
  git diff --check, git diff --exit-code HEAD -- deerflow).
- [x] 4.2 Fresh verification receipt (argv/cwd/exit/stdout/stderr, HEAD revision,
  dirty status, per-file digests, all red outputs quoted, UNVERIFIED notes
  incl. real-ladder event shapes and no size bound). Verify: receipt newer than
  last edit, every exit matches.
