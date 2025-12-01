"""
State Manager - Session and drop state tracking with crash recovery support.

Handles:
- Session state persistence (conversation history, metadata)
- Drop state tracking (proposed → researching → synthesizing → complete)
- Atomic file writes (prevent corruption)
- Autosave conversation after each message

Follows Anthropic's memory tool pattern for persistent state.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DropState(str, Enum):
    """Drop lifecycle states."""
    PROPOSED = "proposed"
    RESEARCHING = "researching"
    SYNTHESIZING = "synthesizing"
    COMPLETE = "complete"
    FAILED = "failed"


class StateManager:
    """
    Manages session and drop state with crash recovery support.

    Key responsibilities:
    - Track session state (conversation, current drop)
    - Track drop state (lifecycle: proposed → complete)
    - Autosave conversation after each message
    - Atomic file writes (no corruption)
    - Detect incomplete drops on startup

    Example:
        manager = StateManager(session_path=Path("projects/demo-company/sessions/session-1"))
        manager.autosave_conversation(messages)
        manager.update_drop_state("drop-1", DropState.RESEARCHING)
    """

    def __init__(self, session_path: Path):
        """
        Initialize state manager for a session.

        Args:
            session_path: Path to session directory (e.g., projects/demo-company/sessions/session-1)
        """
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # State files
        self.conversation_temp_file = self.session_path / "conversation-temp.md"
        self.session_state_file = self.session_path / "session-state.json"

    def autosave_conversation(self, messages: List[Dict[str, str]]) -> None:
        """
        Autosave conversation after each message (crash recovery).

        Writes to temporary file atomically to prevent corruption.

        Args:
            messages: List of chat messages [{"role": "user", "content": "..."}, ...]
        """
        # Format conversation as markdown
        conversation_md = self._format_conversation_md(messages)

        # Atomic write (tmp → rename)
        self._atomic_write(self.conversation_temp_file, conversation_md)

    def load_conversation(self) -> Optional[List[Dict[str, str]]]:
        """
        Load conversation from temp file (for crash recovery).

        Returns:
            List of messages or None if no saved conversation
        """
        if not self.conversation_temp_file.exists():
            return None

        conversation_md = self.conversation_temp_file.read_text(encoding="utf-8")
        return self._parse_conversation_md(conversation_md)

    def promote_conversation_to_drop(self, drop_id: str, messages: List[Dict[str, str]]) -> None:
        """
        Promote temp conversation to drop folder (on research start).

        Copies conversation-temp.md → drops/drop-N/conversation-history.md

        Args:
            drop_id: Drop folder name (e.g., "drop-1")
            messages: List of chat messages
        """
        drop_path = self.session_path / "drops" / drop_id
        drop_path.mkdir(parents=True, exist_ok=True)

        conversation_md = self._format_conversation_md(messages)
        history_file = drop_path / "conversation-history.md"

        self._atomic_write(history_file, conversation_md)

    def update_drop_state(self, drop_id: str, state: DropState) -> None:
        """
        Update drop state (for crash recovery).

        Saves to drops/drop-N/drop-state.json atomically.

        Args:
            drop_id: Drop folder name (e.g., "drop-1")
            state: New drop state
        """
        drop_path = self.session_path / "drops" / drop_id
        drop_path.mkdir(parents=True, exist_ok=True)

        state_file = drop_path / "drop-state.json"

        # Load existing state or create new
        if state_file.exists():
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
        else:
            state_data = {
                "drop_id": drop_id,
                "created_at": datetime.now().isoformat()
            }

        # Update state (handle both string and Enum)
        state_data["state"] = state.value if hasattr(state, 'value') else state
        state_data["updated_at"] = datetime.now().isoformat()

        # Atomic write
        self._atomic_write(state_file, json.dumps(state_data, indent=2))

    def get_drop_state(self, drop_id: str) -> Optional[DropState]:
        """
        Get current drop state.

        Args:
            drop_id: Drop folder name

        Returns:
            DropState or None if drop doesn't exist
        """
        state_file = self.session_path / "drops" / drop_id / "drop-state.json"

        if not state_file.exists():
            return None

        state_data = json.loads(state_file.read_text(encoding="utf-8"))
        return DropState(state_data["state"])

    def find_incomplete_drops(self) -> List[Dict[str, Any]]:
        """
        Find drops that didn't complete (crash recovery).

        Returns:
            List of incomplete drops with metadata:
            [{"drop_id": "drop-1", "state": "researching", "created_at": "..."}, ...]
        """
        incomplete = []

        drops_dir = self.session_path / "drops"
        if not drops_dir.exists():
            return incomplete

        for drop_dir in drops_dir.iterdir():
            if not drop_dir.is_dir():
                continue

            state_file = drop_dir / "drop-state.json"
            if not state_file.exists():
                continue

            state_data = json.loads(state_file.read_text(encoding="utf-8"))
            state = DropState(state_data["state"])

            # Incomplete states
            if state in [DropState.PROPOSED, DropState.RESEARCHING, DropState.SYNTHESIZING]:
                incomplete.append(state_data)

        return incomplete

    def save_session_state(self, state: Dict[str, Any]) -> None:
        """
        Save session-level state (current drop, research flag, etc.).

        Args:
            state: Session state dict (arbitrary JSON-serializable data)
        """
        self._atomic_write(self.session_state_file, json.dumps(state, indent=2))

    def load_session_state(self) -> Optional[Dict[str, Any]]:
        """
        Load session-level state.

        Returns:
            Session state dict or None if no saved state
        """
        if not self.session_state_file.exists():
            return None

        return json.loads(self.session_state_file.read_text(encoding="utf-8"))

    def _atomic_write(self, file_path: Path, content: str) -> None:
        """
        Atomic file write (prevents corruption).

        Write to temp file, then rename (atomic operation on most filesystems).

        Args:
            file_path: Destination file path
            content: Content to write
        """
        tmp_file = file_path.with_suffix(file_path.suffix + '.tmp')
        tmp_file.write_text(content, encoding="utf-8")
        tmp_file.replace(file_path)  # Atomic rename

    def _format_conversation_md(self, messages: List[Dict[str, str]]) -> str:
        """
        Format conversation messages as markdown.

        Args:
            messages: List of chat messages

        Returns:
            Markdown formatted conversation
        """
        lines = ["# Conversation History\n"]

        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            lines.append(f"## {role}\n")
            lines.append(f"{content}\n")

        return "\n".join(lines)

    def _parse_conversation_md(self, conversation_md: str) -> List[Dict[str, str]]:
        """
        Parse markdown conversation back to messages list.

        Args:
            conversation_md: Markdown formatted conversation

        Returns:
            List of chat messages
        """
        messages = []
        current_role = None
        current_content = []

        for line in conversation_md.split("\n"):
            if line.startswith("## USER"):
                if current_role:
                    messages.append({"role": current_role, "content": "\n".join(current_content).strip()})
                current_role = "user"
                current_content = []
            elif line.startswith("## ASSISTANT"):
                if current_role:
                    messages.append({"role": current_role, "content": "\n".join(current_content).strip()})
                current_role = "assistant"
                current_content = []
            elif line.startswith("# "):
                # Skip title
                continue
            else:
                current_content.append(line)

        # Add last message
        if current_role:
            messages.append({"role": current_role, "content": "\n".join(current_content).strip()})

        return messages
