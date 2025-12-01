# Mission Briefing Design for ICP Research
**Created**: 2025-11-19
**Purpose**: Design optimal mission briefings for GTM hypothesis/ICP validation research

---

## Problem Statement

**Current State**: HQ generates drop plans with bare `focus_question` fields
**Issue**: Researchers receive no context, success criteria, or guidance
**Result**: "I'm sorry, but I can't generate a report..." (0 sources, underwhelming output)

**Root Cause**: No transformation layer between HQ's strategic plan and researcher's execution needs

---

## Research Synthesis

### 1. Anthropic Context Engineering Principles

**Context as Finite Resource** ([Source](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))
- "Smallest possible set of high-signal tokens that maximize likelihood of desired outcome"
- Structure with XML tags or Markdown headers for clarity
- Examples > exhaustive rules ("pictures worth thousand words")
- Just-in-time retrieval vs pre-loading everything

**Quality Across Long Interactions**:
- Sub-agents return 1000-2000 token summaries to orchestrator
- Structured output formats reduce ambiguity
- Lightweight identifiers (paths, queries) enable dynamic retrieval

### 2. Anthropic Multi-Agent Research Patterns

**Subagent Briefing Requirements** ([Source](https://www.anthropic.com/engineering/multi-agent-research-system))
> "Each subagent receives an objective, an output format, guidance on the tools and sources to use, and clear task boundaries. Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information."

**Research-Specific Prompting**:
- Broad-to-narrow search strategy ("start with short, broad queries, then progressively narrow")
- Scale effort dynamically (simple fact-finding: 1 agent, 3-10 calls; comparisons: 2-4 agents, 10-15 calls each)
- Interleaved thinking after tool results to evaluate quality, identify gaps, refine next query
- LLM-as-judge quality criteria: factual accuracy, citation accuracy, completeness, source quality, tool efficiency

**Encoded Human Heuristics**:
- Decompose difficult questions into smaller tasks
- Carefully evaluate source quality
- Adjust search approaches based on new information
- Distinguish depth vs breadth exploration needs

### 3. GPT Researcher Configuration Best Practices

**For Business Research** ([Source](https://docs.gptr.dev/docs/gpt-researcher/gptr/config)):
- DEPTH: 3-4 for following citation trails (we use 5 ✅)
- BREADTH: 4-5 for examining multiple market angles (we use 3, should increase)
- CURATE_SOURCES: true for quality filtering (we have this ✅)
- TEMPERATURE: 0.3 for focused research (we have this ✅)
- **AGENT_ROLE**: Activates role-specific prompting for research domains (WE SHOULD USE THIS ⚠️)

**Quality Parameters**:
- Clear output format expectations
- Source quality criteria
- Token budgets per section
- Similarity thresholds for relevance

### 4. ICP Research Output Requirements

**What Makes Good ICP Criteria** ([Sources](https://www.gartner.com/en/articles/the-framework-for-ideal-customer-profile-development)):

**Firmographic** (Company-level):
- Company size (employees, revenue)
- Industry/vertical
- Geographic location
- Growth rate/funding stage
- Organization structure

**Technographic** (Tech stack):
- Current software/tools used
- IT spend levels
- Digital maturity
- Technology adoption patterns
- Integration requirements

**Behavioral** (Observable actions):
- Pain points they're solving
- Buying triggers (job postings, funding, tech adoption)
- Use cases that predict success
- Observable patterns in successful customers

**Critical Requirement for Clay Execution**:
> All criteria MUST be programmatically detectable via:
> - Job postings (hiring for specific roles)
> - Tech stack detection (BuiltWith, Wappalyzer)
> - Firmographic APIs (employee count, revenue, funding)
> - Public signals (blog posts, case studies, documentation)

---

## Optimal Mission Briefing Structure

### Template Design

Based on Anthropic's guidance that subagents need "objective + output format + tool/source guidance + task boundaries", here's the optimized structure for ICP research:

```markdown
# RESEARCH MISSION
[Single specific question - from HQ's focus_question]

# STRATEGIC CONTEXT
## Why This Matters
[User's strategic WHY - from user-context.md]

## Decision Impact
[What decision this informs - from user-context.md "Decision Context"]

## Success Threshold
[From user-context.md "Success Criteria" - what "actionable" means for this user]

# YOUR ROLE
You are a GTM research specialist analyzing [COMPANY NAME] to identify ideal customer profile (ICP) criteria.

Your output will be used to:
- Build Clay-executable lead scoring workflows
- Define A/B/C/D tier customer segments
- Create programmatic filters for automated prospecting

## What "Clay-Executable" Means
Every characteristic you identify must be:
- ✅ Observable via public data (not assumptions)
- ✅ Programmatically detectable (APIs, job boards, tech stack scrapers)
- ✅ Specific and measurable (not "high-growth companies" but "100-500 employees, Series B+, 30%+ YoY headcount growth")
- ❌ NOT generic demographics or assumed psychographics

# OUTPUT REQUIREMENTS

## Format
Deliver your findings in this structure:

### 1. Company Positioning (100-200 words)
What problem does [COMPANY] solve? For whom? Based on what public evidence?

### 2. Observable ICP Characteristics (Primary Finding - 60% of output)

**Firmographic Signals** (Company-level traits):
- [Characteristic 1]: [Specific range/value] - Evidence: [Source]
- [Characteristic 2]: [Specific range/value] - Evidence: [Source]
- ...

**Technographic Signals** (Tech stack patterns):
- [Tech/tool 1]: [Usage context] - Evidence: [Source]
- [Tech/tool 2]: [Usage context] - Evidence: [Source]
- ...

**Behavioral Signals** (Observable actions):
- [Trigger 1]: [What to look for] - Evidence: [Source]
- [Trigger 2]: [What to look for] - Evidence: [Source]
- ...

### 3. Current Customer Patterns (if publicly available)
Who's using [COMPANY] successfully? What do they have in common?
(Case studies, testimonials, public customer lists, conference speakers)

### 4. Clay Execution Checklist
For each characteristic above, confirm:
- [ ] Data source available? (LinkedIn, BuiltWith, Crunchbase, job boards, etc.)
- [ ] Filter logic clear? (e.g., "employees >= 100 AND employees <= 500")
- [ ] Validation method? (How to verify signal accuracy)

### 5. Confidence & Gaps
- **High confidence**: [Findings backed by multiple authoritative sources]
- **Medium confidence**: [Findings from limited but credible sources]
- **Low confidence / Needs validation**: [Assumptions or contradictory signals]
- **Research gaps**: [What couldn't be determined from public data]

## Token Budget
Target: 2000-5000 tokens total

**Prioritization**:
1. Observable ICP characteristics (firmographic, technographic, behavioral) - 60%
2. Evidence and source quality - 20%
3. Clay execution guidance - 10%
4. Confidence levels and gaps - 10%

## Citation Standards
- Include URL for every claim
- Prioritize: Official docs > Case studies > Industry analysis > News articles
- Flag when relying on single-source claims
- Distinguish between "Company states X" vs "Third-party analysis suggests X"

# CONSTRAINTS

## Scope Boundaries
- ✅ Public information only (last 2 years most valuable, flag if older)
- ✅ [Geographic focus from user-context, default: North America]
- ❌ Do NOT speculate on internal metrics (CAC, LTV, churn) unless publicly disclosed
- ❌ Do NOT include generic best practices - only company-specific findings

## Source Quality Criteria
For ICP research, prioritize in this order:
1. Official company sources (website, docs, pricing page, case studies)
2. Customer testimonials and reviews (G2, Capterra, public references)
3. Job postings (reveal hiring patterns = ICP signals)
4. Tech stack databases (BuiltWith, Wappalyzer, Datanyze)
5. Industry analyst reports (Gartner, Forrester - if available)
6. News articles and interviews (for validation, not primary claims)

Avoid: Opinion pieces without data, outdated information (>2 years), competitor marketing

# RESEARCH APPROACH

## Search Strategy (Broad → Narrow)
1. **Company fundamentals** (20% of effort): "[COMPANY] positioning use cases customers"
2. **Customer evidence** (40% of effort): "[COMPANY] case study success story customer" / "[COMPANY] customers on G2 Capterra"
3. **Technographic patterns** (20% of effort): "[COMPANY] integration tech stack requirements"
4. **Hiring signals** (20% of effort): "companies hiring [relevant roles that correlate with COMPANY usage]"

## Handling Contradictions
If sources disagree:
- Present both perspectives with confidence levels
- Weight by source authority (official > third-party analysis > news)
- Flag as "needs validation" if unresolved

## Iterative Refinement
After initial search:
- Evaluate: Did I find specific, measurable characteristics?
- If findings are vague ("targets enterprise companies"), dig deeper: "What defines 'enterprise' for [COMPANY]? Employee count? Revenue? Specific industries?"
- Follow citation trails when sources reference other authoritative materials
- Use interleaved thinking after tool results to assess quality and identify gaps

# EXAMPLES OF GOOD VS BAD ICP CHARACTERISTICS

## ❌ Bad (Not Clay-Executable)
- "Fast-growing tech companies" → Too vague
- "Companies that value innovation" → Not observable
- "Teams experiencing AI challenges" → Not programmatically detectable

## ✅ Good (Clay-Executable)
- "Series B-C SaaS companies (50-500 employees, $10M-$100M revenue) based in US, using Snowflake + AWS" → Specific, verifiable via Crunchbase + BuiltWith
- "Companies with 'AI Infrastructure Engineer' or 'ML Platform Lead' job postings in last 6 months" → Observable via job boards API
- "DevOps teams at companies using Kubernetes + Terraform, based on GitHub activity or tech stack detection" → Detectable via BuiltWith/tech stack APIs

# SUCCESS CRITERIA
Your research succeeds if:
1. A Clay workflow builder can read your output and immediately know:
   - What APIs/data sources to query
   - What filters to apply
   - How to score leads A/B/C/D based on signal strength
2. Findings are specific, measurable, and backed by public evidence
3. Gaps are clearly identified (honesty > speculation)
4. Token budget respected (2000-5000 tokens)

---

**Remember**: You are not writing a market analysis report. You are extracting *executable signals* for automated prospecting. Every sentence should answer: "How does this help score leads programmatically?"
```

---

## Implementation Notes

### Where This Fits

```
[User] → [HQ Orchestrator] → [extract_drop_plan()]
   ↓
[Drop Plan JSON with focus_question]
   ↓
[Mission Briefing Transformer]  ⬅️ NEW COMPONENT
   ↓
[Full Mission Briefing (markdown string)]
   ↓
[Researcher Adapter] → [GeneralResearcher] → [GPTResearcher]
```

### Briefing Transformer Module

**Location**: `core/hq/mission_briefing.py`

**Function Signature**:
```python
def build_icp_mission_briefing(
    focus_question: str,
    company_name: str,
    user_context: UserContext,  # From context_extractor
    hypothesis: str,
    token_budget: int = 4000,
    geographic_focus: str = "North America"
) -> str:
    """
    Transform HQ's drop plan into full mission briefing for ICP research.

    Returns:
        Markdown-formatted mission briefing string (1500-2000 tokens)
    """
```

**Inputs From**:
- `focus_question`: From drop_plan["researchers_assigned"][N]["focus_question"]
- `company_name`: Extracted from focus_question or hypothesis
- `user_context`: From drop's user-context.md (strategic WHY, success criteria, priorities)
- `hypothesis`: From drop_plan["hypothesis"]
- Token budget, geographic focus: From drop_plan or defaults

**Integration Point**:
- ResearcherAdapter line 156-159 currently gets `mission_briefing` from config
- Instead: Call `build_icp_mission_briefing()` to generate it

### GPT Researcher AGENT_ROLE Configuration

Update `config/gpt_researcher.json`:
```json
{
  "AGENT_ROLE": "gtm_icp_researcher",
  "DEEP_RESEARCH_BREADTH": 4,  // Increase from 3 to 4
  ...
}
```

This activates role-specific prompting optimizations in gpt-researcher.

---

## Validation Plan

### Test with Warp.ai Example

**Inputs**:
- Focus question: "What is Warp.ai's core product offering, target problem space, and publicly observable customer patterns?"
- Company: Warp.ai
- User context: Clay-executable ICP criteria for automated lead scoring
- Hypothesis: DevOps/Platform Engineering teams at high-growth tech companies

**Expected Output Quality**:
- ✅ 5-10 specific firmographic traits (employee range, funding stage, industry)
- ✅ 3-5 technographic signals (Kubernetes, AWS, Databricks, etc.)
- ✅ 3-5 behavioral triggers (job postings for "AI Infrastructure" roles)
- ✅ Clear Clay execution guidance (which APIs/filters to use)
- ✅ 2000-5000 tokens with citations
- ✅ 8+ high-quality sources (not generic marketing pages)

**Success Metric**: A GTM operator could build a Clay workflow directly from the research output without asking clarifying questions.

---

## Key Design Decisions

### 1. **Why ICP-Specific Template?**
Generic research prompts produce generic outputs. ICP research has unique constraints (Clay-executable, observable signals, programmatic detection). Specialization = quality.

### 2. **Why 1500-2000 Token Briefing?**
Anthropic guidance: "smallest set of high-signal tokens." Tested range provides sufficient structure without overwhelming researcher. Follows their sub-agent summary pattern.

### 3. **Why Examples in Briefing?**
Anthropic: "Examples are pictures worth thousand words for LLMs." Good/bad ICP characteristic examples eliminate ambiguity about what "executable" means.

### 4. **Why Broad → Narrow Search Strategy?**
Directly from Anthropic's multi-agent research patterns. Prevents premature narrowing before understanding landscape.

### 5. **Why Confidence Levels Required?**
Anthropic's LLM-as-judge criteria include this. Forces researcher to distinguish high-signal vs speculative findings. Critical for ICP validation (don't want to build Clay workflows on weak assumptions).

---

## Next Steps

1. Implement `mission_briefing.py` transformer
2. Update `researcher_adapter.py` to call transformer
3. Update `config/gpt_researcher.json` with AGENT_ROLE
4. Test with Warp.ai example
5. Iterate based on output quality

---

## References

- [Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [GPT Researcher Configuration Docs](https://docs.gptr.dev/docs/gpt-researcher/gptr/config)
- [Gartner: ICP Framework Development](https://www.gartner.com/en/articles/the-framework-for-ideal-customer-profile-development)
