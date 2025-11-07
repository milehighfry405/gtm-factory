"""
Demo script to test Researcher module in isolation.

This allows you to:
- Test mission briefing quality → research quality
- See actual gpt-researcher output
- Validate token budgets
- Check source quality

Run this BEFORE building full UI to validate researcher works.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from core.researcher import GeneralResearcher

# Load environment variables
load_dotenv()


def print_banner(text: str):
    """Print formatted banner."""
    print("\n" + "="*80)
    print(text)
    print("="*80 + "\n")


async def main():
    print_banner("🔬 GTM Factory - Researcher Demo")

    # Check for API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("\nPlease add your OpenAI API key to .env:")
        print("OPENAI_API_KEY=your-key-here")
        return

    # Setup
    project_path = Path(__file__).parent / "projects" / "demo-company"
    session_id = "session-demo-researcher"
    drop_path = project_path / "sessions" / session_id / "drops" / "drop-1"
    drop_path.mkdir(parents=True, exist_ok=True)

    print(f"📁 Drop folder: {drop_path}")
    print(f"💡 Using GPT-4o for research (premium models enabled)\n")

    # Initialize researcher
    researcher = GeneralResearcher(verbose=True)

    # Example mission briefing (following HQ template)
    print_banner("Mission Briefing")

    mission_briefing = """
RESEARCH MISSION: What are the top 3 use cases for MLOps platforms in production environments as of 2024?

STRATEGIC CONTEXT:
User is evaluating MLOps platforms for adoption in their organization.
They need to understand current market applications to assess fit with their needs.

Decision context: Inform platform selection and implementation roadmap for Q1 2025.

Mental models:
- Use cases should be proven in production (not experimental)
- Need concrete examples from real organizations
- Looking for patterns across vendors (not vendor-specific features)

YOUR PURPOSE:
Provide evidence-based insights for platform evaluation.
User will use this to:
1. Validate their assumptions about MLOps use cases
2. Identify gaps in their current understanding
3. Present findings to engineering leadership

SUCCESS CRITERIA:
- Identify 3 concrete use cases with real-world examples
- Confidence level per use case (High/Medium/Low)
- Source citations from reputable sources (vendor docs, case studies, industry reports)
- Flag any conflicting information or uncertainty

TOKEN BUDGET:
Deliver complete findings in 2000-5000 tokens.

Prioritize:
1. Direct answer to the question (top 3 use cases)
2. Real-world examples and evidence
3. Confidence indicators
4. Source citations
5. Knowledge gaps or areas requiring deeper investigation

CONSTRAINTS:
- Focus on 2023-2024 data (flag older information explicitly)
- Prioritize: official vendor documentation, customer case studies, reputable industry sources
- Scope: Production use cases only (not academic/research applications)
- Geography: Global perspective (North America and Europe primarily)

RESEARCH APPROACH:
1. Break into sub-questions:
   - What use cases are most frequently mentioned in vendor materials?
   - What use cases appear in customer testimonials/case studies?
   - What patterns emerge across multiple sources?

2. Source evaluation:
   - High confidence: Official docs, verified case studies, industry research
   - Medium confidence: Vendor blogs, conference talks, expert opinions
   - Low confidence: Opinion pieces, unverified claims

3. Handle contradictions:
   - If sources disagree, explicitly note the contradiction
   - Assess which source is more credible and why
   - Don't hide uncertainty - flag it clearly
"""

    print(mission_briefing)
    print("\n⏳ Executing research (this takes ~3 minutes)...\n")

    # Execute research
    try:
        output = await researcher.execute_research(
            mission_briefing=mission_briefing,
            drop_path=drop_path,
            researcher_id="researcher-demo"
        )

        # Display results
        print_banner("📊 Research Results")
        print(f"✅ Research completed successfully!\n")
        print(f"📄 Token count: {output.token_count} tokens")
        print(f"📚 Sources: {len(output.sources)} sources")
        print(f"💰 Cost: ${output.cost:.2f}")
        print(f"⏱️  Runtime: {output.runtime_seconds:.1f} seconds")
        print(f"\n📁 Output saved to: {drop_path / 'researcher-demo-output.md'}")

        # Check token budget
        if output.token_count < 2000:
            print(f"\n⚠️  WARNING: Output is below 2000 token target ({output.token_count} tokens)")
            print("Consider refining mission briefing for more comprehensive coverage.")
        elif output.token_count > 5000:
            print(f"\n⚠️  WARNING: Output exceeds 5000 token target ({output.token_count} tokens)")
            print("Consider refining mission briefing to be more focused.")
        else:
            print(f"\n✅ Token budget GOOD: {output.token_count} tokens (target: 2000-5000)")

        # Preview findings
        print_banner("📝 Research Findings Preview")
        preview_length = 500  # Show first 500 chars
        preview = output.findings[:preview_length]
        print(preview)
        if len(output.findings) > preview_length:
            print("\n... (truncated, see full output in file)")

        print_banner("🎯 Next Steps")
        print("1. Read full research output:")
        print(f"   {drop_path / 'researcher-demo-output.md'}")
        print("\n2. Evaluate quality:")
        print("   - Does it answer the research question?")
        print("   - Are sources credible and properly cited?")
        print("   - Is confidence level indicated per finding?")
        print("   - Are knowledge gaps identified?")
        print("\n3. Refine mission briefing if needed:")
        print("   - Edit this script's mission_briefing variable")
        print("   - Run again to see quality improvement")
        print("\n4. When ready, proceed to Session 4: Generators")

    except Exception as e:
        print_banner("❌ Research Failed")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check OPENAI_API_KEY in .env")
        print("2. Ensure internet connection is working")
        print("3. Check OpenAI API status: https://status.openai.com/")


if __name__ == "__main__":
    asyncio.run(main())
