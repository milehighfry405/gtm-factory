"""
General Researcher - Wrapper around gpt-researcher for executing research tasks.

This module provides a thin wrapper that:
- Takes mission briefings from HQ
- Configures gpt-researcher with best-in-class models
- Executes research asynchronously
- Validates output token count
- Saves research to drop folders
"""

import os
import asyncio
import logging
import sys
from io import StringIO
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from gpt_researcher import GPTResearcher
from pydantic import BaseModel

# Silence verbose gpt-researcher logging at the source
logging.getLogger("gpt_researcher").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)


@dataclass
class ResearchOutput:
    """
    Structured output from a research task.

    Attributes:
        findings: The research report markdown
        sources: List of sources cited
        token_count: Approximate token count of findings
        cost: Estimated cost in USD
        runtime_seconds: How long research took
        researcher_id: Identifier for this researcher
    """
    findings: str
    sources: list
    token_count: int
    cost: float
    runtime_seconds: float
    researcher_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "researcher_id": self.researcher_id,
            "token_count": self.token_count,
            "cost": self.cost,
            "runtime_seconds": self.runtime_seconds,
            "sources_count": len(self.sources),
            "timestamp": datetime.now().isoformat()
        }


class GeneralResearcher:
    """
    Wrapper around gpt-researcher that executes research tasks from HQ mission briefings.

    Responsibilities:
    - Configure gpt-researcher with premium models (no cost constraints)
    - Execute research tasks asynchronously
    - Validate output quality (token budget, structure)
    - Save findings to drop folders
    - Return structured metadata

    Usage:
        researcher = GeneralResearcher()
        output = await researcher.execute_research(
            mission_briefing="[HQ's detailed briefing]",
            drop_path=Path("projects/company/sessions/session-1/drops/drop-1"),
            researcher_id="researcher-1"
        )
    """

    def __init__(
        self,
        model_fast: str = "openai:gpt-4o-mini",  # For summaries
        model_smart: str = "openai:gpt-4o",      # For report synthesis
        verbose: bool = False,
        config_path: Optional[str] = None
    ):
        """
        Initialize GeneralResearcher.

        Args:
            model_fast: Model for fast operations (summaries). Default: gpt-4o-mini
            model_smart: Model for smart operations (report synthesis). Default: gpt-4o
            verbose: Enable debug logging
            config_path: Path to gpt-researcher config JSON file
        """
        self.model_fast = model_fast
        self.model_smart = model_smart
        self.verbose = verbose

        # Use config file if provided, otherwise default to project config
        if config_path is None:
            # Default to project config
            project_root = Path(__file__).parent.parent.parent
            config_path = str(project_root / "config" / "gpt_researcher.json")

        self.config_path = config_path

        # Verify config file exists
        if not Path(config_path).exists():
            print(f"WARNING: Config file not found: {config_path}")
            print("         Using gpt-researcher defaults instead")
        else:
            print(f"[RESEARCHER] Using config: {config_path}")

        # Set LLM models via env vars (overrides config file)
        # TODO: Switch to GPT-5 when streaming ready (45% fewer errors)
        os.environ["FAST_LLM"] = model_fast
        os.environ["SMART_LLM"] = model_smart

    async def execute_research(
        self,
        query: str,
        context: str,
        drop_path: Path,
        researcher_id: str = "researcher-1",
        max_retries: int = 2
    ) -> ResearchOutput:
        """
        Execute a single research task.

        Args:
            query: Short, focused research question (from HQ's focus_question)
            context: Detailed research guidance (from mission briefing transformer)
            drop_path: Path to drop folder where output will be saved
            researcher_id: Identifier for this researcher (e.g., "researcher-1")
            max_retries: Number of retries on failure

        Returns:
            ResearchOutput with findings, sources, metadata

        Raises:
            Exception: If research fails after retries
        """
        start_time = datetime.now()

        # Ensure drop path exists
        drop_path.mkdir(parents=True, exist_ok=True)

        # Execute research with retries
        for attempt in range(max_retries + 1):
            try:
                # Initialize researcher with query + context separation
                # Key: query = short question, context = detailed guidance
                researcher = GPTResearcher(
                    query=query,  # Short focused question
                    context=context,  # Detailed mission briefing
                    report_type="research_report",
                    report_source="web_search",
                    tone="detailed and analytical",
                    config_path=self.config_path,
                    verbose=self.verbose
                )

                # Execute research (verbose output is controlled by config VERBOSE=false)
                print(f"[{researcher_id}] Conducting research...")

                await researcher.conduct_research()

                print(f"[{researcher_id}] Writing report...")
                findings = await researcher.write_report()

                print(f"[{researcher_id}] Report complete: {len(findings)} characters")

                # Get research metadata
                sources = researcher.get_research_sources()
                cost = researcher.get_costs()

                # Calculate runtime
                runtime = (datetime.now() - start_time).total_seconds()

                # Estimate token count (rough: 1 token ~= 4 chars)
                token_count = len(findings) // 4

                # Print source quality summary
                print(f"\n[{researcher_id}] RESEARCH SUMMARY:")
                print(f"  Output: {token_count} tokens ({len(findings)} chars)")
                print(f"  Sources: {len(sources)} used")
                print(f"  Cost: ${cost:.2f}")
                print(f"  Runtime: {runtime:.1f}s")

                # Show top sources used
                if sources:
                    print(f"\n[{researcher_id}] TOP SOURCES:")
                    for idx, source in enumerate(sources[:5], 1):
                        url = source.get('url', 'N/A')
                        title = source.get('title', 'Unknown')[:60]
                        print(f"  {idx}. {title}")
                        print(f"     {url}")

                # Validate token budget (warn if outside 2-5K range)
                if token_count < 2000:
                    print(f"\nWARNING: {researcher_id} output is {token_count} tokens (target: 2000-5000). May be incomplete.")
                elif token_count > 5000:
                    print(f"\nWARNING: {researcher_id} output is {token_count} tokens (target: 2000-5000). Mission briefing may need refinement.")

                # Save findings to drop folder
                output_file = drop_path / f"{researcher_id}-output.md"
                output_file.write_text(findings, encoding="utf-8")

                # Create research output
                output = ResearchOutput(
                    findings=findings,
                    sources=sources,
                    token_count=token_count,
                    cost=cost,
                    runtime_seconds=runtime,
                    researcher_id=researcher_id
                )

                if self.verbose:
                    print(f"[OK] {researcher_id} completed: {token_count} tokens, {len(sources)} sources, ${cost:.2f}, {runtime:.1f}s")

                return output

            except Exception as e:
                if attempt < max_retries:
                    print(f"[WARN] {researcher_id} attempt {attempt + 1} failed: {e}. Retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"[ERROR] {researcher_id} failed after {max_retries + 1} attempts")
                    raise

    async def execute_multiple(
        self,
        research_tasks: list[tuple[str, str]],  # List of (query, context) pairs
        drop_path: Path
    ) -> list[ResearchOutput]:
        """
        Execute multiple research tasks in parallel.

        Args:
            research_tasks: List of (query, context) tuples - one per researcher
            drop_path: Path to drop folder

        Returns:
            List of ResearchOutput objects
        """
        tasks = [
            self.execute_research(
                query=query,
                context=context,
                drop_path=drop_path,
                researcher_id=f"researcher-{i+1}"
            )
            for i, (query, context) in enumerate(research_tasks)
        ]

        return await asyncio.gather(*tasks)
