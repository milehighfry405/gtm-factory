"""
Integration tests for HQ → Researcher handoff.

Tests that the complete workflow works:
- HQ extracts user context
- HQ saves context to drop
- Researcher loads context
- Researcher executes based on HQ's mission briefing
- Research outputs save to drop folder
- Drop folder contains complete snapshot

This is the CRITICAL path - if this breaks, user loses conversation and has to restart.
"""

import pytest
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from core.hq import HQOrchestrator, ContextExtractor, MemoryManager, UserContext
from core.researcher import GeneralResearcher

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure for testing."""
    project_path = tmp_path / "projects" / "test-company"
    project_path.mkdir(parents=True, exist_ok=True)
    return project_path


@pytest.fixture
def sample_conversation():
    """Sample conversation between user and HQ."""
    return [
        {
            "role": "user",
            "content": "I want to research Arthur.ai's downmarket opportunity"
        },
        {
            "role": "assistant",
            "content": "Let me clarify: when you say 'downmarket,' what size companies? And what decision will this inform?"
        },
        {
            "role": "user",
            "content": "Companies with 10-50 employees. We're deciding whether to build a self-serve product tier."
        },
        {
            "role": "assistant",
            "content": "Got it. What would make this opportunity 'real' versus just theoretically possible?"
        },
        {
            "role": "user",
            "content": "We need to see demand signals - existing attempts to use Arthur for smaller deployments, competitors moving downmarket, pricing thresholds that make sense."
        }
    ]


@pytest.fixture
def sample_user_context():
    """Sample user context extracted from conversation."""
    return UserContext(
        strategic_why="User is evaluating whether to build self-serve product tier for small companies (10-50 employees)",
        decision_context="Informs product roadmap decision: build vs. don't build self-serve tier",
        mental_models=["Demand signals indicate opportunity", "Pricing threshold is critical constraint"],
        priorities={
            "must_have": ["Evidence of existing demand", "Competitor positioning"],
            "nice_to_have": ["Market size estimates", "Technical feasibility"]
        },
        constraints=["Target: 10-50 employee companies", "Need pricing threshold data"],
        success_criteria="Clear evidence of demand signals and viable pricing model for self-serve tier",
        hypothesis="Arthur.ai has viable downmarket opportunity in 10-50 employee segment"
    )


class TestHQResearcherIntegration:
    """Test complete HQ → Researcher workflow."""

    @pytest.mark.asyncio
    async def test_complete_drop_workflow_with_research(
        self,
        temp_project,
        sample_conversation,
        sample_user_context
    ):
        """
        CRITICAL END-TO-END TEST: Complete drop creation with actual research.

        This simulates the full user workflow:
        1. User has conversation with HQ
        2. HQ extracts user context
        3. HQ creates drop folder
        4. HQ saves conversation + context
        5. HQ crafts mission briefing
        6. Researcher executes research
        7. Research output saved to drop
        8. Drop folder contains complete snapshot

        If ANY step breaks, user has to restart conversation.
        """
        # Step 1: Setup HQ and memory
        session_id = "session-1-arthur-downmarket"
        memory = MemoryManager(temp_project, session_id)

        # Step 2: Create drop folder
        drop_path = memory.create_drop_directory("drop-1")
        assert drop_path.exists(), "❌ CRITICAL: Drop folder not created"

        # Step 3: Save conversation history (HQ's job)
        conv_path = memory.save_conversation_history(sample_conversation)
        assert conv_path.exists(), "❌ CRITICAL: Conversation history not saved"

        # Step 4: Save user context (HQ's job)
        context_md = sample_user_context.to_markdown()
        context_path = memory.save_user_context(context_md, "drop-1")
        assert context_path.exists(), "❌ CRITICAL: User context not saved"

        # Step 5: HQ crafts mission briefing (this is what HQ would generate)
        mission_briefing = f"""
        RESEARCH MISSION: What evidence exists for demand in the 10-50 employee segment for MLOps/model monitoring platforms?

        STRATEGIC CONTEXT:
        {sample_user_context.strategic_why}

        Decision context: {sample_user_context.decision_context}

        Mental models:
        {chr(10).join('- ' + model for model in sample_user_context.mental_models)}

        YOUR PURPOSE:
        Provide evidence-based answer for product roadmap decision: should Arthur.ai build a self-serve tier for small companies?

        SUCCESS CRITERIA:
        - Identify concrete demand signals (existing workarounds, competitor moves, customer requests)
        - Assess pricing threshold expectations for this segment
        - Confidence level per finding (High/Medium/Low)
        - Source citations for all claims

        TOKEN BUDGET:
        Deliver complete findings in 2000-5000 tokens.
        Prioritize:
        1. Direct evidence of demand
        2. Pricing/packaging insights
        3. Competitor positioning
        4. Market size context

        CONSTRAINTS:
        - Focus on 10-50 employee companies specifically
        - Prioritize: SaaS/tech companies, recent data (2023-2024)
        - Look for: competitor pricing, customer testimonials, industry reports
        """

        # Step 6: Researcher executes (this is the handoff point)
        researcher = GeneralResearcher(verbose=True)
        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=drop_path,
            researcher_id="researcher-1"
        )

        # Step 7: Verify research output saved
        research_file = drop_path / "researcher-1-output.md"
        assert research_file.exists(), "❌ CRITICAL: Research output not saved"

        # Step 8: Verify drop folder has complete snapshot
        assert (drop_path / "user-context.md").exists(), "❌ CRITICAL: User context missing from drop"
        assert (drop_path / "conversation-history.md").exists(), "❌ CRITICAL: Conversation missing from drop"
        assert (drop_path / "researcher-1-output.md").exists(), "❌ CRITICAL: Research output missing from drop"

        # Step 9: Verify research output quality
        assert output.findings, "❌ CRITICAL: No research findings"
        assert output.sources, "❌ CRITICAL: No sources tracked"
        assert output.token_count > 500, "❌ CRITICAL: Output too short"

        # Step 10: Verify we can reload everything (critical for next session)
        loaded_conv = memory.load_conversation_history()
        assert loaded_conv is not None, "❌ CRITICAL: Can't reload conversation"
        assert len(loaded_conv) == len(sample_conversation), "❌ CRITICAL: Conversation corrupted"

        print(f"✅ Complete drop workflow succeeded: {output.token_count} tokens, {len(output.sources)} sources")

    @pytest.mark.asyncio
    async def test_multiple_researchers_in_single_drop(self, temp_project, sample_user_context):
        """
        Test that HQ can assign multiple researchers to one drop (2-4 researchers pattern).

        Workflow:
        1. HQ creates drop
        2. HQ saves user context
        3. HQ crafts 3 mission briefings (different angles)
        4. 3 researchers execute in parallel
        5. All outputs save to same drop folder
        """
        session_id = "session-multi-researcher"
        memory = MemoryManager(temp_project, session_id)

        # Create drop
        drop_path = memory.create_drop_directory("drop-1")

        # Save user context
        context_md = sample_user_context.to_markdown()
        memory.save_user_context(context_md, "drop-1")

        # HQ crafts 3 mission briefings (different sub-questions)
        briefings = [
            f"""
            RESEARCH MISSION: What is Arthur.ai's current pricing and packaging model?
            STRATEGIC CONTEXT: {sample_user_context.strategic_why}
            TOKEN BUDGET: 2000-5000 tokens
            """,
            f"""
            RESEARCH MISSION: Which competitors offer downmarket/self-serve tiers and how are they priced?
            STRATEGIC CONTEXT: {sample_user_context.strategic_why}
            TOKEN BUDGET: 2000-5000 tokens
            """,
            f"""
            RESEARCH MISSION: What are typical budget constraints for MLOps tools in 10-50 employee companies?
            STRATEGIC CONTEXT: {sample_user_context.strategic_why}
            TOKEN BUDGET: 2000-5000 tokens
            """
        ]

        # Execute all researchers in parallel
        researcher = GeneralResearcher(verbose=True)
        outputs = await researcher.execute_multiple(
            mission_briefings=briefings,
            drop_path=drop_path
        )

        # Verify all researchers completed
        assert len(outputs) == 3, "❌ CRITICAL: Should have 3 research outputs"

        # Verify all outputs saved to drop
        assert (drop_path / "researcher-1-output.md").exists(), "❌ Researcher 1 output missing"
        assert (drop_path / "researcher-2-output.md").exists(), "❌ Researcher 2 output missing"
        assert (drop_path / "researcher-3-output.md").exists(), "❌ Researcher 3 output missing"

        # Verify drop has user context
        assert (drop_path / "user-context.md").exists(), "❌ User context missing"

        print(f"✅ Multi-researcher drop completed: {len(outputs)} researchers")

    def test_user_context_loads_correctly_for_researcher(self, temp_project, sample_user_context):
        """
        Test that user context saved by HQ can be loaded by Researcher.

        This validates the file format is compatible across modules.
        """
        session_id = "session-context-test"
        memory = MemoryManager(temp_project, session_id)

        # HQ saves context
        context_md = sample_user_context.to_markdown()
        drop_path = memory.create_drop_directory("drop-1")
        context_path = memory.save_user_context(context_md, "drop-1")

        # Verify file exists
        assert context_path.exists(), "❌ Context file not saved"

        # Load context (simulating what Researcher would see)
        loaded_context = context_path.read_text(encoding="utf-8")

        # Verify key information is present
        assert "strategic_why" in loaded_context.lower(), "❌ Strategic WHY missing"
        assert "decision" in loaded_context.lower(), "❌ Decision context missing"
        assert "priorities" in loaded_context.lower(), "❌ Priorities missing"

        # Verify it's valid markdown
        assert "##" in loaded_context or "#" in loaded_context, "❌ Should be markdown format"

    @pytest.mark.asyncio
    async def test_drop_metadata_updated_after_research(self, temp_project):
        """
        Test that drop metadata is updated to include researcher outputs.

        Metadata is used for:
        - Progressive disclosure (scan drops without loading full content)
        - Cross-drop queries
        - Session index
        """
        session_id = "session-metadata-test"
        memory = MemoryManager(temp_project, session_id)

        # Create drop and execute research
        drop_path = memory.create_drop_directory("drop-1")

        mission_briefing = """
        RESEARCH MISSION: Quick test of metadata updates
        TOKEN BUDGET: 1000 tokens
        """

        researcher = GeneralResearcher(verbose=False)
        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=drop_path,
            researcher_id="researcher-metadata"
        )

        # Save drop metadata (HQ would do this)
        metadata = {
            "drop_id": "drop-1",
            "hypothesis": "Test hypothesis",
            "researchers": [output.to_dict()]
        }

        memory.save_drop_metadata(metadata, "drop-1")

        # Verify metadata file exists
        metadata_path = drop_path / "drop-metadata.json"
        assert metadata_path.exists(), "❌ Drop metadata not saved"

        # Verify metadata is lightweight (<2KB for progressive disclosure)
        metadata_size = metadata_path.stat().st_size
        assert metadata_size < 2048, f"❌ Metadata too large ({metadata_size} bytes), should be <2KB"

    @pytest.mark.asyncio
    async def test_session_survives_restart(self, temp_project, sample_conversation):
        """
        CRITICAL: Validate that session can be resumed after restart.

        This is the "Helldiver pain point" test:
        - User has rich conversation
        - System crashes / user closes
        - User reopens
        - Conversation history + context are intact
        - Can continue research
        """
        session_id = "session-restart-test"

        # Simulate initial session
        memory = MemoryManager(temp_project, session_id)
        drop_path = memory.create_drop_directory("drop-1")
        memory.save_conversation_history(sample_conversation)

        # Simulate restart: create NEW memory manager (fresh instance)
        memory_after_restart = MemoryManager(temp_project, session_id)

        # Verify conversation can be loaded
        loaded_conv = memory_after_restart.load_conversation_history()
        assert loaded_conv is not None, "❌ CRITICAL: Conversation lost after restart"
        assert len(loaded_conv) == len(sample_conversation), "❌ CRITICAL: Conversation incomplete"

        # Verify session index still accessible
        session_index = memory_after_restart.get_session_index()
        assert "session_id" in session_index, "❌ CRITICAL: Session index corrupted"

        print("✅ Session survives restart - Helldiver bug prevented")


class TestResearchQuality:
    """Tests for research output quality (manual validation helpers)."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Manual validation test - run explicitly when checking quality")
    async def test_mission_briefing_quality_produces_good_research(self, temp_project):
        """
        Manual test: Run this to validate that mission briefing quality → research quality.

        Compare outputs from:
        - Generic briefing (low quality)
        - Detailed briefing (high quality)

        Expected: Detailed briefing should produce significantly better research.
        """
        researcher = GeneralResearcher(verbose=True)
        drop_path = temp_project / "quality-test"
        drop_path.mkdir(parents=True, exist_ok=True)

        # Low quality briefing (generic)
        generic_briefing = "Research MLOps platforms"

        # High quality briefing (following HQ template)
        detailed_briefing = """
        RESEARCH MISSION: What are the key differentiation factors between leading MLOps platforms (MLflow, Weights & Biases, Arthur.ai) for enterprise deployments?

        STRATEGIC CONTEXT:
        User is a VP of Engineering at a mid-sized SaaS company evaluating MLOps platforms for production deployment.
        They've narrowed to 3 finalists and need to understand differentiation beyond marketing claims.

        Decision context: Which platform to standardize on for company-wide ML infrastructure (multi-year commitment, $100K+ annual spend).

        YOUR PURPOSE:
        Provide objective comparison that highlights genuine technical/operational differences (not just feature lists).
        User will present findings to engineering leadership for final decision.

        SUCCESS CRITERIA:
        - Identify 3-5 key differentiation factors (technical, operational, cost)
        - Real-world evidence (customer case studies, technical docs, independent analysis)
        - Confidence level per factor (High/Medium/Low)
        - Flag where marketing claims contradict user evidence

        TOKEN BUDGET:
        Deliver complete findings in 3000-5000 tokens.
        Prioritize:
        1. Technical architecture differences (deployment model, integrations, scalability)
        2. Operational considerations (team required, learning curve, support)
        3. Total cost of ownership (not just license, but implementation + maintenance)
        4. Evidence quality (official docs > case studies > blog posts)

        CONSTRAINTS:
        - Focus on enterprise deployments (not hobbyist/academic use cases)
        - Prioritize recent data (2023-2024)
        - Look for: official documentation, customer testimonials, third-party analysis
        - Explicitly note where information is missing or contradictory

        RESEARCH APPROACH:
        Break into sub-questions:
        1. What are the core architectural differences?
        2. How do operational requirements differ (team, skills, time-to-value)?
        3. What does TCO look like for each (beyond sticker price)?
        4. Where do independent sources validate/contradict vendor claims?
        """

        # Execute both (run sequentially to see difference)
        print("\n" + "="*80)
        print("GENERIC BRIEFING RESEARCH:")
        print("="*80)
        generic_output = await researcher.execute_research(
            mission_briefing=generic_briefing,
            drop_path=drop_path,
            researcher_id="researcher-generic"
        )

        print("\n" + "="*80)
        print("DETAILED BRIEFING RESEARCH:")
        print("="*80)
        detailed_output = await researcher.execute_research(
            mission_briefing=detailed_briefing,
            drop_path=drop_path,
            researcher_id="researcher-detailed"
        )

        # Print comparison
        print("\n" + "="*80)
        print("COMPARISON:")
        print("="*80)
        print(f"Generic: {generic_output.token_count} tokens, {len(generic_output.sources)} sources")
        print(f"Detailed: {detailed_output.token_count} tokens, {len(detailed_output.sources)} sources")
        print("\nRead outputs at:")
        print(f"- {drop_path / 'researcher-generic-output.md'}")
        print(f"- {drop_path / 'researcher-detailed-output.md'}")
