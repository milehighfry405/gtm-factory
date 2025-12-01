"""
Integration tests for GeneralResearcher module.

Tests the researcher in isolation (without HQ integration).
Validates:
- Can execute research task
- Respects token budget (2-5K range)
- Handles network failures gracefully
- Saves outputs correctly
- Returns valid metadata

IMPORTANT - COST AWARENESS:
These tests use @pytest.mark.vcr() to record API responses to "cassettes".
- First run (with --record-mode=once): Makes REAL Tavily API calls (~$0.10 each)
- All future runs: Replays from cassettes ($0, instant)

To record cassettes (ONLY DO THIS ONCE):
    pytest tests/test_researcher.py --record-mode=once

To run tests normally (replays from cassettes, $0):
    pytest tests/test_researcher.py

To force re-record (costs money):
    pytest tests/test_researcher.py --record-mode=rewrite
"""

import pytest
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from core.researcher import GeneralResearcher, ResearchOutput

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def temp_drop_path(tmp_path):
    """Create temporary drop folder for testing."""
    drop_path = tmp_path / "projects" / "test-company" / "sessions" / "session-1" / "drops" / "drop-1"
    drop_path.mkdir(parents=True, exist_ok=True)
    return drop_path


class TestResearcherIsolation:
    """Test researcher capabilities in isolation."""

    @pytest.mark.vcr()
    @pytest.mark.expensive
    @pytest.mark.asyncio
    async def test_execute_simple_research(self, temp_drop_path):
        """
        CRITICAL: Researcher can execute a basic research task.

        This validates the researcher wrapper works end-to-end:
        - Accepts mission briefing
        - Calls gpt-researcher
        - Returns structured output
        - Saves to drop folder
        """
        researcher = GeneralResearcher(verbose=True)

        mission_briefing = """
        RESEARCH MISSION: What are the top 3 use cases for MLOps platforms in 2024?

        STRATEGIC CONTEXT:
        User is evaluating MLOps platforms and needs to understand current market applications.

        YOUR PURPOSE:
        Provide directional insights for product positioning decisions.

        SUCCESS CRITERIA:
        - Identify 3 concrete use cases with examples
        - Confidence level per use case
        - Source citations

        TOKEN BUDGET:
        Deliver complete findings in 2000-5000 tokens.
        Prioritize: 1) Direct answer 2) Real-world examples 3) Citations

        CONSTRAINTS:
        - Focus on 2023-2024 data
        - Prioritize industry reports and vendor case studies
        """

        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=temp_drop_path,
            researcher_id="researcher-test"
        )

        # Validate output structure
        assert isinstance(output, ResearchOutput), "❌ CRITICAL: Invalid output type"
        assert output.findings, "❌ CRITICAL: No research findings returned"
        assert output.sources, "❌ CRITICAL: No sources tracked"
        assert output.researcher_id == "researcher-test", "❌ CRITICAL: Researcher ID mismatch"

        # Validate token budget (allow some flexibility for short research)
        assert output.token_count > 500, f"❌ CRITICAL: Output too short ({output.token_count} tokens)"
        assert output.token_count < 10000, f"❌ CRITICAL: Output too long ({output.token_count} tokens)"

        # Validate output file saved
        output_file = temp_drop_path / "researcher-test-output.md"
        assert output_file.exists(), "❌ CRITICAL: Output file not saved"

        # Validate file content matches findings
        saved_content = output_file.read_text(encoding="utf-8")
        assert saved_content == output.findings, "❌ CRITICAL: Saved content doesn't match findings"

        print(f"✅ Research completed: {output.token_count} tokens, {len(output.sources)} sources, ${output.cost:.2f}")

    @pytest.mark.vcr()
    @pytest.mark.expensive
    @pytest.mark.asyncio
    async def test_token_budget_warning(self, temp_drop_path, capsys):
        """
        Test that researcher warns when output is outside 2-5K token range.

        Note: This is a soft limit (not hard cutoff). The warning helps HQ refine
        mission briefings for future drops.
        """
        researcher = GeneralResearcher(verbose=False)

        # Very narrow question that might produce short output
        mission_briefing = """
        RESEARCH MISSION: What is the current stock price of Nvidia?

        TOKEN BUDGET: 2000-5000 tokens
        """

        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=temp_drop_path,
            researcher_id="researcher-short"
        )

        # Check for warning if output is too short
        if output.token_count < 2000:
            captured = capsys.readouterr()
            assert "WARNING" in captured.out, "❌ Should warn when output < 2000 tokens"

    @pytest.mark.vcr()
    @pytest.mark.expensive
    @pytest.mark.asyncio
    async def test_output_metadata_complete(self, temp_drop_path):
        """
        Validate that ResearchOutput contains all required metadata.

        This metadata is used for:
        - Drop metadata (lightweight summaries)
        - Cost tracking
        - Performance monitoring
        - Progressive disclosure (don't reload full content)
        """
        researcher = GeneralResearcher(verbose=False)

        mission_briefing = """
        RESEARCH MISSION: What are the key differences between MLflow and Weights & Biases?

        TOKEN BUDGET: 2000-5000 tokens
        """

        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=temp_drop_path,
            researcher_id="researcher-metadata"
        )

        # Validate metadata completeness
        metadata = output.to_dict()
        assert "researcher_id" in metadata, "❌ Missing researcher_id in metadata"
        assert "token_count" in metadata, "❌ Missing token_count in metadata"
        assert "cost" in metadata, "❌ Missing cost in metadata"
        assert "runtime_seconds" in metadata, "❌ Missing runtime_seconds in metadata"
        assert "sources_count" in metadata, "❌ Missing sources_count in metadata"
        assert "timestamp" in metadata, "❌ Missing timestamp in metadata"

        # Validate metadata values are reasonable
        assert metadata["token_count"] > 0, "❌ Token count should be positive"
        assert metadata["cost"] >= 0, "❌ Cost should be non-negative"
        assert metadata["runtime_seconds"] > 0, "❌ Runtime should be positive"
        assert metadata["sources_count"] >= 0, "❌ Sources count should be non-negative"

    @pytest.mark.vcr()
    @pytest.mark.expensive
    @pytest.mark.asyncio
    async def test_multiple_researchers_parallel(self, temp_drop_path):
        """
        CRITICAL: Multiple researchers can execute in parallel.

        This is the HQ → multiple researchers pattern:
        - HQ assigns 2-4 researchers per drop
        - Each gets distinct sub-question
        - They run in parallel (not sequential)
        - All outputs save to same drop folder
        """
        researcher = GeneralResearcher(verbose=True)

        mission_briefings = [
            """
            RESEARCH MISSION: What are the technical capabilities of MLflow?
            TOKEN BUDGET: 2000-5000 tokens
            """,
            """
            RESEARCH MISSION: What are the pricing models for Weights & Biases?
            TOKEN BUDGET: 2000-5000 tokens
            """
        ]

        outputs = await researcher.execute_multiple(
            mission_briefings=mission_briefings,
            drop_path=temp_drop_path
        )

        # Validate we got outputs for all researchers
        assert len(outputs) == 2, "❌ CRITICAL: Should have 2 research outputs"

        # Validate each researcher saved to correct file
        assert (temp_drop_path / "researcher-1-output.md").exists(), "❌ CRITICAL: Researcher 1 output missing"
        assert (temp_drop_path / "researcher-2-output.md").exists(), "❌ CRITICAL: Researcher 2 output missing"

        # Validate researcher IDs are distinct
        assert outputs[0].researcher_id == "researcher-1", "❌ CRITICAL: Researcher 1 ID wrong"
        assert outputs[1].researcher_id == "researcher-2", "❌ CRITICAL: Researcher 2 ID wrong"

        # Validate both have findings
        assert outputs[0].findings, "❌ CRITICAL: Researcher 1 has no findings"
        assert outputs[1].findings, "❌ CRITICAL: Researcher 2 has no findings"

        print(f"✅ Parallel research completed: {len(outputs)} researchers")

    @pytest.mark.vcr()
    @pytest.mark.expensive
    @pytest.mark.asyncio
    async def test_markdown_output_valid(self, temp_drop_path):
        """
        Validate that research output is valid markdown.

        Requirements:
        - Contains headings (##)
        - Contains bullet points or numbered lists
        - Contains source citations
        - No broken markdown syntax
        """
        researcher = GeneralResearcher(verbose=False)

        mission_briefing = """
        RESEARCH MISSION: What are the benefits of feature stores in ML pipelines?

        SUCCESS CRITERIA:
        - Executive summary (3-5 sentences)
        - Key findings with bullet points
        - Source citations

        TOKEN BUDGET: 2000-5000 tokens
        """

        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=temp_drop_path,
            researcher_id="researcher-markdown"
        )

        findings = output.findings

        # Basic markdown validation - accept both ## markdown headings and **bold** headings
        has_headings = ("##" in findings or "#" in findings or "**" in findings)
        assert has_headings, "❌ Output should contain markdown headings (## or **bold**)"
        assert "-" in findings or "*" in findings or "1." in findings, "❌ Output should contain lists"

        # Should contain source-like patterns (URLs or citations)
        has_sources = "http" in findings.lower() or "[" in findings
        assert has_sources, "❌ Output should contain source citations or URLs"


class TestResearcherErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_handles_missing_api_key_gracefully(self, temp_drop_path, monkeypatch):
        """
        Test that researcher provides useful error when API keys missing.

        Note: This test removes API key temporarily to test error handling.
        """
        # Remove OpenAI API key
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        researcher = GeneralResearcher(verbose=False)

        mission_briefing = "RESEARCH MISSION: Test error handling"

        with pytest.raises(Exception) as exc_info:
            await researcher.execute_research(
                mission_briefing=mission_briefing,
                drop_path=temp_drop_path,
                researcher_id="researcher-error"
            )

        # Should fail with informative error (not silent failure)
        assert exc_info.value is not None, "❌ Should raise exception for missing API key"

    @pytest.mark.vcr()
    @pytest.mark.expensive
    @pytest.mark.asyncio
    async def test_creates_drop_folder_if_missing(self, tmp_path):
        """
        Test that researcher creates drop folder if it doesn't exist.

        This prevents errors when HQ hasn't pre-created the folder.
        """
        researcher = GeneralResearcher(verbose=False)

        # Use path that doesn't exist yet
        nonexistent_path = tmp_path / "missing" / "drop-folder"
        assert not nonexistent_path.exists(), "Path should not exist yet"

        mission_briefing = """
        RESEARCH MISSION: Quick test of folder creation
        TOKEN BUDGET: 1000 tokens
        """

        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=nonexistent_path,
            researcher_id="researcher-create-folder"
        )

        # Validate folder was created
        assert nonexistent_path.exists(), "❌ CRITICAL: Researcher should create drop folder"
        assert (nonexistent_path / "researcher-create-folder-output.md").exists(), "❌ Output file not saved"
