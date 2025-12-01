# Session 5: UI (Agent-Computer Interface + Human Interface)

**Date**: 2025-11-06
**Status**: Planning → Ready to Execute

---

## Executive Summary

Build production-ready UI that integrates all existing modules (HQ, Researcher, Generators) with focus on:
1. **Agent-Computer Interface (ACI)** - Equal investment to HCI per Anthropic guidance
2. **Human Interface** - Streamlit chat UI with file navigation and context tracking
3. **Crash Recovery** - Autosave + resume capability (Helldiver lesson learned)
4. **Testing** - 10 mocked tests + 1 real smoke test (~$0.20, avoid credit burn)

**Key Insight**: User NEVER reads files directly - only interacts through HQ chat. HQ summarizes findings AND asks Socratic questions. Files are for AI consumption (Phase 2 tool implementation research will ingest latest.md).

---

## What We're Building

### Session 5a: Agent-Computer Interface (ACI)

**Anthropic Guidance**: "Invest just as much effort in creating good agent-computer interfaces (ACI) as human-computer interfaces (HCI)."

**Files to Create**:
- `/core/ui/adapters/hq_adapter.py` - Wraps HQ for UI integration
- `/core/ui/adapters/researcher_adapter.py` - Wraps Researcher with progress callbacks
- `/core/ui/adapters/generator_adapter.py` - Wraps Generators with status tracking
- `/core/ui/state_manager.py` - Session state, drop state, crash recovery
- `/core/ui/context_tracker.py` - Token counting, context window monitoring
- `/core/ui/__init__.py` - Package exports

**Key Design Principles**:
1. **Don't modify existing modules** (HQ, Researcher, Generators stay as-is)
2. **Thin adapter layer** isolates UI from backend
3. **Progress interfaces** prevent "is it frozen?" confusion
4. **Error state handling** for graceful failures

---

### Session 5b: Human Interface

**Framework**: Streamlit (fastest path to working chat UI, built-in streaming support)

**Files to Create**:
- `/ui/app.py` - Main Streamlit application
- `/ui/components/chat_interface.py` - Chat display and input
- `/ui/components/file_tree.py` - Directory navigation (NO content rendering)
- `/ui/components/context_meter.py` - Token budget tracker with progress bar
- `/ui/components/progress_display.py` - Research and generator progress
- `/ui/components/logs_panel.py` - In-app debugging logs
- `/ui/utils/session_loader.py` - Load/save session state
- `/ui/utils/crash_recovery.py` - Detect and resume incomplete drops

**UI Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ GTM Factory                    Context: 45K/200K (22.5%) ██░│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Chat Interface                    File Tree               │
│  ┌──────────────────────┐          ┌──────────────────┐    │
│  │ HQ: What market...   │          │ session-demo/    │    │
│  │ User: MLOps platform │          │ ├─ drops/        │    │
│  │ HQ: Tell me about... │          │ │  ├─ drop-1/    │    │
│  │                      │          │ │  │  ├─ user... │    │
│  │ [Research Flag: OFF] │          │ │  │  ├─ resea...│    │
│  │                      │          │ │  │  └─ criti...│    │
│  │ ▼ Input here         │          │ │  └─ drop-2/    │    │
│  └──────────────────────┘          │ └─ latest.md     │    │
│                                    └──────────────────┘    │
│                                                             │
│  Progress / Logs Panel                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [INFO] Research started - 3 researchers             │   │
│  │ [PROGRESS] Researcher-1: Searching web...           │   │
│  │ [PROGRESS] Researcher-2: Analyzing sources...       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Workflow (Corrected)

### Phase 1: Initial Chat (Before Research)

1. User opens UI → loads or creates new session
2. User chats with HQ (Socratic questioning)
3. HQ asks questions, extracts strategic WHY internally (not saved yet)
4. User flips **RESEARCH FLAG** when ready
5. HQ proposes research plan (1-4 researchers based on complexity)
6. User confirms or modifies plan

### Phase 2: Research Execution

7. **NOW extract and save context** (AFTER plan confirmation):
   - HQ extracts strategic WHY from conversation → `user-context.md`
   - Save full conversation history → `conversation-history.md`
   - Create drop folder: `drops/drop-N/`
8. Execute research (parallel researchers with real-time progress)
9. Research completes → save researcher outputs to drop folder

### Phase 3: Post-Research Processing

10. Run generators (sequential, fast ~10 seconds total):
    - LatestGenerator: Synthesize findings → `latest.md`
    - CriticalAnalystGenerator: Analyze gaps → `critical-analysis.md`
    - SessionMetadataGenerator: Update metadata → `session-metadata.json`
11. Save all files to drop folder
12. Update drop state: `complete`

### Phase 4: HQ Loads and Responds

13. HQ loads context for next conversation:
    - ✅ Full conversation history (recent messages, compact if needed)
    - ✅ `latest.md` (~2K tokens, synthesized findings)
    - ✅ `critical-analysis.md` (~2K tokens, gaps to explore)
    - ✅ `user-context.md` (~2K tokens, strategic WHY)
    - ❌ Researcher outputs (already compressed in latest.md)
14. **HQ summarizes findings to user**: "Here's what we learned..."
15. **HQ asks Socratic questions** based on critical-analysis.md: "I noticed we're missing X, should we explore that?"
16. Conversation continues (user can flip research flag again for Drop 2)

**CRITICAL**: User NEVER reads files directly. HQ is the ONLY interface.

---

## Context Window Management

**What HQ loads after each drop**:
- Conversation history: ~10-50K tokens (full history, no auto-compaction)
- latest.md: ~2K tokens (synthesized findings)
- critical-analysis.md: ~2K tokens (gaps)
- user-context.md: ~2K tokens (strategic WHY)

**Total: 16-56K tokens** (scales well for 5-10 drops)

**Manual Compaction Control** (user decides when):
```
⚠️ Context window at 80% (160K / 200K)

Options:
[ Compact conversation history ] ← User clicks when ready
[ Continue without compacting  ]

Preview:
- Will summarize messages 1-50
- Keep messages 51-65 verbatim
- Estimated new size: ~80K tokens

[Confirm] [Cancel]
```

**Context Meter** (always visible):
```
Context Window: 45K / 200K (22.5%)
[████░░░░░░░░░░░░░░] Drop 3
```

---

## Crash Recovery Strategy

**Option A (Simple, Robust) - Recommended for MVP**:

### Autosave After Every Message
```python
# After each user/HQ message
save_conversation_temp(session_path, messages)
```

### Atomic File Writes
```python
# Prevent corruption
tmp_file = file_path.with_suffix('.tmp')
tmp_file.write_text(content)
tmp_file.rename(file_path)  # Atomic operation
```

### Drop State Tracking
```python
# drop-state.json in each drop folder
{
  "drop_id": "drop-1",
  "state": "researching",  # proposed → researching → synthesizing → complete
  "created_at": "2025-11-06T10:30:00",
  "updated_at": "2025-11-06T10:45:00"
}
```

### Resume on Startup
```python
incomplete_drops = find_incomplete_drops(session_path)
if incomplete_drops:
    st.warning(f"Drop {drop.id} was interrupted during {drop.state}")
    choice = st.radio(
        "What do you want to do?",
        ["Resume research", "Mark as failed and continue chatting"]
    )
```

### Crash Scenarios Handled

| Scenario | What's Lost | Recovery |
|----------|-------------|----------|
| Mid-chat (before research) | Nothing (autosaved) | Load temp conversation, continue |
| Research proposed, not confirmed | Nothing | Re-propose plan |
| Mid-research | Research progress | Mark drop failed, user retries (2-3 min lost) |
| Mid-generators | Nothing (research saved) | Re-run generators (~10 sec) |
| After generators | Nothing | Load files, continue |

**What's NOT in MVP** (can add later):
- ❌ Checkpoint mid-research (save partial researcher outputs)
- ❌ Retry failed researchers individually
- ❌ Full transaction log (undo/redo)

---

## File Organization

### New Files Created

```
core/ui/
├── __init__.py                     # Package exports
├── state_manager.py                # Session state, drop state, persistence
├── context_tracker.py              # Token counting, window monitoring
└── adapters/
    ├── __init__.py
    ├── hq_adapter.py               # HQ wrapper with streaming
    ├── researcher_adapter.py       # Researcher wrapper with progress callbacks
    └── generator_adapter.py        # Generator wrapper with status tracking

ui/
├── app.py                          # Main Streamlit application
├── components/
│   ├── __init__.py
│   ├── chat_interface.py           # Chat display and input
│   ├── file_tree.py                # Directory navigation
│   ├── context_meter.py            # Token budget tracker
│   ├── progress_display.py         # Research/generator progress
│   └── logs_panel.py               # In-app debugging
└── utils/
    ├── __init__.py
    ├── session_loader.py           # Load/save session state
    └── crash_recovery.py           # Detect/resume incomplete drops

tests/
├── test_ui_adapters.py             # Adapter tests (MOCKED)
├── test_ui_state.py                # State management tests (MOCKED)
├── test_ui_context_tracker.py      # Context tracking tests (MOCKED)
├── test_ui_crash_recovery.py       # Recovery tests (MOCKED)
└── test_ui_full_workflow.py        # ONE REAL smoke test (~$0.20)
```

---

## Testing Strategy

**Following Session 4 pattern** (9 mocked + 2 real → 10 mocked + 1 real):

### Mocked Tests (~10 tests, $0 cost)

1. **test_hq_adapter** - Mock HQ streaming responses
2. **test_researcher_adapter** - Mock research execution with progress callbacks
3. **test_generator_adapter** - Mock synthesis and critical analysis
4. **test_state_manager_save_load** - Session persistence round trip
5. **test_autosave_conversation** - Conversation autosave after each message
6. **test_drop_state_tracking** - State transitions (proposed → complete)
7. **test_context_tracker** - Token counting accuracy
8. **test_crash_recovery_detection** - Find incomplete drops on startup
9. **test_multiple_drops_workflow** - Drop 1 → Drop 2 → Drop 3 state
10. **test_error_handling** - Research failure, API errors, file corruption

### Real Test (1 test, ~$0.20 cost)

**test_full_workflow_smoke_test**:
```python
"""
CRITICAL END-TO-END TEST: Complete user workflow from chat to synthesis.

This is the ONLY test that makes real API calls (~$0.20).
Validates the entire system works.
"""
def test_full_workflow_smoke_test():
    # 1. Create new session
    session = create_session("demo-company")

    # 2. HQ chat (2-3 messages, real Anthropic API)
    hq_response = hq_adapter.chat("I want to research MLOps platforms")
    assert "tell me more" in hq_response.lower()

    # 3. Flip research flag, confirm plan
    plan = hq_adapter.propose_research_plan()
    assert len(plan.researchers) >= 1

    # 4. Execute research (1 researcher, simple query, real Tavily + GPT-4o)
    drop_path = researcher_adapter.execute_research(plan)
    assert (drop_path / "researcher-1-output.md").exists()

    # 5. Run generators (real GPT-4o synthesis + analysis)
    latest = generator_adapter.synthesize_drop(drop_path)
    critical = generator_adapter.analyze_drop(drop_path)
    assert len(latest) > 500
    assert len(critical) > 500

    # 6. Verify session persistence
    session2 = load_session("demo-company")
    assert session2.drops[0].state == "complete"

    # 7. Verify HQ can load context and respond
    hq_response2 = hq_adapter.chat("What did we learn?")
    assert "MLOps" in hq_response2

    print("[OK] FULL WORKFLOW SMOKE TEST PASSED")
    print(f"   Cost: ~$0.20")
```

**Why This Works**:
- Mocked tests catch UI bugs fast (no API wait, no cost)
- 1 real test proves end-to-end integration
- Total cost: ~$0.20 (vs $2-3 if we tested everything)
- Follows testing-strategy-2025-11-06.md guidelines

---

## Key Architectural Decisions

### Decision 1: Streamlit for UI Framework

**Why**: Fastest path to working chat UI, built-in components

**Alternatives considered**:
- Gradio: Similar to Streamlit, more AI-focused
- Flask/FastAPI + React: More control but 5x development time
- Terminal-based (Rich/Textual): Simpler but less visual

**Trade-offs**:
- ✅ Fast MVP, easy to iterate
- ❌ Less control than custom web app (acceptable for MVP)

---

### Decision 2: Adapter Layer (Don't Modify Existing Modules)

**Why**: Isolates UI concerns from business logic, prevents breaking existing tests

**How**:
```python
# HQ Adapter wraps existing HQ without modifying it
class HQAdapter:
    def __init__(self):
        self.orchestrator = Orchestrator()  # Existing Session 2 code

    def chat(self, message: str, on_token: Callable = None):
        """Wrap HQ streaming with progress callback for UI."""
        for token in self.orchestrator.stream_response(message):
            if on_token:
                on_token(token)  # Real-time display in UI
            yield token
```

**Trade-offs**:
- ✅ Existing modules stay unchanged (tests still pass)
- ✅ Clear separation of concerns
- ❌ Slight code duplication (thin wrappers)

---

### Decision 3: Real-Time Progress via Callbacks

**Why**: Better UX than polling, gpt-researcher supports callbacks natively

**How**:
```python
# Researcher Adapter
def execute_research(self, plan, on_progress: Callable):
    for researcher in plan.researchers:
        # gpt-researcher callback support
        researcher.run(
            on_search=lambda: on_progress(f"{researcher.id}: Searching web..."),
            on_analyze=lambda: on_progress(f"{researcher.id}: Analyzing sources..."),
            on_write=lambda: on_progress(f"{researcher.id}: Writing report...")
        )
```

**UI Display**:
```
[PROGRESS] Researcher-1: Searching web...
[PROGRESS] Researcher-2: Analyzing sources...
[PROGRESS] Researcher-3: Writing report...
```

**Trade-offs**:
- ✅ Real-time feedback (user knows it's working)
- ✅ No polling overhead
- ❌ Slightly more complex than status checking

---

### Decision 4: File Tree (No Content Rendering)

**Why**: User interacts ONLY through HQ chat, files are for debugging/verification

**What's Displayed**:
```
session-demo/
├─ drops/
│  ├─ drop-1/
│  │  ├─ user-context.md
│  │  ├─ conversation-history.md
│  │  ├─ researcher-1-output.md
│  │  ├─ researcher-2-output.md
│  │  ├─ critical-analysis.md
│  │  └─ drop-metadata.json
│  └─ drop-2/
└─ latest.md
```

**NOT Displayed**:
- ❌ File content rendering (no markdown viewer)
- ❌ Syntax highlighting
- ❌ File editing

**Why**: User can read files directly in VSCode if needed. UI is for HQ conversation.

---

### Decision 5: Manual Compaction Control

**Why**: User wants control, not automatic summarization mid-conversation

**How**:
- Context meter always visible: `45K / 200K (22.5%)`
- Warning at 80%: "Context window approaching limit"
- Manual button: "Compact conversation history"
- Preview before compacting: "Will summarize messages 1-50, keep 51-65"
- User confirms or cancels

**Trade-offs**:
- ✅ User has full control
- ✅ No surprises (explicit action required)
- ❌ User might hit 200K limit if they ignore warnings (acceptable - clear UI)

---

### Decision 6: Simple Crash Recovery (Option A)

**Why**: Prevents conversation loss (Helldiver pain point) without overengineering

**What's Included**:
- ✅ Autosave after every message
- ✅ Atomic file writes (no corruption)
- ✅ Drop state tracking
- ✅ Resume detection on startup

**What's NOT Included**:
- ❌ Checkpoint mid-research (lose 2-3 min if crash during research)
- ❌ Retry individual researchers
- ❌ Full undo/redo

**Rationale**: Critical thing is conversation history (Session 2 lesson). Research is fast (~2-3 min), user can retry if crash.

---

## Anthropic Patterns Applied

### From Building Effective Agents

**Agent-Computer Interface (ACI)**:
- ✅ Invested equal effort in ACI (adapters, progress interfaces, state management)
- ✅ Tool design optimized for LLM consumption (latest.md narrative format)
- ✅ Error prevention (atomic writes, state tracking)

### From Context Engineering

**Progressive Disclosure**:
- ✅ Load latest.md (~2K) instead of researcher outputs (~15-20K)
- ✅ Metadata-first (session-metadata.json before full content)
- ✅ Just-in-time loading (conversation history, not pre-loaded)

**Context Compaction**:
- ✅ Manual compaction at user discretion
- ✅ Summarize old messages, keep recent verbatim
- ✅ Monitor token usage (context meter always visible)

**Structured Note-Taking**:
- ✅ Persistent files (user-context.md, latest.md, critical-analysis.md)
- ✅ Reload context in future sessions
- ✅ Separate working memory (chat) from long-term storage (files)

### From Streaming API

**Real-Time Feedback**:
- ✅ Stream HQ responses token-by-token
- ✅ Real-time research progress via callbacks
- ✅ Error handling with partial response capture

---

## Implementation Plan

### Phase 1: Core Adapters (ACI)

**Build Order**:
1. `state_manager.py` - Session/drop state, persistence
2. `context_tracker.py` - Token counting, window monitoring
3. `hq_adapter.py` - Wrap HQ with streaming callbacks
4. `researcher_adapter.py` - Wrap Researcher with progress callbacks
5. `generator_adapter.py` - Wrap Generators with status tracking

**Tests**: 5 mocked tests (one per file)

---

### Phase 2: UI Components

**Build Order**:
1. `app.py` - Main Streamlit app structure
2. `chat_interface.py` - Chat display and input
3. `progress_display.py` - Research/generator progress
4. `context_meter.py` - Token budget tracker
5. `file_tree.py` - Directory navigation
6. `logs_panel.py` - In-app debugging

**Tests**: 3 mocked tests (state management, UI interactions, multi-drop workflow)

---

### Phase 3: Crash Recovery

**Build Order**:
1. `session_loader.py` - Load/save session state
2. `crash_recovery.py` - Detect incomplete drops, resume logic

**Tests**: 2 mocked tests (autosave, recovery detection)

---

### Phase 4: Integration Testing

**Build Order**:
1. Wire all components together in `app.py`
2. Manual testing (chat → research → synthesis)
3. **ONE real smoke test** (full workflow, ~$0.20)

**Tests**: 1 real test (end-to-end)

---

## Success Criteria

**MVP is complete when**:
1. ✅ User can chat with HQ (Socratic questioning)
2. ✅ User can flip research flag, confirm plan
3. ✅ Research executes with real-time progress
4. ✅ Generators run, files saved
5. ✅ HQ summarizes findings and asks follow-up questions
6. ✅ User can run multiple drops (Drop 1 → Drop 2 → Drop 3)
7. ✅ Session persists (close/reopen, continue)
8. ✅ Context window tracked, manual compaction works
9. ✅ Crash recovery detects incomplete drops, offers resume
10. ✅ All 11 tests passing (10 mocked + 1 real)

**User Experience**:
- Seamless chat (full conversation history, no gaps)
- Clear progress indicators (not "is it frozen?")
- File tree shows work being done (audit trail)
- Context meter prevents surprises (always know where you are)
- Crash recovery prevents Helldiver frustration

---

## Dependencies

**New Python Packages**:
```
streamlit>=1.28.0
```

**Existing Dependencies** (already installed):
```
anthropic>=0.40.0
openai
gpt-researcher
pydantic
```

---

## Known Limitations (Post-MVP Enhancements)

**Not in MVP**:
1. ❌ Multi-session picker (only one session at a time)
2. ❌ Session archive browsing (no historical search)
3. ❌ Mid-research checkpointing (lose progress if crash)
4. ❌ Individual researcher retry
5. ❌ File content rendering in UI (use VSCode)
6. ❌ Undo/redo capability
7. ❌ Export to structured formats (JSON, CSV)

**Can Add Later** (based on usage):
- Session history/archive
- Advanced crash recovery (checkpointing)
- File content viewer/editor
- Structured export for Phase 2 (tool implementation research)

---

## End State Vision (Phase 2 Context)

**Phase 1 (What we're building)**:
- GTM hypothesis research
- Output: latest.md (synthesized findings)

**Phase 2 (Future)**:
- Tool implementation research
- Input: latest.md from Phase 1
- User: "Implement this GTM hypothesis in Clay"
- New research session investigates: "How to configure Clay given THIS hypothesis"
- Output: Specific Clay instructions + Claude skills files
- Skills files execute (create Clay tables, set filters, etc.)

**Why latest.md format is perfect**:
- Phase 2 researchers read narrative markdown easily
- Extract target criteria: "healthcare companies, 500+ employees, AWS stack"
- Research how to implement that in specific tools
- Skills files execute based on Phase 2 research output

**User's workflow**:
- Phase 1: Chat with HQ → research GTM hypothesis → refine with drops
- Phase 2: "Now implement in Clay" → new research session → skills files execute
- User NEVER reads files, NEVER configures tools manually
- All interaction through AI chat

---

## TODOs for Next Session (Session 6)

After Session 5 complete:
1. Switch from GPT-4o to GPT-5 for synthesis/analysis (once streaming ready)
2. Add dedicated CitationAgent for high-stakes synthesis (Anthropic pattern)
3. Create more test fixtures in `/tests/fixtures/` (avoid credit burn)
4. Use tiktoken for exact token counting (if needed for billing)

---

**Ready to Execute**: Yes
**Estimated Time**: 4-6 hours of focused work
**Estimated Cost**: ~$0.20 (1 real test)
**Risk Level**: Low (all modules already tested, thin adapter layer)

---

**Last Updated**: 2025-11-06
**Next**: Execute Session 5 build
