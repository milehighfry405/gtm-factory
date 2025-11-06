# Quick Start Guide - GTM Factory

## What This System Does

GTM Factory is a multi-agent AI research system that conducts GTM (Go-To-Market) intelligence gathering across multiple sessions, using specialized AI agents that work together to produce executive-ready insights.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    HQ ORCHESTRATOR                       │
│  • Plans research sessions                               │
│  • Dispatches specialist agents                          │
│  • Synthesizes outputs                                   │
└───────────┬─────────────────────────────────────────────┘
            │
            ├──> GENERAL RESEARCHER
            │    • Gathers information from web sources
            │    • Produces structured research documents
            │    • 3-5K token outputs with citations
            │
            ├──> CRITICAL ANALYST
            │    • Evaluates research quality
            │    • Identifies gaps and logical flaws
            │    • Suggests improvements
            │
            ├──> LATEST GENERATOR
            │    • Creates executive intelligence briefs
            │    • Max 1500 words, action-oriented
            │    • Updates Latest.md with insights
            │
            └──> SESSION METADATA GENERATOR
                 • Creates lightweight JSON summaries
                 • Enables cross-session context management
                 • Prevents research duplication
```

## Key Anthropic Patterns Applied

1. **Orchestrator-Workers**: Central HQ delegates to specialized agents
2. **Progressive Disclosure**: Load context just-in-time via lightweight metadata
3. **Token Budget Management**: Every agent has explicit output constraints
4. **Simple, Clear Prompts**: Direct language at "right altitude"
5. **Transparent Reasoning**: Confidence levels and source citations required

## File Organization

```
projects/{company-name}/
├── project_brief.md              # Research objectives
├── sessions/
│   └── {session-id}/
│       ├── session_plan.json     # Agent assignments
│       ├── session_metadata.json # Lightweight summary
│       └── outputs/              # Research documents
└── research_artifacts/
    └── Latest.md                 # Executive intelligence brief
```

## Agent Prompts

All prompts located in `/prompts/` directory:

| Agent | Purpose | Token Budget | Key Output |
|-------|---------|--------------|------------|
| HQ Orchestrator | Session planning & synthesis | 5K plan / 8K synthesis | Session plans, summaries |
| General Researcher | Web research & analysis | 3-5K | Research documents with citations |
| Critical Analyst | Quality evaluation | 3K | Critical analysis reports |
| Latest Generator | Executive briefs | 2K max | Latest.md intelligence brief |
| Session Metadata Generator | Cross-session context | 1K | JSON metadata < 2KB |

## How to Use the System

### 1. Create New Project
```
projects/
└── {your-company}/
    └── project_brief.md
```

### 2. Define Research Objectives
Edit `project_brief.md` with:
- Company overview
- Research questions
- Success criteria
- Stakeholders

### 3. Run Session (Future Implementation)
```python
# This will be implemented in Session 2
hq = HQOrchestrator(project_path="projects/your-company")
hq.run_session(request="Your research question")
```

### 4. Review Outputs
- **Latest.md**: Executive summary with recommendations
- **session_metadata.json**: Quick reference for what was covered
- **outputs/**: Detailed research documents

## Token Budget Strategy

Following Anthropic's context engineering guidance:

| Context Type | Budget | Rationale |
|--------------|--------|-----------|
| Session Metadata | < 2KB | Enable fast scanning of all prior sessions |
| Research Output | 3-5K tokens | Comprehensive but bounded analysis |
| Critical Analysis | 3K tokens | Focus on major issues, not minor nitpicks |
| Executive Brief | 2K tokens | Extreme brevity for executive consumption |
| Synthesis | 8K tokens | Room to connect insights across agents |

## Confidence Levels

All findings tagged with confidence:

- **High**: Official docs, peer-reviewed research, verified data
- **Medium**: Industry reports, expert sources, recent reputable news
- **Low**: Opinion pieces, unverified claims, anonymous sources

## Testing

Run validation tests:
```bash
pytest tests/test_examples.py -v
```

Tests validate:
- Metadata schema compliance
- File size constraints
- Required document sections
- Prompt structure adherence to Anthropic patterns

## Example Project

See `projects/example-company/` for complete working example:
- Market landscape research
- Session metadata
- Executive Latest.md brief

## Next Development Steps

**Session 2**: Implement agent execution layer
- Python classes wrapping Claude API
- Session orchestration logic
- File I/O utilities

**Session 3**: CLI interface
- Project initialization
- Session management
- Interactive mode

**Session 4**: Advanced features
- Multi-session synthesis
- Research deduplication
- Automated follow-up planning

## Key Design Principles

1. **Start Simple**: Use simplest pattern that works
2. **Progressive Disclosure**: Load context only when needed
3. **Explicit Constraints**: Token budgets prevent context rot
4. **Transparent Reasoning**: Confidence levels, citations, assumptions explicit
5. **Actionable Output**: Every research output leads to decisions

## References

- [Session 1 Completion Summary](SESSION_1_COMPLETION_SUMMARY.md)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic: Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
