# Session 4 Plan - Generators Module

**Status**: ⏳ PLANNING
**Prerequisites**: Session 3 complete ✅

---

## What I'm Going to Build

Two generators that turn raw research outputs into living truth documents:

1. **Latest Generator** (`/core/generators/latest_generator.py`)
   - Reads all researcher outputs from a session's drops
   - Synthesizes into single `latest.md` file
   - Handles invalidation (strikethrough when new contradicts old)
   - Updates incrementally as new drops arrive

2. **Session Metadata Generator** (`/core/generators/session_metadata_generator.py`)
   - Creates `session-metadata.json` (session-level index)
   - Creates `drop-metadata.json` (per-drop metadata)
   - Enables progressive disclosure (scan metadata before loading full content)

---

## How It Will Work

### Latest Generator Flow

```
Input: All drops in a session
├── drop-1/
│   ├── researcher-1-output.md (2500 tokens)
│   ├── researcher-2-output.md (3200 tokens)
│   └── user-context.md
├── drop-2/
│   ├── researcher-3-output.md (4100 tokens)
│   └── user-context.md
└── drop-3/
    └── researcher-4-output.md (2800 tokens)

Process:
1. Load all researcher-*-output.md files
2. Combine user contexts from each drop
3. Send to GPT-5 with synthesis prompt
4. Detect contradictions (new vs old info)
5. Apply invalidation (strikethrough old)
6. Output: latest.md (living truth document)

Output Structure (latest.md):
# Session: {hypothesis}

## Strategic Context
{Synthesized user context from all drops}

## Key Findings
1. Finding A (from drop-1, researcher-1)
2. ~~Finding B~~ (invalidated by drop-3, researcher-4)
3. Finding C (from drop-2, researcher-3)

## Sources
- All sources consolidated
- Deduplicated
- Organized by relevance

## Confidence Levels
- High confidence: Findings A, C
- Medium confidence: Finding D
- Invalidated: Finding B

## Evolution
- Drop 1: Initial hypothesis exploration
- Drop 2: Deeper dive into Finding C
- Drop 3: Invalidated Finding B, confirmed A
```

### Metadata Generator Flow

```
Session Metadata (session-metadata.json):
{
  "session_id": "session-1-mlops-evaluation",
  "hypothesis": "MLOps platforms reduce deployment time",
  "created_at": "2024-11-06T10:00:00Z",
  "last_updated": "2024-11-06T15:30:00Z",
  "total_drops": 3,
  "total_researchers": 4,
  "total_tokens": 12600,
  "total_cost": 0.85,
  "drop_summary": [
    {
      "drop_id": "drop-1",
      "created_at": "2024-11-06T10:15:00Z",
      "researchers": 2,
      "tokens": 5700,
      "cost": 0.32
    },
    ...
  ]
}

Drop Metadata (drop-1/drop-metadata.json):
{
  "drop_id": "drop-1",
  "created_at": "2024-11-06T10:15:00Z",
  "user_context": {
    "strategic_why": "Need to justify MLOps investment to leadership",
    "decision_context": "Q1 2025 budget planning"
  },
  "researchers": [
    {
      "researcher_id": "researcher-1",
      "output_file": "researcher-1-output.md",
      "token_count": 2500,
      "sources_count": 12,
      "cost": 0.15,
      "runtime_seconds": 45.2
    },
    {
      "researcher_id": "researcher-2",
      "output_file": "researcher-2-output.md",
      "token_count": 3200,
      "sources_count": 18,
      "cost": 0.17,
      "runtime_seconds": 52.8
    }
  ],
  "total_tokens": 5700,
  "total_cost": 0.32
}
```

---

## Key Implementation Details

### 1. Invalidation Logic (Critical)

**How to detect contradictions:**
- Use `/prompts/critical-analyst.md` to identify conflicts
- Compare new findings against existing `latest.md`
- Flag contradictions with confidence levels
- User-requested: Strikethrough old, keep both visible

**Invalidation format:**
```markdown
## Market Size
- ~~The MLOps market was $1.2B in 2023~~ (Updated in Drop 3)
- The MLOps market is $2.2B in 2024 (Grand View Research, Drop 3)
```

### 2. Synthesis Strategy (GPT-5 Context Window)

**Budget constraints:**
- GPT-5 input limit: 272K tokens
- Each researcher output: 2-5K tokens
- Safe assumption: Can load 50+ researcher outputs

**Synthesis approach:**
- Load ALL researcher outputs (no truncation needed for MVP)
- Include user context from each drop (strategic WHY evolution)
- Synthesis prompt from `/prompts/latest-generator.md`
- Output: Coherent narrative, not just concatenation

### 3. Progressive Disclosure Pattern

**Why this matters:**
- Future sessions need to scan past work quickly
- Don't want to load all `latest.md` files into context
- Metadata enables: "Show me all sessions about MLOps" → scan JSON, load only relevant `latest.md`

**Implementation:**
```python
# Quick scan (no API calls)
sessions = load_all_session_metadata()  # Just read JSON files
mlops_sessions = [s for s in sessions if "mlops" in s["hypothesis"].lower()]

# Selective load (only when needed)
for session in mlops_sessions:
    latest_md = load_latest(session["session_id"])  # Now load full markdown
    # Process...
```

---

## Files I'll Create

```
core/generators/
├── __init__.py                          # Package exports
├── latest_generator.py                  # Synthesis + invalidation (~250 lines)
└── session_metadata_generator.py        # Metadata creation (~150 lines)

tests/
├── test_generators.py                   # Isolation tests (~300 lines)
├── test_full_workflow.py                # End-to-end: HQ → Research → Generate (~200 lines)
└── demos/
    └── demo_generator.py                # Manual testing script

docs/
├── guidelines/
│   └── generator-integration-2025-11-06.md    # Integration docs
└── sessions/
    └── session-4-generators.md                # Session summary (after complete)
```

---

## Testing Strategy (Won't Burn Tokens)

### ONE Real Test
**`test_synthesize_multiple_drops`** - Real GPT-5 API call
- Creates 2-3 mock researcher outputs
- Runs full synthesis
- Validates `latest.md` is coherent
- **Cost**: ~$0.10-0.15 (one-time validation)

### MOCKED Tests (No API Calls)
1. `test_invalidation_detection` - Use fixture with known contradictions
2. `test_metadata_generation` - File I/O only, no LLM
3. `test_progressive_disclosure` - JSON serialization only
4. `test_handles_empty_drops` - Edge case handling
5. `test_session_metadata_format` - Schema validation

**Fixtures to create:**
- `/tests/fixtures/sample_researcher_outputs/` (3-4 markdown files)
- `/tests/fixtures/sample_latest.md` (pre-synthesized output)
- `/tests/fixtures/contradictory_findings.json` (known conflicts)

---

## Key Decisions to Make

### 1. Invalidation Granularity
**Question**: Invalidate at sentence level or finding level?

**Options**:
- Sentence-level: More precise, harder to implement
- Finding-level: Simpler, may strikethrough too much

**Leaning toward**: Finding-level for MVP (simpler, clearer to user)

### 2. Synthesis Model
**Question**: Use GPT-5 or Claude for synthesis?

**Options**:
- GPT-5: 272K context, already using for research
- Claude Sonnet 4.5: 200K context, better at synthesis

**Leaning toward**: GPT-5 for consistency (all outputs use same model family)

### 3. Metadata Storage
**Question**: JSON files or lightweight database (SQLite)?

**Options**:
- JSON: Simple, human-readable, git-friendly
- SQLite: Queryable, faster for large projects

**Leaning toward**: JSON for MVP (matches file-based pattern)

---

## Integration Points

### From Researcher (Session 3)
**What I receive:**
- `researcher-{id}-output.md` files in drop folder
- ResearchOutput metadata (sources, tokens, cost)
- User context from HQ

### To UI (Session 5)
**What I provide:**
- `latest.md` - living truth document
- `session-metadata.json` - quick scan index
- `drop-metadata.json` - per-drop details
- Invalidation markup (strikethrough) that UI can render

---

## Expected Challenges

### Challenge 1: Detecting Contradictions Accurately
**Problem**: GPT-5 might hallucinate contradictions or miss real ones
**Mitigation**: Use critical-analyst.md prompt with strict criteria, require high confidence

### Challenge 2: Maintaining Markdown Formatting
**Problem**: Synthesis might break markdown structure
**Mitigation**: Validate output with markdown parser, add structure tests

### Challenge 3: Incremental Updates
**Problem**: Adding drop-4 shouldn't require re-synthesizing drops 1-3
**Mitigation**: Load existing `latest.md` + new drop, append/update only

### Challenge 4: Token Budget for Many Drops
**Problem**: 50+ drops might exceed 272K tokens
**Mitigation**: For MVP, assume <50 drops per session (safe for 2-5K outputs)

---

## Success Criteria

**Session 4 is complete when:**
- ✅ Latest generator synthesizes 3+ researcher outputs into coherent `latest.md`
- ✅ Invalidation logic correctly strikethroughs contradicted findings
- ✅ Session metadata includes all required fields
- ✅ Drop metadata accurately reflects researcher outputs
- ✅ ONE real test passes (validates GPT-5 synthesis works)
- ✅ MOCKED tests cover edge cases without API calls
- ✅ Integration test shows HQ → Research → Generate workflow works

**Won't burn tokens because:**
- Only 1 real synthesis test (~$0.10-0.15)
- All other tests use fixtures from `/tests/fixtures/`
- Demo script uses pre-captured outputs (no API calls unless explicitly run)

---

## Timeline Estimate

**Phase 1: Latest Generator** (~2 hours)
- Build synthesis logic
- Implement invalidation detection
- Create output formatting

**Phase 2: Metadata Generator** (~1 hour)
- Session metadata generation
- Drop metadata generation
- JSON schema validation

**Phase 3: Testing** (~1.5 hours)
- Create fixtures
- Write mocked tests
- One real synthesis test
- Integration test with HQ + Researcher

**Phase 4: Documentation** (~30 min)
- Update CLAUDE.md
- Write session summary
- Create integration guide

**Total: ~5 hours** (assuming no major blockers)

---

## After Session 4

**What's left:**
- Session 5: UI (chat interface, research flag toggle, progress indicators)
- After Session 5: Full GTM Factory MVP complete!

**Then:**
- Real user testing
- Fix bugs discovered in real usage
- Add nice-to-haves (caching, streaming, custom search providers)

---

**Ready to build?** Yes, but will be careful with token usage:
- ONE real test only
- MOCK everything else
- Demo script won't auto-run (you run it manually if needed)
