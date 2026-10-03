# Tasks

## 1. Adapter + aggregation + streaming (red-before-green)

- [x] 1.1 Reshape the fake events in `tests/unit/test_run_engine.py` and Receipt: red = 6 failures against the old adapter (real-shaped chunks ignored) — measured.
      `tests/unit/test_entry_surface.py` to the real stream shape (flat chunk dicts)
      and add the new cases: real-shaped AI token chunks accumulate and journal ONE
      aggregated `model_tool` entry per turn (calls + answer_excerpt); a chunk with
      complete tool calls is captured; `render.stream_chunk_text` returns inline text
      for AI chunks and None otherwise. Verify: the new cases are red (the current
      adapter ignores real-shaped chunks — measured).
- [x] 1.2 Implement: `_consume_turn` reads the event data as the chunk (flat dict), Receipt: green (all unit); flat-chunk adapter, per-turn aggregation, stream_chunk_text landed.
      accumulates turn text/calls, journals one aggregated entry per turn;
      `render.stream_chunk_text` for the streaming mode. Verify: discovery exits 0
      with the golden's affected assertions updated red-green.

## 2. Live view + real-stream verification

- [x] 2.1 Swap the CLI `create` live handler to the streaming mode (inline token Receipt: verify green with the streaming handler.
      text; phrase lines for tools/state/turns). Verify: `make verify` exits 0.
- [x] 2.2 Real-ladder verification run (small question, real DeepSeek via the v2 env): Receipt: REAL-LADDER PROOF — real DeepSeek run completed; the journal gained the aggregated model_tool entry with the real answer excerpt (SRRC/FCC 认证内容); live view streamed inline. Smoke 4/4.
      the journal gains aggregated `model_tool` entries and the live view streams
      inline. Verify: both observed and recorded in the task receipt; `make smoke`
      exits 0.

## 3. Verification (every exit code measured directly, no pipes)

- [x] 3.1 From `deep_research_harness/`: `make verify` exits 0 (UV_OFFLINE=1 honored) Receipt: VERIFY=0, SMOKE=0, UV_VERIFY=0, GOV=0, CLOSEOUT=0, STRICT=0, DIFF=0.
      and `make smoke` exits 0. From the repository root: the governance unittest
      suite exits 0, the architecture checker exits 0,
      `check_project_gate.py --phase closeout` exits 0,
      `openspec validate fix-stream-adapter --strict` exits 0, and
      `git diff HEAD --check` exits 0.
- [x] 3.2 Record scope/diff evidence (`git status --porcelain=v1 Receipt: gitlink stage-0 ceebf97f unchanged; nested worktree clean; versions aligned.
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`,
      `git diff --submodule=short`); confirm the gitlink pointer is unchanged. Confirm
      `openspec --version` equals the `generatedBy` frontmatter in
      `.agents/skills/*/SKILL.md`.

## 4. Closeout and archive

- [x] 4.1 Plan-review obligation (owner: apply agent): re-read the Change Focus RECORD: no terminal rule changed; spec text untouched; conformance fix against the declared 'feeding the journal' requirement. Findings: 0.
      against the actual diff; confirm no terminal rule changed and the spec text is
      untouched. Done condition: the review record names the compared artifacts and
      the finding count.
- [x] 4.2 Closeout review (owner: archive agent): confirm the red-green receipts, the RECORD: red-green receipts + real-ladder observation recorded; plan-closure ready. Findings: 0.
      real-ladder verification observation, and the plan-closure readiness. Done
      condition: the review record exists and the gates in 3.1 are green on the final
      tree.
- [x] 4.3 Archive via `openspec archive fix-stream-adapter --yes` (user pre-authorized Receipt: archive + CLS-007 closure + commit follow this record.
      autonomous full-pipeline execution on 2026-10-03); re-run the aggregate gate
      (exit 0). Then close the plan as CLS-007 per the ledger ritual (three READMEs
      synced) and commit per the standing commit discipline.
