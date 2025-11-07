# Synthesis Patterns - Anthropic Best Practices

**Researched**: 2025-11-06
**For**: Generators module (Session 4)
**Status**: Active ✅

---

## Overview

Patterns for synthesizing multiple research outputs into coherent documents, based on Anthropic's multi-agent research system and context engineering practices. Covers iterative synthesis, contradiction detection, token budget management, and structured output generation.

---

## Key Principles

### Principle 1: Iterative Synthesis Pattern

**Source**: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

**What**: LeadResearcher collects findings from subagents, synthesizes results, and determines if more research is needed in an iterative loop.

**Why**: Loading all outputs into a single prompt wastes tokens and reduces synthesis quality. Iterative approach scales better and maintains context clarity.

**How**:
1. Collect findings from parallel subagents (3-5 at a time)
2. Synthesize current batch
3. Evaluate completeness
4. If gaps exist, trigger additional research
5. Update running synthesis incrementally

✅ **DO**:
- Process outputs in parallel (not serially)
- Maintain running synthesis that updates incrementally
- Evaluate completeness after each batch
- Return condensed summaries (1,000-2,000 tokens) from workers

❌ **DON'T**:
- Load all research outputs into single prompt
- Synthesize serially (wastes time and tokens)
- Keep full conversation history in context

**For GTM Factory Generators**:
```python
# Good: Iterative synthesis
latest_md = ""
for drop in session_drops:
    researcher_outputs = load_drop_outputs(drop)
    latest_md = synthesize_incremental(latest_md, researcher_outputs)
    save_latest(latest_md)

# Bad: Single-shot synthesis
all_outputs = load_all_drops()  # Huge token waste
latest_md = synthesize(all_outputs)
```

---

### Principle 2: Dedicated Citation Verification

**Source**: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

**What**: After synthesis, pass all findings to a specialized CitationAgent that verifies sources match claims.

**Why**: "Human evaluation catches what automation misses" - contradictions and source quality need dedicated attention.

**How**:
1. Complete initial synthesis
2. Pass synthesis + source list to CitationAgent
3. Check: Do cited sources match claims?
4. Apply corrections/invalidations
5. Return verified output

**Evaluation Rubric**:
- Citation accuracy: Do sources support claims?
- Source quality: Primary > secondary sources
- Subtle biases: Source selection patterns

✅ **DO**:
- Use dedicated agent/prompt for citation checking
- Track which claims come from which sources
- Flag contradictions between sources
- Prefer primary sources

❌ **DON'T**:
- Rely solely on synthesis agent for contradiction detection
- Mix synthesis and citation tasks in single prompt
- Skip human review for critical contradictions

**For GTM Factory Generators**:
```python
# Good: Separate synthesis from citation checking
synthesis = synthesize_findings(researcher_outputs)
verified = verify_citations(synthesis, all_sources)
contradictions = detect_conflicts(verified)
final = apply_invalidations(verified, contradictions)

# Bad: Everything in one prompt
final = synthesize_and_verify_everything(outputs)  # Too complex
```

---

### Principle 3: Token Budget Scaling

**Source**: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

**What**: Scale synthesis complexity based on task difficulty, not arbitrary limits.

**Why**: "Upgrading to Claude Sonnet 4 is larger gain than doubling token budget" - model quality > token quantity.

**Scaling Rules**:
- **Simple synthesis**: 1 agent, 3-10 tool calls
- **Direct comparisons**: 2-4 agents
- **Complex research**: 10+ agents
- **Cost awareness**: Multi-agent = 15× more tokens than single chat

**Sub-Agent Compression**:
- Each worker returns 1,000-2,000 token summaries
- Full findings stay in worker context
- Synthesis agent only sees compressed outputs

✅ **DO**:
- Start with simplest approach (1 agent)
- Scale up only when complexity requires it
- Compress worker outputs before passing to synthesizer
- Use better model (Claude Sonnet 4) over more tokens

❌ **DON'T**:
- Default to multi-agent for simple tasks
- Pass full worker findings to synthesizer
- Ignore cost implications (15× multiplier)

**For GTM Factory Generators**:
```python
# Token budget by complexity
if len(researcher_outputs) <= 3:
    # Simple: 1 synthesis call (~5K tokens input)
    synthesis = synthesize_simple(outputs)
elif len(researcher_outputs) <= 10:
    # Medium: 2 calls (synthesis + citation)
    synthesis = synthesize_medium(outputs)
    verified = verify_citations(synthesis)
else:
    # Complex: Multi-agent pattern
    batches = chunk_outputs(outputs, batch_size=5)
    summaries = [synthesize_batch(b) for b in batches]
    final = synthesize_summaries(summaries)
```

---

### Principle 4: Context Compaction

**Source**: [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**What**: Treat context as finite resource. Summarize conversation history, persist notes externally, clear redundant outputs.

**Why**: Approaching context limits degrades synthesis quality. Compaction maintains focus on high-signal tokens.

**Techniques**:
1. **Summarization**: Compress conversation history, preserve critical decisions
2. **Structured notes**: Agent writes NOTES.md persisted outside context
3. **Tool result clearing**: Remove redundant outputs after processing
4. **Sub-agent isolation**: Detailed context stays in workers, synthesis sees summaries

✅ **DO**:
- Summarize when approaching context limits
- Persist intermediate state externally (NOTES.md, latest.md)
- Clear tool results after processing
- Load data just-in-time (not pre-load everything)

❌ **DON'T**:
- Keep full conversation history in context
- Pre-load all documents
- Maintain redundant outputs in message history

**For GTM Factory Generators**:
```python
# Good: Incremental compaction
class LatestGenerator:
    def synthesize_drop(self, drop_path):
        # Load only new drop
        new_outputs = load_drop(drop_path)

        # Load existing latest.md (compacted state)
        existing = load_latest_md()

        # Synthesize incrementally
        updated = synthesize_incremental(existing, new_outputs)

        # Save compacted state
        save_latest_md(updated)

# Bad: Load everything every time
def synthesize_session(session_path):
    all_drops = load_all_drops(session_path)  # Huge context
    all_outputs = [load_drop(d) for d in all_drops]
    return synthesize(all_outputs)  # Context limit exceeded
```

---

### Principle 5: Structured Output with XML

**Source**: [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**What**: Use XML tags or Markdown headers to organize prompts into clear sections. Simple, direct language for instructions.

**Why**: Token efficiency and clarity. Model parses structure better than unformatted text.

**Structure Pattern**:
```xml
<context>
{Input data here}
</context>

<instructions>
Clear, specific task description.
Use heuristics, not rigid rules.
</instructions>

<output_format>
Expected structure (JSON, Markdown, etc.)
</output_format>
```

**Prompt Guidelines**:
- Extremely clear and simple language
- Specific enough to guide behavior
- Flexible enough for strong heuristics
- Minimal at first, add only what testing reveals as necessary

✅ **DO**:
- Use XML tags for sections
- Simple, direct instructions
- Provide output format example
- Start minimal, iterate based on testing

❌ **DON'T**:
- Wall of text without structure
- Vague instructions
- Overly rigid rules
- Bloated system prompts

**For GTM Factory Generators**:
```xml
<context>
You are synthesizing research findings from multiple researchers.

Researcher 1 findings:
{findings_1}

Researcher 2 findings:
{findings_2}
</context>

<instructions>
1. Identify common themes across researchers
2. Detect contradictions (claims that conflict)
3. Synthesize into coherent narrative
4. Apply strikethrough to invalidated claims
</instructions>

<output_format>
Return JSON:
{
  "synthesis": "# Session Title\n\n## Findings\n...",
  "contradictions": [
    {"old_claim": "...", "new_claim": "...", "source": "researcher-2"}
  ]
}
</output_format>
```

---

## Token Budgets

**Multi-agent multiplier**: 15× more tokens than single chat
**Worker compression**: Return 1,000-2,000 token summaries
**Simple synthesis**: 3-10 tool calls, ~5K input tokens
**Complex synthesis**: 10+ agents, 50K+ input tokens

**For GTM Factory**:
- 3 researcher outputs (2-5K each): ~10K input → Simple (1 call)
- 10 outputs: ~30K input → Medium (2-3 calls with batching)
- 50+ outputs: ~150K input → Complex (multi-agent with compression)

---

## Common Mistakes

1. **Loading everything upfront**: Wastes tokens, degrades quality → Use just-in-time loading
2. **Single-shot synthesis**: Doesn't scale → Use iterative synthesis with compaction
3. **Mixing synthesis and citation**: Too complex for single prompt → Use dedicated agents
4. **Ignoring cost**: Multi-agent = 15× multiplier → Scale appropriately by complexity
5. **Rigid rules over heuristics**: Reduces model flexibility → Provide guidelines, not rules

---

## Latest Updates (2025)

- **Context engineering** replaces "prompt engineering" terminology
- **Claude Sonnet 4**: Better than doubling token budget for synthesis quality
- **Multi-agent systems**: Proven pattern for complex synthesis (Anthropic's own research system)
- **Just-in-time loading**: Preferred over pre-loading all data
- **Structured note-taking**: Agents persist memory externally (NOTES.md pattern)

---

## Resources

1. [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) - Synthesis patterns, citation verification
2. [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) - Compaction, progressive disclosure
3. [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) - General agent patterns

---

**Last Updated**: 2025-11-06
**Used In**: Session 4 (Generators module)
