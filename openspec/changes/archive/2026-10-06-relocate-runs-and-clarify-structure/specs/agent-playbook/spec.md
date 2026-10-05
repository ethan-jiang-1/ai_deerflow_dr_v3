# Spec Delta

## MODIFIED Requirements

### Requirement: The entry face is a menu with routing, never a recipe

`deep_research_harness/COMMANDS.md` SHALL list every legal command surface (the six
CLI verbs and the make targets) with one entry per surface, and SHALL NOT carry
procedural sequences: steps, ordered instructions, and scenario walkthroughs live only
in playbook files. Every entry whose execution needs procedure SHALL carry exactly one
routing line naming its playbook file, and every routing target SHALL exist under
`deep_research_harness/docs/playbook/`. The menu's command set SHALL mirror the closed
entry-surface vocabulary and SHALL NOT introduce a second command vocabulary.

#### Scenario: The menu routes without embedding procedure

- **WHEN** the entry face is read to answer "what can be handled", and each routing
  line's target path is resolved under `docs/playbook/`
- **THEN** the command entries match the closed six-verb vocabulary plus the declared
  make targets, no entry contains an ordered procedural sequence, and every routing
  target exists
