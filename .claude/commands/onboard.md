# /onboard - Load Context Fast

**Purpose**: Get Claude Code up to speed in <10 seconds with exactly what it needs to work effectively.

**User runs**: `/onboard` → You load context and output concise summary.

---

## Step 1: Read CLAUDE.md (Already Auto-Loaded)

CLAUDE.md is automatically in your context. Extract these key sections:

1. **Current State** - What session you're working on
2. **File Organization** - Where code lives
3. **Commands** - How to run things
4. **Active Gotchas** - Current blockers/issues

**You now know**: What's been done, what's next, where things go.

---

## Step 2: Check Recent Session History

Look at `docs/sessions/` to see what was recently completed:

```bash
ls -t docs/sessions/ | head -3
```

**This shows**: Last 3 sessions completed (most recent first)

**If user wants details**: "See docs/sessions/session-N-{name}.md for full context"
**If just onboarding**: Mention they exist but don't load them (progressive disclosure)

---

## Step 2.5: Check Available Guidelines

Look at `docs/guidelines/` to see what Anthropic best practices we have:

```bash
ls docs/guidelines/*.md
```

**Extract topics covered**: Just list the guideline names (don't load content yet)

**This shows**: What Anthropic patterns/practices we've already researched

**If user wants details**: "See docs/guidelines/{topic}.md for full guidance"
**If just onboarding**: Mention they exist (progressive disclosure)

---

## Step 2.75: Check Testing Setup (Important for Cost Awareness)

**Always mention testing info in onboarding output** - tests can burn API credits if used incorrectly.

### Check if Cassettes Exist:
```bash
ls tests/cassettes/ 2>/dev/null || echo "Not recorded yet"
```

If cassettes exist, agent knows tests are ready to run ($0 cost).
If not, agent knows to warn about recording cost.

### Key Testing Facts:
- **VCR Pattern Active**: Tests use pytest-recording to record/replay HTTP responses
- **Default Mode**: `vcr_record_mode = none` (never records unless explicitly told)
- **Cost Protection**: Expensive tests marked with `@pytest.mark.expensive`
- **First Run**: Costs ~$1 to record cassettes (Tavily + OpenAI/Anthropic)
- **Future Runs**: $0 (replays from cassettes)

### Test Documentation Structure:
```
docs/guidelines/
  ├── testing-quickstart.md           # Quick start (5 min read)
  └── project-health-audit-2025-11-19.md  # Full testing strategy

tests/
  ├── README-TESTING.md               # Comprehensive testing guide
  ├── cassettes/                      # VCR cassettes (may not exist yet)
  ├── test_researcher.py              # 7 expensive tests (Tavily)
  ├── test_generators.py              # 2 expensive tests (OpenAI)
  └── pytest.ini                      # Config (in root)
```

### How to Run Tests Safely:

**If cassettes don't exist yet** (first time):
```bash
# Record cassettes (costs ~$1 one-time)
pytest -m expensive --record-mode=once
```

**Normal test runs** (free):
```bash
# Run all tests (replays from cassettes, $0)
pytest

# Run only cheap tests (no API calls at all)
pytest -m "not expensive"
```

**CRITICAL**: Never run `pytest -m expensive --record-mode=rewrite` unless prompts changed - this re-records everything and costs money.

---

## Step 3: Check Git Status

```bash
git status
```

**Extract**:
- Uncommitted changes (if any)
- Current branch
- Files modified

**This tells you**: What's in progress, if anything needs committing

---

## Step 4: Check Recent Commits

```bash
git log --oneline -3
```

**This shows**: Last 3 commits (most recent work)

---

## Step 5: Output Concise Summary

**Format**:

```
✓ Context Loaded

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT: GTM Factory
Chat-based GTM research system with compounding knowledge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 CURRENT STATE
┌─────────────────────────────────────────────────
│ Active Work: Session {N} - {Name} ⏳
│ Recent: Session {N-1} ✅ ({Name})
│ Completed: Sessions {range} ✅
└─────────────────────────────────────────────────

📂 WHERE THINGS LIVE
┌─────────────────────────────────────────────────
│ Code: /core/{module}/
│ Prompts: /prompts/ (shared, reference don't copy)
│ Tests: /tests/test_{module}.py
│ Docs: /docs/sessions/ (historical context)
└─────────────────────────────────────────────────

🔧 COMMANDS
┌─────────────────────────────────────────────────
│ /onboard  - Load context (this command)
│ /learn    - Research Anthropic best practices before building
│ /commit   - Archive session & commit
│ {other commands from CLAUDE.md}
└─────────────────────────────────────────────────

{IF GOTCHAS EXIST}
⚠️  ACTIVE GOTCHAS
┌─────────────────────────────────────────────────
│ {Gotcha 1 from CLAUDE.md}
│ {Gotcha 2 from CLAUDE.md}
└─────────────────────────────────────────────────
{END IF}

{IF UNCOMMITTED CHANGES}
📝 UNCOMMITTED CHANGES
┌─────────────────────────────────────────────────
│ {files modified}
│ → Run /commit when ready
└─────────────────────────────────────────────────
{END IF}

🎯 NEXT STEPS
┌─────────────────────────────────────────────────
│ Working on: {What Session N is building}
│ Location: {Which /core/{module}/ you'll work in}
│ Reference: {Which /prompts/ file to use}
└─────────────────────────────────────────────────

📚 RECENT HISTORY (if needed)
┌─────────────────────────────────────────────────
│ {Session N-1}: {name} - docs/sessions/session-{N-1}-{name}.md
│ {Session N-2}: {name} - docs/sessions/session-{N-2}-{name}.md
│ {Session N-3}: {name} - docs/sessions/session-{N-3}-{name}.md
└─────────────────────────────────────────────────

📖 ANTHROPIC GUIDELINES (if needed)
┌─────────────────────────────────────────────────
│ {guideline-1} - docs/guidelines/{file1}.md
│ {guideline-2} - docs/guidelines/{file2}.md
│ {guideline-3} - docs/guidelines/{file3}.md
└─────────────────────────────────────────────────

🧪 TESTING INFO
┌─────────────────────────────────────────────────
│ VCR Pattern: Record once (~$1), replay forever ($0)
│ Cassettes: {exists OR "Not recorded yet - run: pytest -m expensive --record-mode=once"}
│ Quick Start: docs/guidelines/testing-quickstart.md
│ Full Guide: tests/README-TESTING.md
│
│ Commands:
│   pytest                    # Run all tests (uses cassettes, $0)
│   pytest -m "not expensive" # Skip API tests entirely
└─────────────────────────────────────────────────

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Ready to work! What should we build?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Example Output (Session 2)

```
✓ Context Loaded

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT: GTM Factory
Chat-based GTM research system with compounding knowledge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 CURRENT STATE
┌─────────────────────────────────────────────────
│ Active Work: Session 2 - HQ Orchestrator ⏳
│ Recent: Session 1 ✅ (Foundation - Prompts)
│ Completed: None yet
└─────────────────────────────────────────────────

📂 WHERE THINGS LIVE
┌─────────────────────────────────────────────────
│ Code: /core/hq/ (You'll build here)
│ Prompts: /prompts/hq-orchestrator.md (Reference this)
│ Tests: /tests/test_hq.py (Create tests here)
│ Docs: /docs/sessions/ (Historical context)
└─────────────────────────────────────────────────

🔧 COMMANDS
┌─────────────────────────────────────────────────
│ /onboard  - Load context (this command)
│ /commit   - Archive session & commit
└─────────────────────────────────────────────────

🎯 NEXT STEPS
┌─────────────────────────────────────────────────
│ Working on: Build HQ Orchestrator
│   - core/hq/orchestrator.py (Socratic conversation)
│   - core/hq/context_extractor.py (Strategic WHY)
│   - core/hq/memory_manager.py (File persistence)
│ Location: /core/hq/
│ Reference: /prompts/hq-orchestrator.md
└─────────────────────────────────────────────────

📚 RECENT HISTORY (if needed)
┌─────────────────────────────────────────────────
│ Session 1: Foundation - docs/sessions/session-1-foundation.md
└─────────────────────────────────────────────────

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Ready to work! What should we build?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Critical Rules

1. **Be fast** - Entire output in <10 seconds
2. **Be scannable** - Visual hierarchy with boxes/sections
3. **Be concise** - No walls of text, bullet points only
4. **Progressive disclosure** - Mention history exists, don't load it unless user asks
5. **Action-oriented** - End with "What should we build?" to prompt user

---

## If User Asks for Historical Context

**User**: "What happened in Session 5?"

**You**: Read `docs/sessions/session-5-{name}.md` and summarize:

```
📖 Session 5: {Name}

Built:
- {File 1}
- {File 2}

Key Decisions:
- {Decision 1}
- {Decision 2}

Gotchas:
- {Issue and solution}

Full details: docs/sessions/session-5-{name}.md
```

**Don't load automatically** - only when asked.

---

## If No docs/sessions/ Yet

**First session ever** - just show:

```
📚 RECENT HISTORY
┌─────────────────────────────────────────────────
│ No prior sessions yet - this is the beginning!
└─────────────────────────────────────────────────
```

---

**Goal**: User types `/onboard`, gets instantly oriented, knows exactly what to do.
