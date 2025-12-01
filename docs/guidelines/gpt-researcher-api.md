# GPT Researcher API Documentation
**Created**: 2025-11-20
**Purpose**: Document gpt-researcher library API for GTM Factory integration

---

## Key Finding: Context Parameter EXISTS

**Discovery**: `GPTResearcher.__init__()` accepts a `context` parameter!

This was initially missed, causing the mission briefing transformer to fail. The library DOES support custom guidance - just not as the `query` parameter.

---

## Constructor Parameters

```python
GPTResearcher(
    query: str,                    # REQUIRED - Short research question
    report_type: str = "research_report",
    report_format: str = "markdown",
    report_source: str = "web",
    tone: Tone = Tone.Objective,
    source_urls: list[str] | None = None,
    document_urls: list[str] | None = None,
    complement_source_urls: bool = False,
    query_domains: list[str] | None = None,
    documents: Any = None,
    vector_store: Any = None,
    vector_store_filter: Any = None,
    config_path: Any = None,
    websocket: Any = None,
    agent: Any = None,
    role: Any = None,
    parent_query: str = "",
    subtopics: list | None = None,
    visited_urls: set | None = None,
    verbose: bool = True,
    context: Any = None,           # ✅ SUPPORTS CUSTOM CONTEXT!
    headers: dict | None = None,
    max_subtopics: int = 5,
    log_handler: Any = None,
    prompt_family: str | None = None,
    mcp_configs: list[dict] | None = None,
    mcp_max_iterations: int | None = None,
    mcp_strategy: str | None = None,
    **kwargs
)
```

---

## Correct Usage Pattern

### ❌ WRONG (what we were doing)
```python
# Passing 10k char mission briefing as query
researcher = GPTResearcher(
    query=mission_briefing,  # Too long, causes refusal
    report_type="research_report"
)
```

### ✅ CORRECT
```python
# Short query + detailed context
researcher = GPTResearcher(
    query="What are Warp's best customer characteristics?",  # Short question
    context=mission_briefing_guidance,  # Detailed guidance here
    report_type="research_report"
)
```

---

## Architecture Implications

**Mission Briefing Transformer CAN Work**

The transformer should generate TWO outputs:
1. **Query** (short, focused question) → Goes to `query` param
2. **Context** (detailed guidance) → Goes to `context` param

**Current Split**:
- Query: HQ's `focus_question` (already short and focused)
- Context: Mission briefing guidance (ICP criteria, success criteria, format requirements)

---

## Testing Strategy

**VCR Pattern** (record-once-replay-forever):

```bash
# First run: Record cassettes (~$0.50)
pytest tests/test_gpt_researcher_*.py --record-mode=once

# Subsequent runs: Free
pytest tests/test_gpt_researcher_*.py
```

**Test Files**:
- `test_gpt_researcher_api.py` - API validation
- `test_gpt_researcher_context.py` - Context effectiveness

---

## Next Steps

1. ✅ Validate context parameter works (test_gpt_researcher_context.py)
2. Update GeneralResearcher to pass context correctly
3. Mission briefing transformer generates context string (not query)
4. Integration test full flow

---

## References

- Source: `inspect.signature(GPTResearcher.__init__)`
- Test: `tests/test_gpt_researcher_api.py::test_api_documentation`
