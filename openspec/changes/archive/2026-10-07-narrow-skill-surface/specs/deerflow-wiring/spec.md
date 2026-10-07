# deerflow-wiring Delta

## MODIFIED Requirements

### Requirement: Skill selection is declared, not implicit

The bound client's skill surface (`available_skills`) SHALL be sourced from an explicit
declaration in the owning configuration file of the selected ladder, resolved at
assembly time and passed to the binding — never hard-coded at the binding site. The
declaration SHALL default to the unwired posture (no skills declared), and the default
assembly SHALL preserve the unwired binding behavior exactly. A declaration that
resolves to a non-default posture SHALL be a conscious configuration act, not a
fallback.

The research ladders (`base` and `fixture`) SHALL each declare exactly the narrowed
research skill surface — `deep-research` and nothing else: the model-visible skill
catalog injected into the lead agent's system prompt during a research run SHALL
contain the deep-research entry and SHALL NOT contain entries for skills unrelated to
research. Narrowing the visible catalog grants no tools, permissions, routes, or
forced usage: whether the agent loads and follows the skill remains the agent's own
decision.

A contract guard SHALL lock the declaration posture offline (stdlib-only, no framework
import): it SHALL fail when the binding stops sourcing the skill surface from the
declaration, when the default posture silently changes, when the declaration parser
swallows or coerces a declared value, or when either research ladder's declared skill
list is no longer exactly `deep-research`. Loading-level activation semantics for the
declared surface — that the framework injects the narrowed catalog into the
model-visible prompt — SHALL be proven by the fixture-ladder CLI journey's snapshot
assertions (zero credentials). Usage-level quality — whether the agent actually loads
and follows the deep-research methodology on real runs — remains outside this
requirement's scope and needs credentialed real-ladder evidence.

#### Scenario: Default posture is declared-none and preserved

- **WHEN** the configuration declares no skills and assembly builds the client through
  a recording stand-in
- **THEN** the binding receives the unwired skill posture (no skills), matching the
  pre-declaration binding behavior

#### Scenario: An implicit or coerced skill surface fails the guard

- **WHEN** the binding hard-codes a skill surface, ignores the declaration, or the
  declaration parser coerces or swallows a declared value
- **THEN** the offline contract guard fails naming the violated seam

#### Scenario: Declaration drift fails loudly without touching the framework

- **WHEN** the guard runs offline (no framework import, no credentials)
- **THEN** it validates the declaration-to-binding seam using the contract mirror and
  recording stand-ins only

#### Scenario: The research ladders declare exactly the narrowed surface

- **WHEN** the offline guard reads the checked-in ladder configurations
- **THEN** both `base` and `fixture` declare a skill list of exactly `deep-research`,
  and any widening, narrowing, or removal of the declaration fails the guard

#### Scenario: The narrowed catalog is what the model sees

- **WHEN** a fixture-ladder create runs on the real CLI subprocess and the assembly
  snapshot's system prompt is inspected
- **THEN** the skill catalog index contains the `deep-research` entry and contains no
  entry for skills unrelated to research, with no credential required

#### Scenario: A silently dropped declaration trips the journey

- **WHEN** the framework ignores the declared skill list or the declared name cannot be
  resolved at injection time
- **THEN** the fixture-ladder journey's narrowed-catalog snapshot assertion fails,
  exposing the dropped declaration deterministically
