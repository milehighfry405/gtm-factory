# GTM Factory - Project Structure & Documentation Map

**Last Updated**: 2025-11-19

This document explains where everything lives and how different types of documentation are organized.

---

## 📁 Top-Level Structure

```
gtm-factory/
├── CLAUDE.md                   # Main coordination file (read this first)
├── README.md                   # User-facing project overview
├── pytest.ini                  # Pytest configuration (VCR settings)
├── pyproject.toml             # Python dependencies & build config
│
├── .claude/                    # Claude Code commands
│   └── commands/
│       ├── onboard.md         # Context loading (includes testing info)
│       └── commit.md          # Smart commit with session archiving
│
├── core/                       # Implementation code
│   ├── hq/                    # HQ orchestrator (Socratic questioning)
│   ├── researcher/            # Research wrapper (gpt-researcher + Tavily)
│   ├── generators/            # Synthesis, critical analysis, metadata
│   └── ui/                    # UI adapters (Streamlit integration)
│
├── ui/                         # Streamlit application
│   ├── app.py                 # Main application
│   └── components/            # UI components
│
├── tests/                      # Test suite
│   ├── README-TESTING.md      # Comprehensive testing guide
│   ├── cassettes/             # VCR cassettes (recorded API responses)
│   ├── test_researcher.py     # 7 expensive tests (Tavily)
│   ├── test_generators.py     # 2 expensive tests (OpenAI)
│   └── ...
│
├── docs/                       # Documentation
│   ├── guidelines/            # Best practices & research
│   ├── sessions/              # Session summaries (auto-created by /commit)
│   ├── session plans/         # Planning docs
│   └── archive/               # Old/deprecated docs
│
├── prompts/                    # Shared AI prompts (referenced by code)
│   ├── hq-orchestrator.md
│   ├── general-researcher.md
│   └── ...
│
└── projects/                   # Runtime data (gitignored)
    └── {company}/
        └── sessions/
            └── session-{id}/
                ├── drops/
                └── latest.md
```

---

## 📚 Documentation Organization

### Primary Coordination
- **CLAUDE.md** - Main coordination file
  - What's built (build status)
  - What's next (current session)
  - Where things go (file organization)
  - How to work (coordination rules)

### Commands (`.claude/commands/`)
- **onboard.md** - Load context fast (<10 seconds)
  - Includes testing info
  - Shows git status
  - Lists recent sessions & guidelines
- **commit.md** - Auto-archive & commit
  - Creates session summaries
  - Updates CLAUDE.md
  - Prunes old sessions

### Testing Documentation

#### Quick Reference
- **docs/guidelines/testing-quickstart.md** - 5 minute quick start
  - How to avoid burning credits
  - Record cassettes once (~$1)
  - Run tests forever ($0)

#### Comprehensive Guide
- **tests/README-TESTING.md** - Full testing documentation
  - VCR pattern explained
  - Cost breakdown
  - Troubleshooting
  - Best practices

#### Research & Strategy
- **docs/guidelines/project-health-audit-2025-11-19.md** - Deep research
  - LLM testing strategies
  - Code audit tools
  - Best practices research
  - Workflow optimization

### Guidelines (docs/guidelines/)

Research findings and best practices from Anthropic docs:
- `building_agents.md` - Official Anthropic agent patterns
- `streaming-api-2025-11-06.md` - Streaming API best practices
- `orchestrator-workers-2025-11-06.md` - Multi-agent patterns
- `context-management-2025-11-06.md` - Token management
- `researcher-integration-2025-11-06.md` - Research module patterns
- `synthesis-patterns-2025-11-06.md` - Synthesis generation
- `testing-strategy-2025-11-06.md` - Testing approach
- `testing-quickstart.md` - Quick start for tests (NEW)
- `project-health-audit-2025-11-19.md` - Full project audit (NEW)

### Session Summaries (docs/sessions/)

Auto-created by `/commit` command:
- `session-1-foundation.md`
- `session-2-hq-orchestrator.md`
- `session-3-researcher.md`
- `session-4-generators-final.md`
- `session-5-ui-final.md`

**Format**: What was built, key decisions, gotchas discovered, testing, next steps

---

## 🧪 Testing Structure

### Configuration
- **pytest.ini** (root) - Main pytest config
  - `vcr_record_mode = none` (default: never record)
  - Test markers defined (`expensive`, `vcr`, `asyncio`)
  - Coverage settings

### Tests
- **test_researcher.py** - 7 tests with Tavily API calls
  - All marked `@pytest.mark.vcr()` + `@pytest.mark.expensive`
  - First run: ~$0.70 (records to cassettes)
  - Future runs: $0 (replays from cassettes)

- **test_generators.py** - 2 tests with OpenAI API calls
  - All marked `@pytest.mark.vcr()` + `@pytest.mark.expensive`
  - First run: ~$0.20
  - Future runs: $0

- **test_hq.py**, **test_ui.py**, etc. - Mostly mocked tests
  - No external API calls
  - Always free to run

### Cassettes (tests/cassettes/)
- VCR cassettes (YAML files)
- Recorded HTTP request/response pairs
- Committed to git (team doesn't need to re-record)
- Re-record only when prompts/APIs change

---

## 🔄 Workflow for Agents

### Starting Fresh (Use /onboard)
1. Agent runs `/onboard`
2. Loads CLAUDE.md (auto-loaded)
3. Checks recent sessions
4. Checks available guidelines
5. **Checks if test cassettes exist** (important!)
6. Checks git status
7. Outputs summary with testing info

### Testing (Cost-Aware)
1. **First time**: Record cassettes
   ```bash
   pytest -m expensive --record-mode=once  # ~$1 one-time
   ```
2. **Normal runs**: Use cassettes
   ```bash
   pytest  # $0, <30 seconds
   ```
3. **Skip expensive**: Only fast tests
   ```bash
   pytest -m "not expensive"  # $0, <5 seconds
   ```

### Completing Work (Use /commit)
1. Agent runs `/commit`
2. Pre-commit verification
3. Understands what changed (from git diff + context)
4. Determines current session (from CLAUDE.md)
5. Creates session summary in `docs/sessions/`
6. Updates CLAUDE.md (marks complete, prunes old)
7. Creates commit with rich context
8. Asks about push

---

## 📖 Documentation Hierarchy

```
Quick Orientation:
  └─> /onboard command (instant, scannable)

Need Testing Info:
  └─> docs/guidelines/testing-quickstart.md (5 min)
      └─> tests/README-TESTING.md (comprehensive)
          └─> docs/guidelines/project-health-audit-2025-11-19.md (deep dive)

Need Historical Context:
  └─> CLAUDE.md (recent 3 sessions)
      └─> docs/sessions/session-N-{name}.md (full session details)

Need Best Practices:
  └─> docs/guidelines/{topic}.md

Need Code Reference:
  └─> core/{module}/ (implementation)
      └─> tests/test_{module}.py (validation)
          └─> prompts/{module}.md (AI instructions)
```

---

## 🎯 Key Principles

### Documentation
1. **CLAUDE.md is source of truth** - Always current, always < 250 lines
2. **Progressive disclosure** - Mention exists, load only when needed
3. **No duplication** - One concept, one location
4. **Rich summaries** - Session docs are detailed, CLAUDE.md is minimal

### Testing
1. **VCR pattern** - Record once, replay forever
2. **Cost protection** - Default mode never records
3. **Clear markers** - Expensive tests clearly marked
4. **Safety first** - Can't accidentally burn credits

### Organization
1. **Code** → `/core/{module}/`
2. **Tests** → `/tests/test_{module}.py`
3. **Prompts** → `/prompts/{module}.md`
4. **Docs** → `/docs/{guidelines|sessions|archive}/`
5. **Commands** → `/.claude/commands/{name}.md`

---

## 🚀 Quick Reference for Agents

### Need to Understand Project?
→ Run `/onboard`

### Need to Run Tests?
→ Check if cassettes exist: `ls tests/cassettes/`
→ If yes: `pytest` (free)
→ If no: `pytest -m expensive --record-mode=once` (costs ~$1 once)

### Need to Test Without Cost?
→ `pytest -m "not expensive"` (skip all API tests)

### Need Best Practices?
→ Read `docs/guidelines/{relevant-topic}.md`

### Need Historical Context?
→ Read `docs/sessions/session-{N}-{name}.md`

### Done with Work?
→ Run `/commit` (auto-archives everything)

---

**Goal**: Every agent knows exactly where to find what they need, and can't accidentally burn API credits.
