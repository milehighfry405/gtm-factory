"""
Generator Adapter - Wraps generators for UI integration with status tracking.

Provides:
- Synthesis execution with status updates
- Critical analysis execution with status updates
- Metadata generation

Does NOT modify existing generators - thin adapter layer only.
"""

from pathlib import Path
from typing import Optional, Callable
from enum import Enum

from core.generators.latest_generator import LatestGenerator
from core.generators.critical_analyst_generator import CriticalAnalystGenerator
from core.generators.session_metadata_generator import SessionMetadataGenerator


class GeneratorStatus(str, Enum):
    """Generator status for UI display."""
    IDLE = "idle"
    SYNTHESIZING = "synthesizing"
    ANALYZING = "analyzing"
    GENERATING_METADATA = "generating_metadata"
    COMPLETE = "complete"
    FAILED = "failed"


class GeneratorAdapter:
    """
    UI adapter for Generators.

    Wraps existing generators to provide UI-friendly interface:
    - Status tracking for synthesis/analysis
    - Progress callbacks
    - Error handling

    Example:
        adapter = GeneratorAdapter()

        def on_status(status, message):
            print(f"{status}: {message}")

        latest_md = adapter.synthesize_drop(
            session_path=Path("..."),
            drop_id="drop-1",
            on_status=on_status
        )
    """

    def __init__(self):
        """Initialize generator adapter."""
        self.latest_gen = LatestGenerator()
        self.critical_gen = CriticalAnalystGenerator()
        self.metadata_gen = SessionMetadataGenerator()

        self.status = GeneratorStatus.IDLE

    def synthesize_drop(
        self,
        session_path: Path,
        drop_id: str,
        on_status: Optional[Callable[[GeneratorStatus, str], None]] = None
    ) -> str:
        """
        Synthesize research outputs into latest.md.

        Args:
            session_path: Path to session directory
            drop_id: Drop folder name
            on_status: Callback(status, message) for UI updates

        Returns:
            latest.md content
        """
        try:
            self.status = GeneratorStatus.SYNTHESIZING
            if on_status:
                on_status(GeneratorStatus.SYNTHESIZING, "Synthesizing findings...")

            # Execute synthesis
            latest_md = self.latest_gen.synthesize_drop(
                session_path=session_path,
                drop_id=drop_id
            )

            # Save to session directory
            self.latest_gen.save_latest(session_path, latest_md)

            self.status = GeneratorStatus.COMPLETE
            if on_status:
                on_status(GeneratorStatus.COMPLETE, f"Synthesis complete ({len(latest_md)} chars)")

            return latest_md

        except Exception as e:
            self.status = GeneratorStatus.FAILED
            if on_status:
                on_status(GeneratorStatus.FAILED, f"Synthesis failed: {str(e)}")
            raise

    def analyze_drop(
        self,
        session_path: Path,
        drop_id: str,
        on_status: Optional[Callable[[GeneratorStatus, str], None]] = None
    ) -> str:
        """
        Generate critical analysis of research outputs.

        Args:
            session_path: Path to session directory
            drop_id: Drop folder name
            on_status: Callback(status, message) for UI updates

        Returns:
            critical-analysis.md content
        """
        try:
            self.status = GeneratorStatus.ANALYZING
            if on_status:
                on_status(GeneratorStatus.ANALYZING, "Analyzing research gaps...")

            # Execute analysis
            critical_md = self.critical_gen.analyze_drop(
                session_path=session_path,
                drop_id=drop_id
            )

            # Save to drop directory
            drop_path = session_path / "drops" / drop_id
            self.critical_gen.save_analysis(drop_path, critical_md)

            self.status = GeneratorStatus.COMPLETE
            if on_status:
                on_status(GeneratorStatus.COMPLETE, f"Analysis complete ({len(critical_md)} chars)")

            return critical_md

        except Exception as e:
            self.status = GeneratorStatus.FAILED
            if on_status:
                on_status(GeneratorStatus.FAILED, f"Analysis failed: {str(e)}")
            raise

    def generate_metadata(
        self,
        session_path: Path,
        on_status: Optional[Callable[[GeneratorStatus, str], None]] = None
    ) -> dict:
        """
        Generate session metadata for progressive disclosure.

        Args:
            session_path: Path to session directory
            on_status: Callback(status, message) for UI updates

        Returns:
            Session metadata dict
        """
        try:
            self.status = GeneratorStatus.GENERATING_METADATA
            if on_status:
                on_status(GeneratorStatus.GENERATING_METADATA, "Generating metadata...")

            # Generate metadata
            metadata = self.metadata_gen.generate_session_metadata(session_path)

            # Save to session directory
            self.metadata_gen.save_session_metadata(session_path, metadata)

            self.status = GeneratorStatus.COMPLETE
            if on_status:
                on_status(GeneratorStatus.COMPLETE, "Metadata generated")

            return metadata

        except Exception as e:
            self.status = GeneratorStatus.FAILED
            if on_status:
                on_status(GeneratorStatus.FAILED, f"Metadata generation failed: {str(e)}")
            raise

    def get_status(self) -> GeneratorStatus:
        """
        Get current generator status.

        Returns:
            Current status
        """
        return self.status
