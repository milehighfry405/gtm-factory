"""
Session Metadata Generator - Creates JSON metadata for progressive disclosure.

Enables lightweight scanning of session history without loading full content.
Follows Anthropic's "just-in-time" loading pattern.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class SessionMetadataGenerator:
    """
    Generates metadata files for progressive disclosure.

    Creates:
    - session-metadata.json (session-level summary)
    - drop-metadata.json (per-drop details)

    Enables pattern: Scan metadata → Load only relevant latest.md

    Example:
        generator = SessionMetadataGenerator()
        metadata = generator.generate_session_metadata(
            session_path=Path("projects/demo-company/sessions/session-1")
        )
    """

    def generate_session_metadata(self, session_path: Path) -> Dict:
        """
        Generate session-metadata.json from session directory.

        Args:
            session_path: Path to session directory

        Returns:
            Dict with session metadata
        """
        # Extract session info from path
        session_id = session_path.name  # e.g., "session-demo-researcher"

        # Find all drops
        drops_path = session_path / "drops"
        drop_folders = sorted([d for d in drops_path.iterdir() if d.is_dir()])

        # Generate drop summaries
        drop_summaries = []
        total_researchers = 0
        total_tokens = 0
        total_cost = 0.0

        for drop_folder in drop_folders:
            drop_meta = self._generate_drop_summary(drop_folder)
            drop_summaries.append(drop_meta)

            total_researchers += drop_meta.get("researchers_count", 0)
            total_tokens += drop_meta.get("total_tokens", 0)
            total_cost += drop_meta.get("total_cost", 0.0)

        # Get creation/update timestamps
        created_at = self._get_oldest_timestamp(session_path)
        last_updated = self._get_newest_timestamp(session_path)

        # Build session metadata
        metadata = {
            "session_id": session_id,
            "created_at": created_at,
            "last_updated": last_updated,
            "total_drops": len(drop_folders),
            "total_researchers": total_researchers,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 2),
            "drops": drop_summaries
        }

        return metadata

    def _generate_drop_summary(self, drop_path: Path) -> Dict:
        """Generate summary metadata for a single drop."""
        drop_id = drop_path.name

        # Count researcher outputs
        researcher_files = list(drop_path.glob("researcher-*-output.md"))
        researchers_count = len(researcher_files)

        # Calculate totals (would come from researcher metadata in real system)
        # For now, estimate based on file sizes
        total_tokens = 0
        for file in researcher_files:
            content = file.read_text(encoding="utf-8")
            # Rough estimate: 4 chars per token
            total_tokens += len(content) // 4

        # Estimate cost (very rough: $0.01 per 1K tokens)
        total_cost = (total_tokens / 1000) * 0.01

        # Get timestamp
        created_at = datetime.fromtimestamp(drop_path.stat().st_mtime).isoformat()

        return {
            "drop_id": drop_id,
            "created_at": created_at,
            "researchers_count": researchers_count,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 2)
        }

    def generate_drop_metadata(self, drop_path: Path) -> Dict:
        """
        Generate drop-metadata.json for a single drop.

        Includes detailed info about each researcher output.
        """
        drop_id = drop_path.name

        # Load user context
        user_context_file = drop_path / "user-context.md"
        user_context = None
        if user_context_file.exists():
            content = user_context_file.read_text(encoding="utf-8")
            # Extract strategic WHY (first 200 chars as summary)
            user_context = {
                "summary": content[:200] + "..." if len(content) > 200 else content
            }

        # Collect researcher outputs
        researcher_outputs = []
        total_tokens = 0
        total_cost = 0.0

        for file in sorted(drop_path.glob("researcher-*-output.md")):
            researcher_id = file.stem

            content = file.read_text(encoding="utf-8")
            token_count = len(content) // 4  # Rough estimate
            cost = (token_count / 1000) * 0.01

            total_tokens += token_count
            total_cost += cost

            researcher_outputs.append({
                "researcher_id": researcher_id,
                "output_file": file.name,
                "token_count": token_count,
                "cost": round(cost, 2)
            })

        # Build metadata
        metadata = {
            "drop_id": drop_id,
            "created_at": datetime.fromtimestamp(drop_path.stat().st_mtime).isoformat(),
            "user_context": user_context,
            "researchers": researcher_outputs,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 2)
        }

        return metadata

    def save_session_metadata(self, session_path: Path, metadata: Dict):
        """Save session-metadata.json to session directory."""
        metadata_file = session_path / "session-metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8"
        )

    def save_drop_metadata(self, drop_path: Path, metadata: Dict):
        """Save drop-metadata.json to drop directory."""
        metadata_file = drop_path / "drop-metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8"
        )

    def _get_oldest_timestamp(self, session_path: Path) -> str:
        """Get oldest file timestamp in session (creation time)."""
        timestamps = []
        for file in session_path.rglob("*"):
            if file.is_file():
                timestamps.append(file.stat().st_mtime)

        if timestamps:
            oldest = min(timestamps)
            return datetime.fromtimestamp(oldest).isoformat()
        return datetime.now().isoformat()

    def _get_newest_timestamp(self, session_path: Path) -> str:
        """Get newest file timestamp in session (last update)."""
        timestamps = []
        for file in session_path.rglob("*"):
            if file.is_file():
                timestamps.append(file.stat().st_mtime)

        if timestamps:
            newest = max(timestamps)
            return datetime.fromtimestamp(newest).isoformat()
        return datetime.now().isoformat()
