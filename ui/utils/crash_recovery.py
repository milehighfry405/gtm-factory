"""
Crash Recovery - Detect and recover from incomplete drops.
"""

from pathlib import Path
from typing import List, Dict, Any
from core.ui import StateManager, DropState


class CrashRecovery:
    """
    Handle crash recovery for interrupted drops.

    Features:
    - Detect incomplete drops on startup
    - Offer resume or mark as failed
    - Resume research from last successful point
    """

    def __init__(self, state_manager: StateManager):
        """
        Initialize crash recovery.

        Args:
            state_manager: State manager for current session
        """
        self.state_manager = state_manager

    def find_incomplete_drops(self) -> List[Dict[str, Any]]:
        """
        Find drops that didn't complete.

        Returns:
            List of incomplete drop metadata
        """
        return self.state_manager.find_incomplete_drops()

    def mark_as_failed(self, drop_id: str) -> None:
        """
        Mark drop as failed (user chose not to resume).

        Args:
            drop_id: Drop folder name
        """
        self.state_manager.update_drop_state(drop_id, DropState.FAILED)

    def can_resume(self, drop_id: str) -> bool:
        """
        Check if drop can be resumed.

        Args:
            drop_id: Drop folder name

        Returns:
            True if drop has enough state to resume
        """
        drop_state = self.state_manager.get_drop_state(drop_id)

        # Can only resume from researching state
        # (proposed = nothing done yet, synthesizing = research complete)
        return drop_state == DropState.RESEARCHING

    def resume_drop(self, drop_id: str) -> Dict[str, Any]:
        """
        Resume interrupted drop.

        Args:
            drop_id: Drop folder name

        Returns:
            Resume info dict with state and next steps
        """
        if not self.can_resume(drop_id):
            raise ValueError(f"Cannot resume drop {drop_id}")

        # Load drop metadata to see what was completed
        session_path = self.state_manager.session_path
        drop_path = session_path / "drops" / drop_id

        # Check what files exist
        has_user_context = (drop_path / "user-context.md").exists()
        has_conversation = (drop_path / "conversation-history.md").exists()

        researcher_outputs = list(drop_path.glob("researcher-*-output.md"))
        has_research = len(researcher_outputs) > 0

        return {
            "drop_id": drop_id,
            "has_user_context": has_user_context,
            "has_conversation": has_conversation,
            "has_research": has_research,
            "researcher_count": len(researcher_outputs),
            "next_step": "run_generators" if has_research else "restart_research"
        }
