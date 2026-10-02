# Tasks

## 1. Guidance hardening

- [x] 1.1 Add three discipline sections to `openspec/change-guidance/core/change-practice.md`:
      the Alternatives convention (design.md carries `## Alternatives` — real rejected
      alternatives, or `none: <rationale>`; the process-layer home for negative knowledge),
      the exemption criterion (mechanical or local edits are exempt; diff size is not the
      criterion — the absence of a durable tradeoff is), and the supersession discipline
      (new record plus cross-links, never in-place rewrite; full absorption of every
      unique rationale, alternative, consequence, and verification gap before
      replacement; archived records are frozen snapshots cited only as history). Verify:
      the three sections exist and the guidance checker passes
      (`python3 openspec/governance/check_change_guidance.py` exit 0).
- [x] 1.2 Add the Alternatives design rule to `openspec/config.yaml` `rules.design`:
      a change's design MUST carry an `## Alternatives` section when real alternatives
      were considered and rejected (each with why it lost), or state `none: <rationale>`
      explicitly; reversing an earlier decision adds a new record with cross-links
      instead of rewriting in place. Verify: the rule text exists in config.yaml and
      `openspec instructions design --change harden-change-practice-guidance --json`
      output carries it in its rules; the guidance checker still passes (exit 0).
- [x] 1.3 Reserve the `known-limitations.md` row in `deep_research_harness/docs/README.md`
      (status marker: to be created by the first product change that owns a limitation;
      declared as the product-layer home for current known limitations, separate from the
      process-layer Alternatives home). Verify: the row exists and
      `python3 openspec/governance/check_doc_hygiene.py` exits 0.

## 2. Verification (every exit code measured directly)

- [x] 2.1 Run the governance unittest suite
      (`python3 -m unittest discover -s openspec/tests/governance -q`) and confirm exit 0.
- [x] 2.2 Run the aggregate gate
      (`python3 openspec/governance/check_project_gate.py --phase closeout`) and confirm
      exit 0 with all components green.
- [x] 2.3 Run `openspec validate harden-change-practice-guidance --strict` (exit 0) and
      `git diff HEAD --check` (exit 0).

## 3. Closeout and archive

- [x] 3.1 Closeout review: compare the Change Focus against the actual diff and evidence;
      confirm this change's own design.md exercised the new Alternatives convention;
      every actionable finding becomes an unchecked task or an approved re-scope.
- [x] 3.2 After user approval, archive via `openspec archive harden-change-practice-guidance`;
      re-run the aggregate gate (exit 0) and mark gaps B and F absorbed in the DSH
      borrowing plan's landing table, leaving C as the next queue item.
