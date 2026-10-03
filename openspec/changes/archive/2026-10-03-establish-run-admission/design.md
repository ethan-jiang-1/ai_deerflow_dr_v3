# Design

## Context

Verified current state (this session): `engine/` is the only empty layer; the run-bundle
substrate (RUB-001) provides the bundle handle, lease-checked stores, the atomic file
layer, and a journal whose `admission` anchor category is reserved and waiting. The
import policy pins `runtime = {domain, agents}` — runtime cannot import engine, which
blocks the only composing writer from enforcing the validator hold point. v2 reached
engine transitively (runtime → graph → engine); with graph deliberately removed, the
direction needs completing, not restoring. The bundle plan's decision 4 is fully
specified (validator 写前跑, three dispositions, PhaseVerdict pass/blocked, repair
budgets cut, RT10 register). Policy routing: `control-placement`,
`workflow-outcome-review`, `change-admission` (tables in the proposal). No StateGraph
transition/predicate exists on this surface.

## Goals / Non-Goals

**Goals:**

- The hold point is a machine: nothing enters `evidence/` without an engine-rendered
  verdict, and every disposition (including rejections) is recorded.
- The ledger is tamper-evident: a sha256 chain over canonical JSON, verified on every
  read, failing loudly at the first broken link.
- The gate is a minimal honest derivation (`pass`/`blocked`, unmet named), and the
  quality register (RT10) exists and cannot silently rot.
- The import direction is completed deliberately so the composition layer can do its
  declared job.

**Non-Goals:**

- No repair budgets, no pending/suspended states, no HITL surfaces.
- No wiring-side producers (the callers of admission arrive with the wiring change), no
  CLI, no checkpoint writes.
- No ledger size bound: the ledger is the permanent quality record of a bundle —
  bounded retention is the journal's job; erasure is the bundle's (deletion is
  permanent).

## Decisions

1. **`runtime`'s internal allowance gains `engine`** — `runtime = ["domain", "engine",
   "agents"]` in the manifest, mirrored into the checker's
   `REQUIRED_INTERNAL_IMPORT_POLICY`. Rationale: the harness guide declares runtime the
   composition home, and only the composing writer can refuse verdict-less commits —
   a policy engine cannot enforce a hold point it is never called from. No cycle
   (`engine` stays `{domain}`); the direction discipline survives (domain ← engine ←
   runtime is a strictly deepening chain, exactly v2's shape via graph). Alternative
   (admission policy in domain so runtime can reach it) rejected: it contradicts the
   bundle plan's "engine 层" and the harness guide's own decision table
   (validation/gate/admission policy → engine). Alternative (verdict passed in by an
   outer caller) rejected: it makes the hold point opt-out, which is no hold point.
2. **The hash chain commits to canonical JSON.** `entry_hash = sha256(prev_hash +
   canonical_entry_json)` where canonical = `json.dumps(entry_without_hash,
   sort_keys=True, ensure_ascii=False, separators=(",", ":"))`; genesis `prev_hash` =
   64 zeros; `content_hash` = sha256 of the artifact bytes. Reading verifies every link
   and the recorded `entry_hash`, failing at the first offending sequence. Field edits,
   insertions, and deletions all break the chain. The entry itself is a closed field
   set (v2's small-vocabulary lesson): `seq`, `ts`, `disposition`, `kind`, `filename`,
   `artifact_path` (absent on rejects), `content_hash`, `result_code`, `reasons`,
   `replay_of` (absent unless `replay`), `prev_hash`, `entry_hash` — `from_dict`
   rejects unknown or missing fields loudly.
3. **The hold point is enforced by API shape plus a defensive refusal, honestly.**
   `runtime/admission.py` exposes only `submit_artifact(handle, submission)`; the
   internal commit refuses a `verdict=None` and refuses `admit`/`replay` dispositions
   on non-`ok` verdicts. Python cannot make objects unforgable in-process; the guarantee
   is the declared API path, the type flow (engine-owned `ValidatorVerdict`), and the
   negative controls — recorded as such rather than dressed up as cryptographic.
4. **Validator rules are ordered, closed, and minimal** (v2's small-set lesson):
   kind outside the closed set → `schema_malformed`; unsafe filename →
   `schema_malformed`; provenance missing/producer-less → `missing_provenance`; empty
   content → `empty_content`; content hash already admitted → `duplicate_content`;
   otherwise `ok`. Rejections carry the code plus human-readable reasons; nothing is
   repaired silently.
5. **Replay is rework, recorded honestly**: the submission's `content_hash` must match a
   previously `reject`-ed entry and the fresh verdict must be `ok` — the ledger records
   `replay` referencing the rejected sequence, and the reworked content is placed. A
   duplicate of admitted content is `duplicate_content`, never a silent overwrite. The
   division of labor: the engine renders verdicts only; the runtime selects the
   disposition from the verdict plus ledger facts (`ok` + unseen hash → `admit`;
   `ok` + hash matching a rejected entry → `replay`; non-`ok` → `reject`) — so the
   policy stays pure and the materialization stays honest about why it chose.
6. **Gate inputs are declared requirements plus admitted facts** — `GateRequirement`
   pairs a closed artifact kind with a minimum admitted count; the derivation renders
   `pass` only when every requirement is covered by `admit` (not `replay`-only,
   `reject`) entries. Who declares requirements is the caller's job (entry/wiring); the
   gate stays pure.
7. **The quality register is code-backed**: `engine/machines.py` declares the machine
   list (validator, gate, ledger chain verification, application unit gate, repository
   governance gates) with the invariant each guarantees; `docs/quality-register.md` is
   the human surface; a unit test fails on drift between the declared list and the
   register. The register is the RT10 answer: one look shows which machines guard
   quality.
8. **Ledger placement follows the contract**: entries in `evidence/submissions.jsonl`;
   admitted content at `evidence/{kind}/{filename}` with a validated safe basename;
   `final_report` artifacts also land under `evidence/{kind}/` in this change (routing
   a copy to `final/` is the reporting flow's job, which arrives with wiring).

## Alternatives

- **Admission policy in `domain/`** — rejected: see decision 1; it contradicts the plan
  decision and the project's own decision table, and domain would stop being the pure
  typed-facts layer.
- **Verdict supplied by an outer caller (runtime stays engine-free)** — rejected: the
  hold point becomes optional, exactly the "安静烂掉" failure the quality mapping exists
  to prevent.
- **A new composition layer above runtime** — rejected: no such layer is declared; the
  guide already assigns composition to runtime; inventing a layer for one call chain is
  the complexity the import completion avoids.
- **Unbound the ledger with journal-style retention** — rejected: the ledger is the
  traceability record (质量追溯); bounding it would sacrifice the property the QC
  mapping names. The journal remains the bounded surface.
- **Cryptographic signing of ledger entries** — deferred: sha256 chaining is
  tamper-*evident*, which is the v2-inherited property; signing adds key management
  with no adversary model in a local research harness. Revisit if bundles leave the
  machine.

## Risks / Trade-offs

- [Python objects are forgable in-process] → the hold point is enforced by API shape,
  type flow, and negative controls (decision 3, honestly stated); a hostile in-process
  caller is outside the threat model of a deterministic local harness.
- [Canonical JSON drift across Python versions] → the canonical form pins
  `sort_keys`, `separators`, and `ensure_ascii` explicitly and is exercised by chain
  round-trip tests; any future change to it is a ledger-format change requiring an
  owning change.
- [Ledger grows without bound on rejection storms] → accepted deliberately (decision:
  traceability over boundedness); the journal stays the bounded surface, and bundle
  deletion is the erasure path.
- [Import-policy edit touches the checker] → the edit is mirrored in the split-manifest
  fixture and verified by the governance suite; the policy remains non-weakenable in
  the sense that matters (no cycle; directions still deepen domain ← engine ← runtime).

## Migration Plan

Single apply, red-before-green per group: domain+engine tests red → engine modules
green; runtime admission/ledger tests red → runtime modules green; checker policy +
manifest + fixture updated together (governance suite stays green); quality register +
sync test land with the engine; register RUA-001 and create the main spec during apply.
Then the verification sequence, reviews, archive, commit. Rollback is reverting the
edits; RUA-001 takes a retirement marker if abandoned post-registration.

## Open Questions

(none — the import-direction completion, chain construction, and closed sets were
pinned against the bundle plan, the architecture policy, and the v2 reference this
session)
