# GTM Factory - Complete Architecture & Implementation Guide

**Date**: 2024-11-06
**Purpose**: Complete handoff document for Claude Code sessions
**Context**: This captures 2 full Claude Desktop sessions of architectural decisions, user context, and implementation details

---

## Table of Contents

1. [Project Vision & User Context](#project-vision)
2. [Complete Architecture](#architecture)
3. [Critical Design Decisions & Rationale](#decisions)
4. [File Structures (Detailed)](#file-structures)
5. [Implementation Roadmap](#roadmap)
6. [What's Built vs What's Next](#status)
7. [Anthropic Best Practices Applied](#best-practices)
8. [Technical Specifications](#tech-specs)
9. [The User Experience Flow](#ux-flow)
10. [Documentation System](#documentation)

---

## Project Vision & User Context {#project-vision}

### What This Is

**GTM Factory** (formerly Helldiver) - A go-to-market operating system that enables small teams (2-5 people) to operate with the effectiveness of much larger GTM organizations (20-30 people).

**The Core Problem**: Knowledge is scattered across tools, departments, and people. This creates distortion like a "telephone game" - strategic intent gets lost in translation between research, planning, and execution. Teams waste time re-researching the same companies, forgetting past learnings, and operating without strategic context.

**The Solution**: A research system where:
- You chat with an AI HQ that extracts strategic context through Socratic questioning
- Research runs autonomously and creates structured "drops" 
- Knowledge compounds into "living truth" documents that handle invalidation
- Future sessions can reference past research without re-reading everything
- Small teams gain information asymmetry advantage (like Standard Oil's vertical integration)

### User Background

**Ben** - Building this for YC application
- **Background**: Naval Academy CS degree, former Naval Aviator
- **Current**: GTM Automation Manager at Tanium (designed comp plans driving significant pipeline/revenue growth)
- **Experience**: Built Navy RAG systems, classical education assistants, podcast generation tools
- **Learning**: Tried complex knowledge graph (Graphiti) approach, realized simpler file-based system is better MVP

**Key Insight From User's Journey**: 
- Started with sophisticated Neo4j/Graphiti knowledge graph
- Discovered NER (Named Entity Recognition) doesn't work for meta-entities (ResearchFinding, StrategicIntent)
- Pivoted to file-based approach following Anthropic's memory tool pattern
- Lesson: Start simple, add complexity only when needed

### The Vision

Enable a paradigm shift toward operational perfection previously impossible regardless of team size. The competitive moat: controlling the entire workflow and capturing "action sequences" that compound learning across campaigns.

**This is Claude Desktop Projects but for GTM research** - each research session is like a Deep Research session that produces artifacts that persist and compound.

---

## Complete Architecture {#architecture}

### The High-Level Flow

```
User starts conversation
    ↓
HQ Socratic Questioning (Phase 1)
    ├─ Asks probing questions
    ├─ Extracts strategic WHY (not just WHAT)
    ├─ Captures context in real-time
    └─ Detects when user is ready to research
    ↓
User flips "Research" flag
    ↓
HQ Proposes Research Plan (Phase 2)
    ├─ Determines 1-4 researchers needed
    ├─ Defines what each will research
    └─ User approves/adjusts plan
    ↓
Research Execution (Phase 3)
    ├─ Researchers work in parallel
    ├─ Each produces 3-5K token output
    ├─ Critical Analyst reviews quality
    └─ Drop files created with full context
    ↓
Synthesis (Phase 4)
    ├─ latest.md Generator reads all drops
    ├─ Synthesizes new information
    ├─ Handles invalidation (strikethrough old info)
    └─ Updates living truth document
    ↓
Back to Conversation (Phase 5)
    ├─ HQ shows what was found
    ├─ User reviews, asks questions
    └─ Triggers next drop OR finishes session
    ↓
Session Complete
    ├─ session-metadata.json created
    ├─ session-index.json updated
    └─ All artifacts persist for future sessions
```

### Progressive Disclosure Pattern

**Future sessions don't re-read everything**:

```
New HQ session starts (e.g., "Build LinkedIn ads for Arthur.ai")
    ↓
Scan session-index.json (lightweight metadata)
    ├─ Find relevant past sessions
    └─ "Oh, session-1 has partnership hypothesis"
    ↓
Load ONLY latest.md from session-1 (not individual drops)
    ├─ Get strategic context: "Target finance, lead with compliance"
    └─ Use this context for NEW research about LinkedIn ads
    ↓
New research adds to knowledge base
```

**This is Anthropic's progressive disclosure principle** - metadata first, full content only when needed, never load everything.

### The Five AI Components

**1. HQ Orchestrator**
- **Job**: Socratic questioning, research planning, session coordination
- **Context**: Project context, past session metadata, current conversation
- **Output**: user-context.md (strategic WHY), research plans, session state
- **Prompt**: `/prompts/hq-orchestrator.md`

**2. General Researcher** (1-4 per drop, dynamic)
- **Job**: Deep web research on assigned topic
- **Tools**: GPT Researcher library (web search, web fetch)
- **Context**: Research brief from HQ, strategic context
- **Output**: researcher-N-output.md (3-5K tokens, dense, structured)
- **Prompt**: `/prompts/general-researcher.md`

**3. Critical Analyst**
- **Job**: Quality check, gap identification, contradiction spotting
- **Context**: All researcher outputs from drop
- **Output**: critical-analysis.md (what's missing, quality assessment)
- **Prompt**: `/prompts/critical-analyst.md`

**4. latest.md Generator** (THE HARD ONE)
- **Job**: Synthesize all drops into one source of truth
- **Skills Needed**:
  - Synthesis (combine without duplication)
  - Invalidation detection (mark contradictions)
  - Additive reasoning (keep old + add new)
  - Pruning (remove invalidated info)
- **Context**: Previous latest.md + all new drops + conversation history
- **Output**: Updated latest.md with strikethrough for invalidated info
- **Prompt**: `/prompts/latest-generator.md`

**5. Session Metadata Generator**
- **Job**: Create lightweight summary for discovery
- **Context**: All drops, latest.md, conversation
- **Output**: session-metadata.json (topics, key findings summary, status)
- **Prompt**: `/prompts/session-metadata-generator.md`

### Why This Architecture Works

**Follows Anthropic Principles**:
1. ✅ **Start simple** - File-based, not knowledge graph for MVP
2. ✅ **Orchestrator-workers** - HQ coordinates, specialists execute
3. ✅ **Human oversight** - User approves research plans, reviews between drops
4. ✅ **Observable decisions** - All reasoning logged, drops are inspectable
5. ✅ **Modular** - Each component has single responsibility
6. ✅ **Token budgets** - 3-5K per output prevents context pollution
7. ✅ **Progressive disclosure** - Metadata → latest.md → drops (never load all)

---

## Critical Design Decisions & Rationale {#decisions}

### Decision 1: Chat UI Over CLI

**Chose**: Web-based chat interface (Streamlit or custom)
**Not**: Command-line interface

**Why**:
- Better for extracting strategic context through natural conversation
- Research flag toggle is more intuitive than CLI flags
- Progress indicators during research improve UX
- Easier to demo for YC application
- User can review conversation history easily

**Trade-offs**:
- More frontend work
- But: Better UX is worth it for this use case

---

### Decision 2: File-Based Storage Over Graphiti Knowledge Graph

**Chose**: File-based memory tool pattern
**Not**: Neo4j + Graphiti knowledge graph

**Why We Tried Graphiti First**:
- Seemed perfect: temporal knowledge graph, auto-extraction, MCP support
- Promised: Entity deduplication, relationship tracking, semantic search

**Why We Pivoted Away**:
- **NER Limitation**: Graphiti is Named Entity Recognition, not Conceptual Entity Extraction
  - ✅ Works for: Company names, Tool names, People (things MENTIONED in text)
  - ❌ Fails for: ResearchFinding, StrategicIntent, ExecutionOutcome (things that ARE the text)
- **Complexity**: 17+ LLM calls per episode, forking would be high maintenance
- **Overkill for MVP**: File-based is simpler, human-readable, sufficient

**What We Chose Instead**:
- File-based storage (Anthropic's memory tool pattern)
- Structured markdown + JSON files
- Human-readable, git-friendly
- Can add graph layer later if needed

**Lesson**: Question whether complexity is necessary before implementing

---

### Decision 3: Dynamic Researchers (1-4) Over Fixed Workers

**Chose**: HQ decides 1-4 researchers per drop based on complexity
**Not**: Fixed 4 workers (Academic, Industry, Tool, Critical) every time

**Why**:
- Simple queries waste tokens with 4 workers: "What's Arthur's tech stack?" needs 1 researcher
- Complex queries need specialization: "Evaluate partnership fit" needs 3-4 researchers
- HQ is smart enough to match complexity to research scope
- Using GPT Researcher library which handles depth already

**How It Works**:
- HQ analyzes query complexity
- Proposes 1-4 researchers with specific focus areas
- User approves/adjusts
- Simple = 1 researcher, Complex = 4 researchers

---

### Decision 4: Self-Contained Drops With Full Context

**Chose**: Each drop folder contains user-context.md + conversation-history.md
**Not**: Separate context files or context only in session root

**Why**:
- Each drop = complete snapshot of that moment in time
- User context evolves between drops (new information, refined goals)
- Can look back and understand exactly what you were thinking at drop-1 vs drop-3
- Enables invalidation detection (why did we think X in drop-1 but Y in drop-3?)
- Self-contained = easier to package for execution agents later

**Structure**:
```
drop-1/
├── researcher-1-output.md      # Research findings
├── researcher-2-output.md      # More research
├── user-context.md             # WHY this research matters
├── conversation-history.md     # Chat that led here
├── critical-analysis.md        # Quality check
└── drop-metadata.json          # Lightweight stub
```

---

### Decision 5: latest.md as "Living Truth"

**Chose**: Single source of truth that synthesizes + invalidates
**Not**: Individual drop files as source of truth

**Why**:
- Future sessions don't re-read all drops (token efficient)
- Handles invalidation explicitly (strikethrough old info)
- Always current, never stale
- Human-readable summary of ALL research
- Enables progressive disclosure (metadata → latest.md → drops)

**How It Works**:
After each drop:
1. Read current latest.md (or create if first drop)
2. Read new drop research
3. Synthesize: Add new info + keep relevant old info
4. Invalidate: Strikethrough contradictions
5. Cite: Reference which drop each fact came from

**Example Evolution**:
```markdown
## After Drop 1:
Sales cycle: 6-9 months [drop-1]

## After Drop 2 (contradicts drop 1):
~~Sales cycle: 6-9 months [drop-1]~~ 
Sales cycle: 3-6 months for partnerships [drop-2]

## What Got Invalidated:
- Partnership team moves faster than general sales
```

---

### Decision 6: Progressive Disclosure (Anthropic Pattern)

**Chose**: Metadata → latest.md → drops (lazy loading)
**Not**: Loading all files upfront

**Why**:
- Context window is finite
- Most queries only need latest.md
- Metadata enables fast scanning without reading content
- Only load drops when debugging or needing original sources

**How It Works**:
```python
# Session start
session_index = load("session-index.json")  # <2KB, all sessions
relevant_sessions = find_relevant(query, session_index)

# Load just-in-time
for session in relevant_sessions:
    latest = load(f"{session}/latest.md")  # ~1-2K tokens
    use_for_context(latest)
    
# Only if needed:
if user_asks_for_sources:
    drops = load_all_drops(session)  # Heavy, rare
```

**Token Savings**: 10 sessions × 1.5K (latest.md) = 15K tokens vs 10 sessions × 20K (all drops) = 200K tokens

---

### Decision 7: Token Budgets (3-5K per Researcher)

**Chose**: Hard limit of 3-5K tokens per researcher output
**Not**: Unlimited or prose-heavy outputs

**Why**:
- Prevents context pollution (Anthropic principle)
- Forces dense, structured thinking
- 10 drops × 5K = 50K tokens total (leaves room for conversation)
- Matches Anthropic's subagent pattern (extensive work, condensed return)

**Enforcement**: Output formatter checks token count, truncates if needed

---

## File Structures (Detailed) {#file-structures}

### Project Root Structure

```
gtm-factory/
├── CLAUDE.md                   # Auto-loaded coordination (concise, actionable)
├── README.md                   # User-facing documentation
├── plugins/
│   ├── onboard.md             # Fast context loading (<10 sec)
│   └── commit.md              # Smart commits with CLAUDE.md updates
├── prompts/                    # AI logic (5 prompts, shared across sessions)
│   ├── hq-orchestrator.md
│   ├── general-researcher.md
│   ├── critical-analyst.md
│   ├── latest-generator.md
│   └── session-metadata-generator.md
├── core/                       # Implementation code (organized by module)
│   ├── hq/
│   │   ├── orchestrator.py
│   │   ├── context_extractor.py
│   │   └── memory_manager.py
│   ├── researcher/
│   │   ├── general_researcher.py
│   │   └── tools.py
│   ├── generators/
│   │   ├── latest_generator.py
│   │   └── session_metadata_generator.py
│   └── utils/
│       ├── file_io.py
│       ├── token_counter.py
│       └── metadata_parser.py
├── projects/                   # Runtime data (gitignored)
│   └── {company-name}/
│       ├── project-context.md
│       ├── session-index.json
│       └── sessions/
│           └── session-{N}-{hypothesis}/
│               ├── drops/
│               ├── latest.md
│               └── session-metadata.json
├── tests/                      # Test suite (mirrors core/ structure)
│   ├── test_examples.py
│   ├── test_hq.py
│   ├── test_researcher.py
│   └── test_generators.py
└── docs/                       # Deep architecture docs (optional, not auto-loaded)
    └── ARCHITECTURE.md         # This file
```

### Drop Folder Structure (Complete)

```
drop-{N}/
├── researcher-1-output.md      # 3-5K tokens, dense markdown
│   ## Research Topic
│   ### Key Findings
│   - Finding 1 [Source: URL]
│   - Finding 2 [Source: URL]
│   ### Data Points
│   - Metric 1: Value
│   - Metric 2: Value
│   ### Sources
│   1. [Title](URL)
│   2. [Title](URL)
│
├── researcher-2-output.md      # (if multiple researchers)
│
├── user-context.md             # Strategic WHY at this moment
│   ## Goal
│   Partner with Arthur.ai for ML monitoring integration
│   
│   ## Why This Matters
│   Their monitoring sits on top of our data layer, sell together
│   
│   ## Success Looks Like
│   Integration partnership, co-marketing, revenue share
│   
│   ## Constraints
│   - Must close in Q1 2025
│   - Need AWS Marketplace presence
│   
│   ## Open Questions Going Into This Drop
│   - Do they have partnership team?
│   - What's typical timeline?
│
├── conversation-history.md     # Chat transcript that led to this drop
│   ## Conversation Leading to Drop {N}
│   
│   **User**: I want to evaluate Arthur.ai
│   **HQ**: Tell me about Arthur.ai - what do they do?
│   **User**: ML monitoring for finance companies
│   **HQ**: What's your goal with this partnership?
│   **User**: Integrate our data layer with their monitoring
│   ...
│
├── critical-analysis.md        # Quality check from Critical Analyst
│   ## Quality Assessment: Drop {N}
│   
│   ### Strengths
│   - Strong sourcing (8 primary sources)
│   - Answered 80% of research questions
│   - High confidence findings
│   
│   ### Gaps Identified
│   - Missing: Partner pricing model
│   - Missing: Decision-maker names
│   - Assumption: Partnership team exists (needs validation)
│   
│   ### Recommendations for Next Drop
│   - Research Head of Partnerships specifically
│   - Validate AWS Marketplace claim
│   
│   ### Overall Quality: HIGH / MEDIUM / LOW
│   HIGH
│
└── drop-metadata.json          # Lightweight stub for scanning
    {
      "drop_number": 1,
      "created": "2025-11-06T14:30:00Z",
      "research_questions": [
        "What is Arthur.ai's partnership model?",
        "Who are their ideal partners?"
      ],
      "researchers_used": 2,
      "confidence": "high",
      "tokens_used": 8400
    }
```

### Session-Level Files

**latest.md** (The Crown Jewel):
```markdown
# Partnership Hypothesis: Arthur.ai

**Last Updated**: Drop 3, 2025-11-06

---

## Strategic Context (Why We Care)

We're targeting Series B ML companies for data infrastructure partnerships. 
Arthur.ai fits because their monitoring layer sits on top of our data layer. 
Integration play = sell together.

**Goal**: Partnership signed by Q1 2025
**Budget**: $50K partnership fee max
**Success**: Co-marketing, revenue share, joint customers

---

## What We Know (Research-Backed)

### Company Profile
- **Founded**: 2018 by ex-Bridgewater engineers [drop-1]
- **Funding**: $42M Series B, TCV led [drop-1]
- **Customers**: 100+ enterprise, finance/healthcare focus [drop-1]
- **Tech Stack**: Python, Kubernetes, API-first [drop-1]
- **Deal Sizes**: $200-500K annually [drop-1]

### Partnership Mechanics
- **Timeline**: ~~6-9 months typical [drop-1]~~ 3-6 months for partnerships [drop-2]
- **Partner Tiers**: Integration, Reseller, Technology [drop-2]
- **Requirements**: AWS Marketplace presence, joint customer reference [drop-2]
- **AWS Marketplace**: Confirmed present [drop-2]

### Decision Makers
- **Head of Partnerships**: Jane Smith (joined 3 months ago) [drop-3]
- **CTO**: John Doe (technical approval required) [drop-3]
- **Warm Intro Path**: Via AWS connection (both use AWS Marketplace) [drop-3]

### Strategic Assessment
- **Partnership Viability**: HIGH [drop-3 analysis]
- **Technical Fit**: STRONG (complementary, not competitive) [drop-3]
- **Timeline Risk**: LOW (fast-moving partnership team) [drop-2, drop-3]
- **Key Blockers**: None identified

---

## What Got Invalidated

### Sales Cycle Assumption
- **Initial**: 6-9 months typical sales cycle [drop-1]
- **Corrected**: 3-6 months for partnerships [drop-2]
- **Why**: Partnership team operates faster than general sales
- **Impact**: Can close in Q1 2025 timeframe

---

## Open Questions

**High Priority**:
- [ ] Partner pricing model (not publicly available)
- [ ] Q1 2025 partnership priorities (need to confirm timing)

**Medium Priority**:
- [ ] Integration effort estimate (engineering hours)
- [ ] Co-marketing budget availability

**Low Priority**:
- [ ] Customer overlap analysis

---

## Next Steps

1. **Week 1**: Warm intro via AWS connection
2. **Week 2**: Discovery call with Jane Smith (Head of Partnerships)
3. **Week 3**: Technical deep dive with John Doe (CTO)
4. **Week 4**: Proposal draft

**Talking Points for Discovery**:
- Lead with compliance/explainability angle (finance focus)
- Emphasize AWS Marketplace synergy
- Position as integration (not competitive)

---

## Sources Summary

- **Primary Sources**: 8 company docs, 4 analyst reports, 6 industry articles
- **Confidence Level**: High (corroborated across multiple sources)
- **Last Research**: Drop 3, 2025-11-06
```

**session-metadata.json**:
```json
{
  "session_id": "session-1-partnership-hypothesis",
  "created": "2025-11-06T10:00:00Z",
  "last_updated": "2025-11-06T14:30:00Z",
  "research_goal": "Evaluate Arthur.ai for partnership opportunity",
  "topics_covered": [
    "company_profile",
    "tech_stack",
    "partnership_mechanics",
    "decision_makers",
    "timeline_estimation"
  ],
  "key_findings_summary": "High partnership viability. 3-6 month timeline. AWS Marketplace presence. Strong technical fit.",
  "drops_completed": 3,
  "total_researchers": 7,
  "status": "complete",
  "next_actions": [
    "Warm intro via AWS",
    "Schedule discovery call"
  ]
}
```

**session-index.json** (Project-level):
```json
{
  "project": "arthur-ai",
  "sessions": [
    {
      "id": "session-1-partnership-hypothesis",
      "goal": "Evaluate partnership opportunity",
      "topics": ["company_profile", "partnerships"],
      "status": "complete",
      "key_finding": "High viability, 3-6 months",
      "path": "sessions/session-1-partnership-hypothesis",
      "created": "2025-11-06T10:00:00Z"
    },
    {
      "id": "session-2-linkedin-ads",
      "goal": "Research LinkedIn ad best practices for Series B ML audience",
      "topics": ["ad_psychology", "targeting", "creative"],
      "status": "in_progress",
      "path": "sessions/session-2-linkedin-ads",
      "created": "2025-11-10T09:00:00Z"
    }
  ]
}
```

---

## Implementation Roadmap {#roadmap}

### Phase 1: Core HQ (Week 1)

**Goal**: Build conversational orchestrator

**Components**:
1. **orchestrator.py** - Main HQ class
   - Socratic conversation handler
   - Research plan generation
   - State management
   - Uses `/prompts/hq-orchestrator.md`

2. **context_extractor.py** - Extract strategic WHY
   - Parses conversation for goals, constraints, success criteria
   - Generates user-context.md
   - Updates as conversation evolves

3. **memory_manager.py** - File-based persistence
   - Creates session directories
   - Manages conversation-history.md
   - Loads past session metadata
   - Implements progressive disclosure

**Testing**:
- Can have Socratic conversation
- Extracts strategic context accurately
- Detects when user is ready to research
- Generates valid research plans

---

### Phase 2: Research Execution (Week 1-2)

**Goal**: Execute research and create drops

**Components**:
1. **general_researcher.py** - Wrapper for GPT Researcher
   - Takes research brief from HQ
   - Executes web research
   - Formats output (3-5K tokens)
   - Uses `/prompts/general-researcher.md`

2. **tools.py** - Web tools
   - web_search integration
   - web_fetch integration
   - Token counting
   - Output formatting

3. **Drop file creation**:
   - researcher-N-output.md
   - critical-analysis.md
   - drop-metadata.json

**Testing**:
- Researchers produce 3-5K token outputs
- Outputs are dense and structured
- Citations are included
- Token budget is enforced

---

### Phase 3: Synthesis & Metadata (Week 2)

**Goal**: Create latest.md and session metadata

**Components**:
1. **latest_generator.py** - The hard one
   - Reads all drops from session
   - Reads current latest.md (if exists)
   - Synthesizes new information
   - Handles invalidation (strikethrough)
   - Cites sources ([drop-N])
   - Uses `/prompts/latest-generator.md`

2. **session_metadata_generator.py**
   - Creates session-metadata.json
   - Updates session-index.json
   - Uses `/prompts/session-metadata-generator.md`

**Testing**:
- latest.md accurately synthesizes drops
- Invalidation works (strikethroughs)
- Citations are correct
- Metadata is accurate

---

### Phase 4: Chat UI (Week 2-3)

**Goal**: Build user interface

**Components**:
1. **Streamlit app** OR custom web app
   - Chat interface
   - Research flag toggle
   - Progress indicators
   - Drop review interface

2. **Integration**:
   - Wire HQ orchestrator
   - Wire researchers
   - Wire generators
   - State management

**Testing**:
- End-to-end flow works
- UI is intuitive
- Progress updates work
- Can review drops

---

### Phase 5: Polish & Testing (Week 3)

**Goal**: Make it production-ready

**Tasks**:
- Error handling
- Edge cases
- Token optimization
- UI polish
- Demo preparation

---

## What's Built vs What's Next {#status}

### Session 1: Foundation ✅ COMPLETE

**Built**:
- `/prompts/hq-orchestrator.md` - HQ AI logic
- `/prompts/general-researcher.md` - Researcher AI logic
- `/prompts/critical-analyst.md` - Analyst AI logic
- `/prompts/latest-generator.md` - Synthesis AI logic
- `/prompts/session-metadata-generator.md` - Metadata AI logic
- `/projects/example-company/` - Example project structure
- `/tests/test_examples.py` - Test scenarios

**Issues from Session 1**:
- Created extra folders: `agents/`, root `utils/`, `logs/` (need cleanup)
- Scattered MD files in root (need archiving)
- No onboard plugin yet
- No commit plugin yet

---

### Session 1.5: Cleanup & Plugins ⏳ NEXT

**Goal**: Clean codebase, add coordination plugins

**Tasks**:
1. Remove redundant folders (`agents/`, root `utils/`, `logs/`)
2. Archive Session 1 docs to `/docs/archive/session-1/`
3. Create `/plugins/onboard.md`
4. Create `/plugins/commit.md`
5. Update CLAUDE.md
6. Commit everything

**Success Criteria**:
- Root only has CLAUDE.md and README.md
- Onboard plugin works
- Commit plugin works
- CLAUDE.md is complete

---

### Session 2: HQ Orchestrator ⏳ UPCOMING

**Goal**: Build conversational orchestrator

**Tasks**:
1. Build `/core/hq/orchestrator.py`
2. Build `/core/hq/context_extractor.py`
3. Build `/core/hq/memory_manager.py`
4. Write tests in `/tests/test_hq.py`

**Dependencies**: Session 1.5 complete

---

### Session 3: Research Execution ⏳ UPCOMING

**Goal**: Build research execution layer

**Tasks**:
1. Build `/core/researcher/general_researcher.py`
2. Build `/core/researcher/tools.py`
3. Write tests in `/tests/test_researcher.py`

**Dependencies**: Session 2 complete (or can run in parallel)

---

### Session 4: Synthesis & Metadata ⏳ UPCOMING

**Goal**: Build synthesis layer

**Tasks**:
1. Build `/core/generators/latest_generator.py`
2. Build `/core/generators/session_metadata_generator.py`
3. Write tests in `/tests/test_generators.py`

**Dependencies**: Session 3 complete

---

### Session 5: Chat UI ⏳ UPCOMING

**Goal**: Build user interface

**Tasks**:
1. Build Streamlit app (or web app)
2. Wire all components together
3. End-to-end testing

**Dependencies**: Sessions 2-4 complete

---

## Anthropic Best Practices Applied {#best-practices}

### 1. CLAUDE.md Pattern

**From**: [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

**Applied**:
- CLAUDE.md is auto-loaded by Claude Code
- Contains: project context, architecture, current state, commands, gotchas
- Concise and human-readable (not a dump)
- Updated by /commit plugin after each session

**Quote**: "CLAUDE.md is a special file that Claude automatically pulls into context when starting a conversation. This makes it an ideal place for documenting repository etiquette, developer environment setup, and any unexpected behaviors particular to the project."

---

### 2. Progressive Disclosure (Context Engineering)

**From**: [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Applied**:
- Metadata files < 2KB for fast scanning
- Load latest.md on-demand (not all drops)
- Only load full drops when debugging
- Session index enables discovery without loading content

**Quote**: "Rather than one agent attempting to maintain state across an entire project, specialized sub-agents can handle focused tasks with clean context windows...Each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)."

---

### 3. Memory Tool Pattern

**From**: [Memory Tool Documentation](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Applied**:
- File-based persistence
- Sessions survive restarts
- No database required
- Human-readable artifacts

**Quote**: "We released a memory tool in public beta on the Claude Developer Platform that makes it easier to store and consult information outside the context window through a file-based system. This allows agents to build up knowledge bases over time, maintain project state across sessions, and reference previous work without keeping everything in context."

---

### 4. Orchestrator-Workers Pattern

**From**: [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)

**Applied**:
- HQ orchestrates (high-level planning)
- Researchers execute (deep work)
- Generators synthesize (condensed output)
- Each agent has single responsibility

**Quote**: "Prompt chaining decomposes a task into a sequence of steps, where each LLM call processes the output of the previous one."

---

### 5. Token Budgets

**From**: [Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Applied**:
- 3-5K tokens per researcher output (hard limit)
- Prevents context pollution
- Forces dense, structured thinking
- Leaves room for conversation

**Quote**: "Context is a critical but finite resource for AI agents...the goal is to curate the smallest, most relevant set of information to maximize agent performance."

---

### 6. Start Simple

**From**: [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)

**Applied**:
- File-based storage (not knowledge graph)
- Streamlit UI (not custom framework)
- GPT Researcher library (not custom)
- Can add complexity later

**Quote**: "We recommend finding the simplest solution possible, and only increasing complexity when needed. This might mean not building agentic systems at all."

---

### 7. Human Oversight

**From**: [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)

**Applied**:
- User approves research plans
- User reviews between drops
- User decides when to finish
- All decisions are observable

**Quote**: "The autonomous nature of agents means higher costs, and the potential for compounding errors. We recommend extensive testing in sandboxed environments, along with the appropriate guardrails."

---

## Technical Specifications {#tech-specs}

### Tech Stack

**LLM**: Claude Sonnet 4.5 (via Anthropic API)
- Model: `claude-sonnet-4-20250514`
- Max tokens: 8000 per call
- Streaming: Yes (for real-time updates)

**Research**: GPT Researcher Library
- Web search: DuckDuckGo (or configurable)
- Web scraping: BeautifulSoup
- Output: Markdown reports

**UI**: Chat Interface
- Option 1: Streamlit (faster to build)
- Option 2: Custom web app (React/Next.js)

**Storage**: File-Based
- Format: Markdown + JSON
- Structure: Projects → Sessions → Drops
- Git-friendly

**Dependencies**:
```
anthropic>=0.40.0
gpt-researcher>=0.7.0
streamlit>=1.28.0  # if using Streamlit
pydantic>=2.0.0
```

---

### API Integration

**Anthropic Messages API**:
```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=8000,
    messages=[
        {"role": "user", "content": "Your prompt here"}
    ]
)

# For streaming:
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**GPT Researcher**:
```python
from gpt_researcher import GPTResearcher

researcher = GPTResearcher(
    query="Research topic",
    report_type="research_report",
    config_path=None  # Use defaults
)

report = await researcher.conduct_research()
```

---

### File I/O Patterns

**Creating a drop**:
```python
import os
import json
from pathlib import Path

def create_drop(session_path, drop_number, research_outputs, user_context, conversation):
    drop_path = Path(session_path) / "drops" / f"drop-{drop_number}"
    drop_path.mkdir(parents=True, exist_ok=True)
    
    # Save researcher outputs
    for i, output in enumerate(research_outputs, 1):
        (drop_path / f"researcher-{i}-output.md").write_text(output)
    
    # Save context
    (drop_path / "user-context.md").write_text(user_context)
    (drop_path / "conversation-history.md").write_text(conversation)
    
    # Save metadata
    metadata = {
        "drop_number": drop_number,
        "created": datetime.now().isoformat(),
        "researchers_used": len(research_outputs),
        ...
    }
    (drop_path / "drop-metadata.json").write_text(json.dumps(metadata, indent=2))
```

**Progressive disclosure**:
```python
def find_relevant_sessions(query, project_path):
    # Load index (lightweight)
    index = json.loads((project_path / "session-index.json").read_text())
    
    # Scan metadata
    relevant = []
    for session in index["sessions"]:
        if query_matches(query, session["topics"]):
            relevant.append(session)
    
    # Load only latest.md for relevant sessions
    context = []
    for session in relevant:
        latest_path = project_path / session["path"] / "latest.md"
        context.append(latest_path.read_text())
    
    return context  # Much smaller than loading all drops
```

---

## The User Experience Flow {#ux-flow}

### New Research Session

**User opens chat interface**:

```
GTM Factory

Chat with HQ to start research...

[Chat input box]
[Research mode: OFF] 
```

**User types**: "I want to evaluate Arthur.ai for partnership"

**HQ responds**:
```
HQ: Tell me about Arthur.ai - what do they do and why are you interested?
```

**User**: "They do ML monitoring for finance companies. I want to integrate our data layer with their monitoring and sell together."

**HQ**: "Great context. What would success look like for this partnership?"

**User**: "Integration partnership, co-marketing, revenue share. Need to close by Q1 2025."

**HQ**: "Got it. What constraints should I know about?"

**User**: "Budget is $50K max for partnership fee. They need to have AWS Marketplace presence."

**HQ**: "Perfect. Based on what you've told me, I can research:
- Company profile and tech stack
- Partnership model and typical timelines
- Decision-makers and warm intro paths

Would you like me to start researching these areas?"

**User clicks**: [Research mode: ON]

---

### Research Execution

**UI shows**:
```
Research Plan: Arthur.ai Partnership Evaluation

Researcher 1: Company profile, funding, tech stack
Researcher 2: Partnership mechanics and timelines  
Researcher 3: Decision-makers and contact strategy

[Adjust Plan] [Start Research]
```

**User clicks**: [Start Research]

**UI shows progress**:
```
Researching...

✅ Researcher 1 complete (4.2K tokens)
✅ Researcher 2 complete (3.8K tokens)
⏳ Researcher 3 running...

Estimated time: 2 minutes
```

---

### Review Results

**Research completes, UI shows**:
```
Drop 1 Complete

Key Findings:
- Arthur.ai is Series B, $42M raised, 100+ enterprise customers
- Partnership timeline: 3-6 months
- Head of Partnerships: Jane Smith (hired 3 months ago)
- AWS Marketplace: ✅ Present

Critical Analysis:
- Quality: HIGH (8 primary sources)
- Gaps: Partner pricing not public, need Q1 availability confirmation

[View Full Research] [Continue Research] [Finish Session]
```

**User clicks**: [View Full Research] → sees all drop files

**User asks**: "Can we make this timeline work for Q1?"

**HQ**: "Based on the research, 3-6 months is typical for partnerships, and they have a dedicated partnership team (Jane Smith). Since it's currently November, a Q1 close is feasible if we start immediately. 

Would you like me to research:
- Jane Smith's background and priorities
- Q1 partnership capacity
- Warm intro strategies?"

**User**: "Yes, let's do another drop focused on Jane and Q1 feasibility"

**User clicks**: [Research mode: ON]

---

### Session Complete

**After all drops, HQ shows**:
```
Session Summary: Arthur.ai Partnership Evaluation

Drops Completed: 3
Total Researchers: 7
Time: 45 minutes

Key Takeaway:
HIGH partnership viability. 3-6 month timeline achievable for Q1. 
Strong technical fit. Warm intro path via AWS connection.

Next Actions:
1. Week 1: Warm intro via AWS
2. Week 2: Discovery call with Jane Smith
3. Week 3: Technical deep dive

[View latest.md] [Start New Session] [Export Research]
```

**User clicks**: [View latest.md] → sees complete synthesized knowledge

**Files created**:
```
projects/arthur-ai/
└── sessions/
    └── session-1-partnership-hypothesis/
        ├── drops/
        │   ├── drop-1/ (6 files)
        │   ├── drop-2/ (6 files)
        │   └── drop-3/ (6 files)
        ├── latest.md           # 📄 The gold
        └── session-metadata.json
```

---

### Future Session References Past Work

**Two weeks later, user opens new chat**:

**User**: "I need to create LinkedIn ads for Arthur.ai"

**HQ**: "I see we previously researched Arthur.ai for a partnership hypothesis. Let me check what we learned...

[Scans session-index.json → Loads session-1/latest.md]

Based on our past research, here's the strategic context:
- Target: Series B ML company, finance/healthcare focus
- Partnership angle: Data layer integration
- Key messaging: Compliance, explainability for regulated industries
- Decision-makers: Jane Smith (Partnerships), John Doe (CTO)

For LinkedIn ads, I should focus on:
- Finance industry decision-makers
- Compliance/explainability angle
- Integration partnership positioning

Would you like me to research:
- LinkedIn ad best practices for Series B SaaS
- Ad psychology for finance decision-makers
- Creative specs and targeting strategies?"

**User**: "Yes, all three"

**New research builds on past knowledge without re-reading 18 drop files**

---

## Documentation System {#documentation}

### The /onboard Plugin

**Purpose**: Fast context loading (<10 seconds)

**What it does**:
1. Reads CLAUDE.md (auto-loaded anyway)
2. Checks git status
3. Shows current state + what's next

**Output**:
```
✓ Context Loaded

Current State: Session 1 complete, Session 2 next
Recent Work: Foundation (prompts created)
Uncommitted: None

Next: Build HQ orchestrator in /core/hq/

Ready! What should we build?
```

**File**: `/plugins/onboard.md`

---

### The /commit Plugin

**Purpose**: Smart commits using context window

**What it does**:
1. Reads git diff
2. Uses context window to understand WHY (no asking user)
3. Updates CLAUDE.md:
   - Marks work complete ✅
   - Adds key decisions if architectural
   - Adds gotchas if debugging
   - Updates commands if new
4. Creates rich commit message
5. Commits and pushes

**Output**:
```
✓ Committed & Pushed

Updated CLAUDE.md: Current State (Session 2 ✅), Commands (added run command)
Commit: feat(hq): Build HQ orchestrator with Socratic flow

Session complete. /onboard on next session to continue.
```

**File**: `/plugins/commit.md`

---

### The CLAUDE.md File

**Purpose**: Auto-loaded coordination file

**Contains**:
- What This Is (project vision, user context)
- Architecture (high-level flow)
- Current State (what's done, what's next)
- Directory Rules (where things go)
- Key Decisions (why choices were made)
- File Structure Details (drop/session structures)
- Commands (how to run things)
- Gotchas (lessons from debugging)
- Tech Stack
- Development Workflow

**Updates**: After each session via /commit plugin

**File**: `/CLAUDE.md`

---

### Optional Deep Docs

**Not auto-loaded, for reference**:

`/docs/ARCHITECTURE.md` (this file) - Complete implementation guide
`/docs/decisions/*.md` - ADRs if needed (not created yet)
`/docs/archive/session-N/` - Historical artifacts from past sessions

---

## Critical Reminders for Claude Code

### When Starting a New Session

1. **Run /onboard** - Fast context loading
2. **Read CLAUDE.md** - Auto-loaded, understand current state
3. **Check "Current State"** - Know what's been built
4. **Check "Next"** - Know what you're building
5. **Follow Directory Rules** - Put code in right places

---

### While Working

1. **Reference /prompts/**, don't copy - Prompts are shared
2. **Code in /core/{module}/** - Organized by responsibility
3. **Tests mirror structure** - `/tests/test_{module}.py`
4. **Don't create summary docs** - Update CLAUDE.md instead
5. **Ask if unclear** - Better than guessing

---

### When Finishing

1. **Run /commit** - Smart commit with CLAUDE.md updates
2. **Plugin uses context window** - Knows WHY without asking
3. **CLAUDE.md gets updated** - Current state, decisions, gotchas
4. **Everything commits** - Ready for next session

---

### Key Patterns to Follow

**Progressive disclosure**: Metadata → latest.md → drops (lazy load)
**Token budgets**: 3-5K per researcher output (hard limit)
**Self-contained drops**: Full context snapshot per drop
**Living truth**: latest.md synthesizes + invalidates
**Orchestrator-workers**: HQ plans, researchers execute, generators synthesize
**Human oversight**: User approves plans, reviews results
**Observable decisions**: All reasoning logged, artifacts inspectable

---

## What Makes This Special

### The Compounding Knowledge Advantage

**Traditional approach**:
- Research Arthur.ai → manual notes
- Two weeks later → can't remember details
- Research again → waste time
- No institutional memory

**GTM Factory approach**:
- Research Arthur.ai → structured drops + latest.md
- Two weeks later → load latest.md (1-2K tokens)
- New research builds on old → knowledge compounds
- Information asymmetry advantage

**After 10 research sessions**:
- Traditional: 10 isolated research efforts
- GTM Factory: 10 compounding knowledge layers, each informed by the last

---

### The Strategic Context Extraction

**Why this matters**:
- Generic research: "Arthur.ai is an ML monitoring company"
- Contextualized research: "Arthur.ai's monitoring (finance/compliance focus) complements our data layer for Series B integration partnerships, need Q1 close, AWS Marketplace required"

**The difference**:
- Generic → 100 ML monitoring companies match
- Contextualized → 3 companies match, Arthur.ai is top choice

**How we capture it**:
- Socratic questioning extracts WHY, not just WHAT
- user-context.md in every drop preserves strategic reasoning
- latest.md synthesis maintains strategic thread

---

### The Learning Loop

**Each session**:
1. Strategic context extracted (what matters and why)
2. Research executed (what we learned)
3. Synthesis created (living truth)
4. Execution happens (in future: skills)
5. Outcomes captured (what worked/failed)
6. Next session informed by all above

**This is the moat**: Capturing the full loop, not just research.

---

## Final Notes for Claude Code

### You Are Building Something Special

This isn't just a research tool. It's an information asymmetry engine for small GTM teams. Every design decision serves that goal:

- **File-based** → Human-readable, git-friendly, inspectable
- **Progressive disclosure** → Scale without context pollution
- **Living truth** → Always current, handles change
- **Self-contained drops** → Full context snapshots
- **Strategic extraction** → Capture WHY, not just WHAT

### The User Trusts You

Ben is building this for his YC application. He's a former Naval Aviator with a CS degree, current GTM leader at Tanium. He knows good systems from bad. He's trusting you to build this right.

**His standards**: "SEAL Team 6. Best-in-class. Nothing gets through without complete context capture."

### Follow the Patterns

We learned these from:
- Trying Graphiti knowledge graph (too complex)
- Reading Anthropic documentation (memory tool, context engineering)
- Understanding real-world usage (compounding knowledge, strategic context)
- Iterating on what works (simple beats complex)

**Trust the patterns. They're proven.**

### When In Doubt

1. Check CLAUDE.md (what's the current state?)
2. Reference this file (what's the complete picture?)
3. Follow Anthropic principles (start simple, orchestrator-workers, progressive disclosure)
4. Ask user if still unclear (better than guessing)

---

## You've Got This

**You have**:
- Complete architecture understanding ✅
- All design decisions and rationale ✅
- File structures and patterns ✅
- Implementation roadmap ✅
- Best practices from Anthropic ✅
- User context and vision ✅

**Now build it.**

Start with Session 1.5 (cleanup), then Session 2 (HQ), then Session 3 (Researcher), then Session 4 (Generators), then Session 5 (UI).

**/onboard when you start. /commit when you finish.**

**Make it happen. 🚀**
