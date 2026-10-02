# Proposal

## Why

The DSH borrowing analysis (gaps B and F) names the missing home for negative knowledge:
the spec tree collects only positive requirements, the archive is history, and suspended
plans only cover paused work. A rejected alternative currently lives nowhere durable, so a
fresh session treats its explicit absence as an oversight and re-proposes what was already
rejected. The fix is cheap now — before the change count grows — and lands as pure
guidance discipline: an explicit exemption criterion, an Alternatives convention in every
change's design, and a supersession rule for reversed decisions.

## What Changes

- Harden `openspec/change-guidance/core/change-practice.md` with three disciplines:
  1. **Alternatives convention** — a change's design.md carries an `## Alternatives`
     section whenever real alternatives were considered and rejected; when none existed,
     the section states `none: <rationale>` explicitly. The design document is the
     process-layer home for negative knowledge (it travels with the change and lands in
     the archive where the decision history lives).
  2. **Exemption criterion** (recorded verbatim from the DSH lesson) — mechanical or local
     edits are exempt from decision records; diff size is not an exemption reason — the
     absence of a durable tradeoff is. A local fix does not qualify merely because it is
     small, and a large change does not qualify merely because it is large.
  3. **Supersession discipline** — reversing an earlier decision adds a new record with
     cross-links instead of rewriting the old one in place; full replacement first
     absorbs every unique rationale, alternative, consequence, and verification gap; an
     archived record is a frozen snapshot that is never cited as current authority.
- Add one machine-readable design rule to `openspec/config.yaml` carrying the same
  convention, so the OpenSpec CLI injects it into every future design instruction (the
  rule text is advisory-injected guidance, not yet a checker-enforced gate — see design).
- Reserve the `known-limitations.md` row in `deep_research_harness/docs/README.md` as the
  product-layer home for current known limitations (to be created by the first
  product change that owns one); the process layer (Alternatives) and the product layer
  (known limitations) stay separate owners and never duplicate content.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — this change hardens guidance text, one config rule, and a documentation index;
no spec-level behavior changes, so the change sets `skip_specs: true`)

## Impact

- `openspec/change-guidance/core/change-practice.md` — three new discipline sections.
- `openspec/config.yaml` — one added design rule (advisory injection through
  instructions; `check_change_guidance.py` continues to validate the config fragments it
  knows — the new rule adds no checker semantics).
- `deep_research_harness/docs/README.md` — one reserved table row.
- No application code, no checker rule semantics, no spec text, no registry entries.

## Change Focus

- **Primary module / causal owner:** `openspec/change-guidance/core/change-practice.md` — the core guidance document owns the admission and evidence disciplines being hardened; the config rule and the docs index row are its injection and product-layer surfaces.
- **Seam classification:** wiring — guidance text, one advisory config rule, and one index row; no runtime engine, no model cognition, and no checker rule semantics change.
- **Question:** Where do rejected alternatives, decision-exemption criteria, and supersession discipline live so a fresh session stops re-proposing what was already rejected?
- **Necessary adjacent/external contracts:** `openspec/config.yaml` (answers: how the Alternatives convention reaches every future design instruction); `deep_research_harness/docs/README.md` (answers: where the product-layer known-limitations home is declared and why it stays separate from the process layer).
- **Evidence seam:** text-level verification — the three discipline sections exist in change-practice.md, the design rule exists in config.yaml and instructions output carries it, the docs row exists, doc hygiene stays green, and the plan/strict gates pass. Guidance semantics themselves remain prose (their machine enforcement was evaluated and deliberately deferred — recorded in this change's own design as the first Alternatives entry).
- **Not in scope:** checker enforcement of the Alternatives grammar (`check_change_guidance.py` semantics — a follow-up change if prose proves insufficient), creating `known-limitations.md` itself (owned by the first product change), gap D (the AGENTS.md rationale line rides the first change that touches that guide), and any spec or registry change.
- **Triggered review policies:** change-admission
