# Design

## Context

Verified current state (this session): the harness source tree is empty — `domain/`,
`engine/`, `runtime/` hold only skeleton `__init__.py` files; the Makefile gate is a loud
stub; no `.venv` exists, the system `python3` has no pytest, and the CI governance job
runs `UV_OFFLINE=1 make verify` with **no dependency-install step** — so the gate can only
honestly promise stdlib-only execution. The import policy pins `runtime = ["domain",
"agents"]`: runtime can never import the engine layer, and that policy is non-weakenable
(checker-hardcoded, spec-owned). The bundle plan's decisions 1/2/3/5/6 are polished with
their evidence base in `_backlog/_reference/v2-run-bundle-implementation.md`; the v2
facts this design reuses are cited below. Policy routing: `control-placement`,
`workflow-outcome-review`, `change-admission` (tables in the proposal); no StateGraph
transition/predicate exists on this surface — the state machine is plain Python by ruled
decision.

## Goals / Non-Goals

**Goals:**

- The run bundle substrate exists as pure deterministic harness code: directory
  contract, single-authority state machine (CAS + lease), crash detection, bounded
  journal with protected anchors, permanent deletion, recorded composition.
- `make verify` becomes a real gate on the day the first tests land (this change), and
  stays offline-safe forever.
- Every failure path fails loudly in human-readable terms (v2 anti-patterns — silent
  migration, pretend-alive, O(n²) journal — are structurally excluded).

**Non-Goals:**

- No validator/hash-chain ledger/gate admission machinery (bundle plan decision 4 — next
  change; the journal reserves the `admission` category so anchors predate the ledger).
- No CLI subcommands (entry plan), no embedded client or real checkpoint writes (wiring
  plan), no HITL, no checkpoint format wrapping, no pytest/ruff as gate dependencies, no
  `proof-lanes.toml`, no CI workflow change.

## Decisions

1. **Pure rules live in `domain/`; `runtime/` only materializes them.** The import
   policy forbids runtime→engine, so the transition rules, detection predicate, journal
   retention/eviction policy, and closed vocabularies are domain (runtime-consumable);
   `engine/` stays empty this change and receives the admission policy with the decision-4
   change. Alternative (relax `REQUIRED_INTERNAL_IMPORT_POLICY` so runtime can import
   engine) rejected: the policy is non-weakenable by spec; weakening it for convenience
   trades a direction guarantee for nothing.
2. **`make verify` = stdlib unittest over `tests/`, zero external dependencies.** The CI
   job installs nothing, so a pytest/uv gate would fail offline on a fresh checkout.
   Concretely `PYTHONPATH=src python3 -m unittest discover -s tests` — the `src` layout
   makes the package importable without installation. pytest and ruff stay in the dev
   group as local conveniences and never gate. Alternative (uv-synced pytest gate with a
   committed lock) rejected: `UV_OFFLINE=1` on a cacheless runner cannot resolve it.
3. **`start` publishes atomically via a staging directory** (v2 `_publish_sync` pattern:
   build `.staging-{bundle_id}` with mode 0700, materialize all subtrees + `state.json`,
   `os.replace` onto the bundle root, fsync the parent; on failure remove the staging
   tree). A partially materialized bundle is therefore never discoverable — the
   "exactly materialized" requirement holds by construction.
4. **State writes are revision-CAS + atomic replace** (v2 `BundleStateStore` pattern:
   read → validate → reduce → write with `O_EXCL` temp + `os.replace` + fsync; conflict
   rejected naming expected and actual revision). No cross-process `flock` this change:
   the process model is a single foreground pump, CAS already detects drift between
   pump/`status`/`cancel` writers, and the loser re-reads. Deferred: add flock only if a
   real multi-writer pattern appears.
5. **Lease liveness = (`st_dev`, `st_ino`) re-check before every write** (v2
   `ensure_live`/`_require_live_bundle` discipline), kept as a small runtime helper used
   by both the state writer and the journal appender. A replaced or moved directory
   rejects the write loudly; no repair is attempted.
6. **Journal = append-only JSONL with on-write bounded retention.** Appends use
   `O_APPEND` single-write semantics; retention (entry-count bound, priority eviction,
   `admission` anchors never evicted) and compaction (threshold-triggered rewrite that
   preserves anchors plus the recent tail, atomically replaced) are pure domain policy
   functions; a corrupted tail fails the read naming the site. The eight start-up
   categories are a closed set in the domain module.
7. **Bucket = `d_` + creation date (`YYYYMMDD`).** v2's bucket was a hash of
   (user id, outer thread id) — multi-user containment machinery v3 does not have; a
   date bucket gives human-scannable grouping with zero invented identity. If
   multi-operator semantics arrive, the owning change re-pins. `bundle_id` is a UUID4
   generated by `start`; a colliding bundle path fails at staging time.
8. **`state.json` carries a closed field set** (v2's schema evolution lesson): 
   `schema_version` (1), `revision`, `status`, `thread_id`, `owner_pid`,
   `deerflow_pin`, `generation`, `composition`, `cancel_requested`, `auto_proceed_count`,
   `auto_proceed_bound`. `cancel` CAS-writes `cancel_requested: true` on `active`; the
   pump-side transition to `cancelled` follows the pure rule and lands with wiring.
   `thread_id` is generated by `start` (the wiring change reuses it as the client
   thread). One UUID serves as both the bundle directory name and the `thread_id` —
   v3 is one run = one thread, so the twin-identity machinery v2 needed has no
   question to answer here.
9. **Clarification continuation is a pure predicate over a minimal typed tool-call
   structure**, deliberately not deerflow event types — the embedded event shapes are
   mirrored by the wiring change, which adapts them onto this predicate. The bound
   (N=2) and count live in `state.json`; exhaustion routes the unanswered question text
   to `diagnostics/` and returns `failed-resume`.
10. **Owner-PID liveness is an injectable probe with one default implementation**
    (`os.kill(pid, 0)`); the injection is a test seam over the same rule, not a second
    authority. Tests use a genuinely exited child process, not mocks of the rule.
11. **`checkpoint.sqlite` is contract, not artifact, in this change.** Creating an empty
    SQLite file without the saver would produce an unopenable misleading artifact; the
    fail-loud open policy is specified now and the file appears with the wiring change's
    first checkpoint write.
12. **The gate itself gets a red proof.** `make verify`'s first landing includes a
    negative check: break a test, watch `make verify` exit non-zero, restore — a gate
    that cannot go red does not count as landed.

## Alternatives

- **Transition rules in `engine/` with a relaxed import policy** — rejected: see
  decision 1; the direction guarantee is spec-owned and non-weakenable.
- **pytest/uv as the verify gate** — rejected: see decision 2; the CI job installs
  nothing, so the gate must be stdlib. Revisit only if the CI workflow gains a real
  dependency-install step.
- **Cross-process `flock` serialization on state writes** — deferred: the process model
  is a single foreground pump; CAS detects multi-writer drift and the loser re-reads.
  Revisit with the entry-surface change if concurrent CLI actions become a real pattern.
- **v2-style hashed scope bucket** — rejected: it answers a multi-user containment
  question v3 does not have; date buckets are honest and scannable (decision 7).
- **Create `checkpoint.sqlite` at `start`** — rejected: an empty file is not a valid
  database and would mislead every later open (decision 11).

## Risks / Trade-offs

- [Two writers race on `state.json` (pump vs `status` crash transfer)] → CAS rejects the
  loser naming revisions; the loser re-reads and re-decides — unit test covers the
  conflict path; no lock is held across I/O.
- [Journal grows unbounded between compactions] → retention runs on append against an
  entry-count bound; compaction triggers at a threshold of the bound; both are pure
  functions with negative controls.
- [POSIX-only primitives (`O_NOFOLLOW`, `os.replace`, `st_dev`/`st_ino`)] → accepted;
  the repo targets POSIX exactly as v2 did, and the plan's shared-safe-layer abstraction
  confines the platform surface to one runtime module.
- [UUID collision on `bundle_id`] → staging creation fails loudly on an existing path;
  probability is negligible and the failure is safe.
- [The gate grows beyond stdlib] → the Makefile target is one line; revisiting needs a
  CI change first (decision 2's condition is explicit).

## Migration Plan

Single apply, red-before-green per group: domain tests red → domain modules green;
runtime tests red → runtime modules green; gate becomes real with its own red proof;
docs aligned; register RUB-001 and create the main spec during apply (the
establish-project-structure lesson: archive drops header lines, so the main spec is
never born from archive). Then the verification sequence and closeout. Rollback is
reverting the edits; RUB-001 takes a retirement marker if abandoned post-registration.

## Open Questions

(none — bucket semantics, field set, and layer placement were pinned against the v2
reference and the import policy this session; nothing deferrable remains that could
change the specs, the approach, or the task breakdown)
