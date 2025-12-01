"""
Test if gpt-researcher's 'context' parameter improves research quality.

Discovery: GPTResearcher.__init__() accepts a 'context' parameter!
This test validates whether passing detailed context helps.
"""

import pytest
from gpt_researcher import GPTResearcher


@pytest.mark.asyncio
@pytest.mark.vcr
@pytest.mark.expensive
async def test_with_vs_without_context():
    """
    Compare research quality: query-only vs query+context.

    Hypothesis: Providing context improves relevance and specificity.
    """

    query = "What are the characteristics of Warp terminal's best customers?"

    # Test 1: Query only (no context)
    print("\n=== TEST 1: Query Only ===")
    researcher_no_context = GPTResearcher(
        query=query,
        report_type="research_report",
        verbose=False
    )

    await researcher_no_context.conduct_research()
    report_no_context = await researcher_no_context.write_report()
    sources_no_context = researcher_no_context.get_research_sources()

    print(f"Sources: {len(sources_no_context)}")
    print(f"Report length: {len(report_no_context)} chars")

    # Test 2: Query with context
    print("\n=== TEST 2: Query + Context ===")

    context_string = """
You are researching to build Clay-executable ICP criteria.

Focus on OBSERVABLE characteristics:
- Firmographic: Company size, funding stage, industry
- Technographic: Tech stack, tools used
- Behavioral: Job postings, hiring patterns

Output must be specific and measurable (not "fast-growing companies" but "50-500 employees, Series B+").
Prioritize publicly verifiable data sources.
"""

    researcher_with_context = GPTResearcher(
        query=query,
        report_type="research_report",
        context=context_string,  # Provide guidance
        verbose=False
    )

    await researcher_with_context.conduct_research()
    report_with_context = await researcher_with_context.write_report()
    sources_with_context = researcher_with_context.get_research_sources()

    print(f"Sources: {len(sources_with_context)}")
    print(f"Report length: {len(report_with_context)} chars")

    # Validate both work
    assert len(sources_no_context) > 0, "Query-only should find sources"
    assert len(sources_with_context) > 0, "Query+context should find sources"

    # Document findings
    print("\n=== COMPARISON ===")
    print(f"Sources - No context: {len(sources_no_context)}, With context: {len(sources_with_context)}")
    print(f"Report - No context: {len(report_no_context)} chars, With context: {len(report_with_context)} chars")

    # Save reports for manual quality comparison
    import os
    os.makedirs("tests/output", exist_ok=True)

    with open("tests/output/report_no_context.md", "w", encoding="utf-8") as f:
        f.write(f"# Report (No Context)\n\nQuery: {query}\n\n{report_no_context}")

    with open("tests/output/report_with_context.md", "w", encoding="utf-8") as f:
        f.write(f"# Report (With Context)\n\nQuery: {query}\nContext: {context_string}\n\n{report_with_context}")

    print("\nReports saved to tests/output/ for manual comparison")
