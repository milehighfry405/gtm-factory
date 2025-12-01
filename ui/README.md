# GTM Factory UI - Streamlit Interface

**Session 5 Complete** - Full UI with crash recovery, context tracking, and real-time progress

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Set Environment Variables

Create a [.env](.env) file in the project root:

```bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

### 3. Run the App

```bash
streamlit run ui/app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Features

### Chat Interface
- Seamless conversation with HQ orchestrator
- Research flag toggle (flip when ready to research)
- Streaming responses with real-time token display
- Autosave after every message (crash recovery)

### Context Window Management
- Real-time token usage display (200K limit)
- Warning at 80% threshold
- Manual compaction control (you decide when)
- Displays conversation + loaded files breakdown

### Research Execution
- Confirm research plan before execution
- Real-time progress updates per researcher
- Parallel researcher execution
- Drop state tracking (proposed → researching → synthesizing → complete)

### File Tree
- Browse project directory structure
- See file sizes
- NO content rendering (interact through HQ only)

### Crash Recovery
- Detects incomplete drops on startup
- Offers resume or mark-as-failed options
- Atomic file writes prevent corruption
- Drop state preserved across restarts

### Logs Panel
- In-app debugging logs
- Info/warning/error levels
- Expandable panel at bottom

---

## Workflow

### First Drop

1. **Chat with HQ** (2-3 messages)
   - HQ asks Socratic questions
   - Clarifies your hypothesis

2. **Flip Research Flag**
   - Toggle in sidebar when ready
   - HQ proposes research plan

3. **Confirm Plan**
   - Review 1-4 researcher tasks
   - Click "Confirm and Execute"

4. **Watch Progress**
   - Real-time status per researcher
   - Parallel execution
   - Synthesis after research completes

5. **Continue Conversation**
   - HQ summarizes findings
   - Asks follow-up questions
   - latest.md loaded into context

### Subsequent Drops

1. Continue chatting with HQ
2. Flip research flag again when ready
3. HQ proposes new drop plan
4. Repeat process

Each drop compounds on previous knowledge (progressive disclosure pattern).

---

## Manual Smoke Test (~$0.20)

Before committing Session 5, run this workflow:

```bash
# 1. Start app
streamlit run ui/app.py

# 2. Chat with HQ (2-3 messages)
"I want to test outbound GTM for a new AI code editor"

# 3. Flip research flag
# 4. Confirm research plan
# 5. Watch research execute
# 6. Verify files created:
#    - projects/{company}/sessions/{session}/drops/drop-1/researcher-*-output.md
#    - projects/{company}/sessions/{session}/latest.md
#    - projects/{company}/sessions/{session}/drops/drop-1/critical-analysis.md

# 7. Continue conversation with HQ
# 8. Flip research flag for Drop 2
# 9. Repeat

# 10. Test crash recovery:
#     - Start research
#     - Kill Streamlit (Ctrl+C)
#     - Restart app
#     - Verify incomplete drop detected
#     - Mark as failed or resume
```

**Expected Cost**: ~$0.20 (2 drops, 2-4 researchers per drop, ~3K tokens each)

---

## Architecture

### Adapter Pattern (Session 5a - ACI)

**Why**: Integrate UI without modifying existing modules (Session 2-4 tests still pass)

**Core Adapters**:
- `core/ui/state_manager.py` - Session/drop state, crash recovery, autosave
- `core/ui/context_tracker.py` - Token counting, warning thresholds
- `core/ui/adapters/hq_adapter.py` - Wraps HQOrchestrator, adds streaming callbacks
- `core/ui/adapters/researcher_adapter.py` - Wraps GeneralResearcher, parallel execution
- `core/ui/adapters/generator_adapter.py` - Wraps generators, status callbacks

### UI Components (Session 5b - Human UI)

**Streamlit Components**:
- `ui/app.py` - Main entry point, adapter initialization
- `ui/components/chat_interface.py` - Chat UI with research flag
- `ui/components/context_meter.py` - Token usage display
- `ui/components/file_tree.py` - Directory browser
- `ui/components/progress_display.py` - Research/generator progress
- `ui/components/logs_panel.py` - Debugging logs

### Crash Recovery

**How It Works**:
1. **Autosave**: Conversation saved after every message to `.tmp` file, atomically renamed
2. **Drop State**: Each drop has state file (proposed, researching, synthesizing, complete, failed)
3. **Incomplete Detection**: On startup, scan for drops in `researching` or `synthesizing` state
4. **Resume/Fail**: User chooses to resume or mark as failed

**Acceptable Loss**: If crash mid-research, lose 2-3 min of progress (can restart research)

---

## Testing

### Automated Tests (No API Calls)

```bash
# 10 mocked tests
pytest tests/test_ui.py -v

# Validation script
python tests/demos/demo_ui_validation.py
```

### Manual Smoke Test (~$0.20)

See workflow above.

---

## Anthropic Patterns Applied

1. **ACI = HCI**: Invested equal effort in Agent-Computer Interface (adapters) and Human-Computer Interface (UI)
2. **Memory Tool Pattern**: File-based persistence (user-context.md, conversation-history.md, latest.md)
3. **Progressive Disclosure**: Load metadata first, content on-demand
4. **Context Management**: Manual compaction control, token tracking, 200K limit

---

## File Structure

```
ui/
├── app.py                      # Main Streamlit app
├── components/
│   ├── __init__.py
│   ├── chat_interface.py       # Chat with research flag
│   ├── context_meter.py        # Token usage display
│   ├── file_tree.py            # Directory browser
│   ├── progress_display.py     # Research/generator progress
│   └── logs_panel.py           # Debugging logs
└── utils/
    ├── __init__.py
    ├── session_loader.py       # Session persistence
    └── crash_recovery.py       # Incomplete drop detection

core/ui/
├── state_manager.py            # Session/drop state management
├── context_tracker.py          # Token counting
└── adapters/
    ├── __init__.py
    ├── hq_adapter.py           # HQ wrapper
    ├── researcher_adapter.py   # Researcher wrapper
    └── generator_adapter.py    # Generator wrapper
```

---

## Troubleshooting

**"Session state does not function when running without streamlit run"**
- This is expected. Only run tests via `pytest`, not direct Python import.

**"ANTHROPIC_API_KEY not found"**
- Set in [.env](.env) file in project root

**"Incomplete drop detected on startup"**
- Previous session crashed mid-research
- Choose "Resume" to continue or "Mark as Failed" to skip

**Context window warning at 80%**
- Click "Compact Conversation History" button
- Review preview before confirming
- Manually decide when to compact (no auto-summarization)

---

## Next Steps

After Session 5 validation:
1. Run manual smoke test (~$0.20)
2. Verify full workflow works end-to-end
3. Commit Session 5 (single commit for 5a + 5b)
4. System is production-ready for GTM research!

---

**Last Updated**: 2025-11-06 (Session 5 complete)
