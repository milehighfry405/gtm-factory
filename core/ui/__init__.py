"""
UI module - Agent-Computer Interface (ACI) layer for GTM Factory.

Provides adapters and utilities for integrating backend modules with UI:
- State management (session/drop persistence, crash recovery)
- Context tracking (token counting, window monitoring)
- Adapters (HQ, Researcher, Generators)

Following Anthropic guidance: "Invest just as much effort in creating good
agent-computer interfaces (ACI) as human-computer interfaces (HCI)."
"""

from core.ui.state_manager import StateManager, DropState
from core.ui.context_tracker import ContextTracker
from core.ui.adapters.hq_adapter import HQAdapter
from core.ui.adapters.researcher_adapter import ResearcherAdapter, ResearcherStatus
from core.ui.adapters.generator_adapter import GeneratorAdapter, GeneratorStatus

__all__ = [
    "StateManager",
    "DropState",
    "ContextTracker",
    "HQAdapter",
    "ResearcherAdapter",
    "ResearcherStatus",
    "GeneratorAdapter",
    "GeneratorStatus",
]
