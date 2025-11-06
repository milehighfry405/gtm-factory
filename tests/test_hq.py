"""
Integration tests for HQ Orchestrator critical paths.

These tests verify the end-to-end flows that would be devastating if broken:
- Conversation history gets saved
- User context extraction works
- Drop folders are created correctly
- Files can be loaded back
- System prompt loads properly

We DON'T test:
- Quality of Socratic questions (subjective)
- Research quality (requires actual API calls)
- User satisfaction

We DO test:
- The plumbing works (save/load, folder creation)
- Integration points don't break
- Critical paths complete without errors
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from core.hq.memory_manager import MemoryManager
from core.hq.context_extractor import UserContext


class TestMemoryManagerCriticalPath:
    """Test that conversation and context persistence works."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_conversation_save_and_load_round_trip(self, temp_project):
        """
        CRITICAL: Verify conversation history survives save/load cycle.

        This catches the bug you mentioned: "chat history wasn't being saved"
        """
        manager = MemoryManager(temp_project, "session-1-test")

        # Simulate a conversation
        conversation = [
            {"role": "user", "content": "Research Arthur.ai's downmarket opportunity"},
            {"role": "assistant", "content": "What size companies are you targeting?"},
            {"role": "user", "content": "10-50 employees, maybe up to 100"}
        ]

        # Save it
        saved_path = manager.save_conversation_history(conversation)
        assert saved_path.exists(), "Conversation file wasn't created"

        # Load it back
        loaded = manager.load_conversation_history()
        assert loaded is not None, "Couldn't load conversation back"
        assert "10-50 employees" in loaded, "Conversation content was lost"
        assert "Arthur.ai" in loaded, "Conversation content was corrupted"

    def test_user_context_persists_in_drop_folder(self, temp_project):
        """
        CRITICAL: User context must save to drop folder for later reference.

        Without this, you lose the strategic WHY after each drop.
        """
        manager = MemoryManager(temp_project, "session-1-test")

        # Create user context
        context = UserContext(
            strategic_why="Evaluate downmarket expansion for Arthur.ai",
            decision_context="Product roadmap prioritization",
            mental_models=["Jobs-to-be-done framework"],
            priorities={"must_have": ["Pricing feasibility"], "nice_to_have": ["Competitor analysis"]},
            constraints=["Limited engineering resources"],
            success_criteria="Clear go/no-go decision on downmarket"
        )

        # Save to drop-1
        saved_path = manager.save_user_context(context.to_markdown(), drop_id="drop-1")
        assert saved_path.exists(), "User context file wasn't created in drop folder"

        # Verify it's in the right place
        expected_path = temp_project / "sessions" / "session-1-test" / "drops" / "drop-1" / "user-context.md"
        assert saved_path == expected_path, "User context saved to wrong location"

        # Load it back
        loaded = manager.load_user_context(drop_id="drop-1")
        assert loaded is not None, "Couldn't load user context back"
        assert "Arthur.ai" in loaded, "User context content was lost"
        assert "downmarket" in loaded, "User context content was corrupted"

    def test_drop_metadata_is_lightweight(self, temp_project):
        """
        CRITICAL: Drop metadata must be <2KB for progressive disclosure.

        Large metadata defeats the purpose of lightweight identifiers.
        """
        manager = MemoryManager(temp_project, "session-1-test")

        metadata = {
            "hypothesis": "Arthur.ai can serve 10-50 employee companies",
            "researchers_count": 2,
            "questions": ["What's the pricing threshold?", "Who are competitors?"],
            "status": "complete"
        }

        saved_path = manager.save_drop_metadata("drop-1", metadata)
        assert saved_path.exists(), "Drop metadata wasn't created"

        # Check size
        file_size = saved_path.stat().st_size
        assert file_size < 2048, f"Drop metadata is {file_size} bytes (should be <2KB)"

        # Verify it loads back correctly
        loaded = manager.load_drop_metadata("drop-1")
        assert loaded is not None, "Couldn't load metadata back"
        assert loaded["hypothesis"] == metadata["hypothesis"], "Metadata corrupted"

    def test_session_index_provides_progressive_disclosure(self, temp_project):
        """
        CRITICAL: Can get overview of all drops without loading full content.

        This is how you avoid loading everything upfront (Anthropic pattern).
        """
        manager = MemoryManager(temp_project, "session-1-test")

        # Create multiple drops with metadata
        for i in range(1, 4):
            manager.save_drop_metadata(f"drop-{i}", {
                "hypothesis": f"Hypothesis {i}",
                "researchers_count": i,
                "status": "complete"
            })

        # Get index (lightweight)
        index = manager.get_session_index()

        assert len(index["drops"]) == 3, "Missing drops in index"
        assert all("hypothesis" in drop for drop in index["drops"]), "Index missing metadata"

        # Verify we got metadata without loading full research
        # (In real system, each drop would have large research files we're NOT loading)
        assert index["session_id"] == "session-1-test"


class TestUserContextExtraction:
    """Test that strategic WHY extraction doesn't fail silently."""

    def test_user_context_to_markdown_is_valid(self):
        """
        CRITICAL: User context must convert to valid markdown.

        If markdown is malformed, files are unreadable later.
        """
        context = UserContext(
            strategic_why="Test strategic reason",
            decision_context="Build vs buy decision",
            mental_models=["First principles"],
            priorities={"must_have": ["Speed"], "nice_to_have": ["Cost"]},
            constraints=["Time limit"],
            success_criteria="Clear recommendation"
        )

        md = context.to_markdown()

        # Basic validation
        assert "# User Context" in md, "Missing markdown header"
        assert "Strategic WHY" in md, "Missing strategic WHY section"
        assert "Test strategic reason" in md, "Content missing from markdown"
        assert "Build vs buy" in md, "Decision context missing"

        # Verify structure
        assert md.count("---") >= 3, "Missing markdown section dividers"

    def test_user_context_handles_empty_lists(self):
        """
        CRITICAL: System shouldn't crash on edge cases.

        User might not provide mental models, nice-to-haves, etc.
        """
        context = UserContext(
            strategic_why="Minimal context",
            decision_context="Quick decision",
            mental_models=[],  # Empty
            priorities={"must_have": ["Something"], "nice_to_have": []},  # Empty nice-to-have
            constraints=[],  # Empty
            success_criteria="Any info"
        )

        md = context.to_markdown()

        # Should still generate valid markdown
        assert "# User Context" in md
        assert "Minimal context" in md


class TestCriticalPathIntegration:
    """Test the full flow that would force conversation restart if broken."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_complete_drop_workflow(self, temp_project):
        """
        CRITICAL END-TO-END TEST: Simulate complete drop creation.

        This is the flow that MUST work or you have to restart:
        1. Start conversation
        2. Extract user context
        3. Create drop folder
        4. Save conversation history
        5. Save user context to drop
        6. Save drop metadata
        7. Verify everything is loadable

        If ANY step breaks, you lose your conversation and have to restart.
        """
        manager = MemoryManager(temp_project, "session-1-arthur")

        # Step 1-2: Simulate conversation and context
        conversation = [
            {"role": "user", "content": "Research Arthur.ai downmarket"},
            {"role": "assistant", "content": "What size companies?"},
            {"role": "user", "content": "10-50 employees"}
        ]

        context = UserContext(
            strategic_why="Downmarket expansion evaluation",
            decision_context="Q2 roadmap decision",
            mental_models=["TAM/SAM/SOM"],
            priorities={"must_have": ["Pricing data"], "nice_to_have": ["Case studies"]},
            constraints=["2-week timeline"],
            success_criteria="Go/no-go recommendation"
        )

        # Step 3: Create drop folder
        drop_path = manager.create_drop_directory("drop-1")
        assert drop_path.exists(), "❌ CRITICAL: Drop folder not created"

        # Step 4: Save conversation
        conv_path = manager.save_conversation_history(conversation)
        assert conv_path.exists(), "❌ CRITICAL: Conversation not saved"

        # Step 5: Save user context to drop
        context_path = manager.save_user_context(context.to_markdown(), drop_id="drop-1")
        assert context_path.exists(), "❌ CRITICAL: User context not saved"

        # Step 6: Save drop metadata
        metadata = {
            "hypothesis": "Arthur.ai can serve 10-50 employee companies profitably",
            "researchers_count": 2,
            "questions": ["Pricing threshold?", "Competitors?"],
            "status": "in_progress"
        }
        meta_path = manager.save_drop_metadata("drop-1", metadata)
        assert meta_path.exists(), "❌ CRITICAL: Drop metadata not saved"

        # Step 7: VERIFY EVERYTHING IS LOADABLE (this is where Helldiver broke)
        loaded_conv = manager.load_conversation_history()
        assert loaded_conv is not None, "❌ CRITICAL: Can't reload conversation"
        assert "10-50 employees" in loaded_conv, "❌ CRITICAL: Conversation data corrupted"

        loaded_context = manager.load_user_context(drop_id="drop-1")
        assert loaded_context is not None, "❌ CRITICAL: Can't reload user context"
        assert "Downmarket expansion" in loaded_context, "❌ CRITICAL: Context data corrupted"

        loaded_meta = manager.load_drop_metadata("drop-1")
        assert loaded_meta is not None, "❌ CRITICAL: Can't reload metadata"
        assert loaded_meta["researchers_count"] == 2, "❌ CRITICAL: Metadata corrupted"

        # SUCCESS: Full workflow completed without errors
        print("✅ Complete drop workflow PASSED - conversation won't be lost")

    def test_folder_naming_is_consistent(self, temp_project):
        """
        CRITICAL: Folder names must be predictable and consistent.

        You mentioned Helldiver used LLM-generated names that sometimes failed.
        We use simple, deterministic naming: drop-1, drop-2, etc.
        """
        manager = MemoryManager(temp_project, "session-1-test")

        # Create multiple drops
        drop1 = manager.create_drop_directory("drop-1")
        drop2 = manager.create_drop_directory("drop-2")
        drop3 = manager.create_drop_directory("drop-3")

        # Verify naming is consistent
        assert drop1.name == "drop-1", "Drop naming not consistent"
        assert drop2.name == "drop-2", "Drop naming not consistent"
        assert drop3.name == "drop-3", "Drop naming not consistent"

        # Verify we can list them reliably
        all_drops = manager.get_all_drop_ids()
        assert len(all_drops) == 3, "Can't reliably list drop folders"
        assert "drop-1" in all_drops, "Missing drop in list"

    def test_system_survives_missing_files(self, temp_project):
        """
        CRITICAL: System should handle missing files gracefully.

        Don't crash if user-context.md or latest.md doesn't exist yet.
        """
        manager = MemoryManager(temp_project, "session-1-test")

        # Try to load files that don't exist
        conv = manager.load_conversation_history()
        assert conv is None, "Should return None for missing file, not crash"

        context = manager.load_user_context()
        assert context is None, "Should return None for missing file, not crash"

        latest = manager.load_latest_md()
        assert latest is None, "Should return None for missing file, not crash"

        # No exceptions = PASS


class TestOrchestratorSystemPrompt:
    """Test that orchestrator can load its system prompt."""

    def test_system_prompt_loads_without_crash(self):
        """
        CRITICAL: If system prompt doesn't load, orchestrator can't function.

        We can't test the full orchestrator without API key, but we can
        test that the prompt file exists and is loadable.
        """
        from core.hq.orchestrator import HQOrchestrator

        # This will fail if prompt file is missing or malformed
        try:
            # We can't instantiate without API key, but we can check the prompt exists
            prompt_path = Path(__file__).parent.parent / "prompts" / "hq-orchestrator.md"
            assert prompt_path.exists(), "❌ CRITICAL: System prompt file missing"

            # Verify it's readable
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()

            assert len(prompt_content) > 100, "System prompt seems too short"
            assert "Socratic" in prompt_content, "System prompt missing key sections"

        except Exception as e:
            pytest.fail(f"❌ CRITICAL: System prompt loading failed: {e}")


if __name__ == "__main__":
    """Run tests with: python -m pytest tests/test_hq.py -v"""
    pytest.main([__file__, "-v", "--tb=short"])
