# Design

## Context

Verified current state: `openspec/specs/` holds two capabilities (project-structure,
ci-governance), both about machine-enforced surfaces. Decision knowledge has no home:
`change-practice.md` states evidence and admission principles but carries no exemption
criterion, no Alternatives convention, and no supersession rule; the config design rules
say nothing about rejected alternatives; the docs index has no known-limitations row. The
DSH borrowing analysis (gaps B and F) prescribes exactly this hardening, and its cost is
lowest before the change count grows. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**

- Every future design.md carries an explicit `## Alternatives` answer (real rejected
  alternatives, or `none: <rationale>`), so negative knowledge always travels with its
  change and lands in the archive where decision history lives.
- A one-line exemption criterion ends both failure directions (mechanical archiving of
  trivial edits / silent skipping of real tradeoffs).
- Reversed decisions supersede by new-record-plus-cross-link, never in-place rewriting,
  with a full-absorption obligation before replacement.
- The product-layer known-limitations home is declared without being created.

**Non-Goals:**

- No checker enforcement of the Alternatives grammar, no `known-limitations.md` file, no
  AGENTS.md edit (gap D rides a later change), no spec or registry changes.

## Decisions

1. **Process-layer home = design.md `## Alternatives` section.** The design artifact is
   the only place negative knowledge already travels with its change: it is written at
   propose time (when alternatives are actually being weighed), reviewed at polish, and
   archived with the change. Alternatives: a decisions/ directory of standalone ADRs was
   rejected — a second ledger beside `_backlog` and `openspec/` for a category the change
   flow already carries adds a third home and migration rules; the `_backlog` plan's
   risk/tradeoff section was rejected — plans close and sink into `_done/`, losing
   retrieval (the DSH plan itself notes this failure mode).
2. **Syntax-over-semantics, but deferred enforcement.** The judgment "were there real
   rejected alternatives" is semantic and cannot be machine-decided; what CAN be checked
   is the grammar (the section exists, with `none: <rationale>` as the explicit-absence
   form). This change lands the convention as injected guidance (config design rule);
   checker enforcement is deliberately deferred until prose proves insufficient — the
   "borrow under pressure" discipline, applied to our own machinery. Alternative:
   wire `check_change_guidance.py` to require the section now was rejected as scope
   creep into checker semantics, which this change explicitly excludes (and which would
   need its own owning spec conversation).
3. **Exemption criterion copied near-verbatim from the DSH lesson.** Mechanical or local
   edits are exempt; diff size is not the criterion — the absence of a durable tradeoff
   is. Kept as one sentence so it survives as a quotable rule.
4. **Supersession as three clauses.** New record + cross-links (never in-place rewrite);
   full absorption before replacement (rationale, alternatives, consequences,
   verification gaps); archived records are frozen snapshots cited only as history.
   Alternative: a single "don't rewrite history" line was rejected — the absorption
   obligation is the part that prevents deleting someone else's hard-won坑.
5. **Product-layer home declared, not created.** One reserved row in the docs index,
   owned by the first product change that has a real limitation to record. Creating an
   empty `known-limitations.md` now was rejected — an empty file is an unowned promise;
   the process layer (Alternatives) and product layer (known limitations) stay separate
   owners by content type, never duplicating.

## Alternatives

- **Standalone ADR directory (`docs/adr/`)** — rejected: adds a third ledger beside
  `_backlog` and `openspec/`; the change flow already carries design artifacts to
  archive, so negative knowledge rides the existing vehicle.
- **`_backlog` plan sections as the home** — rejected: plans close and sink into
  `_done/`; retrieval degrades exactly when a fresh session needs the rejection record.
- **Checker-enforced Alternatives grammar now** — deferred: the semantic half cannot be
  machine-decided and the grammar half adds checker semantics this change excludes;
  revisit with evidence if prose discipline drifts.
- **Empty `known-limitations.md` scaffold** — rejected: an empty file is an unowned
  promise; the owning product change creates it with real content.

## Risks / Trade-offs

- [Injected guidance is still prose; agents may skip the section] → the convention is
  now in the instruction path (config design rule), this change's own design exercises
  it, and polish reviews check it; if drift appears, the deferred checker change is the
  recorded next step with a ready design (decision 2).
- [Config rule text is advisory, not gate-enforced] → stated honestly in the rule's own
  wording and here; no enforcement is claimed.
- [`none: <rationale>` becomes boilerplate] → the exemption criterion (decision 3) gives
  reviewers the test for when the section must carry real content; polish review is the
  semantic check.

## Migration Plan

Single apply: edit change-practice.md (three sections), add the config design rule, add
the docs index row; verify by text presence, instructions output, doc hygiene, and the
plan/closeout gates. Rollback is reverting three text edits; no state, no registry.
