"""
HQ Adapter - Wraps HQOrchestrator for UI integration.

Provides:
- Streaming chat with progress callbacks
- Research plan proposal
- Context extraction
- Load latest.md + critical-analysis.md after each drop

Does NOT modify existing HQOrchestrator - thin adapter layer only.
"""

from pathlib import Path
from typing import Optional, Callable, List, Dict, Any, Generator
from core.hq.orchestrator import HQOrchestrator
from core.hq.context_extractor import ContextExtractor


class HQAdapter:
    """
    UI adapter for HQ Orchestrator.

    Wraps existing HQOrchestrator to provide UI-friendly interface:
    - Stream responses with token callbacks
    - Load context files (latest.md, critical-analysis.md)
    - Extract user context for drop creation
    - Propose research plans

    Example:
        adapter = HQAdapter(
            api_key=api_key,
            project_path=Path("projects/demo-company"),
            session_id="session-1"
        )

        # Stream chat response
        for token in adapter.chat_stream("What are MLOps platforms?", on_token=print):
            pass  # Tokens printed via callback

        # Load context after drop
        adapter.load_drop_context("drop-1")

        # Propose research plan
        plan = adapter.propose_research_plan()
    """

    def __init__(
        self,
        api_key: str,
        project_path: Path,
        session_id: str,
        model: str = "claude-sonnet-4-5",
        mode: str = "general"
    ):
        """
        Initialize HQ adapter.

        Args:
            api_key: Anthropic API key
            project_path: Path to /projects/{company}/
            session_id: Session identifier
            model: Claude model to use
            mode: Research mode ("icp-validation", "gtm-execution", or "general")
        """
        self.orchestrator = HQOrchestrator(
            api_key=api_key,
            project_path=project_path,
            session_id=session_id,
            model=model,
            mode=mode
        )
        self.context_extractor = ContextExtractor(api_key=api_key)
        self.session_path = project_path / "sessions" / session_id

        # Track current drop for context loading
        self.current_drop_id: Optional[str] = None

        # Loaded context (after drops) - DEPRECATED, keeping for compatibility
        self.latest_md: Optional[str] = None
        self.critical_analysis_md: Optional[str] = None
        self.user_context_md: Optional[str] = None

    def chat_stream(
        self,
        user_message: str,
        on_token: Optional[Callable[[str], None]] = None,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """
        Stream chat response with optional token callback.

        Args:
            user_message: User's message
            on_token: Optional callback called for each token
            max_tokens: Maximum tokens in response

        Yields:
            Response tokens
        """
        for token in self.orchestrator.chat_stream(user_message, max_tokens):
            if on_token:
                on_token(token)
            yield token

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get current conversation history.

        Returns:
            List of messages: [{"role": "user", "content": "..."}, ...]
        """
        return self.orchestrator.conversation_history.copy()

    def load_conversation_history(self, messages: List[Dict[str, str]]) -> None:
        """
        Load conversation history (for crash recovery).

        Args:
            messages: List of conversation messages
        """
        self.orchestrator.conversation_history = messages

    def extract_user_context(self) -> str:
        """
        Extract strategic WHY from conversation.

        Uses ContextExtractor to pull user's goals, constraints, decision context.

        Returns:
            User context markdown content
        """
        context_obj = self.context_extractor.extract(
            self.orchestrator.conversation_history
        )
        return context_obj.to_markdown()

    def propose_research_plan(self) -> Dict[str, Any]:
        """
        Propose research plan based on conversation.

        HQ analyzes conversation and determines:
        - Number of researchers needed (1-4)
        - Each researcher's focus area
        - Expected output format

        Returns:
            Research plan dict:
            {
                "drop_id": "drop-1",
                "researchers": [
                    {"id": "researcher-1", "focus": "Market sizing", ...},
                    ...
                ]
            }
        """
        # Use HQOrchestrator's extract_drop_plan method
        return self.orchestrator.extract_drop_plan()

    def load_drop_context(self, drop_id: str) -> None:
        """
        Load context files after drop completes.

        Loads into HQ's context:
        - ALL researcher outputs (full content, 3-5K tokens each)
        - critical-analysis.md (gaps/contradictions to explore)

        Does NOT load:
        - user-context.md (HQ already has conversation history)
        - latest.md (built AFTER conversation, not before)

        Args:
            drop_id: Drop folder name (e.g., "drop-1")
        """
        # Set current drop ID for _inject_drop_context()
        self.current_drop_id = drop_id

        print(f"[HQ ADAPTER] load_drop_context() called for {drop_id}")

        # Inject into HQ's system context (for next conversation)
        self._inject_drop_context()

    def _inject_drop_context(self) -> None:
        """
        Inject drop context into HQ's conversation.

        Loads ALL researcher outputs + critical analysis so HQ has
        100% of information for intelligent Socratic conversation.

        Does NOT load:
        - user-context.md (HQ already has conversation history)
        - latest.md (built AFTER conversation, not before)
        """
        context_parts = []

        # Load ALL researcher outputs (FULL content)
        drop_path = self.session_path / "drops" / self.current_drop_id
        if drop_path.exists():
            researcher_files = sorted(drop_path.glob("researcher-*-output.md"))

            for researcher_file in researcher_files:
                context_parts.append(f"<researcher_output file='{researcher_file.name}'>")
                context_parts.append(researcher_file.read_text(encoding="utf-8"))
                context_parts.append("</researcher_output>")
                print(f"[HQ ADAPTER] Loaded {researcher_file.name} ({len(researcher_file.read_text(encoding='utf-8'))} chars)")

            # Load critical analysis
            critical_file = drop_path / "critical-analysis.md"
            if critical_file.exists():
                context_parts.append("<critical_analysis>")
                context_parts.append("AI has a tendency to be agreeable. Use this analysis to guide your questions.")
                context_parts.append(critical_file.read_text(encoding="utf-8"))
                context_parts.append("</critical_analysis>")
                print(f"[HQ ADAPTER] Loaded critical-analysis.md ({len(critical_file.read_text(encoding='utf-8'))} chars)")

        if context_parts:
            # Add as assistant message (internal context, not shown to user)
            context_message = {
                "role": "assistant",
                "content": "\n\n".join(context_parts)
            }
            self.orchestrator.conversation_history.append(context_message)
            print(f"[HQ ADAPTER] Injected drop context: {len(context_parts)} parts, {len(context_message['content'])} total chars")

    def get_loaded_context_size(self) -> Dict[str, int]:
        """
        Get size of loaded context files (for token tracking).

        Returns:
            Dict mapping file to character count.
        """
        if not self.current_drop_id:
            return {}

        drop_path = self.session_path / "drops" / self.current_drop_id
        context_sizes = {}

        # Count researcher outputs
        if drop_path.exists():
            for researcher_file in drop_path.glob("researcher-*-output.md"):
                context_sizes[researcher_file.name] = len(researcher_file.read_text(encoding="utf-8"))

            # Count critical analysis
            critical_file = drop_path / "critical-analysis.md"
            if critical_file.exists():
                context_sizes["critical-analysis.md"] = len(critical_file.read_text(encoding="utf-8"))

        return context_sizes
