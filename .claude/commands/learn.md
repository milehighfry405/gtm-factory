# /learn - Research & Update Best Practices

**Purpose**: Research Anthropic best practices for upcoming work, check what we already know, and update our knowledge base with new findings.

**User runs**: `/learn` → You research, compare with existing guidelines, and add new knowledge.

---

## Step 1: Check Existing Guidelines

**Read all files in** `/docs/guidelines/`:
```bash
ls docs/guidelines/*.md
```

**For each guideline file, extract**:
- What topics it covers
- What Anthropic resources it references (URLs)
- What principles/patterns it documents
- Date/version if available

**Create mental inventory**: "We already have guidance on X, Y, Z from these Anthropic sources"

---

## Step 2: Understand What We're Building

From conversation context, identify:
- **What we're building**: (e.g., "HQ Orchestrator with Socratic questioning")
- **Key technologies**: (e.g., "Streaming API, prompt engineering, context management")
- **Architecture patterns**: (e.g., "Orchestrator-workers, file-based memory")
- **Challenges**: (e.g., "Token budgets, progressive disclosure")

---

## Step 3: Identify Knowledge Gaps

**Compare**: What we're building vs what's in existing guidelines

**Gaps to fill**:
- Topics we're about to use that aren't documented yet
- Updated guidance (2025 vs older docs)
- Specific patterns for our use case

**Example**:
- ✅ Have: "Building agents for startups" (general philosophy)
- ❌ Need: "Streaming API best practices" (technical implementation)
- ❌ Need: "System prompt structure with XML tags" (specific pattern)

---

## Step 4: Search Anthropic for Missing Knowledge

Use WebSearch with `allowed_domains: ["anthropic.com"]` to find:

**Core resources** (search every time):
1. "Anthropic building effective agents 2025"
2. "Anthropic prompt engineering best practices"
3. "Anthropic context engineering"
4. "Anthropic Claude API documentation"

**Based on gaps identified**:

**If building conversational agents**:
- "Anthropic streaming responses"
- "Anthropic multi-turn conversation"
- "Anthropic system prompts structure"

**If building prompt logic**:
- "Anthropic XML tags prompts"
- "Anthropic few-shot examples"
- "Anthropic chain of thought"

**If managing memory/state**:
- "Anthropic memory tool pattern"
- "Anthropic file-based persistence"
- "Anthropic progressive disclosure"

**If building tools/functions**:
- "Anthropic tool use best practices"
- "Anthropic tool documentation"

**If using subagents**:
- "Anthropic subagent patterns"
- "Anthropic orchestrator workers"

---

## Step 5: Fetch & Extract

For each relevant NEW resource (not already in guidelines):
1. Use WebFetch to get full content
2. Extract:
   - ✅ Specific code examples
   - ⚠️ Common mistakes (anti-patterns)
   - 🎯 Performance optimizations
   - 📊 Token budget recommendations
   - 🔄 Latest API features (2025)

---

## Step 6: Present Findings

**Format**:

```markdown
📚 LEARNED: {Topic}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## What We Already Know

✅ From docs/guidelines/{file}.md:
- {Existing principle 1}
- {Existing principle 2}
- Source: {URL from existing guidelines}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## New Knowledge from Anthropic

### {New Topic 1}

**Source**: {URL}
**Date**: {2025 or note if older}

✅ DO:
- {Specific guidance}
- {Code pattern}

❌ DON'T:
- {Anti-pattern}
- {Why problematic}

**Code Example**:
```python
{Actual example from Anthropic}
```

### {New Topic 2}
{Same format...}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## How This Changes Our Plan

**Before /learn**:
{What we were going to do}

**After /learn**:
{Updated approach based on Anthropic guidance}
{Why this is better}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Saving to Guidelines

Creating: docs/guidelines/{topic}-{date}.md

This will contain:
- All new knowledge extracted
- Links to Anthropic sources
- Code examples
- DO/DON'T patterns

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Ready to build with latest Anthropic guidance!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 7: Save New Guidelines

**Create new file**: `docs/guidelines/{topic}-{YYYY-MM-DD}.md`

**Format**:
```markdown
# {Topic} - Anthropic Best Practices

**Researched**: {Date}
**For**: {What we're building}
**Status**: Active ✅

---

## Overview

{1-2 sentence summary of what this covers}

---

## Key Principles

### Principle 1: {Name}

**Source**: [{Title}]({URL})

**What**: {Clear explanation}

**Why**: {Rationale from Anthropic}

**How**: {Implementation guidance}

**Code Example**:
```python
{Example from Anthropic docs}
```

✅ DO:
- {Specific guidance}

❌ DON'T:
- {Anti-pattern}

### Principle 2: {Name}
{Same format...}

---

## Token Budgets

{Any specific numbers from Anthropic}

---

## Common Mistakes

1. **{Mistake}**: {Why it's bad} → {Do this instead}
2. **{Mistake}**: {Why it's bad} → {Do this instead}

---

## Latest Updates (2025)

- {New feature or pattern}
- {Deprecated approach}

---

## Resources

1. [{Title}]({URL}) - {Brief description}
2. [{Title}]({URL}) - {Brief description}

---

**Last Updated**: {Date}
**Used In**: {Which sessions/components used this}
```

**Save the file**, then tell user it's been added to guidelines.

---

## Step 8: Update Existing Guidelines (If Needed)

**If new info updates existing guideline**:
1. Read existing file
2. Add section: "## Updated: {Date}"
3. Add new principles/patterns
4. Mark old info as deprecated if needed
5. Update "Last Updated" date

**Don't duplicate** - if it's already documented, just reference it.

---

## Critical Rules

1. **Check first** - Always read existing guidelines before searching
2. **Anthropic only** - Only search anthropic.com domains
3. **No duplication** - If guideline exists with same info, just reference it
4. **Date everything** - Mark when researched, note if guidance is old
5. **Save new knowledge** - Always create/update guideline file
6. **Be specific** - Extract actual patterns, not generic "follow best practices"
7. **Flag conflicts** - If Anthropic contradicts existing guidelines, highlight it

---

## Example Usage

**User**: "Let's build the HQ Orchestrator"
**User**: `/learn`

**You do**:
1. Read docs/guidelines/*.md (find we have "building agents" but not "streaming API")
2. Search: "Anthropic streaming API", "Anthropic system prompts", etc.
3. Extract new patterns not in existing guidelines
4. Present findings with "What We Already Know" + "New Knowledge"
5. Create docs/guidelines/streaming-api-2025-11-06.md
6. Show user what was added

**Result**: Our guidelines folder grows with each /learn, becoming compounding knowledge base

---

## If Conflicts Detected

**If new Anthropic guidance conflicts with existing guidelines**:

```
⚠️  CONFLICT DETECTED

Existing Guideline: docs/guidelines/{file}.md says {X}
Source: {URL from guideline}

New Anthropic Guidance: {Y}
Source: {New URL}
Date: {2025 or newer}

Recommendation: {Suggest updating guideline with new info}

Should I update the guideline with newer Anthropic guidance?
```

---

## Guidelines Folder Structure

```
docs/guidelines/
├── building-agents-2025-11-03.md         (startup philosophy)
├── prompt-engineering-2025-11-06.md      (prompt patterns)
├── streaming-api-2025-11-06.md           (technical implementation)
├── context-management-2025-11-06.md      (progressive disclosure)
└── orchestrator-patterns-2025-11-06.md   (multi-agent coordination)
```

**Each session adds knowledge**, **never loses it**.

---

**Goal**: Build a compounding knowledge base of Anthropic best practices, checking what we know before searching for new info, and always saving discoveries.
