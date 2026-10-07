# deerflow-wiring Delta

## ADDED Requirements

### Requirement: Skill selection is declared, not implicit

The bound client's skill surface (`available_skills`) SHALL be sourced from an explicit
declaration in the owning configuration file of the selected ladder, resolved at
assembly time and passed to the binding — never hard-coded at the binding site. The
declaration SHALL default to the unwired posture (no skills declared), and the default
assembly SHALL preserve the current binding behavior exactly. A declaration that
resolves to a non-default posture SHALL be a conscious configuration act, not a
fallback.

A contract guard SHALL lock the default posture offline (stdlib-only, no framework
import): it SHALL fail when the binding stops sourcing the skill surface from the
declaration, when the default posture silently changes, or when the declaration parser
swallows or coerces a declared value. Actual skill activation semantics — what the
framework loads and with what quality — are outside this requirement's scope and need
their own cognitive-program establishment before any non-default declaration ships.

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
