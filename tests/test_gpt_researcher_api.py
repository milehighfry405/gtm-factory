"""
Test gpt-researcher API to understand what parameters it accepts.

This is the foundation test - validates our understanding of the library
we're wrapping. Must pass before building higher-level abstractions.

VCR Pattern:
- First run: pytest tests/test_gpt_researcher_api.py --record-mode=once (~$0.50)
- Subsequent runs: pytest tests/test_gpt_researcher_api.py ($0)
"""

import pytest
from gpt_researcher import GPTResearcher


@pytest.mark.asyncio
@pytest.mark.vcr
@pytest.mark.expensive
async def test_minimal_query():
    """
    Test 1: Minimal working example.

    Validates: What's the simplest query that works?
    """
    researcher = GPTResearcher(
        query="What is Anthropic?",
        report_type="research_report"
    )

    await researcher.conduct_research()
    report = await researcher.write_report()
    sources = researcher.get_research_sources()

    # Validate basic functionality
    assert len(report) > 100, "Report should have content"
    assert len(sources) > 0, "Should find sources"
    assert isinstance(sources, list), "Sources should be a list"


@pytest.mark.asyncio
@pytest.mark.vcr
@pytest.mark.expensive
async def test_query_with_config():
    """
    Test 2: Query with config file.

    Validates: Can we use config file to customize behavior?
    """
    researcher = GPTResearcher(
        query="What is Warp terminal?",
        report_type="research_report",
        config_path="config/gpt_researcher.json"
    )

    await researcher.conduct_research()
    report = await researcher.write_report()
    sources = researcher.get_research_sources()

    assert len(sources) > 0, "Config should not break source retrieval"
    assert len(report) > 100, "Should generate substantial report"


@pytest.mark.asyncio
@pytest.mark.vcr
@pytest.mark.expensive
async def test_complex_question():
    """
    Test 3: Complex research question.

    Validates: Does gpt-researcher handle multi-part questions?
    """
    query = (
        "What are the observable characteristics (firmographic, technographic, "
        "behavioral) of companies that adopt AI developer tools?"
    )

    researcher = GPTResearcher(
        query=query,
        report_type="research_report"
    )

    await researcher.conduct_research()
    report = await researcher.write_report()
    sources = researcher.get_research_sources()

    assert len(sources) > 0, "Complex questions should still find sources"
    # Don't assert on quality here - just that it doesn't break


@pytest.mark.asyncio
async def test_query_length_limit():
    """
    Test 4: What's the query length limit?

    Validates: How long can the query be before it breaks?
    Non-VCR test - just initialization validation.
    """
    short_query = "What is X?"
    medium_query = "What are the key characteristics of X? " * 10  # ~400 chars
    long_query = "What are the detailed characteristics of X? " * 100  # ~4000 chars

    # All should initialize without error
    r1 = GPTResearcher(query=short_query, report_type="research_report")
    r2 = GPTResearcher(query=medium_query, report_type="research_report")
    r3 = GPTResearcher(query=long_query, report_type="research_report")

    assert r1 is not None
    assert r2 is not None
    assert r3 is not None

    # Note: This doesn't test execution, just that the library accepts long queries
    # Actual behavior with long queries will be in VCR tests


def test_api_documentation():
    """
    Test 5: Document what GPTResearcher constructor accepts.

    This test documents our understanding of the API.
    Run: pytest tests/test_gpt_researcher_api.py::test_api_documentation -v
    """
    import inspect

    sig = inspect.signature(GPTResearcher.__init__)
    params = list(sig.parameters.keys())

    print("\n" + "="*80)
    print("GPTResearcher.__init__() Parameters:")
    print("="*80)
    for param_name in params:
        if param_name == 'self':
            continue
        param = sig.parameters[param_name]
        default = param.default if param.default != inspect.Parameter.empty else "REQUIRED"
        print(f"  {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'} = {default}")
    print("="*80)

    # Assert key parameters exist
    assert 'query' in params, "Should accept 'query' parameter"
    assert 'report_type' in params, "Should accept 'report_type' parameter"

    # Document: Does it accept custom prompts/instructions?
    has_custom_prompt = any(
        name in params
        for name in ['instructions', 'context', 'system_prompt', 'briefing', 'guidance']
    )

    print(f"\nSupports custom prompts/instructions: {has_custom_prompt}")

    if not has_custom_prompt:
        print("\n⚠️  FINDING: gpt-researcher does NOT support custom instruction prompts")
        print("   We can only pass a 'query' string - no way to inject detailed guidance")
        print("   This means mission briefing transformer won't work as designed")


# Document expected behavior in docstring
"""
FINDINGS (to be updated after running tests):

1. Minimal query works: [YES/NO]
2. Config file works: [YES/NO]
3. Complex questions work: [YES/NO]
4. Query length limit: [N characters before breaking]
5. Supports custom prompts: [YES/NO]

ARCHITECTURE IMPLICATIONS:
- If custom prompts NOT supported: Must use focus_question only, OR switch to direct Anthropic API
- If query length limited: Mission briefing transformer unusable with gpt-researcher
- If config file works: Can tune via config, but not per-query customization

ACTION ITEMS:
1. Run: pytest tests/test_gpt_researcher_api.py --record-mode=once
2. Document findings in docs/guidelines/gpt-researcher-api.md
3. Make architectural decision based on facts
"""
