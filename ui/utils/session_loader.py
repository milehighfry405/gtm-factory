"""
Session Loader - Utilities for loading and saving session state.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json


class SessionLoader:
    """
    Load and save session state.

    Handles:
    - Session metadata
    - Conversation history
    - Current state (drop counter, research flag, etc.)
    """

    @staticmethod
    def load_session(session_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load session state from disk.

        Args:
            session_path: Path to session directory

        Returns:
            Session state dict or None if not found
        """
        state_file = session_path / "session-state.json"

        if not state_file.exists():
            return None

        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    @staticmethod
    def save_session(session_path: Path, state: Dict[str, Any]) -> None:
        """
        Save session state to disk.

        Args:
            session_path: Path to session directory
            state: Session state dict
        """
        session_path.mkdir(parents=True, exist_ok=True)
        state_file = session_path / "session-state.json"

        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    @staticmethod
    def get_drop_count(session_path: Path) -> int:
        """
        Get number of drops in session.

        Args:
            session_path: Path to session directory

        Returns:
            Number of drops
        """
        drops_dir = session_path / "drops"

        if not drops_dir.exists():
            return 0

        return len([d for d in drops_dir.iterdir() if d.is_dir() and d.name.startswith("drop-")])
