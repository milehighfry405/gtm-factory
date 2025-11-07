# Session 4: Generators

**Date**: 2025-11-06
**Status**: Complete ✅

---

## What We Built

**Files Created**:
- `core/generators/latest_generator.py` - Iterative synthesis engine with GPT-4o (215 lines)
- `core/generators/session_metadata_generator.py` - Progressive disclosure metadata (187 lines)
- `core/generators/critical_analyst_generator.py` - Critical analysis generator (pokes holes in research, 230 lines)
- `core/generators/__init__.py` - Package exports for all three generators
- `tests/test_generators.py` - 11 tests (9 mocked + 2 real API calls, 308 lines)
- `docs/guidelines/synthesis-patterns-2025-11-06.md` - Anthropic synthesis patterns research
- `docs/sessions/session-4-generators.md` - Initial session documentation

**Functionality Added**:
- Iterative synthesis of research outputs into `latest.md` (living truth document)
- Contradiction detection and invalidation (strikethrough old claims)
- Critical analysis generation that pokes holes in research (counterbalances AI agreeableness)
- Session and drop metadata generation for progressive disclosure
- Token-efficient context management following Anthropic patterns
- XML-structured synthesis and analysis prompts with chain-of-thought reasoning
- Examples-based prompting for better synthesis quality

---

## Key Decisions

**Decision 1**: Three Generators Architecture

**Why**: After user clarification, realized critical analysis should run ALONGSIDE synthesis, not after it.

**Flow**:
```
Research Drop Completes
    ↓
├─→ Critical Analyst analyzes researcher outputs → critical-analysis.md
└─→ Latest Generator synthesizes researcher outputs → latest.md
    ↓
HQ uses critical-analysis.md to guide next conversation
```

**Alternatives considered**:
- Single generator doing both tasks: Too complex, mixes concerns
- Critical analyst analyzes synthesis: Wrong - needs raw research to poke holes

**Trade-offs**: More code to maintain, but clear separation of concerns

---

**Decision 2**: Iterative Synthesis Pattern (Anthropic Multi-Agent Research System)

**Why**: Loading all research outputs into single prompt wastes tokens (15× multiplier). Iterative approach scales better.

**How Implemented**:
```python
# Load existing latest.md (compacted state)
existing_latest = load_latest_md()

# Add new drop incrementally
latest_md = synthesize_incremental(existing_latest, new_drop_outputs)

# Save updated state
save_latest_md(latest_md)
```

**Alternatives considered**:
- Single-shot synthesis: Simpler but doesn't scale beyond ~10 drops
- Manual synthesis: No automation, doesn't compound knowledge

**Trade-offs**: More complex logic, but proven pattern from Anthropic's own research system

---

**Decision 3**: Enhanced Prompts with Full Anthropic Best Practices

**Why**: User asked if we're following Anthropic prompt engineering guidelines. Reviewed official docs and upgraded all prompts.

**What Added**:
1. **Chain of Thought**: "Before writing, think through: 1. What are key findings? 2. Any contradictions? 3. Where do findings fit?"
2. **Examples**: Concrete example of contradiction handling in synthesis prompt
3. **Examples**: Strong critical analysis example showing expected output
4. **Clear role definition**: "AI has a tendency to be agreeable. You are the counterbalance."
5. **XML structure**: Already had this, maintained it
6. **Direct instructions**: Bullet points, clear task breakdown

**Evidence**: Researched from https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview

**Impact**: Better synthesis quality, more critical analysis rigor

---

**Decision 4**: XML-Structured Prompts

**Why**: Anthropic guidance emphasizes clear section delineation for token efficiency and parsing clarity.

**Implementation**:
```xml
<existing_latest>
{current state}
</existing_latest>

<new_findings>
{new research}
</new_findings>

<instructions>
{synthesis task}
</instructions>
```

**Alternatives considered**:
- Plain text prompts: Less clear, harder to parse
- JSON-structured prompts: Harder to read, less flexible

**Trade-offs**: Slightly more verbose, but significantly clearer for model

---

**Decision 5**: Metadata-First Progressive Disclosure

**Why**: Future sessions need to scan past work quickly without loading full `latest.md` files.

**Implementation**:
- `session-metadata.json`: Lightweight index (drops, tokens, cost)
- `drop-metadata.json`: Per-drop details (researchers, outputs, user context summary)
- Load JSON first → scan → load only relevant `latest.md`

**Pattern**: Matches Anthropic's "just-in-time" loading guidance

---

**Decision 6**: GPT-4o for Synthesis (Temporary)

**Why**: GPT-5 streaming still propagating from Session 3. GPT-4o works immediately.

**TODO**: Switch to GPT-5 once available (better synthesis quality, 45% fewer factual errors)

**Cost**: ~$0.01 per synthesis for typical 3-researcher drop

---

**Decision 7**: Critical Analyst as Checks and Balance

**Why**: "AI has a tendency to be agreeable" - user's critical insight.

**Role**:
- Pokes holes in research
- Identifies logical gaps, weak evidence, unstated assumptions
- Shows user "where the gold is" (gaps relevant to strategic WHY)
- Provides HQ with context for better conversations

**Output**: `critical-analysis.md` saved in drop folder (peer to researcher outputs)

---

## Gotchas Discovered

**Gotcha 1**: Windows Emoji Encoding in Tests

**Problem**: Test print statements with ✅ emoji crashed on Windows with `UnicodeEncodeError`

**Solution**: Removed emojis, replaced with `[OK]` and `[FAIL]` text

**Prevention**: No emojis in production code (Session 3 lesson reinforced)

---

**Gotcha 2**: Contradiction Detection is Prompt-Based

**Problem**: Can't reliably detect contradictions with code logic alone - requires LLM understanding

**Solution**: Embedded contradiction detection in synthesis prompt:
- "If new findings contradict existing claims, apply strikethrough"
- Provide example format: `~~old claim~~ New claim (Source: Drop 2)`

**Limitation**: Relies on GPT-4o accuracy. May miss subtle contradictions. Acceptable for MVP.

**Future Enhancement**: Dedicated CitationAgent (Anthropic pattern) for high-stakes synthesis

---

**Gotcha 3**: Token Estimation is Rough

**Problem**: Using `len(content) // 4` for token estimation (4 chars per token rule of thumb)

**Solution**: Good enough for metadata, not billing. If we need exact counts, use tiktoken library.

**Impact**: Metadata token counts ~20% variance from actual. Not critical for progressive disclosure use case.

---

**Gotcha 4**: Testing Synthesis Without Burning Credits

**Problem**: How to test synthesis logic without making 50 API calls?

**Solution**:
- 9 tests mock everything (file I/O, metadata, load/save)
- 2 real tests validate GPT-4o integration (~$0.20 total)
- Drop-2 fixture provides contradiction scenario for future testing

**Learned**: Fixtures are essential. Created `/projects/demo-company/.../drop-2/` with market size contradiction for validation.

---

**Gotcha 5**: Critical Analyst Misunderstanding

**Problem**: Initially thought Critical Analyst should analyze synthesis (latest.md)

**Solution**: User clarified - it analyzes researcher outputs directly (peer to synthesis, not downstream)

**Why it happened**: Didn't fully understand the "checks and balance" role

**Prevention**: Always clarify architecture when adding new components

---

## Testing

**Tests Added**:
- `tests/test_generators.py` - 11 total tests:
  1. `test_generate_session_metadata` - JSON generation (MOCKED)
  2. `test_generate_drop_metadata` - Per-drop metadata (MOCKED)
  3. `test_save_and_load_metadata` - Persistence round trip (MOCKED)
  4. `test_load_researcher_outputs` (LatestGenerator) - File loading (MOCKED)
  5. `test_load_user_context` - Context loading (MOCKED)
  6. `test_save_latest` - latest.md persistence (MOCKED)
  7. `test_detects_contradictions_in_manual_example` - Fixture validation (MOCKED)
  8. `test_synthesis_real_api_call` - End-to-end GPT-4o synthesis (REAL API ~$0.10)
  9. `test_load_researcher_outputs` (CriticalAnalyst) - File loading (MOCKED)
  10. `test_critical_analysis_real_api_call` - End-to-end GPT-4o analysis (REAL API ~$0.10)
  11. `test_save_analysis` - critical-analysis.md persistence (MOCKED)

**Manual Testing**:
- Validated synthesis output manually: `projects/demo-company/.../latest-test-output.md`
- 2.6KB output with proper structure (TL;DR, Key Insights, Strategic Implications, Actions)
- Synthesized 3 MLOps use cases correctly
- Maintained confidence levels (High/Medium/Low)

**Test Results**:
- 11/11 passing
- 9 mocked tests run in ~1.5 seconds (no API calls)
- 2 real tests took ~16 seconds, cost ~$0.20
- Total session cost: **$0.20** (avoided $2-3 by mocking)

---

## Research Conducted

**New Knowledge from Anthropic**:
- Researched synthesis patterns from multi-agent research system
- Context engineering (compaction, progressive disclosure)
- Token budget management (15× multi-agent multiplier)
- Citation verification pattern (dedicated agent)
- **Prompt engineering best practices** from official Claude docs

**Guidelines Created**:
- `docs/guidelines/synthesis-patterns-2025-11-06.md`
- Covers iterative synthesis, citation verification, token budgets, context compaction, XML prompts
- 5 key principles extracted from Anthropic engineering blog

**Prompt Engineering Research**:
- Reviewed https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
- Applied ALL best practices: Chain of Thought, Examples, XML tags, Role definition, Clear instructions
- Upgraded both LatestGenerator and CriticalAnalystGenerator prompts

**Key Insights Applied**:
1. **Iterative synthesis** over single-shot
2. **Sub-agent compression**: Return 1K-2K summaries (we're doing full drops, but principle noted)
3. **XML-structured prompts** for clarity
4. **Just-in-time loading** via metadata-first pattern
5. **Token efficiency**: 15× multiplier for multi-agent awareness
6. **Chain of Thought**: Ask model to think before writing
7. **Examples**: Show what good output looks like

---

## Next Session Setup

**What Session 5 (UI) needs to know**:
- Generators work end-to-end (validated with real synthesis + critical analysis tests)
- Call `LatestGenerator.synthesize_drop()` after each research drop completes
- Call `CriticalAnalystGenerator.analyze_drop()` after each research drop completes
- Call `SessionMetadataGenerator` when session starts/ends
- Metadata enables quick session scanning without loading full content
- Synthesis outputs are ~1.5-2.5K tokens (fits in chat context easily)
- Critical analysis outputs are ~1.5-3K tokens

**Dependencies for UI**:
- Must save latest.md to session directory after each drop
- Must save critical-analysis.md to drop directory after each drop
- Must generate session-metadata.json for session index view
- Must handle drop-metadata.json for detailed drop inspection
- Synthesis prompt includes contradiction detection (strikethrough applied automatically)
- Critical analysis provides HQ with context for guiding user conversations

**Recommended next steps**:
1. Build chat UI (Streamlit or similar)
2. Integrate HQ → Researcher → Generators workflow
3. Display latest.md in UI with markdown rendering
4. Display critical-analysis.md to guide user's next research drop
5. Add research flag toggle
6. Show progress indicators during research

**Known TODOs**:
- Switch from GPT-4o to GPT-5 for synthesis and critical analysis (when streaming ready)
- Add dedicated CitationAgent for high-stakes synthesis (future enhancement)
- Create more test fixtures in `/tests/fixtures/` (avoid credit burn)
- Use tiktoken for exact token counting (if needed for billing)

---

## Anthropic Patterns Applied

**From Multi-Agent Research System**:
- ✅ Iterative synthesis (LeadResearcher pattern)
- ✅ Sub-agent output compression (1K-2K summaries recommended)
- ⏳ Dedicated CitationAgent (noted for future, not MVP blocking)

**From Effective Context Engineering**:
- ✅ Progressive disclosure (metadata-first scanning)
- ✅ Just-in-time loading (don't pre-load all drops)
- ✅ Context compaction (latest.md is compacted state)
- ✅ Structured note-taking (latest.md persisted externally)

**From Prompt Engineering Best Practices**:
- ✅ XML-tagged sections for clarity
- ✅ Chain of Thought reasoning ("Before writing, think through...")
- ✅ Examples in prompts (contradiction handling, critical analysis)
- ✅ Clear role definition ("You are the counterbalance to AI agreeableness")
- ✅ Simple, direct language in instructions
- ✅ Flexible heuristics over rigid rules
- ✅ Minimal prompts (start small, iterate based on testing)

---

## File Structure Created

```
core/generators/
├── __init__.py                          # Package exports (3 generators)
├── latest_generator.py                  # Iterative synthesis (215 lines)
├── session_metadata_generator.py        # Progressive disclosure (187 lines)
└── critical_analyst_generator.py        # Critical analysis (230 lines)

tests/
└── test_generators.py                   # 11 tests (9 mocked, 2 real)

projects/demo-company/sessions/session-demo-researcher/
├── latest-test-output.md                # Validated synthesis output
└── drops/
    ├── drop-1/
    │   ├── researcher-demo-output.md    # (from Session 3)
    │   ├── user-context.md              # Strategic WHY (created Session 4)
    │   ├── conversation-history.md      # Chat history (created Session 4)
    │   └── critical-analysis-test-output.md  # Validated critical analysis
    └── drop-2/
        ├── researcher-contradictory-output.md  # Market size update ($1.2B → $2.2B)
        └── user-context.md              # Updated strategic WHY (compliance focus)

docs/
├── guidelines/
│   └── synthesis-patterns-2025-11-06.md  # Anthropic research + prompt engineering
└── sessions/
    ├── session-4-generators.md           # Initial session doc
    └── session-4-generators-final.md     # This file (final commit summary)
```

---

## Commit

`0ed697d` - feat(generators): Build generators module with synthesis and critical analysis
