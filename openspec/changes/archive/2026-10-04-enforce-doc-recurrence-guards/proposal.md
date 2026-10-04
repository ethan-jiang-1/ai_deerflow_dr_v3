# Proposal: Enforce Doc Recurrence Guards

## Why

Two document-recurrence mechanisms survived the first two hygiene sweeps because no
rule reaches them: inline counts in the root README drift at every archive (corrected
to 11/31 by `doc-hygiene-second-sweep`, and the next archive makes them wrong again),
and ledger "补记" rows land outside their tables (B3/B5 in the second sweep; the same
blank-line pattern was already fixed once by CLS-012's C7). Both were verified as
live-a-green-tree defects — the checkers pass while the narrative is wrong. The
operator has now ruled on all five deferred decisions (count enforcement form, row
placement rule, profile disambiguation, six-step gate authority, routing tables), so
the guards can land as a single checker-semantics change.

## What Changes

- **Counts are machine-pinned** (operator ruling: checker 钉死): the document-hygiene
  checker computes the capability-spec and archived-change counts itself and requires
  the root `README.md` status line to match them; a drifting number fails loudly
  naming both the computed and the declared value.
- **Ledger rows must sit inside their tables** (operator ruling: 加行位置校验): the
  ledger-consistency rule gains a placement check — an archive/work-item row must be
  contiguous with its declared table; blank-line-shattered tables and rows dangling
  after a code fence (the B3/B5 shapes) fail loudly.
- **`MARKER_ALLOWLIST` stale path repaired** (conformance): the justification for the
  genuinely-empty `agents/` layer references
  `_backlog/plans/2026-10-04-fresh-agent-doc-cleanup.md`, which now lives in
  `_done/_closed_plans/`; the justification text is corrected (checker-file edit
  owned here).
- **Budget ratchet executed** (ordinary edit per the doc-budgets spec): root
  `AGENTS.md` 2435 → 2425, `deep_research_harness/AGENTS.md` 6864 → 6863, matching
  the measured sizes recorded by `doc-hygiene-second-sweep`.
- **A5 (profile) disambiguation lands in `CONTEXT-MAP.md`** (operator ruling): one
  entry separating root `profiles/` (local run profiles) from
  `openspec/change-guidance/profiles/` (policy profiles).
- **C2 (six-step gate) authority declared** (operator ruling): one line in harness
  `AGENTS.md` and one in `openspec/change-guidance/profiles/node-agent/node-agent.md`
  declaring that divergence is allowed and the harness version is the application
  authority (net-negative or neutral in the budgeted file).
- **C3 recorded as accepted**: the three overlapping routing tables stand as
  docs-as-contract per the Reader Roles division — recorded here, zero edits.
- **No runtime code changes; no spec file outside the doc-truthfulness delta.**

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `doc-truthfulness`: the ledger-consistency requirement gains row-placement
  validation (rows contiguous with their table), and a new requirement pins the root
  README's capability/archive counts to machine-computed values.

## Impact

- Modified: `openspec/governance/check_doc_hygiene.py` (count rule, row-placement
  rule, allowlist justification text, lowered ceilings in `DOC_BUDGETS`),
  `openspec/tests/governance/test_terminology_rules.py` or the doc-hygiene self-test
  (negative controls for both new rules), `CONTEXT-MAP.md`, harness `AGENTS.md`
  (one line, budget-neutral), `openspec/change-guidance/profiles/node-agent/node-agent.md`
  (one line).
- Not touched: all other checkers, capability specs other than the delta, harness
  runtime/CLI, CI workflow semantics, `deerflow/` gitlink (read-only).
- Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink;
  this change reads nothing inside it.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` — the
  checker owns every rule this change adds or repairs; the content edits (A5/C2) are
  conformance to the rulings it enforces.
- **Seam classification:** deterministic-guardrail — two new red-first rules and one
  justification repair over textual facts; no model, prompt, or state machine.
- **Question:** Can the two proven recurrence mechanisms (inline counts, ledger row
  placement) be closed with checker rules whose red is demonstrated before green,
  while the two budgeted resident edits stay at or under their ratcheted-down ceilings?
- **Necessary adjacent/external contracts:** `doc-budgets` capability (answers: the
  ratchet discipline the lowered ceilings follow — lowering is ordinary, no
  justification needed); `doc-truthfulness` capability (answers: the declaring-table
  and allowlist forms the new rules must follow); the operator rulings of 2026-10-04
  (answers: why these five forms and not their alternatives).
- **Evidence seam:** red-first negative controls for the count rule and the
  row-placement rule (mismatched fixture → non-zero exit naming the violation; then
  green on the real tree), `check_doc_hygiene.py` `--self-test`, the full closeout
  gate, and `make verify` — all exit codes read directly.
- **Not in scope:** the `state.json` transient-missing diagnosis (running as a
  separate investigation), any further ceiling raise, rewording of the three routing
  tables (C3 accepted), CI workflow semantics.
- **Triggered review policies:** control-placement, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| Root README counts must equal machine-computed inventory | Human judgment (operator chose enforcement over pointerization) | Checker computes `len(specs)`/`len(archive)` and regex-compares the README status line | non-bypassable | A drifted count fails loudly naming both values; recovery is correcting the number | The manual re-count ritual after every archive is retired | Negative control: fixture mismatch → non-zero; real tree → 0 |
| Ledger archive rows must sit inside their declared tables | Human judgment (operator chose machine validation) | Row-placement check inside the ledger-consistency rule (contiguity with the table header block) | non-bypassable | Dangling/shattered rows fail loudly naming the surface and row; recovery is moving the row | The twice-recurred B3/B5 manual repair loop is closed | Negative control: dangling-row fixture → non-zero; real tree → 0 |
| `agents/` allowlist justification references the moved plan | Human judgment (none — mechanical repair) | Allowlist entry text corrected to the `_closed_plans` location | bounded-repair | Dangling allowlist entries already fail loudly (existing rule) | No rule change; the justification stops lying about a path | Doc-hygiene checker exit 0; allowlist rule's own negative control |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| Count drift after an archive | Count-pinning rule | Editor updates the README number (or the inventory changed and the number is right — then the rule's computation is wrong and that is a checker bug routed to a new bug) | Non-zero naming computed vs declared | Fix the number, re-run | Negative control pins the rule's red |
| Ledger row lands outside its table | Row-placement rule | Editor moves the row into the table | Non-zero naming surface and row | Move the row, re-run | Negative control pins the rule's red |
| Resident edit exceeds a ratcheted ceiling | Budget rule (existing) | Shrink the edit; the ratchet forbids raising without justification | Non-zero naming file and ceiling | Trim wording, re-run | Existing budget negative control |
