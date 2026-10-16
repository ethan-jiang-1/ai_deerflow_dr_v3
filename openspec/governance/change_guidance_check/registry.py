"""Policy documents and the enabled profile/policy registries.

@impl CHA-001"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import (
    CONTROL_PLACEMENT_POLICY,
    GUIDANCE_ROOT,
    NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
    WORKFLOW_OUTCOME_REVIEW_POLICY,
)

@dataclass(frozen=True)
class PolicyDocument:
    """Canonical policy documentation route, without behavioral authority."""

    path: Path
    index_link: str


@dataclass(frozen=True)
class ProfileDefinition:
    """One reusable profile and its complete canonical policy set."""

    index_path: Path
    policies: frozenset[str]


@dataclass(frozen=True)
class WorkstreamFocus:
    """A workstream section within an active bounded program proposal."""

    stable_id: str
    section: str


def _policy_document(name: str) -> PolicyDocument:
    paths = {
        "authority-and-projections": "core/change-practice.md",
        "change-admission": "core/change-practice.md",
        "local-context": "local/deep-research.md",
        "agent-information-map": "local/deep-research.md",
        "participant-outcomes": "profiles/workflow-control/workflow-control.md",
        "human-interaction-integrity": "profiles/workflow-control/workflow-control.md",
        "control-and-recovery": "profiles/workflow-control/workflow-control.md",
        "workflow-outcome-review": "profiles/workflow-control/workflow-control.md",
        "control-placement": "profiles/workflow-control/workflow-control.md",
        "node-agent-workflow-integrity": "profiles/node-agent/node-agent.md",
        "deerflow-downstream-boundary": "profiles/deerflow-downstream/deerflow-downstream.md",
    }
    return PolicyDocument(
        path=GUIDANCE_ROOT / paths[name],
        index_link=paths[name],
    )


LOCAL_POLICY_REGISTRY = {
    "local-context": _policy_document("local-context"),
    "authority-and-projections": _policy_document("authority-and-projections"),
    "participant-outcomes": _policy_document("participant-outcomes"),
    "human-interaction-integrity": _policy_document("human-interaction-integrity"),
    "control-and-recovery": _policy_document("control-and-recovery"),
    WORKFLOW_OUTCOME_REVIEW_POLICY: _policy_document(WORKFLOW_OUTCOME_REVIEW_POLICY),
    NODE_AGENT_WORKFLOW_INTEGRITY_POLICY: _policy_document(NODE_AGENT_WORKFLOW_INTEGRITY_POLICY),
    "change-admission": _policy_document("change-admission"),
    "agent-information-map": _policy_document("agent-information-map"),
}
PROFILE_DEFINITIONS = {
    "workflow-control": ProfileDefinition(
        GUIDANCE_ROOT / "profiles/workflow-control/workflow-control.md",
        frozenset(
            {
                "participant-outcomes",
                "human-interaction-integrity",
                "control-and-recovery",
                WORKFLOW_OUTCOME_REVIEW_POLICY,
                CONTROL_PLACEMENT_POLICY,
            }
        ),
    ),
    "node-agent": ProfileDefinition(
        GUIDANCE_ROOT / "profiles/node-agent/node-agent.md",
        frozenset({NODE_AGENT_WORKFLOW_INTEGRITY_POLICY}),
    ),
    "deerflow-downstream": ProfileDefinition(
        GUIDANCE_ROOT / "profiles/deerflow-downstream/deerflow-downstream.md",
        frozenset({"deerflow-downstream-boundary"}),
    ),
}
ENABLED_PROFILES = frozenset(PROFILE_DEFINITIONS)
POLICY_REGISTRY = {
    **LOCAL_POLICY_REGISTRY,
    **{
        policy: _policy_document(policy)
        for profile_name in ENABLED_PROFILES
        for policy in PROFILE_DEFINITIONS[profile_name].policies
    },
}
