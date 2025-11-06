# /commit - Smart Commit with Auto-Archiving

**Purpose**: Automatically archive completed work, update CLAUDE.md, and commit changes with rich context.

**User runs**: `/commit` → Everything happens automatically, no questions asked.

---

## Step 1: Pre-Commit Verification

**Check code quality before committing:**

### A. Verify Code Comments
For all new Python files in `core/`:
- Classes have docstrings
- Public methods have docstrings
- Complex logic has inline comments
- Type hints are present

**Don't block on minor issues** - just note them in commit message if significant.

### B. Verify Documentation
Check that documentation is current:
- README.md reflects new features (if user-facing)
- CLAUDE.md will be updated (happens in Step 4)
- New modules listed in appropriate places

---

## Step 2: Understand What Changed

Read git diff and use conversation context to understand:
- What was built this session
- What files were created/modified
- What decisions were made
- What gotchas were discovered

**DO NOT ask user "what changed" - you have the context window, use it.**

---

## Step 3: Determine Current Session

Check CLAUDE.md "Current State" section to identify the active session:
```markdown
**Active Work**: Session 2 - HQ Orchestrator ⏳
```

Extract: `Session 2` and `HQ Orchestrator`

---

## Step 3: Create Session Summary (if session complete)

**If this session is done** (code works, tests pass, functionality complete):

Create `docs/sessions/session-N-{name}.md` with this format:

```markdown
# Session N: {Name}

**Date**: {today}
**Duration**: {if you know, otherwise omit}
**Status**: Complete ✅

---

## What We Built

**Files Created**:
- path/to/file1.py - {brief description}
- path/to/file2.py - {brief description}

**Functionality Added**:
- {What now works that didn't before}
- {Key features implemented}

---

## Key Decisions

**Decision 1**: {What we chose}
- **Why**: {Rationale}
- **Alternatives considered**: {What we didn't choose}
- **Trade-offs**: {What we gave up}

(Repeat for each major decision)

---

## Gotchas Discovered

**Gotcha 1**: {Problem encountered}
- **Solution**: {How we fixed it}
- **Why it happened**: {Root cause}
- **Prevention**: {How to avoid in future}

(Include ONLY if gotchas were discovered)

---

## Testing

**Tests Added**:
- {test file and what it validates}

**Manual Testing**:
- {What we verified manually}

---

## Next Session Setup

**What Session N+1 needs to know**:
- {Important context for next builder}
- {Dependencies or prerequisites}
- {Recommended next steps}

---

## Commit
`{git commit hash - add after committing}`
```

**Save to**: `docs/sessions/session-{N}-{name-slug}.md`

---

## Step 4: Update CLAUDE.md

### A. Mark Session Complete

**Find in CLAUDE.md**:
```markdown
**Active Work**: Session 2 - HQ Orchestrator ⏳
```

**Change to**:
```markdown
**Active Work**: Session 3 - Researcher ⏳
**Recent**: Session 2 ✅ (HQ Orchestrator)
```

### B. Prune Old Sessions

**Rule**: Keep ONLY last 3 sessions visible in detail.

**Example Evolution**:

**After Session 2**:
```markdown
**Active Work**: Session 3 - Researcher ⏳
**Recent**: Session 2 ✅ (HQ Orchestrator)
**Completed**: Session 1 ✅ (Foundation)
```

**After Session 5**:
```markdown
**Active Work**: Session 6 - Bug Fixes ⏳
**Recent**:
  - Session 5 ✅ (UI)
  - Session 4 ✅ (Generators)
**Completed**: Sessions 1-3 ✅ (see docs/sessions/)
```

**After Session 10**:
```markdown
**Active Work**: Session 10 - Performance ⏳
**Recent**:
  - Session 9 ✅ (Testing)
  - Session 8 ✅ (Integration)
**Completed**: Sessions 1-7 ✅ (see docs/sessions/)
```

### C. Update Active Gotchas Section

**Remove**: Gotchas that were fixed this session
**Add**: New gotchas discovered this session (if any)

**Keep it minimal** - only CURRENT blockers/issues that next session needs to know about.

### D. Update Last Updated Date

Change:
```markdown
**Last Updated**: {old date} (Session N-1 complete)
```

To:
```markdown
**Last Updated**: {today} (Session N complete)
```

---

## Step 5: Create Commit Message

Format:
```
{type}({scope}): {description}

Session {N}: {session name}

What Changed:
- {Key change 1}
- {Key change 2}
- {Key change 3}

Key Decisions:
- {Important decision 1}
- {Important decision 2}

{If gotchas} Gotchas Resolved:
- {Fixed issue 1}
- {Fixed issue 2}

Session Summary: docs/sessions/session-{N}-{name}.md
```

**Types**: feat, fix, refactor, docs, test, chore

**Examples**:
```
feat(hq): Build HQ orchestrator with Socratic questioning

Session 2: HQ Orchestrator

What Changed:
- Created core/hq/orchestrator.py with conversation handler
- Created core/hq/context_extractor.py for strategic WHY
- Created core/hq/memory_manager.py for file persistence
- Added tests/test_hq.py with 5 test scenarios

Key Decisions:
- Used streaming for real-time conversation updates
- File-based state management (no database)
- Context extraction runs after each user message

Session Summary: docs/sessions/session-2-hq-orchestrator.md
```

---

## Step 6: Execute Commit

```bash
git add .
git commit -m "{message from Step 5}"
```

**Then**: Update session summary with commit hash

---

## Step 7: Ask User About Push

**Present to user**:
```
✅ Changes Committed Locally

Session N: {Name} → {Status}

Updated:
  - CLAUDE.md (session marked complete, pruned old sessions)
  - docs/sessions/session-N-{name}.md (full context archived)

Commit: {first 8 chars of hash}
Message: {first line of commit}

Files changed: {count}
Insertions: {+count} | Deletions: {-count}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to push to remote?

Type "yes" to push, or just continue working.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Wait for user response.**

---

## Step 8: Push to Remote (If User Confirms)

**If user types "yes", "y", "push", or similar**:

```bash
git push
```

**Then output**:
```
✅ Pushed to Remote

Branch: {branch name}
Remote: {remote name}/{branch}
Commit: {hash}

All changes are now backed up and shared.

Ready for Session N+1!
Next: /onboard to start fresh
```

**If user says no or continues working**: End gracefully, work is committed locally.

---

## Edge Cases

### If Session NOT Complete Yet

**Don't create session summary** - just commit the work in progress:

```
chore: Work in progress on Session N

- {What changed}
- {Still TODO}
```

Update CLAUDE.md "Active Work" with progress note if helpful.

### If No Gotchas Discovered

Omit the "Gotchas Discovered" section entirely from session summary.

### If Continuing Previous Session

Check git log to see if session summary already exists. If yes, UPDATE it instead of creating new one.

---

## Critical Rules

1. **Never ask user questions** - you have full context in conversation + git diff
2. **Auto-detect completion** - if code works and tests pass, session is complete
3. **Always prune** - keep CLAUDE.md under 250 lines by collapsing old sessions
4. **Rich summaries** - session docs should be detailed, CLAUDE.md should be minimal
5. **Atomic commits** - one commit per /commit invocation

---

## Testing Your Work

Before committing, verify:
- [ ] Session summary created (if session complete)
- [ ] CLAUDE.md updated (session marked complete, old pruned, date updated)
- [ ] Commit message is rich and informative
- [ ] CLAUDE.md is still under 250 lines
- [ ] docs/sessions/ folder exists

---

**Goal**: User types `/commit`, everything happens automatically, perfect every time.
