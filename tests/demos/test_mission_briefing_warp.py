"""
Test Mission Briefing Transformer with Warp.ai Example

This validates that the briefing transformer generates high-quality mission briefings
for ICP validation research without making any API calls (free test).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.hq.mission_briefing import build_mission_briefing
from core.hq.context_extractor import UserContext


def test_warp_ai_briefing():
    """Test mission briefing generation for Warp.ai ICP validation."""

    print("="*80)
    print("MISSION BRIEFING TRANSFORMER TEST - Warp.ai ICP Validation")
    print("="*80)

    # Simulate user context from Warp.ai session
    user_context = UserContext(
        strategic_why="Build Clay-executable ICP criteria to identify and score potential Warp.ai customers at scale",
        decision_context="Validate ICP segments to enable automated lead scoring and prioritization (A/B/C/D tiers) in Clay workflows",
        success_criteria="Extract specific, measurable characteristics (tech stack, company size, roles hired, workload types) - not generic demographics - that enable A/B/C/D tier scoring in Clay",
        mental_models=[
            "Observable signals predict conversion - focus on measurable patterns over assumptions",
            "Reconnaissance before validation - gather foundational understanding before testing specific segments",
            "Clay-executable criteria - ICP characteristics must be programmatically detectable (job postings, tech stack, employee count, funding)",
            "Speed over perfection - 'move fast', 'take your best guess', prioritize action over analysis"
        ],
        priorities={
            "must_have": [
                "Observable/measurable ICP characteristics (technographic, firmographic, behavioral)",
                "Specific problem Warp.ai solves (actual, not assumed)",
                "Current customer patterns from public evidence",
                "Clay-executable signals (can be detected programmatically)"
            ],
            "nice_to_have": [
                "Detailed customer case studies",
                "Comprehensive market positioning"
            ]
        },
        constraints=[
            "Must use publicly available information only",
            "Single researcher for reconnaissance phase (budget/speed constraint implied)",
            "Need to move fast - minimal planning, rapid execution"
        ]
    )

    # HQ's drop plan (focus_question)
    focus_question = "What is Warp.ai's core product offering, target problem space, and publicly observable customer patterns?"
    hypothesis = "Warp.ai targets DevOps/Platform Engineering teams at high-growth tech companies (100-1000 employees) with complex AI/ML infrastructure needs"
    research_mode = "icp-validation"

    print(f"\n1. INPUT:")
    print(f"   Focus Question: {focus_question}")
    print(f"   Hypothesis: {hypothesis}")
    print(f"   Research Mode: {research_mode}")

    # Generate mission briefing
    print(f"\n2. GENERATING MISSION BRIEFING...")
    mission_briefing = build_mission_briefing(
        focus_question=focus_question,
        user_context=user_context,
        research_mode=research_mode,
        hypothesis=hypothesis,
        company_name="Warp.ai",
        token_budget=4000,
        geographic_focus="North America"
    )

    print(f"\n3. OUTPUT QUALITY CHECK:")
    print(f"   Briefing length: {len(mission_briefing)} characters (~{len(mission_briefing)//4} tokens)")
    print(f"   Target: 1500-2000 tokens (6000-8000 chars)")

    # Quality checks
    checks = {
        "Contains research mission": "# RESEARCH MISSION" in mission_briefing,
        "Contains strategic context": "# STRATEGIC CONTEXT" in mission_briefing,
        "Contains ICP-specific guidance": "Clay-executable" in mission_briefing,
        "Contains firmographic signals": "Firmographic Signals" in mission_briefing,
        "Contains technographic signals": "Technographic Signals" in mission_briefing,
        "Contains behavioral signals": "Behavioral Signals" in mission_briefing,
        "Contains output requirements": "# OUTPUT REQUIREMENTS" in mission_briefing,
        "Contains research approach": "# RESEARCH APPROACH" in mission_briefing,
        "Contains good/bad examples": "Good vs Bad" in mission_briefing or "❌ BAD" in mission_briefing,
        "Contains token budget": "TOKEN BUDGET" in mission_briefing,
        "Contains constraints": "# CONSTRAINTS" in mission_briefing,
        "Contains source quality criteria": "Source Quality" in mission_briefing,
        "Mentions Warp.ai": "Warp.ai" in mission_briefing,
        "Length appropriate": 6000 <= len(mission_briefing) <= 10000
    }

    print(f"\n4. QUALITY CHECKS:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False

    # Print sample sections
    print(f"\n5. SAMPLE SECTIONS:")

    # Extract and print mission section
    if "# RESEARCH MISSION" in mission_briefing:
        mission_start = mission_briefing.index("# RESEARCH MISSION")
        mission_end = mission_briefing.index("\n#", mission_start + 20) if "\n#" in mission_briefing[mission_start + 20:] else len(mission_briefing)
        mission_section = mission_briefing[mission_start:mission_end].strip()
        print(f"\n   --- RESEARCH MISSION ---")
        print(f"   {mission_section[:300]}...")

    # Extract and print ICP guidance sample
    if "Firmographic Signals" in mission_briefing:
        icp_start = mission_briefing.index("Firmographic Signals")
        icp_sample = mission_briefing[icp_start:icp_start + 400]
        print(f"\n   --- ICP GUIDANCE SAMPLE ---")
        print(f"   ...{icp_sample}...")

    # Save full briefing to file for manual review
    output_file = project_root / "tests" / "demos" / "warp_mission_briefing_output.md"
    output_file.write_text(mission_briefing, encoding="utf-8")
    print(f"\n6. FULL BRIEFING SAVED TO:")
    print(f"   {output_file}")
    print(f"   Review this file to validate briefing quality manually")

    # Final verdict
    print(f"\n" + "="*80)
    if all_passed:
        print("✅ ALL QUALITY CHECKS PASSED")
        print("\nNext step: Run actual research with this briefing to validate output quality")
        print("Expected: 8+ sources, specific ICP characteristics, Clay execution guidance")
    else:
        print("❌ SOME QUALITY CHECKS FAILED")
        print("\nReview the briefing and fix issues before running research")
    print("="*80)

    return all_passed


if __name__ == "__main__":
    success = test_warp_ai_briefing()
    sys.exit(0 if success else 1)
