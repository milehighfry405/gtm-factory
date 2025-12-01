"""
UI Adapters - Thin wrappers around existing modules for UI integration.

All adapters follow the same pattern:
- Do NOT modify existing modules
- Add progress callbacks for UI
- Add status tracking
- Handle errors gracefully
"""

from core.ui.adapters.hq_adapter import HQAdapter
from core.ui.adapters.researcher_adapter import ResearcherAdapter, ResearcherStatus
from core.ui.adapters.generator_adapter import GeneratorAdapter, GeneratorStatus

__all__ = [
    "HQAdapter",
    "ResearcherAdapter",
    "ResearcherStatus",
    "GeneratorAdapter",
    "GeneratorStatus",
]
