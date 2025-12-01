"""
Tests for UI module (adapters, state management, context tracking).

Testing Strategy (Session 5):
- MOCKED tests for all components (no API calls)
- Manual smoke test documented in session-5-ui-final.md

Total: 10 mocked tests (this file) + 1 manual smoke test
Cost: $0 for mocked tests, ~$0.20 for manual smoke test
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from core.ui import StateManager, DropState, ContextTracker


class TestStateManager:
    """Test state management and crash recovery."""

    def test_autosave_conversation(self, tmp_path):
        """Test conversation autosave after each message."""
        manager = StateManager(session_path=tmp_path)

        messages = [
            {"role": "user", "content": "Test message 1"},
            {"role": "assistant", "content": "Test response 1"}
        ]

        # Autosave
        manager.autosave_conversation(messages)

        # Verify file exists
        assert manager.conversation_temp_file.exists()

        # Verify content
        loaded = manager.load_conversation()
        assert len(loaded) == 2
        assert loaded[0]["role"] == "user"
        assert loaded[1]["role"] == "assistant"

        print("[OK] Autosave conversation works")

    def test_drop_state_tracking(self, tmp_path):
        """Test drop state transitions (proposed → complete)."""
        manager = StateManager(session_path=tmp_path)

        drop_id = "drop-1"

        # Update state: proposed
        manager.update_drop_state(drop_id, DropState.PROPOSED)
        assert manager.get_drop_state(drop_id) == DropState.PROPOSED

        # Update state: researching
        manager.update_drop_state(drop_id, DropState.RESEARCHING)
        assert manager.get_drop_state(drop_id) == DropState.RESEARCHING

        # Update state: complete
        manager.update_drop_state(drop_id, DropState.COMPLETE)
        assert manager.get_drop_state(drop_id) == DropState.COMPLETE

        print("[OK] Drop state tracking works")

    def test_find_incomplete_drops(self, tmp_path):
        """Test crash recovery detection."""
        manager = StateManager(session_path=tmp_path)

        # Create complete drop (should not be detected)
        manager.update_drop_state("drop-1", DropState.COMPLETE)

        # Create incomplete drop (should be detected)
        manager.update_drop_state("drop-2", DropState.RESEARCHING)

        # Find incomplete
        incomplete = manager.find_incomplete_drops()

        assert len(incomplete) == 1
        assert incomplete[0]["drop_id"] == "drop-2"
        assert incomplete[0]["state"] == "researching"

        print("[OK] Crash recovery detection works")

    def test_atomic_file_writes(self, tmp_path):
        """Test atomic writes prevent corruption."""
        manager = StateManager(session_path=tmp_path)

        test_file = tmp_path / "test.txt"

        # Write content
        manager._atomic_write(test_file, "test content")

        # Verify no .tmp file left behind
        assert not (tmp_path / "test.txt.tmp").exists()

        # Verify content
        assert test_file.read_text() == "test content"

        print("[OK] Atomic writes work")


class TestContextTracker:
    """Test context window tracking."""

    def test_token_estimation(self):
        """Test token counting from conversation."""
        tracker = ContextTracker(max_tokens=200000)

        messages = [
            {"role": "user", "content": "a" * 1000},  # ~250 tokens
            {"role": "assistant", "content": "b" * 1000}  # ~250 tokens
        ]

        tracker.add_conversation(messages)

        # Rough estimate: 2000 chars / 4 = 500 tokens
        assert tracker.total_tokens() == 500

        print("[OK] Token estimation works")

    def test_percentage_calculation(self):
        """Test context window percentage."""
        tracker = ContextTracker(max_tokens=1000)

        messages = [{"role": "user", "content": "a" * 400}]  # ~100 tokens
        tracker.add_conversation(messages)

        # Should be ~10%
        assert 9 <= tracker.percentage() <= 11

        print("[OK] Percentage calculation works")

    def test_warning_threshold(self):
        """Test warning at 80% threshold."""
        tracker = ContextTracker(max_tokens=1000)

        # Add 900 chars (~225 tokens, ~22.5%)
        messages = [{"role": "user", "content": "a" * 900}]
        tracker.add_conversation(messages)
        assert not tracker.should_warn(threshold=80.0)

        # Add more but stay under 80%
        tracker.add_file_content("latest_md", "b" * 2000)  # 225 + 500 = 725 tokens (72.5%)
        assert not tracker.should_warn(threshold=80.0)

        # Add more to push over 80%
        tracker.add_file_content("critical_analysis_md", "c" * 400)  # 725 + 100 = 825 tokens (82.5%)
        assert tracker.should_warn(threshold=80.0)

        print("[OK] Warning threshold works")


class TestHQAdapter:
    """Test HQ adapter (mocked)."""

    @patch('core.ui.adapters.hq_adapter.HQOrchestrator')
    def test_chat_stream_with_callback(self, mock_orchestrator):
        """Test streaming chat with token callbacks."""
        # Mock streaming response
        mock_instance = mock_orchestrator.return_value
        mock_instance.chat_stream.return_value = iter(["Hello", " ", "world"])

        from core.ui.adapters.hq_adapter import HQAdapter

        adapter = HQAdapter(
            api_key="test-key",
            project_path=Path("projects/test"),
            session_id="session-test"
        )

        # Collect tokens via callback
        tokens = []
        def on_token(token):
            tokens.append(token)

        # Stream response
        list(adapter.chat_stream("test message", on_token=on_token))

        # Verify callback was called
        assert tokens == ["Hello", " ", "world"]

        print("[OK] HQ adapter streaming works")


class TestResearcherAdapter:
    """Test researcher adapter (mocked)."""

    @pytest.mark.asyncio
    async def test_execute_research_plan(self):
        """Test parallel research execution with progress callbacks."""
        from core.ui.adapters.researcher_adapter import ResearcherAdapter, ResearcherStatus
        from core.researcher.general_researcher import ResearchOutput

        adapter = ResearcherAdapter()

        plan = {
            "researchers": [
                {"id": "researcher-1", "focus": "Market sizing"},
                {"id": "researcher-2", "focus": "Competitive landscape"}
            ]
        }

        # Track progress callbacks
        progress_updates = []
        def on_progress(researcher_id, status, message):
            progress_updates.append((researcher_id, status, message))

        # Mock the execute_research method
        with patch.object(adapter, '_execute_single_researcher') as mock_execute:
            # Mock successful outputs
            mock_output_1 = ResearchOutput(
                findings="Test findings 1",
                sources=[],
                token_count=1000,
                cost=0.05,
                runtime_seconds=10.0,
                researcher_id="researcher-1"
            )
            mock_output_2 = ResearchOutput(
                findings="Test findings 2",
                sources=[],
                token_count=1200,
                cost=0.06,
                runtime_seconds=12.0,
                researcher_id="researcher-2"
            )

            mock_execute.side_effect = [mock_output_1, mock_output_2]

            # Execute
            outputs = await adapter.execute_research_plan(
                plan=plan,
                drop_path=Path("/tmp/drop-1"),
                on_progress=on_progress
            )

            # Verify outputs
            assert len(outputs) == 2

        print("[OK] Researcher adapter parallel execution works")


class TestGeneratorAdapter:
    """Test generator adapter (mocked)."""

    @patch('core.ui.adapters.generator_adapter.LatestGenerator')
    def test_synthesize_drop(self, mock_latest_gen):
        """Test synthesis with status callbacks."""
        from core.ui.adapters.generator_adapter import GeneratorAdapter, GeneratorStatus

        # Mock generator
        mock_instance = mock_latest_gen.return_value
        mock_instance.synthesize_drop.return_value = "# Latest\n\nTest synthesis"

        adapter = GeneratorAdapter()

        # Track status callbacks
        statuses = []
        def on_status(status, message):
            statuses.append((status, message))

        # Execute synthesis
        latest_md = adapter.synthesize_drop(
            session_path=Path("/tmp/session"),
            drop_id="drop-1",
            on_status=on_status
        )

        # Verify
        assert "Test synthesis" in latest_md
        assert len(statuses) >= 2  # At least start and complete

        print("[OK] Generator adapter synthesis works")


# Manual Smoke Test (documented, not automated)
"""
MANUAL SMOKE TEST (Run before final commit):

1. Install dependencies:
   pip install -r requirements.txt

2. Set environment variables:
   export ANTHROPIC_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export TAVILY_API_KEY="your-key"

3. Run Streamlit app:
   streamlit run ui/app.py

4. Test full workflow:
   a. Chat with HQ (2-3 messages)
   b. Flip research flag
   c. Confirm research plan
   d. Watch research execute
   e. Verify latest.md and critical-analysis.md created
   f. Continue conversation with HQ
   g. Flip research flag for Drop 2
   h. Repeat

5. Test crash recovery:
   a. Start research
   b. Kill Streamlit mid-research
   c. Restart app
   d. Verify incomplete drop detected
   e. Mark as failed or resume

Expected cost: ~$0.20
Expected time: 10-15 minutes
"""

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
