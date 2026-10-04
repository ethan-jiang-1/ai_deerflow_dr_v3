# Design

## Decisions

1. The guard reads the three surfaces as text (stdlib, no YAML parser in the gate lane).
2. cli.py's subcommand names come from its own COMMANDS tuple plus the add_parser sites —
   the first run caught the loop-tuple indirection (four verbs registered via a loop are
   invisible to a literal add_parser scan); the guard now pins the declared tuple.
3. Registered in the quality register via machines.py — the register-sync test enforces
   the pairing.

## Alternatives

YAML-parsing the config — rejected (stdlib gate lane). Skipping the guard as "docs only" —
rejected: the digest's docs-as-contract discipline exists exactly for this surface.

## Risks / Trade-offs

[Extraction regex breaks on format changes] — fail-closed (a shape it cannot read is red).

## Migration Plan

Already applied (e2a21d8); this artifact set records it. Archive follows.

## Open Questions

(none)
