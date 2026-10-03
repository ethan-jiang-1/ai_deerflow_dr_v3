# Design

## Context

Verified this session: the substrate's actions exist and are smoke-proven
(`bundle_actions.start/status/cancel/refine`, the run engine with terminal honesty, the
fixture ladder running the real client chain); the import policy pins
runtime = {domain, engine, agents} and the package-root layer imports nothing — so a
package-internal CLI would either violate the direction policy or require a new
ownership layer plus a project-structure spec delta. The wiring smoke surfaced the
framework's LLM-error-fallback behavior (a normal AI message with
`deerflow_error_fallback`) — a real product limitation that belongs in the reserved
`known-limitations.md` slot. Policy routing: `control-placement`,
`workflow-outcome-review`, `change-admission`; no StateGraph transition/predicate is
authored here.

## Goals / Non-Goals

**Goals:**

- A human can run the whole lifecycle: create (fixture ladder, live view) → watch →
  status → cancel/refine → inspect — with every EV2 layer usable on day one.
- One rendering vocabulary, deterministic strings, tested; the CLI stays presentation
  only.

**Non-Goals:**

- No TUI, no background workers, no admission producers, no Langfuse enablement, no
  output i18n, no CI wiring of the integration lane.

## Decisions

1. **The CLI is a standalone consumer script outside the governed package**
   (`deep_research_harness/cli.py`, `python cli.py <command>`). The import policy
   governs the package's internal composition; the CLI is a boundary consumer exactly
   like the tests, which also live outside `src/`. Alternative (a new `cli` ownership
   layer) rejected for this change: it would require a project-structure spec delta
   (the accepted spec names the four canonical layers), checker/manifest/fixture edits,
   and a guide re-render — machinery whose only yield today is where a thin script
   lives. Revisit through an owning change if the CLI ever grows composition logic
   (it must stay thin; semantics belong to runtime).
2. **The live view joins the pump as an optional hook, not a fourth rule sink.**
   `run_research(handle, *, stream_fn, on_event=None)` — the hook receives the same
   events the journal consumes; journal and terminal rules are untouched. The CLI
   passes a terminal renderer; the library default (None) keeps the smoke's behavior
   identical.
3. **One renderer module, deterministic phrases.** `runtime/render.py` formats events
   and journal entries into stable human strings (e.g. `tool web_search`, `state ->
   failed-resume (owner PID no longer alive)`); the same phrases serve the live view
   and the journal projection, so the golden replay pins real output. Volatile values
   (timestamps, ids) are excluded from the golden's shape assertions.
4. **`watch` is a bounded tail, not a daemon**: it reads the journal from its start
   position, renders new lines, and exits after a `terminal` entry — a terminal run
   renders recent history and exits. No polling-forever loop exists in v1.
5. **`inspect` renders recorded facts only**: journal timeline, admitted evidence from
   the ledger, the assembly snapshot, and — when the framework is importable — the
   checkpoint thread summary via the binding. Nothing is reconstructed from memory
   outside the owners.
6. **`known-limitations.md` activates now** with the wiring smoke's finding (framework
   LLM-error fallback renders as a normal AI message). The reserved docs slot's
   activation is this change's documentation duty; the entry is a product-level
   limitation visible to the non-AI handover, kept separate from design-time
   `## Alternatives`.

## Alternatives

- **A new `cli` ownership layer inside the package** — rejected: see decision 1; the
  spec delta plus checker/manifest/fixture/guide edits buy nothing for a thin script.
  Revisit when CLI composition logic is real.
- **`python -m deerflow_deep_research` with a package-root `__main__.py`** — rejected:
  the package-root layer imports nothing internal under the current policy, so the
  module would be an empty shim around a script outside the policy anyway.
- **Watch polling with a daemon loop** — rejected: the ruled process model is a
  foreground pump plus a bounded attach; a forever-loop watcher is the v2 theater the
  plan cut.
- **`create` defaulting to the `base` ladder** — rejected: defaulting to the
  credential-requiring ladder fails loudly in the common no-credential case; the
  fixture default fails nothing and rehearses the real chain.

## Risks / Trade-offs

- [The CLI script sits outside the layer policy's scan] → accepted and recorded: it is
  a consumer like the tests; its thinness is enforced by review (6.1) and the journey
  test proves it adds no second authority.
- [Renderer strings drift silently] → the golden replay and unit assertions pin the
  exact phrases; changes are visible in diffs.
- [Watch on a slow run holds the terminal open] → the bounded tail is the declared
  behavior (exit on terminal entry); Ctrl-C remains the human's own exit for a live
  view.

## Migration Plan

Single apply, red-before-green per group: renderer + engine-hook tests red → modules
green; CLI parsing/command tests red → cli.py green; journey + golden integration
tests green in the synced environment; governance registration (ENS-001, main spec,
required-paths, docs scope); verification sequence; reviews; archive; commit. Rollback
is reverting the edits; ENS-001 takes a retirement marker if abandoned
post-registration.

## Open Questions

(none — placement, rendering ownership, and EV2 evidence were pinned against the entry
plan and the wiring smoke's findings this session)
