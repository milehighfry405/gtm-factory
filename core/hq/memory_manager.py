"""
Memory Manager: File-based persistence for GTM Factory sessions.

Implements Anthropic's memory tool pattern using file-based storage.
Handles conversation history, user context, drop metadata, and progressive disclosure.

Based on Anthropic's context management best practices.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json


class MemoryManager:
    """
    Manages persistent storage for GTM Factory sessions.

    Implements file-based memory pattern:
    - user-context.md: Strategic WHY (reload every session)
    - conversation-history.md: Full transcript (reference, don't reload)
    - drop-metadata.json: Lightweight summaries for cross-drop queries
    - session-metadata.json: Session-level index
    - latest.md: Living truth document (synthesized findings)

    Attributes:
        project_path: Path to /projects/{company-name}/
        session_path: Path to current session directory
        session_id: Session identifier (e.g., "session-1-hypothesis")
    """

    def __init__(self, project_path: Path, session_id: str):
        """
        Initialize memory manager for a session.

        Creates necessary directory structure if it doesn't exist:
        /projects/{company}/sessions/{session-id}/
        /projects/{company}/sessions/{session-id}/drops/

        Args:
            project_path: Absolute path to /projects/{company-name}/
            session_id: Session identifier (e.g., "session-1-hypothesis")
        """
        self.project_path = Path(project_path)
        self.session_id = session_id
        self.session_path = self.project_path / "sessions" / session_id

        # Create directory structure
        self.session_path.mkdir(parents=True, exist_ok=True)
        (self.session_path / "drops").mkdir(exist_ok=True)

    def save_conversation_history(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> Path:
        """
        Save full conversation history to conversation-history.md.

        This file is for audit/reference only - not reloaded automatically.
        Use progressive disclosure: read only when needed.

        Args:
            conversation_history: List of message dicts (role, content)

        Returns:
            Path to saved conversation-history.md file
        """
        file_path = self.session_path / "conversation-history.md"

        # Format conversation as markdown
        md_content = f"""# Conversation History

**Session**: {self.session_id}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        for msg in conversation_history:
            role = msg['role'].upper()
            content = msg['content']
            md_content += f"## [{role}]\n\n{content}\n\n---\n\n"

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return file_path

    def save_user_context(self, user_context_md: str, drop_id: Optional[str] = None) -> Path:
        """
        Save user context to user-context.md.

        If drop_id is provided, saves in drop folder.
        Otherwise, saves at session level.

        This file should be reloaded in future sessions - it's the strategic WHY.

        Args:
            user_context_md: Markdown-formatted user context (from ContextExtractor)
            drop_id: Optional drop identifier (e.g., "drop-1")

        Returns:
            Path to saved user-context.md file
        """
        if drop_id:
            # Save in drop folder
            drop_path = self.session_path / "drops" / drop_id
            drop_path.mkdir(parents=True, exist_ok=True)
            file_path = drop_path / "user-context.md"
        else:
            # Save at session level
            file_path = self.session_path / "user-context.md"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(user_context_md)

        return file_path

    def save_drop_metadata(self, drop_id: str, metadata: Dict[str, Any]) -> Path:
        """
        Save lightweight drop metadata for progressive disclosure.

        Metadata should be <2KB - just enough to decide if we need full content.

        Args:
            drop_id: Drop identifier (e.g., "drop-1")
            metadata: Dict with keys: hypothesis, researchers_count, questions, created_at, etc.

        Returns:
            Path to saved drop-metadata.json file
        """
        drop_path = self.session_path / "drops" / drop_id
        drop_path.mkdir(parents=True, exist_ok=True)

        file_path = drop_path / "drop-metadata.json"

        # Add timestamp if not present
        if 'created_at' not in metadata:
            metadata['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        return file_path

    def save_session_metadata(self, metadata: Dict[str, Any]) -> Path:
        """
        Save session-level metadata for session index.

        Used for cross-session queries and onboarding.

        Args:
            metadata: Dict with keys: session_id, hypothesis, drops_count, status, etc.

        Returns:
            Path to saved session-metadata.json file
        """
        file_path = self.session_path / "session-metadata.json"

        # Add timestamp if not present
        if 'created_at' not in metadata:
            metadata['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if 'updated_at' not in metadata:
            metadata['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        return file_path

    def save_latest_md(self, latest_md: str) -> Path:
        """
        Save latest.md - the living truth document.

        This file synthesizes all drops and handles invalidation.
        Always reload this (not individual drops) for current state.

        Args:
            latest_md: Markdown-formatted living truth document

        Returns:
            Path to saved latest.md file
        """
        file_path = self.session_path / "latest.md"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(latest_md)

        return file_path

    def load_user_context(self, drop_id: Optional[str] = None) -> Optional[str]:
        """
        Load user context from user-context.md.

        Args:
            drop_id: Optional drop identifier to load from drop folder

        Returns:
            User context markdown string, or None if not found
        """
        if drop_id:
            file_path = self.session_path / "drops" / drop_id / "user-context.md"
        else:
            file_path = self.session_path / "user-context.md"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_conversation_history(self) -> Optional[str]:
        """
        Load conversation history from conversation-history.md.

        Returns:
            Conversation history markdown string, or None if not found
        """
        file_path = self.session_path / "conversation-history.md"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_latest_md(self) -> Optional[str]:
        """
        Load latest.md - the living truth document.

        Returns:
            Latest.md markdown string, or None if not found
        """
        file_path = self.session_path / "latest.md"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_drop_metadata(self, drop_id: str) -> Optional[Dict[str, Any]]:
        """
        Load drop metadata JSON.

        Args:
            drop_id: Drop identifier

        Returns:
            Metadata dict, or None if not found
        """
        file_path = self.session_path / "drops" / drop_id / "drop-metadata.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_session_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Load session metadata JSON.

        Returns:
            Metadata dict, or None if not found
        """
        file_path = self.session_path / "session-metadata.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_all_drop_ids(self) -> List[str]:
        """
        Get list of all drop IDs for this session.

        Uses progressive disclosure: returns lightweight identifiers, not full content.

        Returns:
            List of drop IDs (e.g., ["drop-1", "drop-2"])
        """
        drops_path = self.session_path / "drops"

        if not drops_path.exists():
            return []

        return [d.name for d in drops_path.iterdir() if d.is_dir()]

    def get_drop_path(self, drop_id: str) -> Path:
        """
        Get path to specific drop directory.

        Args:
            drop_id: Drop identifier

        Returns:
            Path to drop directory
        """
        return self.session_path / "drops" / drop_id

    def create_drop_directory(self, drop_id: str) -> Path:
        """
        Create drop directory structure.

        Args:
            drop_id: Drop identifier (e.g., "drop-1")

        Returns:
            Path to created drop directory
        """
        drop_path = self.session_path / "drops" / drop_id
        drop_path.mkdir(parents=True, exist_ok=True)

        return drop_path

    def get_session_index(self) -> Dict[str, Any]:
        """
        Get lightweight session index for progressive disclosure.

        Returns metadata for ALL drops without loading full content.

        Returns:
            Dict with session info and list of drop metadata
        """
        index = {
            "session_id": self.session_id,
            "session_path": str(self.session_path),
            "drops": []
        }

        # Add session metadata if exists
        session_meta = self.load_session_metadata()
        if session_meta:
            index.update(session_meta)

        # Add drop metadata (lightweight)
        for drop_id in self.get_all_drop_ids():
            drop_meta = self.load_drop_metadata(drop_id)
            if drop_meta:
                index["drops"].append({
                    "drop_id": drop_id,
                    **drop_meta
                })

        return index
