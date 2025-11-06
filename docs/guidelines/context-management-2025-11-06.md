# Context Management & File-Based Memory - Anthropic Best Practices

**Researched**: 2025-11-06
**For**: HQ Orchestrator memory management and progressive disclosure
**Status**: Active ✅

---

## Overview

Strategies for managing context as a finite resource: memory tools for persistence, progressive disclosure for efficiency, and file-based patterns for cross-session continuity.

---

## Key Principles

### Principle 1: Memory Tool Pattern (File-Based Persistence)

**Source**: [Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**What**: Anthropic's memory tool enables agents to store/retrieve information outside context window through file-based system.

**Why**: Decouples working memory (context) from long-term storage (files). Enables cross-session continuity.

**How**: Agents create persistent files (NOTES.md, CLAUDE.md, user-context.md) that reload in future sessions.

**Code Pattern**:
```python
# Session 1: Save persistent memory
def save_user_context(context_data):
    with open("projects/company/user-context.md", "w") as f:
        f.write(context_data)

# Session 2: Load without re-asking
def load_user_context():
    with open("projects/company/user-context.md", "r") as f:
        return f.read()  # User's goals, constraints already captured
```

✅ DO:
- Create structured files for persistent memory (user-context.md, conversation-history.md)
- Use file system for long-term storage
- Reload context in future sessions
- Write notes regularly (not just at end)

❌ DON'T:
- Try to keep everything in context window
- Lose state between sessions
- Write memory only at task completion

### Principle 2: Progressive Disclosure

**Source**: [Context Engineering - Progressive Disclosure](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**What**: Load context incrementally through exploration, not all upfront.

**Why**: "Find the smallest set of high-signal tokens that maximize likelihood of desired outcome."

**How**: Use lightweight identifiers (file paths), load content on-demand, maintain only necessary working memory.

**Pattern**:
```python
# DON'T: Load everything upfront
all_sessions = [load(f) for f in glob("sessions/*")]  # Wastes tokens

# DO: Load metadata first, content on-demand
session_metadata = load("session-index.json")  # <2KB
relevant = find_relevant(query, session_metadata)
if need_details:
    content = load(relevant["latest_path"])  # Just-in-time
```

✅ DO:
- Load file metadata first (paths, sizes, dates)
- Use `glob` patterns to discover files
- Load full content only when needed
- Maintain lightweight identifiers in context

❌ DON'T:
- Load all files upfront
- Keep full documents in context
- Re-read files unnecessarily

### Principle 3: Structured Note-Taking

**Source**: [Context Engineering - Structured Note-Taking](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**What**: Agents regularly write persistent notes outside context window, reinject at strategic points.

**Why**: Separates working memory (current task) from long-term storage (project state).

**How**: Create files like NOTES.md, TODO.md, user-context.md that persist across context resets.

**Example Files**:
```
projects/arthur-ai/
├── user-context.md         # Strategic WHY (reload every session)
├── conversation-history.md # Full transcript (reference, don't reload)
├── research-plan.json      # Current drop plan
└── latest.md              # Synthesized findings (living truth)
```

✅ DO:
- Write strategic info to persistent files
- Separate "always reload" from "reference only"
- Update notes as understanding evolves
- Use consistent file naming

❌ DON'T:
- Keep notes only in context
- Mix working memory with persistent storage
- Use one giant file for everything

### Principle 4: Lightweight Identifiers Over Full Content

**Source**: [Context Engineering - Claude Code Pattern](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**What**: Use file paths, URLs, queries instead of full data objects.

**Why**: Reduces context usage dramatically. Agent can fetch on-demand.

**How**: Pass paths/refs, not content. Use tools (glob, grep, read) to retrieve.

**Code Example**:
```python
# DON'T: Include full content
context = {
    "research_1": open("drop-1/research.md").read(),  # 4K tokens
    "research_2": open("drop-2/research.md").read(),  # 4K tokens
    "research_3": open("drop-3/research.md").read(),  # 4K tokens
}  # Total: 12K tokens

# DO: Include lightweight refs
context = {
    "drop_paths": [
        "drop-1/research.md",
        "drop-2/research.md",
        "drop-3/research.md"
    ]  # Total: ~100 tokens
}

# Agent loads on-demand when needed
if need_drop_1_details:
    content = read("drop-1/research.md")
```

✅ DO:
- Pass file paths, not file contents
- Use metadata (size, date) as implicit signals
- Load content only when analysis requires it
- Keep reference lists in context

❌ DON'T:
- Include full documents in context
- Load "just in case" (load when needed)
- Lose track of what files exist

### Principle 5: Context Compaction for Long Tasks

**Source**: [Context Engineering - Compaction](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**What**: Summarize conversation history, reinitiate with condensed context + recent messages.

**Why**: Long conversations exceed context limits. Compaction preserves continuity.

**How**: Periodically summarize history, restart with summary + new messages.

**Pattern**:
```python
if message_count > 20:  # Approaching limit
    # Summarize history
    summary = summarize_conversation(messages[:-5])

    # Restart with summary + recent
    new_context = [
        {"role": "system", "content": summary},  # Condensed history
        *messages[-5:]  # Recent messages
    ]

    # Continue from here
    continue_conversation(new_context)
```

✅ DO:
- Monitor message count / token usage
- Summarize periodically (every 20-30 messages)
- Keep recent messages verbatim
- Include summary in new context

❌ DON'T:
- Wait until context exhausted
- Lose conversation continuity
- Summarize too frequently (expensive)

---

## Token Budgets

- **Metadata files**: <2KB each (session-index.json, drop-metadata.json)
- **Persistent context**: 1-3K tokens (user-context.md, reload every session)
- **Reference-only**: Don't load (conversation-history.md, kept for audit)
- **Summaries**: 500-1K tokens (compacted history)

---

## Common Mistakes

1. **Loading Everything**: Reading all files upfront → Use progressive disclosure
2. **No Persistence**: Keeping state only in context → Use memory files
3. **Full Content in Context**: Including documents → Use file paths
4. **No Compaction**: Let context grow unbounded → Summarize periodically

---

## Latest Updates (2025)

- Memory tool in public beta on Claude Platform
- Claude 4 has better file management capabilities
- NOTES.md pattern now recommended in official docs

---

## Resources

1. [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) - Complete guide
2. [Managing Context](https://www.anthropic.com/news/context-management) - Memory tool announcement
3. [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) - Context best practices

---

**Last Updated**: 2025-11-06
**Used In**: Session 2 (Memory Manager), all future sessions (persistent state)
