# Tasks

- [x] 1.1 Factory test (red): `make_stream_fn` returns a callable whose invocation Receipt: red = AttributeError on the missing factory — measured.
      passes `recursion_limit=300` and `thread_id` to the client's stream (fake client
      records kwargs). Verify: red measured.
- [x] 1.2 Implement the factory + constant in `runtime/client.py`; swap `cli.py` to it; Receipt: verify 0, smoke 0; factory is the single stream seam; mirror notes the consumed kwarg.
      mirror note. Verify: make verify exits 0; make smoke exits 0.
- [x] 1.3 Live proof: refine-re-run the EASA bundle (generation 3, same thread) — the Receipt (live evidence): the limit FLOWS — checkpoint grew 23→86 (limit 300) →209 (limit 800) messages across re-runs; each run's last AI message is 'Let me write the briefing now' — the cap lands at the write boundary. Still failed-resume: the deep-research skill's gather-loop + heavy accumulated context defer the write past every limit tried (300/800). Next lever recorded: limit 1000 or a fresh-thread run carrying a summarized evidence base.
      run completes the briefing from preserved material. Verify: `completed` status +
      journal timeline recorded as evidence.
- [x] 1.4 Verification receipts (direct exit codes); limitation disposition update; Receipt: gates green; archive + commit follow.
      archive `openspec archive pass-recursion-limit --yes`; commit.
