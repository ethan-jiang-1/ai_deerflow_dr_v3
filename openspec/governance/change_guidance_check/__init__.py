"""Implementation of the Change Guidance checker.

The executable entry point stays at `../check_change_guidance.py`: the aggregate
gate, the CI canonical sequence and the copied-script test fixture all address
that path. This package holds the rules; the entry point holds the CLI and
delegates its whole attribute surface here.

@impl CHA-001
"""

from __future__ import annotations

import sys
from pathlib import Path

# The entry point is copied into a temporary repository by the governance
# fixtures; resolving the kernel and this package from *this* file's directory
# keeps a copied entry point working on its own copy.
_GOVERNANCE_DIR = str(Path(__file__).resolve().parent)
if _GOVERNANCE_DIR not in sys.path:
    sys.path.insert(0, _GOVERNANCE_DIR)

from .constants import *  # noqa: F401,F403  (declared tables are the package surface)
from .constants import __dict__ as _constants_dict
from .facade import main, validate
from .guidance import (
    _validate_change_guidance_tree,
    _validate_claude_guide,
    _validate_focus_gate,
    _validate_information_map,
    _validate_llm_node_authoring_pointer,
    _validate_node_edit_map_route,
    _validate_product_context,
)
from .helpers import (
    ContractViolation,
    _comma_separated_values,
    _field_value,
    _is_markdown_separator,
    _line_count,
    _read_file,
    _require_fragment,
    _scoped_code,
    _section_after_heading,
    _single_markdown_table_lines,
    _table_cells,
    _validate_legacy_triggered_policies_field,
    _validate_required_fields,
    _validate_seam_classification,
)
from .proposals import (
    _triggered_policies,
    _validate_active_changes,
    _validate_authoring_pointer,
    _validate_ordinary_proposal,
    _validate_program_proposal,
    _workstream_sections,
)
from .registry import (
    ENABLED_PROFILES,
    LOCAL_POLICY_REGISTRY,
    POLICY_REGISTRY,
    PROFILE_DEFINITIONS,
    PolicyDocument,
    ProfileDefinition,
    WorkstreamFocus,
    _policy_document,
)
from .reviews import (
    _review_section,
    _validate_control_placement_review,
    _validate_node_agent_review,
    _validate_selected_policy_reviews,
    _validate_workflow_outcome_review,
)
from .tasks import _validate_change_tasks

# Re-export every declared constant by name, so `check_change_guidance.CONSTANT`
# keeps working for tests, fixtures and human readers.
globals().update(
    {
        name: value
        for name, value in _constants_dict.items()
        if not name.startswith("__") and name not in {"re", "Path"}
    }
)

__all__ = [name for name in globals() if not name.startswith("__")]
