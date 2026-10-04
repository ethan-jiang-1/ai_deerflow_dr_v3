# Proposal

## Why

The command surface (COMMANDS.md, Makefile targets, cli.py subcommands) is documentation-as-deliverable: the digest's docs-as-contract discipline requires the three surfaces to stay mutually consistent by test, not by review vigilance. The wiring smoke also just extended CI runtime, making the documented command set a moving surface worth pinning. (Process disclosure: the guard code landed in commit e2a21d8 before this artifact set existed — the apply batch skipped the OpenSpec scaffold; this artifact set is the post-hoc record, created the same session with the implementation diff unchanged.)

## What Changes

- The command-surface guard (`tests/unit/test_command_surface.py`, landed in e2a21d8): COMMANDS.md's documented make targets exist in the Makefile; cli.py's declared subcommand verbs (the COMMANDS tuple + add_parser sites) are all documented in COMMANDS.md; the guard itself is registered in the quality register (machines.py sync test enforces the pairing).

## Capabilities

### New Capabilities
(none — docs-as-contract enforcement; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- Modified (in e2a21d8): `engine/machines.py` (command-surface-guard machine), `docs/quality-register.md` (row), `tests/unit/test_command_surface.py`. No product code.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/COMMANDS.md` — the documented command surface; the guard pins it against the deliverable.
- **Seam classification:** deterministic-guardrail — mechanical consistency check over three text surfaces.
- **Question:** How does the documented command surface stay identical to the deliverable (Makefile targets, cli subcommands) by machine, so doc drift fails the suite?
- **Necessary adjacent/external contracts:** the quality register (answers: where the guard is declared and its pairing enforced); cli.py + Makefile (answers: the extraction sources the guard reads).
- **Evidence seam:** the unit guard green on the real surfaces; the negative control (removing a documented target turned it red — measured in-session).
- **Not in scope:** registry-style doc linting beyond the command surface, CI changes.
- **Triggered review policies:** change-admission
