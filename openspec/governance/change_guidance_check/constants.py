"""Declared paths, anchors, field names and line budgets of the guidance tree.

@impl CHA-001"""

from __future__ import annotations

import re
from pathlib import Path

GUIDANCE_ROOT = Path("openspec/change-guidance")
RETIRED_GUIDANCE_ROOTS = (
    Path("openspec/agent-charter"),
    Path("openspec/policies"),
    Path("openspec/guardrails"),
    Path("openspec/governance/agent-charter"),
)
GUIDANCE_ROOT_MEMBERS = frozenset({"README.md", "core", "profiles", "local"})
NODE_AUTHORING_PATH = GUIDANCE_ROOT / "profiles/node-agent/node-agent.md"
OPEN_SPEC_README_PATH = Path("openspec/README.md")
CONFIG_PATH = Path("openspec/config.yaml")
PRODUCT_ROOT = Path("openspec/product")
PRODUCT_DOCUMENT_PATH = PRODUCT_ROOT / "README.md"
PRODUCT_ROOT_MEMBERS = frozenset({"README.md"})
PRODUCT_ROUTE_ANCHOR = "product/README.md"
PLATFORM_ROOT = Path("openspec/platform")
GUIDE_PATH = Path("deep_research_harness/AGENTS.md")
CLAUDE_GUIDE_PATH = Path("deep_research_harness/CLAUDE.md")
README_PATH = Path("deep_research_harness/README.md")
DOCS_INDEX_PATH = Path("deep_research_harness/docs/README.md")
FOCUSED_DOC_PATHS = (
    Path("deep_research_harness/docs/control-map.md"),
    Path("deep_research_harness/docs/local-operations.md"),
    Path("deep_research_harness/docs/testing-and-evaluation.md"),
)
CHANGES_ROOT = Path("openspec/changes")
FOCUS_BEGIN = "<!-- BEGIN: DEEP-RESEARCH-FOCUS-GATE -->"
FOCUS_END = "<!-- END: DEEP-RESEARCH-FOCUS-GATE -->"
CONTEXT_EXPANSION_HEADING = "## Context Expansion Gate"
CONTEXT_EXPANSION_SENTENCE = "A possible future use is not enough to expand scope."
PROGRAM_ROUTE_ANCHOR = "Program form: `## Program Focus` with at least two"
FOCUS_HEADING = "## Change Focus"
FOCUS_FIELDS = (
    "Primary module / causal owner",
    "Seam classification",
    "Question",
    "Necessary adjacent/external contracts",
    "Evidence seam",
    "Not in scope",
    "Triggered review policies",
)
PROGRAM_FOCUS_HEADING = "## Program Focus"
PROGRAM_FOCUS_FIELDS = (
    "Program outcome",
    "Candidate / obligation budget",
    "Declared workstream order",
    "Program decision authority",
    "Shared archive invariant",
    "Program failure / recovery",
    "Split / expansion rule",
    "Not in scope",
)
WORKSTREAM_FOCUS_PREFIX = "### Workstream Focus: "
WORKSTREAM_FIELDS = (
    *FOCUS_FIELDS,
    "Candidate / obligation IDs",
    "Target / retirement",
    "Surface grade",
    "Decision authority",
    "Negative path / recovery",
)
WORKSTREAM_ID_PATTERN = re.compile(r"[a-z][a-z0-9-]*")
SEAM_CLASSIFICATION_FIELD = "Seam classification"
SEAM_CLASSIFICATIONS = frozenset(
    {"cognitive-program", "human-decision", "deterministic-guardrail", "wiring"}
)
TRIGGERED_POLICIES_FIELD = "Triggered review policies"
LEGACY_TRIGGERED_POLICIES_FIELD = "Triggered charter policies"
WORKFLOW_OUTCOME_REVIEW_POLICY = "workflow-outcome-review"
WORKFLOW_OUTCOME_REVIEW_HEADING = "## Workflow Outcome Review"
WORKFLOW_OUTCOME_REVIEW_COLUMNS = (
    "Failure class",
    "Fact owner",
    "Recovery owner and bound",
    "Terminal disposition",
    "Legal next action",
    "Deterministic evidence seam",
)
NODE_AGENT_WORKFLOW_INTEGRITY_POLICY = "node-agent-workflow-integrity"
NODE_AGENT_REVIEW_HEADING = "## Node Agent Review"
NODE_AGENT_REVIEW_COLUMNS = (
    "Surface",
    "Classification",
    "Bounded cognitive question or no-agent rationale",
    "Input authority boundary",
    "Tool posture and runtime enforcer",
    "Candidate result and deterministic admission owner",
    "Failure owner and bound",
    "Deterministic evidence seam",
)
NODE_AGENT_CLASSIFICATIONS = frozenset({"node-agent", "no-agent"})
CONTROL_PLACEMENT_POLICY = "control-placement"
CONTROL_PLACEMENT_REVIEW_HEADING = "## Control Placement Review"
CONTROL_PLACEMENT_TASKS_RULE = "When `Triggered review policies` includes `control-placement`, tasks.md MUST retain"
APPLY_GUIDANCE = "Review control-placement only when the selected proposal declares it; guidance is advisory."
ARCHIVE_GUIDANCE = "Before archive, review control-placement only when the selected proposal declares it; guidance is advisory."
OPERATION_GUIDANCE_ADVISORY_BOUNDARY = "does not execute commands, create or complete tasks, or block native operations"
CLOSEOUT_EVIDENCE_GUIDANCE = (
    "openspec/governance/selected-change-closeout.py verifies only caller-declared committed ranges"
)
CONTROL_PLACEMENT_REVIEW_COLUMNS = (
    "Changed decision or fact",
    "Cognitive candidate or human judgment",
    "Direct fact and deterministic owner/evaluator",
    "Design posture",
    "Protected invariant or legal recovery",
    "Reuse or complexity removed/avoided",
    "Deterministic evidence seam",
)
CONTROL_PLACEMENT_POSTURES = frozenset(
    {"advisory", "bounded-repair", "human-decision", "non-bypassable"}
)

INFORMATION_MAP_POLICY = GUIDANCE_ROOT / "local/deep-research.md"
INFORMATION_MAP_POLICY_ANCHORS = (
    "## Reader Roles",
    "## Line Budgets",
    "deep_research_harness/docs/README.md",
    "control-map.md",
    "local-operations.md",
    "testing-and-evaluation.md",
    "word-count",
    "product/README.md",
    "60 lines",
    "80 lines",
)
GUIDE_INFORMATION_MAP_ANCHORS = ("## Information Map", "README.md", "Makefile")
CONFIG_INFORMATION_MAP_ANCHORS = (
    "## Default Context Boundary",
    "not a project manual",
)
README_READING_MAP = "## Reading Map"
LINE_BUDGETS = (
    (GUIDE_PATH, 120, 160, False),
    (CLAUDE_GUIDE_PATH, 10, 12, False),
    (CONFIG_PATH, 140, 180, False),
    (PRODUCT_DOCUMENT_PATH, 60, 80, False),
    (README_PATH, 200, None, True),
)
PRODUCT_DOCUMENT_ANCHORS = (
    "> role: concise product-context reading map",
    "> authority: navigation only; definitions, requirements, runtime facts, and LLM-node authoring remain with their named owners",
    "CONTEXT.md",
    "main specs",
    "active delta",
    "code",
    "typed contracts",
    "tests",
        "profiles/node-agent/node-agent.md",
)
PRODUCT_AUTHORITY_CLAIM_PATTERN = re.compile(
    r"\b(?:this (?:page|document|map)|product context)\s+"
    r"(?:defines|owns|controls|authorizes|configures)\b",
    re.IGNORECASE,
)
LLM_NODE_AUTHORING_TRIGGER = "creating, changing, or reviewing an LLM-Bearing Node"
AUTHORING_ROUTE_DEMOTION_ANCHOR = "before implementation navigation"
NODE_AUTHORING_ROUTE_ANCHOR = "profiles/node-agent/node-agent.md"
APPLICATION_NODE_AUTHORING_ROUTE = "deep_research_harness/AGENTS.md"
NODE_EDIT_MAP_ROUTE_STEPS = (
    "1. **Classify the surface**",
    "2. **Node Cognitive Control Contract and local capability**",
    "3. **Prompt builder and model-visible context**",
    "4. **Structured output, feedback, and repair**",
    "5. **Focused proof and applicable cognitive evaluation**",
    "6. **Deterministic handoff owners**",
)
NODE_AUTHORING_SEMANTIC_ANCHORS = (
    "Never infer the seam from the first file found or from presence or absence of a model call.",
    "trusted assignment",
    "delimited untrusted content",
    "runtime enforcer",
    "Feedback is data, not authority",
    "stop condition",
    "cognitive evaluation",
    "limitation",
    "observable behavior",
    "## Non-Model Work",
    "why cognition is not causal",
    "Do not invent a capability, prompt, or repair loop.",
)
LOCAL_CONTEXT_SEAM_OWNER_ANCHORS = (
    "**cognitive-program:**",
    "**deterministic-guardrail:**",
    "**human-decision:**",
    "**wiring:**",
    "does not fabricate a prompt obligation",
)
