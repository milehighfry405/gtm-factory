"""
Mission Briefing Transformer - Converts HQ's strategic plan into execution-ready research briefings.

This module transforms HQ's high-level drop plans (focus_question + context) into detailed
mission briefings optimized for gpt-researcher execution. Follows Anthropic's multi-agent
research pattern where the orchestrator creates plans and a transformer formats them for
execution by specialized subagents.

Key Principle (Anthropic):
"Each subagent receives an objective, an output format, guidance on the tools and sources
to use, and clear task boundaries. Without detailed task descriptions, agents duplicate work,
leave gaps, or fail to find necessary information."

Architecture:
    [HQ Drop Plan] → [Mission Briefing Transformer] → [Full Briefing] → [Researcher]
"""

from typing import Optional
from dataclasses import dataclass
from core.hq.context_extractor import UserContext


def build_mission_briefing(
    focus_question: str,
    user_context: UserContext,
    research_mode: str,
    hypothesis: str,
    company_name: Optional[str] = None,
    token_budget: int = 4000,
    geographic_focus: str = "North America"
) -> str:
    """
    Transform HQ's strategic plan into execution-ready mission briefing.

    Args:
        focus_question: Specific research question from HQ's drop plan
        user_context: Extracted strategic WHY, priorities, mental models
        research_mode: Type of research (icp-validation, competitive-intel, general)
        hypothesis: Overall hypothesis being tested
        company_name: Target company name (extracted from question if not provided)
        token_budget: Target output length (2000-5000 tokens recommended)
        geographic_focus: Geographic scope for research

    Returns:
        Complete mission briefing string (markdown formatted, 1500-2000 tokens)

    Example:
        >>> briefing = build_mission_briefing(
        ...     focus_question="What is Warp.ai's core product offering?",
        ...     user_context=context,
        ...     research_mode="icp-validation",
        ...     hypothesis="Warp.ai targets DevOps teams",
        ...     company_name="Warp.ai"
        ... )
    """
    # Extract company name from question if not provided
    if not company_name:
        company_name = _extract_company_name(focus_question, hypothesis)

    # Build base briefing (context, mission, constraints)
    base_briefing = _build_base_briefing(
        focus_question=focus_question,
        user_context=user_context,
        hypothesis=hypothesis,
        company_name=company_name,
        token_budget=token_budget,
        geographic_focus=geographic_focus
    )

    # Add mode-specific guidance
    mode_guidance = _get_mode_guidance(research_mode, company_name)

    return base_briefing + "\n\n" + mode_guidance


def _extract_company_name(focus_question: str, hypothesis: str) -> str:
    """
    Extract company name from focus question or hypothesis.

    Simple heuristic: Look for capitalized words or domain patterns.
    Falls back to "the target company" if extraction fails.
    """
    # Try to find company name in question (e.g., "What is Warp.ai's...")
    words = focus_question.split()
    for word in words:
        # Look for possessive form (Company's) or capitalized words
        if word.endswith("'s") or word.endswith(".ai") or word.endswith(".io"):
            return word.replace("'s", "").strip()

    # Fallback: Try hypothesis
    if hypothesis:
        words = hypothesis.split()
        for word in words:
            if word[0].isupper() and len(word) > 3 and not word in ["The", "A", "An", "This", "That"]:
                return word.strip()

    return "the target company"


def _build_base_briefing(
    focus_question: str,
    user_context: UserContext,
    hypothesis: str,
    company_name: str,
    token_budget: int,
    geographic_focus: str
) -> str:
    """
    Build base briefing components (always included regardless of mode).

    Structure:
    1. Research Mission (the specific question)
    2. Strategic Context (why this matters, decision impact)
    3. Token Budget & Prioritization
    4. Constraints (scope, sources, geography)
    5. Research Approach (broad→narrow strategy from Anthropic)
    """
    return f"""# RESEARCH MISSION
{focus_question}

# STRATEGIC CONTEXT

## Why This Matters
{user_context.strategic_why}

## Decision Impact
{user_context.decision_context}

## Success Threshold
{user_context.success_criteria}

## User's Mental Models
{_format_mental_models(user_context.mental_models)}

## User's Priorities
{_format_priorities(user_context.priorities)}

# HYPOTHESIS BEING TESTED
{hypothesis}

# TOKEN BUDGET
**Target**: {token_budget} tokens (2000-5000 range)

**Prioritization Guidance**:
1. **Direct answer to research mission** (50% of output)
2. **Evidence and source citations** (25% of output)
3. **Confidence levels and gaps** (15% of output)
4. **Additional context** (10% of output)

Focus on quality over completeness. Better to deeply answer the core question than superficially cover everything.

# CONSTRAINTS

## Scope Boundaries
- **Geography**: Focus on {geographic_focus} unless question explicitly requires global perspective
- **Timeframe**: Prioritize information from last 2 years; flag if relying on older sources
- **Public information only**: Do NOT speculate on internal metrics, private strategies, or unverified claims

## Source Quality Standards
Prioritize sources in this order:
1. **Official sources**: Company website, documentation, pricing pages, official blog posts
2. **Customer evidence**: Case studies, testimonials, reviews (G2, Capterra), public references
3. **Market analysis**: Industry analyst reports (Gartner, Forrester), credible tech journalism
4. **Secondary sources**: News articles, interviews (use for validation, not primary claims)

**Avoid**: Opinion pieces without data, outdated information (>2 years), competitor marketing, unverified rumors

## Citation Requirements
- Include URL for every factual claim
- Distinguish between "Company states X" vs "Third-party analysis suggests X"
- Flag single-source claims (mark as "needs validation")
- If sources contradict, present both perspectives with confidence levels

# RESEARCH APPROACH

## Search Strategy: Broad → Narrow
(From Anthropic's multi-agent research patterns)

**Phase 1 - Landscape** (20% of effort):
- Start with broad queries to understand the domain
- Example: "{company_name} product overview use cases"
- Goal: Establish baseline understanding before diving deep

**Phase 2 - Targeted Investigation** (60% of effort):
- Focus queries on specific aspects of your research question
- Follow citation trails when sources reference authoritative materials
- Adjust search based on what Phase 1 revealed

**Phase 3 - Validation** (20% of effort):
- Cross-reference key findings across multiple sources
- Check for contradictions or gaps
- Confirm recency of information

## Handling Contradictions
When sources disagree:
- Present both perspectives
- Weight by source authority (official > analyst > news)
- Assign confidence levels: High (multiple authoritative sources), Medium (limited sources), Low (single source or contradictory)
- Flag as "needs validation" if unresolved

## Iterative Refinement
After each search iteration:
1. **Evaluate**: Am I answering the core question specifically?
2. **Identify gaps**: What's still unclear or missing?
3. **Refine queries**: Dig deeper into areas that matter most for the research mission
4. **Check token budget**: Am I prioritizing the right information?

Use your thinking/reasoning capabilities to assess search quality and plan next steps.

# OUTPUT FORMAT

Structure your findings clearly:

## [Section 1]: Direct Answer
[Answer the research mission question directly and specifically]

## [Section 2]: Supporting Evidence
[Key findings with citations, organized by theme or pattern]

## [Section 3]: Confidence & Gaps
- **High Confidence**: [Findings backed by multiple authoritative sources]
- **Medium Confidence**: [Findings from limited but credible sources]
- **Low Confidence**: [Single-source claims or contradictory signals]
- **Research Gaps**: [What couldn't be determined from available public information]

## [Section 4]: Sources
[Comprehensive list of sources cited, with URLs and brief descriptions]
"""


def _format_mental_models(mental_models: list) -> str:
    """Format mental models as bullet list."""
    if not mental_models:
        return "- (None specified)"
    return "\n".join(f"- {model}" for model in mental_models)


def _format_priorities(priorities: dict) -> str:
    """Format priorities (must-have vs nice-to-have)."""
    output = []

    if priorities.get("must_have"):
        output.append("**Must Have**:")
        output.extend(f"- {item}" for item in priorities["must_have"])

    if priorities.get("nice_to_have"):
        output.append("\n**Nice to Have**:")
        output.extend(f"- {item}" for item in priorities["nice_to_have"])

    return "\n".join(output) if output else "- (None specified)"


def _get_mode_guidance(research_mode: str, company_name: str) -> str:
    """
    Get mode-specific guidance template.

    Modes:
    - icp-validation: Focus on Clay-executable ICP criteria
    - general: Flexible analysis without domain assumptions
    """
    if research_mode == "icp-validation":
        return _get_icp_validation_template(company_name)
    else:
        return _get_general_research_template(company_name)


def _get_icp_validation_template(company_name: str) -> str:
    """
    ICP Validation mode - specialized for extracting Clay-executable customer profile criteria.

    Focus: Observable, programmatically-detectable characteristics (firmographic, technographic, behavioral).
    """
    return f"""# MODE-SPECIFIC GUIDANCE: ICP VALIDATION

## Your Specialized Role
You are a **GTM research specialist** analyzing {company_name} to identify **Ideal Customer Profile (ICP) criteria**.

Your output will be used to:
- Build **Clay-executable lead scoring workflows**
- Define **A/B/C/D tier customer segments** based on fit signals
- Create **programmatic filters** for automated prospecting

## What "Clay-Executable" Means

Every ICP characteristic you identify MUST be:

✅ **Observable** via public data (not assumptions about "mindset" or "culture")
✅ **Programmatically detectable** via APIs, databases, or scrapers
✅ **Specific and measurable** (not "high-growth companies" but "100-500 employees, Series B+, 30%+ YoY headcount growth")

❌ **NOT** generic demographics or unverifiable psychographics

## Required ICP Characteristic Types

Your findings MUST categorize signals into these three types:

### 1. Firmographic Signals (Company-Level Traits)
Observable via: Crunchbase, LinkedIn, company websites, financial disclosures

Examples:
- Company size: "100-500 employees"
- Revenue: "$10M-$100M ARR"
- Industry: "B2B SaaS, Fintech, or E-commerce"
- Funding stage: "Series B or C"
- Growth rate: "30%+ YoY headcount growth"
- Geographic location: "Headquarters in US or UK"

### 2. Technographic Signals (Tech Stack Patterns)
Observable via: BuiltWith, Wappalyzer, Datanyze, GitHub, job postings

Examples:
- Infrastructure: "Using AWS or GCP (not Azure)"
- Data stack: "Snowflake + Databricks deployment"
- Tools: "Kubernetes, Terraform, or similar IaC tools"
- Integrations: "Salesforce + HubSpot stack"

### 3. Behavioral Signals (Observable Actions)
Observable via: Job boards, blog posts, conference speakers, funding announcements

Examples:
- Hiring patterns: "Posted 'AI Infrastructure Engineer' or 'ML Platform Lead' job in last 6 months"
- Content signals: "Published blog posts about scaling ML infrastructure"
- Event participation: "Spoke at KubeCon, AWS re:Invent, or similar conferences"
- Funding triggers: "Raised Series B+ in last 12 months"

## ICP-Specific Output Structure

Organize your findings like this:

### 1. Company Positioning (100-200 words)
What problem does {company_name} solve? For whom? Based on what public evidence?
(Official messaging, case studies, product documentation)

### 2. Observable ICP Characteristics (PRIMARY FINDING - 60% of output)

#### Firmographic Signals
- [Signal 1]: [Specific range/value] → **Data source**: [API/database available]
  - Evidence: [URL citation]
- [Signal 2]: [Specific range/value] → **Data source**: [API/database available]
  - Evidence: [URL citation]
(Continue for all firmographic patterns found)

#### Technographic Signals
- [Tech/Tool 1]: [Usage context] → **Data source**: [BuiltWith/Wappalyzer/etc.]
  - Evidence: [URL citation]
- [Tech/Tool 2]: [Usage context] → **Data source**: [BuiltWith/Wappalyzer/etc.]
  - Evidence: [URL citation]
(Continue for all tech stack patterns found)

#### Behavioral Signals
- [Trigger 1]: [What to look for] → **Data source**: [Job boards/events/etc.]
  - Evidence: [URL citation]
- [Trigger 2]: [What to look for] → **Data source**: [Job boards/events/etc.]
  - Evidence: [URL citation]
(Continue for all behavioral patterns found)

### 3. Current Customer Patterns (if publicly available)
Who's using {company_name} successfully? What characteristics do they have in common?
(Analyze case studies, testimonials, public customer lists, G2/Capterra reviews, conference speakers)

### 4. Clay Execution Checklist
For the ICP characteristics above, provide:

**Data Sources Available**:
- Firmographic: [Crunchbase API, LinkedIn Sales Navigator, etc.]
- Technographic: [BuiltWith, Wappalyzer, Datanyze, etc.]
- Behavioral: [LinkedIn Jobs API, AngelList, etc.]

**Sample Filter Logic**:
```
Example: "Company in B2B SaaS industry
         AND employees >= 100 AND employees <= 500
         AND funding_stage IN ['Series B', 'Series C']
         AND tech_stack CONTAINS ['Kubernetes', 'AWS']
         AND job_posting_keywords CONTAINS ['AI Infrastructure', 'ML Platform']"
```

**Confidence in Execution**:
- High: [Characteristics with clear API access and validation methods]
- Medium: [Characteristics requiring manual validation or proxy signals]
- Low: [Characteristics difficult to detect programmatically]

### 5. Confidence & Gaps (15% of output)
- **High Confidence** (multiple authoritative sources): [List findings]
- **Medium Confidence** (limited sources): [List findings]
- **Needs Validation** (assumptions or contradictory signals): [List findings]
- **Research Gaps**: [What couldn't be determined from public data - be honest]

## Examples: Good vs Bad ICP Characteristics

### ❌ BAD (Not Clay-Executable)
- "Fast-growing tech companies" → Too vague, not measurable
- "Companies that value innovation" → Not observable, subjective
- "Teams experiencing AI challenges" → Not programmatically detectable
- "Culture-fit customers" → Impossible to verify via public data

### ✅ GOOD (Clay-Executable)
- "Series B-C SaaS companies, 50-500 employees, $10M-$100M revenue, US-based, using Snowflake + AWS"
  → Specific, verifiable via Crunchbase + BuiltWith

- "Companies with 'AI Infrastructure Engineer' OR 'ML Platform Lead' job postings in last 6 months"
  → Observable via LinkedIn Jobs API or similar

- "DevOps teams at companies using Kubernetes + Terraform (detectable via BuiltWith or GitHub activity)"
  → Detectable via tech stack APIs

- "B2B SaaS companies that raised $20M+ in last 18 months AND are hiring for data engineering roles"
  → Verifiable via Crunchbase API + job board APIs

## Critical Success Criteria for ICP Research

Your research succeeds if a **Clay workflow builder** can:
1. Read your output and immediately identify:
   - Which APIs/data sources to query
   - What filters to apply (boolean logic)
   - How to score leads A/B/C/D based on signal strength
2. Build a working lead scoring system **without asking clarifying questions**
3. Trust the confidence levels you've assigned

Remember: You are NOT writing a market analysis report. You are extracting **executable signals for automated prospecting**. Every sentence should answer: "How does this help score leads programmatically?"
"""


def _get_general_research_template(company_name: str) -> str:
    """
    General Research mode - flexible analysis without domain-specific assumptions.

    Use when research doesn't fit specialized modes (ICP, competitive intel, etc).
    """
    return f"""# MODE-SPECIFIC GUIDANCE: GENERAL RESEARCH

## Your Role
You are a **research specialist** conducting analysis on {company_name} to answer the research mission.

Your output should:
- Directly answer the research question with supporting evidence
- Provide comprehensive analysis appropriate to the question scope
- Cite authoritative sources for all factual claims
- Identify knowledge gaps and areas requiring validation

## Research Approach

**Be Comprehensive Yet Focused**:
- Cover all aspects relevant to answering the research mission
- Don't drift into tangential topics unless they directly support the answer
- Depth over breadth where it matters most

**Evidence-Based Analysis**:
- Every claim should be backed by a credible source
- Distinguish between facts, informed analysis, and speculation
- Present multiple perspectives when sources disagree

**Intellectual Honesty**:
- Clearly identify what you cannot determine from available information
- Don't fill gaps with assumptions - flag them explicitly
- Assign confidence levels based on source quality and agreement

## Success Criteria

Your research succeeds if:
1. The user can **make a decision** based on your findings
2. **Every major claim** is backed by a credible, cited source
3. **Gaps and uncertainties** are explicitly identified
4. The analysis is **proportional to the question** (don't over/under-deliver)

Remember: Your goal is to provide **actionable intelligence**, not exhaustive documentation. Focus on what matters most for answering the research mission.
"""
