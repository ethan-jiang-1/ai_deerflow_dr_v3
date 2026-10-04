
# agent-playbook Specification

## Purpose

Owns the required behavior of the agent invocation surface: `COMMANDS.md` is the entry
face that answers "what can be handled" as a menu with routing lines only, and the
`playbook/` subdirectory owns every procedural detail as Markdown mixed with directly
executable commands, under content and receipt discipline.

## Requirements

### Requirement: The entry face is a menu with routing, never a recipe

`deep_research_harness/COMMANDS.md` SHALL list every legal command surface (the six
CLI verbs and the make targets) with one entry per surface, and SHALL NOT carry
procedural sequences: steps, ordered instructions, and scenario walkthroughs live only
in playbook files. Every entry whose execution needs procedure SHALL carry exactly one
routing line naming its playbook file, and every routing target SHALL exist under
`deep_research_harness/playbook/`. The menu's command set SHALL mirror the closed
entry-surface vocabulary and SHALL NOT introduce a second command vocabulary.

#### Scenario: The menu routes without embedding procedure

- **WHEN** the entry face is read to answer "what can be handled", and each routing
  line's target path is resolved under `playbook/`
- **THEN** the command entries match the closed six-verb vocabulary plus the declared
  make targets, no entry contains an ordered procedural sequence, and every routing
  target exists

### Requirement: Playbook files are MD mixed with real commands under content discipline

Each playbook file SHALL cover one scenario, named by its kebab-case file name, and
SHALL mix Markdown explanation with commands that are directly executable as written.
Each file SHALL state exit-code-level completion criteria for its steps and SHALL
record the gotchas that the environment cannot self-disclose. Playbook files SHALL NOT
copy environment-self-checkable facts (verb lists, configuration formats) that an
owning file already declares; they SHALL reference the owning file instead.

#### Scenario: A playbook command runs as written

- **WHEN** the fixture-ladder playbook's commands are executed in order from
  `deep_research_harness/` on a prepared checkout
- **THEN** each command completes with the file's declared exit-code-level completion
  criteria, ending in a completed fixture run

### Requirement: Receipt discipline keeps playbook facts fresh

A playbook fact that depends on a runtime observation SHALL be backed by a receipt no
older than the last relevant change: the command, its exit code, and the observed
result. When a summon reveals a stale fact, the playbook SHALL be corrected in the
same turn the staleness is discovered; a command that has not been executed in the
current session SHALL NOT be reported as a run result.

#### Scenario: Stale facts are repaired on discovery

- **WHEN** a playbook completion criterion disagrees with the observed exit code of the
  command it documents
- **THEN** the disagreement is treated as a defect in the playbook, and the corrected
  file records the fresh receipt that justifies the new text
