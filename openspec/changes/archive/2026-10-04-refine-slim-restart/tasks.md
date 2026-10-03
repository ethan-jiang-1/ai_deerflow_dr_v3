# Tasks

- [x] 1.1 Unit tests red: rule_refine with next_thread_id (new thread + lineage + default
      unchanged); refine with fresh_context (context file + thread change + prior ids;
      old checkpoint untouched). Verify: red measured.
- [x] 1.2 Implement (state_machine, bundle path helper, bundle_actions, client
      summarizer). Verify: VERIFY=0, SMOKE=0.
- [x] 1.3 Real proof: EASA bundle fresh-thread refine -> light run completes the
      briefing in one shot. Verify: observed + recorded.
- [x] 1.4 Gates (direct exits); receipts; archive; commit.

## Receipt

- [x] red measured (3 errors: missing field/params); green: VERIFY=0, SMOKE=0.
- [x] MACHINERY LIVE-VERIFIED on the EASA bundle: mechanical summary built (929 chars, original question present), gen-6 on a fresh thread, lineage recorded, seed file in request/. 
- HONEST SCOPE CORRECTION: the "completes in one shot" claim is NOT a mechanism guarantee — the deep-research skill re-gathers nondeterministically on any thread (gen-6 hit GraphRecursionError at limit 1000 on the LIGHT thread); strong no-tool directions help (gen-5 completed that way) but are prompt-level, not mechanism-level. The change delivers the light-restart machinery, not a completion guarantee.
- NEW FINDINGS (recorded to known-limitations): (1) checkpoint growth — one bundle's checkpoint.sqlite reached 1GB across five 1000-step generations; per-generation compaction is future work. (2) a transient state.json-missing during the gen-7 attempt on the 1GB bundle (fail-loud StateCorruption, no silent corruption; diagnosis deferred — FS pressure suspected).
- [x] gates below; archive; commit.

