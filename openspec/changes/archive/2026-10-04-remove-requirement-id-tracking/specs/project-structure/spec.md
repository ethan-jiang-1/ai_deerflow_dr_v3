# Spec Delta

> req: PRS-001

## Purpose

<!-- modified capability: project-structure -->

## REMOVED Requirements

### Requirement: Registered requirements are owned by specs

**Reason**: Requirement-number tracking is retired for this project. The registry, the
`> req:` ownership headers, and the orphan/retirement semantics existed only to serve
this tracking; with it gone the requirement has no subject, and keeping it would force
every future spec change to maintain bookkeeping that decides nothing.

**Migration**: Strip every `> req:` header line from all main specs and active delta
specs; delete `openspec/governance/req-registry.yaml` together with
`check_project_reqs.py` and `check_project_req_coverage.py`; remove the
requirement-reservation phase from the plan gate and the two checkers from the closeout
gate inventory; regroup `required-paths.toml` under semantic family names and drop the
`requirement_ids` field from `project-structure.toml`; delete the new-requirement-ID
rule from `openspec/config.yaml`. Structural validation, spec structure validation, and
the closeout gate keep their remaining guarantees unchanged.
