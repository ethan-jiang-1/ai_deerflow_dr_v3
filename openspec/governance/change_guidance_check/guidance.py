"""Guidance tree, product context, focus gate, Claude stub and information map.

@impl CHA-001"""

from __future__ import annotations

import re
from pathlib import Path

from .constants import (
    APPLICATION_NODE_AUTHORING_ROUTE,
    AUTHORING_ROUTE_DEMOTION_ANCHOR,
    CLAUDE_GUIDE_PATH,
    CONFIG_INFORMATION_MAP_ANCHORS,
    CONFIG_PATH,
    CONTEXT_EXPANSION_HEADING,
    CONTEXT_EXPANSION_SENTENCE,
    DOCS_INDEX_PATH,
    FOCUSED_DOC_PATHS,
    GUIDE_INFORMATION_MAP_ANCHORS,
    GUIDE_PATH,
    GUIDANCE_ROOT,
    GUIDANCE_ROOT_MEMBERS,
    INFORMATION_MAP_POLICY,
    INFORMATION_MAP_POLICY_ANCHORS,
    LINE_BUDGETS,
    LLM_NODE_AUTHORING_TRIGGER,
    LOCAL_CONTEXT_SEAM_OWNER_ANCHORS,
    NODE_AUTHORING_ROUTE_ANCHOR,
    NODE_AUTHORING_SEMANTIC_ANCHORS,
    NODE_EDIT_MAP_ROUTE_STEPS,
    OPEN_SPEC_README_PATH,
    PLATFORM_ROOT,
    PRODUCT_AUTHORITY_CLAIM_PATTERN,
    PRODUCT_DOCUMENT_ANCHORS,
    PRODUCT_DOCUMENT_PATH,
    PRODUCT_ROOT,
    PRODUCT_ROOT_MEMBERS,
    PRODUCT_ROUTE_ANCHOR,
    PROGRAM_ROUTE_ANCHOR,
    README_PATH,
    README_READING_MAP,
    RETIRED_GUIDANCE_ROOTS,
)
from .helpers import (
    ContractViolation,
    _line_count,
    _read_file,
    _require_fragment,
    _without_fences,
)
from .registry import ENABLED_PROFILES, POLICY_REGISTRY, PROFILE_DEFINITIONS

def _validate_llm_node_authoring_pointer(text: str, path: Path, *, code_prefix: str) -> None:
    normalized = re.sub(r"\s+", " ", text)
    trigger_position = normalized.find(LLM_NODE_AUTHORING_TRIGGER)
    link_position = normalized.find(NODE_AUTHORING_ROUTE_ANCHOR, trigger_position)
    demotion_position = normalized.find(AUTHORING_ROUTE_DEMOTION_ANCHOR, trigger_position)
    if min(trigger_position, link_position, demotion_position) == -1:
        raise ContractViolation(
            f"{code_prefix}.node_authoring_route_missing",
            f"LLM-node authoring route is missing from {path.as_posix()}",
        )
    if not trigger_position <= link_position < demotion_position:
        raise ContractViolation(
            f"{code_prefix}.node_authoring_route_demoted",
            f"node-agent authoring gate must precede implementation navigation: {path.as_posix()}",
        )


def _validate_node_edit_map_route(node_edit_map: str, path: Path) -> None:
    positions: list[int] = []
    for step in NODE_EDIT_MAP_ROUTE_STEPS:
        position = node_edit_map.find(step)
        if position == -1:
            raise ContractViolation(
                "guidance.node_edit_map_route_missing",
                f"node edit map lacks cognitive-first route step {step!r}: {path.as_posix()}",
            )
        positions.append(position)
    if positions != sorted(positions):
        raise ContractViolation(
            "guidance.node_edit_map_route_order_invalid",
            f"node edit map must retain its ordered cognitive-first route: {path.as_posix()}",
        )
    normalized = re.sub(r"\s+", " ", node_edit_map)
    for anchor in NODE_AUTHORING_SEMANTIC_ANCHORS:
        normalized_anchor = re.sub(r"\s+", " ", anchor)
        if normalized_anchor not in normalized:
            raise ContractViolation(
                "guidance.node_edit_map_semantics_missing",
                f"node edit map lacks semantic gate {anchor!r}: {path.as_posix()}",
            )


def _validate_product_context(root: Path) -> None:
    product_path = root / PRODUCT_ROOT
    if not product_path.is_dir():
        raise ContractViolation(
            "product.document_missing",
            f"product context directory is missing: {PRODUCT_ROOT.as_posix()}",
        )
    if product_path.is_symlink() or {path.name for path in product_path.iterdir()} != PRODUCT_ROOT_MEMBERS:
        raise ContractViolation(
            "product.root_members_mismatch",
            f"product context members must equal {sorted(PRODUCT_ROOT_MEMBERS)!r}: {PRODUCT_ROOT.as_posix()}",
        )
    if (root / PLATFORM_ROOT).exists() or (root / PLATFORM_ROOT).is_symlink():
        raise ContractViolation(
            "product.platform_present",
            f"a platform documentation tree is forbidden: {PLATFORM_ROOT.as_posix()}",
        )

    product_document = _read_file(root, PRODUCT_DOCUMENT_PATH, code="product.document_missing")
    authority_lines = re.findall(
        r"^> authority:.*$", _without_fences(product_document), flags=re.MULTILINE
    )
    if len(authority_lines) != 1 or not authority_lines[0].startswith("> authority: navigation only; "):
        raise ContractViolation(
            "product.authority_claim",
            f"product context must retain its navigation-only authority boundary: {PRODUCT_DOCUMENT_PATH.as_posix()}",
        )
    if PRODUCT_AUTHORITY_CLAIM_PATTERN.search(product_document):
        raise ContractViolation(
            "product.authority_claim",
            f"product context must not claim runtime or specification authority: {PRODUCT_DOCUMENT_PATH.as_posix()}",
        )
    normalized_product_document = product_document.lower()
    for anchor in PRODUCT_DOCUMENT_ANCHORS:
        _require_fragment(
            normalized_product_document,
            anchor.lower(),
            code="product.authority_route_missing",
            detail=(
                f"product context lacks authority-routing anchor {anchor!r}: "
                f"{PRODUCT_DOCUMENT_PATH.as_posix()}"
            ),
        )

    for path in (OPEN_SPEC_README_PATH, CONFIG_PATH, GUIDANCE_ROOT / "README.md"):
        entry = _read_file(root, path, code="product.entry_route_missing")
        _require_fragment(
            entry,
            PRODUCT_ROUTE_ANCHOR,
            code="product.entry_route_missing",
            detail=f"product context route is missing from {path.as_posix()}",
        )


def _validate_change_guidance_tree(root: Path) -> None:
    for retired_root in RETIRED_GUIDANCE_ROOTS:
        path = root / retired_root
        if path.exists() or path.is_symlink():
            raise ContractViolation(
                "guidance.retired_tree_present",
                f"retired guidance tree must be absent: {retired_root.as_posix()}",
            )

    guidance_path = root / GUIDANCE_ROOT
    index_path = GUIDANCE_ROOT / "README.md"
    principles_path = GUIDANCE_ROOT / "core/change-practice.md"
    node_edit_map_path = GUIDANCE_ROOT / "profiles/node-agent/node-agent.md"
    index = _read_file(root, index_path, code="charter.path_missing")
    principles = _read_file(root, principles_path, code="charter.path_missing")
    node_edit_map = _read_file(root, node_edit_map_path, code="guidance.node_edit_map_missing")
    _validate_node_edit_map_route(node_edit_map, node_edit_map_path)
    _require_fragment(
        index,
        APPLICATION_NODE_AUTHORING_ROUTE,
        code="guidance.application_authoring_route_missing",
        detail=f"Change Guidance does not route to the application-owned coding guide: {index_path.as_posix()}",
    )

    if guidance_path.is_symlink() or {path.name for path in guidance_path.iterdir()} != GUIDANCE_ROOT_MEMBERS:
        raise ContractViolation(
            "guidance.root_members_mismatch",
            f"Change Guidance members must equal {sorted(GUIDANCE_ROOT_MEMBERS)!r}: {GUIDANCE_ROOT.as_posix()}",
        )

    expected_members = {
        GUIDANCE_ROOT / "core": {"change-practice.md"},
        GUIDANCE_ROOT / "profiles/workflow-control": {"workflow-control.md"},
        GUIDANCE_ROOT / "profiles/node-agent": {"node-agent.md"},
        GUIDANCE_ROOT / "profiles/deerflow-downstream": {"deerflow-downstream.md"},
        GUIDANCE_ROOT / "local": {"deep-research.md"},
    }
    for directory, members in expected_members.items():
        path = root / directory
        if path.is_symlink() or {item.name for item in path.iterdir()} != members:
            raise ContractViolation("guidance.policy_members_mismatch", f"members mismatch: {directory.as_posix()}")

    unknown_profiles = ENABLED_PROFILES - PROFILE_DEFINITIONS.keys()
    if unknown_profiles:
        raise ContractViolation(
            "guidance.profile_unknown",
            f"enabled profiles are not defined: {sorted(unknown_profiles)!r}",
        )
    for profile_name in ENABLED_PROFILES:
        profile = PROFILE_DEFINITIONS[profile_name]
        _read_file(root, profile.index_path, code="guidance.profile_incomplete")
        for policy in profile.policies:
            document = POLICY_REGISTRY.get(policy)
            if document is None:
                raise ContractViolation(
                    "guidance.profile_incomplete",
                    f"enabled profile {profile_name!r} lacks policy binding {policy!r}",
                )
            _read_file(root, document.path, code="guidance.profile_incomplete")

    _require_fragment(
        index,
        "core/change-practice.md",
        code="charter.index_link_missing",
        detail=f"Change Guidance index does not link to {principles_path.as_posix()}",
    )
    _require_fragment(
        index,
        "## Policy Route",
        code="charter.index_route_missing",
        detail=f"charter index lacks a policy route: {index_path.as_posix()}",
    )
    _require_fragment(
        principles,
        "authority: guidance only",
        code="charter.authority_boundary_missing",
        detail=f"Change Guidance principles lack their non-authority boundary: {principles_path.as_posix()}",
    )
    for policy, document in POLICY_REGISTRY.items():
        policy_text = _read_file(root, document.path, code="charter.path_missing")
        _require_fragment(
            index,
            document.index_link,
            code="charter.index_link_missing",
            detail=f"charter index does not link to {document.path.as_posix()}",
        )
        _require_fragment(
            policy_text,
            "> trigger:",
            code="charter.policy_trigger_missing",
            detail=f"policy lacks a trigger: {document.path.as_posix()}",
        )
        _require_fragment(
            policy_text,
            "authority: guidance only",
            code="charter.policy_boundary_missing",
            detail=f"policy lacks its non-authority boundary: {document.path.as_posix()}",
        )

    local_context_path = GUIDANCE_ROOT / "local/deep-research.md"
    local_context = _read_file(root, local_context_path, code="charter.path_missing")
    _require_fragment(
        local_context,
        CONTEXT_EXPANSION_HEADING,
        code="charter.context_expansion_policy_missing",
        detail=f"local-context policy lacks its context-expansion gate: {local_context_path.as_posix()}",
    )
    _require_fragment(
        local_context,
        PROGRAM_ROUTE_ANCHOR,
        code="charter.program_route_local_context_missing",
        detail=f"local-context policy lacks the bounded-program route: {local_context_path.as_posix()}",
    )
    for anchor in LOCAL_CONTEXT_SEAM_OWNER_ANCHORS:
        _require_fragment(
            local_context,
            anchor,
            code="charter.local_context_seam_owner_missing",
            detail=f"local-context policy lacks seam-owner rule {anchor!r}: {local_context_path.as_posix()}",
        )
    change_admission_path = GUIDANCE_ROOT / "local/deep-research.md"
    change_admission = _read_file(root, change_admission_path, code="charter.path_missing")
    _require_fragment(
        change_admission,
        PROGRAM_ROUTE_ANCHOR,
        code="charter.program_route_change_admission_missing",
        detail=f"change-admission policy lacks the bounded-program route: {change_admission_path.as_posix()}",
    )

    openspec_readme = _read_file(root, OPEN_SPEC_README_PATH, code="guidance.openspec_root_missing")
    for fragment in ("config.yaml", "specs/", "changes/", "change-guidance/README.md", "governance/"):
        _require_fragment(
            openspec_readme,
            fragment,
            code="guidance.openspec_root_route_missing",
            detail=f"OpenSpec root navigation lacks {fragment!r}: {OPEN_SPEC_README_PATH.as_posix()}",
        )


def _validate_focus_gate(root: Path) -> None:
    guide = _read_file(root, GUIDE_PATH, code="guide.missing")
    _validate_node_edit_map_route(guide, GUIDE_PATH)
    _require_fragment(
        guide,
        "Primary application owner",
        code="guide.module_route_missing",
        detail=f"application guide lacks the primary-owner routing table: {GUIDE_PATH.as_posix()}",
    )
    _require_fragment(
        guide,
        CONTEXT_EXPANSION_SENTENCE,
        code="guide.context_expansion_rule_missing",
        detail=f"application guide lacks its context-expansion rule: {GUIDE_PATH.as_posix()}",
    )
    for forbidden in ("openspec/", "../openspec", "openspec.governance"):
        if forbidden in guide:
            raise ContractViolation(
                "guide.upstream_dependency_present",
                f"downstream application guide depends on upstream framework {forbidden!r}",
            )


def _validate_claude_guide(root: Path) -> None:
    claude_guide = _read_file(root, CLAUDE_GUIDE_PATH, code="guide.claude_entrypoint_missing")
    if not re.search(r"^@AGENTS\.md\s*$", claude_guide, flags=re.MULTILINE):
        raise ContractViolation(
            "guide.claude_import_missing",
            f"Claude Code entrypoint must import AGENTS.md: {CLAUDE_GUIDE_PATH.as_posix()}",
        )


def _validate_human_docs(root: Path, readme: str) -> None:
    for path in (DOCS_INDEX_PATH, *FOCUSED_DOC_PATHS):
        relative_to_module = path.relative_to("deep_research_harness").as_posix()
        _require_fragment(
            readme,
            relative_to_module,
            code="readme.docs_link_missing",
            detail=f"README does not link to {relative_to_module}: {README_PATH.as_posix()}",
        )

    docs_index = _read_file(root, DOCS_INDEX_PATH, code="docs.index_missing")
    for path in FOCUSED_DOC_PATHS:
        _read_file(root, path, code="docs.focused_document_missing")
        _require_fragment(
            docs_index,
            path.name,
            code="docs.index_link_missing",
            detail=f"documentation index does not link to {path.name}: {DOCS_INDEX_PATH.as_posix()}",
        )


def _validate_information_map(root: Path) -> list[str]:
    policy = _read_file(root, INFORMATION_MAP_POLICY, code="charter.path_missing")
    for anchor in INFORMATION_MAP_POLICY_ANCHORS:
        _require_fragment(
            policy,
            anchor,
            code="charter.information_map_policy_missing",
            detail=(f"information-map policy lacks required anchor {anchor!r}: {INFORMATION_MAP_POLICY.as_posix()}"),
        )

    guide = _read_file(root, GUIDE_PATH, code="guide.missing")
    for anchor in GUIDE_INFORMATION_MAP_ANCHORS:
        _require_fragment(
            guide,
            anchor,
            code="guide.information_map_missing",
            detail=f"module guide lacks information-map anchor {anchor!r}: {GUIDE_PATH.as_posix()}",
        )

    readme = _read_file(root, README_PATH, code="readme.missing")
    matches = list(re.finditer(r"^## Reading Map\s*$", readme, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "readme.reading_map_missing",
            f"README must contain exactly one {README_READING_MAP!r}: {README_PATH.as_posix()}",
        )
    reading_map_line = readme[: matches[0].start()].count("\n") + 1
    if reading_map_line > 80:
        raise ContractViolation(
            "readme.reading_map_position",
            f"{README_READING_MAP!r} must start within the first 80 lines, found line {reading_map_line}: "
            f"{README_PATH.as_posix()}",
        )
    _validate_human_docs(root, readme)

    config = _read_file(root, CONFIG_PATH, code="config.missing")
    for anchor in CONFIG_INFORMATION_MAP_ANCHORS:
        _require_fragment(
            config,
            anchor,
            code="config.information_map_missing",
            detail=f"OpenSpec configuration lacks information-map anchor {anchor!r}: {CONFIG_PATH.as_posix()}",
        )

    documents = {
        GUIDE_PATH: guide,
        CLAUDE_GUIDE_PATH: _read_file(root, CLAUDE_GUIDE_PATH, code="guide.claude_entrypoint_missing"),
        CONFIG_PATH: config,
        PRODUCT_DOCUMENT_PATH: _read_file(root, PRODUCT_DOCUMENT_PATH, code="product.document_missing"),
        README_PATH: readme,
    }
    warnings: list[str] = []
    for path, warning_at, maximum, warning_is_exclusive in LINE_BUDGETS:
        line_count = _line_count(documents[path])
        warning_reached = line_count > warning_at if warning_is_exclusive else line_count >= warning_at
        if maximum is not None and line_count > maximum:
            raise ContractViolation(
                "entry.line_budget_exceeded",
                f"{path.as_posix()} has {line_count} lines; maximum is {maximum}",
            )
        if warning_reached:
            operator = "above" if warning_is_exclusive else "at or above"
            warnings.append(
                f"[entry.line_budget_warning] {path.as_posix()} has {line_count} lines "
                f"({operator} warning threshold {warning_at})"
            )
    return warnings
