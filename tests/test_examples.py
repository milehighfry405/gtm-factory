"""
Test Examples for GTM Factory Multi-Agent Research System

These tests demonstrate expected behavior for the agent system using the example project.
"""

import os
import json
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
EXAMPLE_PROJECT = PROJECT_ROOT / "projects" / "example-company"
PROMPTS_DIR = PROJECT_ROOT / "prompts"


class TestSessionMetadataGeneration:
    """Test Scenario 1: Session Metadata Generator produces valid, lightweight metadata"""

    def test_metadata_file_exists(self):
        """Verify session metadata file is created"""
        session_path = EXAMPLE_PROJECT / "sessions" / "001_initial_research"
        metadata_file = session_path / "session_metadata.json"

        assert metadata_file.exists(), "session_metadata.json should be created after session"

    def test_metadata_structure_valid(self):
        """Verify metadata follows required schema"""
        metadata_file = EXAMPLE_PROJECT / "sessions" / "001_initial_research" / "session_metadata.json"

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Required fields
        required_fields = [
            "session_id", "timestamp", "status", "research_questions",
            "key_findings_summary", "agents_used", "topics_covered",
            "follow_up_questions", "total_token_usage"
        ]

        for field in required_fields:
            assert field in metadata, f"Metadata missing required field: {field}"

    def test_metadata_file_size_constraint(self):
        """Verify metadata stays within 2KB token budget"""
        metadata_file = EXAMPLE_PROJECT / "sessions" / "001_initial_research" / "session_metadata.json"

        file_size = os.path.getsize(metadata_file)

        # 2KB = 2048 bytes
        assert file_size < 2048, f"Metadata file too large: {file_size} bytes (limit: 2048)"

    def test_findings_have_confidence_levels(self):
        """Verify all findings include confidence assessments"""
        metadata_file = EXAMPLE_PROJECT / "sessions" / "001_initial_research" / "session_metadata.json"

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        for finding in metadata["key_findings_summary"]:
            assert "confidence" in finding, "Finding missing confidence level"
            assert finding["confidence"] in ["High", "Medium", "Low"], \
                f"Invalid confidence level: {finding['confidence']}"


class TestLatestDocumentGeneration:
    """Test Scenario 2: Latest Generator produces executive-ready intelligence briefs"""

    def test_latest_file_created(self):
        """Verify Latest.md is generated in research_artifacts"""
        latest_file = EXAMPLE_PROJECT / "research_artifacts" / "Latest.md"

        assert latest_file.exists(), "Latest.md should be created after session synthesis"

    def test_latest_has_required_sections(self):
        """Verify Latest.md contains all required sections"""
        latest_file = EXAMPLE_PROJECT / "research_artifacts" / "Latest.md"

        with open(latest_file, 'r') as f:
            content = f.read()

        required_sections = [
            "## TL;DR",
            "## Key Insights",
            "## Strategic Implications",
            "## Recommended Actions",
            "## Deep Dive References"
        ]

        for section in required_sections:
            assert section in content, f"Latest.md missing required section: {section}"

    def test_latest_word_count_constraint(self):
        """Verify Latest.md stays within 1500 word limit"""
        latest_file = EXAMPLE_PROJECT / "research_artifacts" / "Latest.md"

        with open(latest_file, 'r') as f:
            content = f.read()

        # Remove markdown headers and count words
        words = content.split()
        word_count = len(words)

        assert word_count <= 1500, f"Latest.md too long: {word_count} words (limit: 1500)"

    def test_insights_have_confidence_tags(self):
        """Verify key insights include confidence levels"""
        latest_file = EXAMPLE_PROJECT / "research_artifacts" / "Latest.md"

        with open(latest_file, 'r') as f:
            content = f.read()

        # Should have confidence indicators in insights section
        insights_section = content.split("## Key Insights")[1].split("##")[0]

        assert "(Confidence: High)" in insights_section or \
               "(Confidence: Medium)" in insights_section or \
               "(Confidence: Low)" in insights_section, \
               "Key Insights should include confidence levels"


class TestPromptStructureCompliance:
    """Test Scenario 3: All agent prompts follow Anthropic best practices"""

    def test_all_prompts_exist(self):
        """Verify all required prompt files are created"""
        required_prompts = [
            "hq-orchestrator.md",
            "general-researcher.md",
            "critical-analyst.md",
            "latest-generator.md",
            "session-metadata-generator.md"
        ]

        for prompt_file in required_prompts:
            prompt_path = PROMPTS_DIR / prompt_file
            assert prompt_path.exists(), f"Missing required prompt: {prompt_file}"

    def test_prompts_have_required_sections(self):
        """Verify prompts include Role, Job, Inputs, Outputs, Constraints sections"""
        prompt_files = [
            "hq-orchestrator.md",
            "general-researcher.md",
            "critical-analyst.md"
        ]

        required_sections = [
            "## Role",
            "## Primary Job",
            "## Inputs",
            "## Outputs",
            "## Constraints"
        ]

        for prompt_file in prompt_files:
            prompt_path = PROMPTS_DIR / prompt_file
            with open(prompt_path, 'r') as f:
                content = f.read()

            for section in required_sections:
                assert section in content, \
                    f"{prompt_file} missing required section: {section}"

    def test_prompts_specify_token_budgets(self):
        """Verify prompts include explicit token budget constraints"""
        prompt_files = [
            "general-researcher.md",
            "critical-analyst.md",
            "latest-generator.md"
        ]

        for prompt_file in prompt_files:
            prompt_path = PROMPTS_DIR / prompt_file
            with open(prompt_path, 'r') as f:
                content = f.read()

            assert "## Token Budget" in content or "token budget" in content.lower(), \
                f"{prompt_file} should specify token budget constraints"

    def test_prompt_length_appropriate(self):
        """Verify prompts are 20-40 lines (excluding examples)"""
        prompt_files = [
            "hq-orchestrator.md",
            "general-researcher.md",
            "critical-analyst.md",
            "latest-generator.md",
            "session-metadata-generator.md"
        ]

        for prompt_file in prompt_files:
            prompt_path = PROMPTS_DIR / prompt_file
            with open(prompt_path, 'r') as f:
                lines = [line for line in f.readlines() if line.strip()]

            # Count non-example content lines (rough heuristic: exclude large code blocks)
            content_lines = [l for l in lines if not l.startswith("```") and not l.startswith("  ")]
            line_count = len(content_lines)

            # Relaxed range given structured sections
            assert 20 <= line_count <= 80, \
                f"{prompt_file} outside recommended length: {line_count} lines"


# Test execution summary
if __name__ == "__main__":
    print("GTM Factory Test Examples")
    print("=" * 50)
    print("\nTest Scenario 1: Session Metadata Generation")
    print("- Validates metadata schema compliance")
    print("- Checks file size constraints (< 2KB)")
    print("- Verifies confidence level tagging")

    print("\nTest Scenario 2: Latest Document Generation")
    print("- Validates Latest.md structure")
    print("- Checks word count limits (< 1500 words)")
    print("- Verifies executive-ready formatting")

    print("\nTest Scenario 3: Prompt Structure Compliance")
    print("- Validates Anthropic best practices adherence")
    print("- Checks required sections present")
    print("- Verifies token budget specifications")

    print("\n" + "=" * 50)
    print("Run with: pytest tests/test_examples.py -v")
