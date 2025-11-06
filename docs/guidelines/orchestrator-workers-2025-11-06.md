# Orchestrator-Workers Pattern - Anthropic Best Practices

**Researched**: 2025-11-06
**For**: HQ Orchestrator coordinating multiple researchers
**Status**: Active ✅

---

## Overview

Multi-agent architecture where a lead agent coordinates specialized subagents operating in parallel. Critical for dynamic research task delegation.

---

## Key Principles

### Principle 1: Lead Agent Decomposes Dynamically

**Source**: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

**What**: Lead agent analyzes query, breaks into subtasks with explicit specifications.

**Why**: Can't predict subtasks upfront—complexity determines decomposition.

**How**: Each subagent receives: clear objective, output format, tool guidance, boundaries.

**Pattern**:
```
Lead Agent Analysis:
1. Understand user query complexity
2. Determine N subagents needed (1-10+)
3. Define each subagent's:
   - Specific objective
   - Expected output format
   - Tools/sources to use
   - Task boundaries
4. Dispatch subagents (parallel)
5. Synthesize results
6. Decide: done or spawn more
```

✅ DO:
- Give each subagent explicit, focused task
- Define output format requirements upfront
- Set clear boundaries to prevent overlap
- Include tool/source guidance

❌ DON'T:
- Use vague task descriptions
- Let subagents overlap (wastes tokens)
- Skip output format specifications

### Principle 2: Scale Dynamically Based on Complexity

**Source**: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

**What**: Simple queries = 1 agent (3-10 tool calls). Complex queries = 10+ agents.

**Why**: Prevents resource waste on straightforward tasks.

**How**: Embed effort guidelines in prompts. Lead agent decides scaling.

**Scaling Rules**:
```
Simple Query:
- 1 agent
- 3-10 tool calls
- Example: "What is Arthur.ai's tech stack?"

Moderate Query:
- 2-3 agents
- 10-20 tool calls each
- Example: "Evaluate partnership fit with Arthur.ai"

Complex Query:
- 10+ agents
- Multiple parallel subtasks
- Example: "Complete market landscape analysis"
```

✅ DO:
- Match agent count to query complexity
- Use 1 agent for straightforward lookups
- Scale up for multi-faceted research

❌ DON'T:
- Use 10 agents for simple queries (wasteful)
- Use 1 agent for complex multi-part research

### Principle 3: Parallelize Subagent Execution

**Source**: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

**What**: Spawn 3-5 subagents concurrently (not serially).

**Why**: Parallel execution cuts research time by up to 90%.

**How**: Lead agent dispatches all subagents at once, waits for all to complete.

**Performance Impact**:
```
Serial Execution:
Agent 1: 30 seconds
Agent 2: 30 seconds
Agent 3: 30 seconds
Total: 90 seconds

Parallel Execution:
All 3 agents: 30 seconds (concurrent)
Total: 30 seconds

Speedup: 90% faster
```

✅ DO:
- Dispatch 3-5 subagents concurrently
- Each subagent makes 3+ parallel tool calls
- Wait for all completions before synthesis

❌ DON'T:
- Run subagents one after another (slow)
- Limit to sequential tool calls

### Principle 4: Manage Context with Persistent Memory

**Source**: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)

**What**: When approaching 200K token limit, save research plans to external memory.

**Why**: Prevents context loss, enables fresh subagents with clean contexts.

**How**: Save state before truncation, spawn subagents with lightweight context.

**Code Pattern**:
```python
# Check context size
if context_tokens > 180000:  # 90% of 200K
    # Save current state
    save_to_memory("research-plan.json", current_plan)
    save_to_memory("findings-so-far.md", synthesis)

    # Spawn fresh subagent with clean context
    subagent = spawn_with_lightweight_context({
        "task": specific_task,
        "plan_ref": "research-plan.json",  # Reference, not full content
    })
```

✅ DO:
- Monitor context token usage
- Save state at 180K tokens (90% of limit)
- Use lightweight references in subagent context
- Spawn fresh subagents when needed

❌ DON'T:
- Wait until 200K limit (too late)
- Include full research history in subagent context
- Lose state when truncating

### Principle 5: Subagents Return Condensed Summaries

**Source**: [Building Effective Agents - Subagents](https://www.anthropic.com/engineering/building-effective-agents)

**What**: Each subagent explores extensively but returns only 1,000-2,000 token summary.

**Why**: Lead agent can't handle full subagent context (would exceed limits).

**How**: Subagent does deep work, synthesizes into concise output.

**Pattern**:
```
Subagent Process:
1. Receive focused task
2. Explore extensively (may use 50K tokens internally)
3. Synthesize findings
4. Return 1-2K token summary to lead

Lead Agent:
1. Receives 5 summaries × 1.5K = 7.5K tokens
2. Synthesizes across all subagents
3. Decides next steps
```

✅ DO:
- Set token budget for subagent outputs (1-2K)
- Subagents synthesize before returning
- Lead agent works with condensed findings

❌ DON'T:
- Return raw research (too large)
- Include full tool call history
- Let subagents dump everything to lead

---

## Token Budgets

- **Subagent exploration**: No limit (use what's needed)
- **Subagent output**: 1,000-2,000 tokens (condensed summary)
- **Context monitoring**: Save state at 180K tokens
- **GTM Factory specific**: 3-5K per researcher output

---

## Common Mistakes

1. **Serial Execution**: Running subagents one by one → Use parallel dispatch
2. **Fixed Agent Count**: Always using N agents → Scale based on complexity
3. **Context Overflow**: Not monitoring 200K limit → Save state at 180K
4. **Verbose Outputs**: Subagents returning everything → Enforce 1-2K summaries

---

## Latest Updates (2025)

- Claude 4 supports even longer contexts (400K in some models)
- Subagent SDK improvements for easier parallel dispatch
- Better context management tooling

---

## Resources

1. [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) - Orchestrator pattern in action
2. [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) - Subagent best practices
3. [Subagents Documentation](https://docs.anthropic.com/en/docs/claude-code/sub-agents) - Technical reference

---

**Last Updated**: 2025-11-06
**Used In**: Session 2 (HQ Orchestrator), Session 3 (Researcher dispatch)
