"""
Researcher Adapter - Wraps GeneralResearcher for UI integration with progress tracking.

Provides:
- Research execution with real-time progress callbacks
- Parallel researcher coordination
- Mission briefing transformation (focus_question → full briefing)
- Status tracking (searching, analyzing, writing)

Architecture:
    [Drop Plan] → [Researcher Adapter] → [Mission Briefing Transformer] → [General Researcher]

Does NOT modify existing GeneralResearcher - thin adapter layer only.
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

from core.researcher.general_researcher import GeneralResearcher, ResearchOutput
from core.hq.mission_briefing import build_mission_briefing
from core.hq.context_extractor import UserContext

# Silence verbose gpt-researcher logging (keep terminal clean)
logging.getLogger("gpt_researcher").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class ResearcherStatus(str, Enum):
    """Researcher lifecycle states for UI display."""
    IDLE = "idle"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    WRITING = "writing"
    COMPLETE = "complete"
    FAILED = "failed"


class ResearcherAdapter:
    """
    UI adapter for General Researcher.

    Wraps existing GeneralResearcher to provide UI-friendly interface:
    - Real-time progress callbacks
    - Parallel researcher execution
    - Status tracking

    Example:
        adapter = ResearcherAdapter()

        def on_progress(researcher_id, status, message):
            print(f"{researcher_id}: {message}")

        outputs = await adapter.execute_research_plan(
            plan={"researchers": [...]},
            drop_path=Path("..."),
            on_progress=on_progress
        )
    """

    def __init__(self):
        """Initialize researcher adapter."""
        self.researchers: Dict[str, GeneralResearcher] = {}
        self.statuses: Dict[str, ResearcherStatus] = {}

    async def execute_research_plan(
        self,
        plan: Dict[str, Any],
        drop_path: Path,
        research_mode: str = "general",
        hypothesis: str = "",
        on_progress: Optional[Callable[[str, ResearcherStatus, str], None]] = None,
        cancellation_flag: Optional[Callable[[], bool]] = None
    ) -> List[ResearchOutput]:
        """
        Execute research plan with parallel researchers.

        Transforms HQ's strategic plan (focus_question) into execution-ready mission briefings
        before passing to researchers. This ensures researchers receive full context, success
        criteria, and output format guidance per Anthropic's multi-agent research patterns.

        Args:
            plan: Research plan from HQ (includes researchers_assigned with focus_question)
            drop_path: Path to drop folder (contains user-context.md)
            research_mode: Type of research (icp-validation, competitive-intel, general)
            hypothesis: Overall hypothesis being tested
            on_progress: Callback(researcher_id, status, message) for UI updates
            cancellation_flag: Optional callable that returns True if research should be cancelled

        Returns:
            List of research outputs
        """
        print("\n" + "="*80)
        print("[RESEARCHER ADAPTER] execute_research_plan() called")
        print(f"[RESEARCHER ADAPTER] Research mode: {research_mode}")
        print("="*80)

        # Support both "researchers" and "researchers_assigned" keys
        researchers_config = plan.get("researchers", plan.get("researchers_assigned", []))
        print(f"[RESEARCHER ADAPTER] Found {len(researchers_config)} researchers in plan")

        # Load user context from drop folder
        user_context = self._load_user_context(drop_path)
        print(f"[RESEARCHER ADAPTER] Loaded user context: {user_context.strategic_why[:100]}...")

        # Create researcher instances
        tasks = []
        for idx, config in enumerate(researchers_config):
            # Generate researcher ID if not provided
            researcher_id = config.get("id", f"researcher-{idx + 1}")

            print(f"[RESEARCHER ADAPTER] Creating researcher {researcher_id}")
            print(f"[RESEARCHER ADAPTER]   Config: {config}")

            researcher = GeneralResearcher(verbose=False)
            self.researchers[researcher_id] = researcher
            self.statuses[researcher_id] = ResearcherStatus.IDLE

            # Ensure config has ID for downstream use
            config["id"] = researcher_id

            # Create async task with mission briefing transformation
            task = self._execute_single_researcher(
                researcher=researcher,
                config=config,
                drop_path=drop_path,
                user_context=user_context,
                research_mode=research_mode,
                hypothesis=hypothesis,
                on_progress=on_progress,
                cancellation_flag=cancellation_flag
            )
            tasks.append(task)

        print(f"[RESEARCHER ADAPTER] Starting {len(tasks)} parallel research tasks...")
        # Execute all researchers in parallel
        outputs = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"[RESEARCHER ADAPTER] All research tasks completed. {len(outputs)} outputs received.")

        # Filter out failed researchers
        successful_outputs = []
        for output in outputs:
            if isinstance(output, ResearchOutput):
                successful_outputs.append(output)
            elif isinstance(output, Exception):
                # Log error but continue (unless it's cancellation)
                if "cancelled" not in str(output).lower():
                    if on_progress:
                        on_progress("system", ResearcherStatus.FAILED, f"Research error: {str(output)}")

        return successful_outputs

    async def _execute_single_researcher(
        self,
        researcher: GeneralResearcher,
        config: Dict[str, Any],
        drop_path: Path,
        user_context: UserContext,
        research_mode: str,
        hypothesis: str,
        on_progress: Optional[Callable[[str, ResearcherStatus, str], None]],
        cancellation_flag: Optional[Callable[[], bool]] = None
    ) -> ResearchOutput:
        """
        Execute single researcher with mission briefing transformation and progress tracking.

        Transforms HQ's focus_question into a full mission briefing before execution.

        Args:
            researcher: GeneralResearcher instance
            config: Researcher configuration from plan (contains focus_question)
            drop_path: Path to drop folder
            user_context: Strategic WHY, priorities, mental models
            research_mode: Type of research (icp-validation, general, etc)
            hypothesis: Overall hypothesis being tested
            on_progress: Progress callback
            cancellation_flag: Optional callable that returns True if research should be cancelled

        Returns:
            Research output
        """
        researcher_id = config["id"]

        # Extract focus question from config
        focus_question = config.get("focus_question", config.get("focus", ""))

        # Build full mission briefing using transformer
        mission_briefing = build_mission_briefing(
            focus_question=focus_question,
            user_context=user_context,
            research_mode=research_mode,
            hypothesis=hypothesis,
            company_name=None,  # Extracted from question/hypothesis by transformer
            token_budget=config.get("token_budget", 4000)
        )

        print(f"\n[{researcher_id}] Mission briefing generated ({len(mission_briefing)} chars)")
        print(f"[{researcher_id}] Focus question: {focus_question}")

        try:
            # Check cancellation before starting
            if cancellation_flag and cancellation_flag():
                raise Exception("Research cancelled by user")

            # Status: Searching
            self.statuses[researcher_id] = ResearcherStatus.SEARCHING
            if on_progress:
                on_progress(researcher_id, "Searching", "Searching web sources")

            # Simulated progress (gpt-researcher doesn't expose callbacks easily)
            # In real implementation, would hook into gpt-researcher internals
            await asyncio.sleep(0.5)  # Give UI time to update

            # Check cancellation
            if cancellation_flag and cancellation_flag():
                raise Exception("Research cancelled by user")

            # Status: Analyzing
            self.statuses[researcher_id] = ResearcherStatus.ANALYZING
            if on_progress:
                on_progress(researcher_id, "Analyzing", "Analyzing sources")

            # Execute research
            output = await researcher.execute_research(
                query=focus_question,  # Short focused question
                context=mission_briefing,  # Detailed mission briefing
                drop_path=drop_path,
                researcher_id=researcher_id
            )

            # Check cancellation after research
            if cancellation_flag and cancellation_flag():
                raise Exception("Research cancelled by user")

            # Status: Writing
            self.statuses[researcher_id] = ResearcherStatus.WRITING
            if on_progress:
                on_progress(researcher_id, "Writing", "Writing report")

            await asyncio.sleep(0.5)  # Give UI time to update

            # Status: Complete
            self.statuses[researcher_id] = ResearcherStatus.COMPLETE
            if on_progress:
                on_progress(
                    researcher_id,
                    "Complete",
                    f"{output.token_count} tokens, ${output.cost:.2f}"
                )

            return output

        except Exception as e:
            # Status: Failed
            self.statuses[researcher_id] = ResearcherStatus.FAILED
            if on_progress:
                on_progress(researcher_id, ResearcherStatus.FAILED, f"Failed: {str(e)}")
            raise

    def get_status(self, researcher_id: str) -> ResearcherStatus:
        """
        Get current status of researcher.

        Args:
            researcher_id: Researcher identifier

        Returns:
            Current status
        """
        return self.statuses.get(researcher_id, ResearcherStatus.IDLE)

    def get_all_statuses(self) -> Dict[str, ResearcherStatus]:
        """
        Get status of all researchers.

        Returns:
            Dict mapping researcher_id to status
        """
        return self.statuses.copy()

    def _load_user_context(self, drop_path: Path) -> UserContext:
        """
        Load user context from drop folder.

        Reads user-context.md which was saved by HQ during context extraction.
        Falls back to minimal context if file doesn't exist.

        Args:
            drop_path: Path to drop folder

        Returns:
            UserContext with strategic WHY, priorities, mental models
        """
        context_file = drop_path / "user-context.md"

        if not context_file.exists():
            print(f"[WARNING] user-context.md not found at {context_file}, using minimal context")
            return UserContext(
                strategic_why="No strategic context available",
                decision_context="Not specified",
                success_criteria="Not specified",
                mental_models=[],
                priorities={"must_have": [], "nice_to_have": []},
                constraints=[]
            )

        # Parse user-context.md (simple markdown parsing)
        content = context_file.read_text(encoding="utf-8")

        # Extract sections using simple text search
        strategic_why = self._extract_section(content, "## Strategic WHY")
        decision_context = self._extract_section(content, "## Decision Context")
        success_criteria = self._extract_section(content, "## Success Criteria")
        mental_models_text = self._extract_section(content, "## Mental Models")
        priorities_text = self._extract_section(content, "## Priorities")
        constraints_text = self._extract_section(content, "## Constraints")

        # Parse mental models (bullet list)
        mental_models = [
            line.strip("- ").strip()
            for line in mental_models_text.split("\n")
            if line.strip().startswith("-")
        ]

        # Parse priorities (must have / nice to have sections)
        priorities = self._parse_priorities(priorities_text)

        # Parse constraints (bullet list)
        constraints = [
            line.strip("- ").strip()
            for line in constraints_text.split("\n")
            if line.strip().startswith("-")
        ]

        return UserContext(
            strategic_why=strategic_why.strip(),
            decision_context=decision_context.strip(),
            success_criteria=success_criteria.strip(),
            mental_models=mental_models,
            priorities=priorities,
            constraints=constraints
        )

    def _extract_section(self, content: str, header: str) -> str:
        """Extract content between header and next header."""
        try:
            start = content.index(header) + len(header)
            # Find next ## header or ---
            next_header_idx = content.find("\n##", start)
            next_divider_idx = content.find("\n---", start)

            # Use whichever comes first (if either exists)
            if next_header_idx == -1 and next_divider_idx == -1:
                return content[start:].strip()
            elif next_header_idx == -1:
                return content[start:next_divider_idx].strip()
            elif next_divider_idx == -1:
                return content[start:next_header_idx].strip()
            else:
                end = min(next_header_idx, next_divider_idx)
                return content[start:end].strip()
        except ValueError:
            return ""

    def _parse_priorities(self, priorities_text: str) -> Dict[str, List[str]]:
        """Parse priorities section into must_have and nice_to_have lists."""
        must_have = []
        nice_to_have = []

        current_section = None
        for line in priorities_text.split("\n"):
            line = line.strip()
            if "### Must Have" in line or "**Must Have**" in line:
                current_section = "must_have"
            elif "### Nice to Have" in line or "**Nice to Have**" in line:
                current_section = "nice_to_have"
            elif line.startswith("-") and current_section:
                item = line.strip("- ").strip()
                if current_section == "must_have":
                    must_have.append(item)
                else:
                    nice_to_have.append(item)

        return {"must_have": must_have, "nice_to_have": nice_to_have}
