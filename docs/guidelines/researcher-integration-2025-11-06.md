# Researcher Integration Guide

**Date**: 2025-11-06
**Status**: Active - foundation for Session 3 implementation

---

## Decision: Use gpt-researcher as Foundation

**Rationale:**
- Built-in web search, scraping, source tracking
- Configurable output via prompts
- Cost-effective ($0.10/research task, 3min runtime)
- Already in dependencies
- Quality controlled via prompt engineering (not code)

**User Confirmation:** "i think we can manage all of this with good prompts"

---

## Architecture

### The Integration Pattern

```
HQ Orchestrator (Anthropic Claude)
    ↓
    [Crafts mission briefing with full context]
    ↓
Researcher Wrapper (Python)
    ↓
    [Passes briefing to gpt-researcher]
    ↓
gpt-researcher (OpenAI GPT-4o)
    ↓
    [Executes research, returns findings]
    ↓
Researcher Wrapper (Python)
    ↓
    [Validates, saves to drop folder]
```

### Key Insight: The Query Parameter IS the Mission Briefing

**Not this:**
```python
researcher = GPTResearcher(query="competitor messaging for SaaS security")
```

**But this:**
```python
mission_briefing = f"""
RESEARCH MISSION: Analyze competitor messaging strategies for SaaS security startups

STRATEGIC CONTEXT:
{user_context.strategic_why}
User is repositioning their product and needs to find gaps in competitor messaging
to exploit for differentiation.

YOUR PURPOSE:
This research will inform positioning decisions for Q1 2025 product launch.
User needs actionable insights, not just data collection.

SUCCESS CRITERIA:
- Identify 3-5 specific messaging gaps competitors aren't addressing
- Assess confidence level for each gap (High/Medium/Low)
- Provide examples with source citations
- Flag any contradictory positioning strategies

TOKEN BUDGET:
Deliver complete findings in 2000-5000 tokens. Structure for clarity:
1. Executive summary (3-5 sentences)
2. Key findings by theme
3. Supporting evidence with citations
4. Confidence indicators per finding
5. Knowledge gaps requiring deeper investigation

CONSTRAINTS:
- Focus on SaaS security startups founded in last 3 years
- Prioritize: company websites, product pages, recent funding announcements
- Geographic focus: North America and Europe
- Flag any information >2 years old as potentially outdated

RESEARCH APPROACH:
Break this into 3-5 sub-questions, research systematically, evaluate source
credibility, identify patterns across sources, note gaps where information is incomplete.
"""

researcher = GPTResearcher(
    query=mission_briefing,
    report_type="custom_report",
    tone="formal and objective"
)
```

---

## gpt-researcher Configuration

### Required Environment Variables (.env)

```bash
# Already have these
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here

# Optional (gpt-researcher defaults)
TAVILY_API_KEY=your-key-here  # Free tier: 1000 requests/month, then $0.002/request
```

### Key Parameters

**Programmatic:**
```python
GPTResearcher(
    query="[mission briefing]",
    report_type="custom_report",  # Enables custom instructions
    tone="formal and objective",
    max_subtopics=3,              # Control breadth
    verbose=True                  # Debug mode
)
```

**Configuration (via .env or code):**
```python
SMART_TOKEN_LIMIT=4000      # Max tokens for report generation
TOTAL_WORDS=1500            # Word count target (soft limit)
MAX_SUBTOPICS=3             # How many angles to research
CURATE_SOURCES=True         # Extra LLM pass for source validation
```

---

## HQ's Responsibility: World-Class Mission Briefings

### What HQ Must Understand About Researchers

**Capabilities:**
- Can search web sources (Tavily, DuckDuckGo, Bing, Google)
- Can process local documents (PDF, text, CSV, Excel, Markdown, etc.)
- Generates 3-5 sub-questions from main query
- Evaluates source credibility automatically
- Tracks citations throughout research
- Produces structured markdown reports
- Default: ~1200 words, configurable to 2K+

**Limitations:**
- Uses OpenAI models (GPT-4o-mini for summaries, GPT-4o for report)
- ~3 minute runtime per research task
- Token budget is "soft" (prompt-guided, not hard cutoff)
- Quality depends entirely on mission briefing clarity
- Cannot reason about user's strategic context unless told explicitly

**Cost Structure:**
- ~$0.10 per research task (OpenAI API calls)
- Tavily search: free tier 1000 requests/month, then $0.002/request
- Total cost scales with number of researchers per drop

### Mission Briefing Template

**HQ should craft briefings with this structure:**

```markdown
RESEARCH MISSION: [Specific, focused question]

STRATEGIC CONTEXT:
[Why user cares - from user-context.md]
[What decision this informs]
[User's mental models and assumptions]

YOUR PURPOSE:
[What user will do with this answer]
[How this fits into larger research campaign]

SUCCESS CRITERIA:
[What "good" looks like for this specific research]
[Format/structure requirements]
[Confidence threshold needed]

TOKEN BUDGET:
Deliver complete findings in 2000-5000 tokens.
Prioritize: [ranked list of what matters most]

CONSTRAINTS:
- Timeframe: [e.g., focus on last 2 years]
- Geography: [e.g., North America only]
- Source types: [e.g., prioritize official docs, research papers]
- Scope boundaries: [what NOT to research]

RESEARCH APPROACH:
[Specific guidance on how to break down the question]
[Source evaluation criteria for this domain]
[How to handle contradictory information]
```

### How HQ Decides: 1 vs 2 vs 3 vs 4 Researchers

**HQ must assess:**
1. **Complexity**: Multiple domains/disciplines involved?
2. **Breadth vs Depth**: Need wide survey or deep dive?
3. **Contradictory info**: Likely to find conflicting sources?
4. **User's decision context**: How thorough does this need to be?

**Decision Matrix:**

**1 Researcher:**
- Single, focused question
- Narrow domain
- User needs directional answer, not comprehensive analysis

**2 Researchers:**
- Question has two distinct angles (e.g., "technical capabilities" + "market positioning")
- Divide and conquer more efficient than single deep dive
- User needs breadth across related topics

**3 Researchers:**
- Complex question spanning multiple domains
- Triangulation needed (validate findings across sources)
- User making high-stakes decision requiring confidence

**4 Researchers:**
- Maximum complexity/breadth
- Multiple contradictory perspectives need reconciliation
- User building comprehensive knowledge base for long-term strategy

**Anti-pattern:** Don't assign multiple researchers to identical questions hoping for better results. Each researcher should have a **distinct sub-question or angle**.

---

## Researcher Wrapper Implementation

### File: `/core/researcher/general_researcher.py`

**Responsibilities:**
1. Accept mission briefing from HQ
2. Configure gpt-researcher
3. Execute research (async)
4. Validate output (token count, structure)
5. Save to drop folder
6. Return research metadata

**Key Methods:**
```python
class GeneralResearcher:
    async def execute_research(
        self,
        mission_briefing: str,
        drop_path: Path,
        researcher_id: str
    ) -> ResearchOutput:
        """
        Execute single research task.

        Args:
            mission_briefing: Full context from HQ
            drop_path: Where to save output
            researcher_id: Identifier for this researcher (e.g., "researcher-1")

        Returns:
            ResearchOutput with findings, sources, token_count, cost
        """
```

**No tools.py needed** - gpt-researcher handles search/scraping.

---

## Integration Points

### HQ → Researcher Handoff

**HQ saves:**
- `user-context.md` - Strategic WHY
- `conversation-history.md` - Full chat transcript
- Drop plan (embedded in conversation or extracted)

**Researcher loads:**
- User context (to build mission briefing)
- Drop plan (how many researchers, their questions)

**Researcher saves:**
- `researcher-1-output.md` - Research findings
- `researcher-2-output.md` - (if multiple)
- Updates drop metadata

### Output Validation

**After gpt-researcher returns report:**
1. Count tokens (use tiktoken library)
2. If > 5000 tokens: log warning, consider re-prompting with stricter budget
3. If < 2000 tokens: validate completeness (did it actually answer the question?)
4. Verify markdown structure is valid
5. Confirm sources are cited

**Don't truncate** - if output is wrong length, issue is with mission briefing quality.

---

## Testing Strategy

**Isolation Tests (`test_researcher.py`):**
- Can execute research task with mock mission briefing
- Respects token budget (validate output < 5000 tokens)
- Handles network failures gracefully
- Saves outputs to correct location
- Returns valid research metadata

**Integration Tests (`test_hq_researcher.py`):**
- HQ drop plan → Researcher execution (full handoff)
- User context available to researcher (loads correctly)
- Research outputs save to correct drop folder structure
- Multiple researchers can run in parallel
- Complete HQ → Researcher workflow end-to-end

**Critical Paths:**
- Mission briefing quality → research quality (manual validation)
- Token budget respected (automated check)
- Source citations present (automated check)
- Drop folder structure consistent (automated check)

---

## Session 3 Deliverables

**Files to Build:**
- `/core/researcher/general_researcher.py` - Wrapper around gpt-researcher
- `/core/researcher/__init__.py` - Package initialization
- `/tests/test_researcher.py` - Isolation tests
- `/tests/test_hq_researcher.py` - Integration tests
- `demo_researcher.py` - Manual testing script

**Files to Update:**
- `/prompts/hq-orchestrator.md` - Add researcher capability knowledge
- `/prompts/general-researcher.md` - Refine based on gpt-researcher integration
- `pyproject.toml` - Add tiktoken for token counting
- `CLAUDE.md` - Mark Session 3 complete

**NOT Building:**
- ❌ tools.py (gpt-researcher has tools)
- ❌ Custom search infrastructure
- ❌ Source validation logic (gpt-researcher handles)

---

## Success Criteria

**Session 3 is complete when:**
- ✅ Can execute single research task via wrapper
- ✅ Token budget respected (2-5K output validated)
- ✅ HQ → Researcher handoff works (integration test passes)
- ✅ Multiple researchers can execute in parallel
- ✅ Drop folder structure matches design
- ✅ Demo script allows manual validation
- ✅ Quality is driven by HQ's mission briefing (not code)

**Quality Bar:**
- Mission briefings are specific, contextual, actionable
- Research outputs directly answer the question
- Source citations are present and credible
- Token budget is respected without truncation
- HQ understands researcher capabilities deeply

---

**Last Updated**: 2025-11-06
**Status**: Ready for Session 3 implementation
