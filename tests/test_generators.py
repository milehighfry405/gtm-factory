"""
Tests for generators module (latest_generator + session_metadata_generator + critical_analyst_generator).

Testing Strategy (Session 4):
- MOCKED tests for file I/O, metadata generation (no API calls)
- ONE real synthesis test to validate GPT-4o integration
- ONE real critical analysis test to validate GPT-4o integration
"""

import pytest
import json
from pathlib import Path
from core.generators import LatestGenerator, SessionMetadataGenerator, CriticalAnalystGenerator


class TestSessionMetadataGenerator:
    """Test metadata generation (NO API calls)."""

    def test_generate_session_metadata(self):
        """
        Validate session metadata generation from demo-company.

        NO API CALLS - Pure file I/O and JSON serialization.
        """
        generator = SessionMetadataGenerator()
        session_path = Path("projects/demo-company/sessions/session-demo-researcher")

        metadata = generator.generate_session_metadata(session_path)

        # Validate structure
        assert "session_id" in metadata, "[FAIL] Missing session_id"
        assert "total_drops" in metadata, "[FAIL] Missing total_drops"
        assert "drops" in metadata, "[FAIL] Missing drops list"

        # Validate values
        assert metadata["session_id"] == "session-demo-researcher"
        assert metadata["total_drops"] >= 1, "[FAIL] Should have at least 1 drop"

        # Validate drop summaries
        for drop in metadata["drops"]:
            assert "drop_id" in drop, "[FAIL] Drop missing drop_id"
            assert "created_at" in drop, "[FAIL] Drop missing timestamp"
            assert "researchers_count" in drop, "[FAIL] Drop missing researcher count"

        print(f"[OK] Session metadata valid: {metadata['total_drops']} drops, {metadata['total_researchers']} researchers")

    def test_generate_drop_metadata(self):
        """
        Validate drop metadata generation.

        NO API CALLS - File I/O only.
        """
        generator = SessionMetadataGenerator()
        drop_path = Path("projects/demo-company/sessions/session-demo-researcher/drops/drop-1")

        metadata = generator.generate_drop_metadata(drop_path)

        # Validate structure
        assert "drop_id" in metadata, "[FAIL] Missing drop_id"
        assert "user_context" in metadata, "[FAIL] Missing user_context"
        assert "researchers" in metadata, "[FAIL] Missing researchers list"

        # Validate researchers
        assert len(metadata["researchers"]) >= 1, "[FAIL] Should have at least 1 researcher"

        for researcher in metadata["researchers"]:
            assert "researcher_id" in researcher, "[FAIL] Researcher missing ID"
            assert "output_file" in researcher, "[FAIL] Researcher missing output file"
            assert "token_count" in researcher, "[FAIL] Researcher missing token count"

        print(f"[OK] Drop metadata valid: {len(metadata['researchers'])} researchers, {metadata['total_tokens']} tokens")

    def test_save_and_load_metadata(self, tmp_path):
        """
        Test metadata persistence (save/load round trip).

        NO API CALLS - File I/O only.
        """
        generator = SessionMetadataGenerator()

        # Create test metadata
        test_metadata = {
            "session_id": "test-session",
            "total_drops": 1,
            "total_tokens": 5000
        }

        # Save
        generator.save_session_metadata(tmp_path, test_metadata)

        # Verify file exists
        metadata_file = tmp_path / "session-metadata.json"
        assert metadata_file.exists(), "[FAIL] Metadata file not created"

        # Load and verify
        loaded = json.loads(metadata_file.read_text())
        assert loaded["session_id"] == "test-session"
        assert loaded["total_drops"] == 1

        print("[OK] Metadata save/load round trip successful")


class TestLatestGenerator:
    """Test latest.md synthesis."""

    def test_load_researcher_outputs(self):
        """
        Test loading researcher outputs from drop folder.

        NO API CALLS - File I/O only.
        """
        generator = LatestGenerator()
        drop_path = Path("projects/demo-company/sessions/session-demo-researcher/drops/drop-1")

        outputs = generator._load_researcher_outputs(drop_path)

        assert len(outputs) >= 1, "[FAIL] Should have at least 1 researcher output"

        for output in outputs:
            assert "researcher_id" in output, "[FAIL] Missing researcher_id"
            assert "findings" in output, "[FAIL] Missing findings"
            assert len(output["findings"]) > 100, "[FAIL] Findings too short"

        print(f"[OK] Loaded {len(outputs)} researcher outputs")

    def test_load_user_context(self):
        """
        Test loading user context from drop folder.

        NO API CALLS - File I/O only.
        """
        generator = LatestGenerator()
        drop_path = Path("projects/demo-company/sessions/session-demo-researcher/drops/drop-1")

        context = generator._load_user_context(drop_path)

        assert context is not None, "[FAIL] User context should exist"
        assert "Strategic WHY" in context or "strategic" in context.lower(), "[FAIL] Context missing strategic WHY"

        print(f"[OK] User context loaded: {len(context)} chars")

    @pytest.mark.asyncio
    async def test_synthesis_real_api_call(self):
        """
        ONE REAL TEST: Validate synthesis with actual GPT-4o call.

        This is the ONLY test that makes an API call (~$0.10-0.15).
        Validates end-to-end synthesis works.
        """
        generator = LatestGenerator()
        session_path = Path("projects/demo-company/sessions/session-demo-researcher")

        # Synthesize drop-1 (first drop, no existing latest.md)
        latest_md = generator.synthesize_drop(
            session_path=session_path,
            drop_id="drop-1",
            existing_latest=None
        )

        # Validate output
        assert latest_md, "[FAIL] CRITICAL: No synthesis output returned"
        assert len(latest_md) > 500, "[FAIL] CRITICAL: Synthesis too short"

        # Should contain key sections
        assert "TL;DR" in latest_md or "Key Insights" in latest_md, "[FAIL] Missing expected sections"
        assert "MLOps" in latest_md, "[FAIL] Missing topic content"

        # Save for manual inspection
        output_file = session_path / "latest-test-output.md"
        output_file.write_text(latest_md, encoding="utf-8")

        print(f"[OK] REAL SYNTHESIS TEST PASSED")
        print(f"   Output: {len(latest_md)} chars")
        print(f"   Saved to: {output_file}")
        print(f"   Cost: ~$0.10-0.15")

    def test_save_latest(self, tmp_path):
        """
        Test saving latest.md to session directory.

        NO API CALLS - File I/O only.
        """
        generator = LatestGenerator()

        test_content = "# Latest: Test Session\n\nThis is test content."
        generator.save_latest(tmp_path, test_content)

        # Verify
        latest_file = tmp_path / "latest.md"
        assert latest_file.exists(), "[FAIL] latest.md not created"

        loaded = latest_file.read_text(encoding="utf-8")
        assert loaded == test_content, "[FAIL] Content mismatch"

        print("[OK] Latest.md save successful")


class TestInvalidationDetection:
    """Test contradiction detection and strikethrough application."""

    def test_detects_contradictions_in_manual_example(self):
        """
        Test invalidation with manually crafted contradiction.

        NO API CALLS - Using drop-1 and drop-2 which have known contradiction.

        Drop-1: "MLOps market was $1.2B"
        Drop-2: "MLOps market is $2.2B" (contradicts drop-1)

        Expected: Synthesis should strikethrough old claim.
        """
        # This test would validate the contradiction detection logic
        # For now, just verify drop-2 file exists and contains contradiction

        drop2_path = Path("projects/demo-company/sessions/session-demo-researcher/drops/drop-2/researcher-contradictory-output.md")

        if not drop2_path.exists():
            pytest.skip("Drop-2 fixture not created yet")

        content = drop2_path.read_text(encoding="utf-8")

        # Verify contradiction is present in drop-2
        assert "$2.2B" in content, "[FAIL] New market size missing"
        assert "$1.2B" in content or "Previous Estimate" in content, "[FAIL] Reference to old estimate missing"

        print("[OK] Contradiction fixture validated (drop-1: $1.2B → drop-2: $2.2B)")


class TestCriticalAnalystGenerator:
    """Test critical analysis generation (pokes holes in research)."""

    def test_load_researcher_outputs(self):
        """
        Test loading researcher outputs for critical analysis.

        NO API CALLS - File I/O only.
        """
        generator = CriticalAnalystGenerator()
        drop_path = Path("projects/demo-company/sessions/session-demo-researcher/drops/drop-1")

        outputs = generator._load_researcher_outputs(drop_path)

        assert len(outputs) >= 1, "[FAIL] Should have at least 1 researcher output"

        for output in outputs:
            assert "researcher_id" in output, "[FAIL] Missing researcher_id"
            assert "content" in output, "[FAIL] Missing content"
            assert len(output["content"]) > 100, "[FAIL] Content too short"

        print(f"[OK] Loaded {len(outputs)} researcher outputs for critical analysis")

    @pytest.mark.asyncio
    async def test_critical_analysis_real_api_call(self):
        """
        ONE REAL TEST: Validate critical analysis with actual GPT-4o call.

        This is the SECOND real API test (~$0.10-0.15).
        Validates end-to-end critical analysis works.
        """
        generator = CriticalAnalystGenerator()
        session_path = Path("projects/demo-company/sessions/session-demo-researcher")

        # Analyze drop-1
        analysis = generator.analyze_drop(
            session_path=session_path,
            drop_id="drop-1"
        )

        # Validate output
        assert analysis, "[FAIL] CRITICAL: No analysis output returned"
        assert len(analysis) > 500, "[FAIL] CRITICAL: Analysis too short"

        # Should contain critical sections
        assert "Critical" in analysis or "Concerns" in analysis or "Issues" in analysis, "[FAIL] Missing critical analysis sections"
        assert "Questions" in analysis or "Gaps" in analysis, "[FAIL] Missing gaps/questions section"

        # Save for manual inspection
        output_file = session_path / "drops" / "drop-1" / "critical-analysis-test-output.md"
        output_file.write_text(analysis, encoding="utf-8")

        print(f"[OK] REAL CRITICAL ANALYSIS TEST PASSED")
        print(f"   Output: {len(analysis)} chars")
        print(f"   Saved to: {output_file}")
        print(f"   Cost: ~$0.10-0.15")

    def test_save_analysis(self, tmp_path):
        """
        Test saving critical-analysis.md to drop directory.

        NO API CALLS - File I/O only.
        """
        generator = CriticalAnalystGenerator()

        # Create mock drop directory
        drop_path = tmp_path / "drop-1"
        drop_path.mkdir()

        test_content = "# Critical Analysis\n\n## Major Issues\n- Issue 1\n- Issue 2"
        generator.save_analysis(drop_path, test_content)

        # Verify
        analysis_file = drop_path / "critical-analysis.md"
        assert analysis_file.exists(), "[FAIL] critical-analysis.md not created"

        loaded = analysis_file.read_text(encoding="utf-8")
        assert loaded == test_content, "[FAIL] Content mismatch"

        print("[OK] Critical analysis save successful")
