# GTM Factory - Project Health Audit & Best Practices

**Date**: 2025-11-19
**Status**: Research complete, immediate fixes applied

---

## Executive Summary

**Good News**: Your architecture is sound, your CLAUDE.md follows Anthropic best practices, and your modules are well-structured.

**The Real Issues**: Workflow execution problems, not technical debt:
1. Multi-day sessions causing context drift (should be 30-min blocks)
2. 100% mocked tests giving false confidence (need fixture-based testing)
3. Trusting "tests pass" instead of manual validation
4. Unnecessary UI reruns causing jumpiness ✅ **FIXED**
5. No systematic code cleanup process

---

## ✅ Immediate Fixes Applied

### 1. UI Jumpiness - FIXED

**Problem**: Unnecessary `st.rerun()` calls causing double-rerun and flash

**Fixed**:
- Removed line 85 rerun (research toggle)
- Removed line 170 rerun (after message append)

**Result**: Streamlit now handles reruns naturally = smooth UI

### 2. Next Steps (In Priority Order)

See "Action Plan" section below

---

## 🔍 Research Findings Summary

### 1. AI Agent Development Best Practices

**Key Principle**: Start simple, add complexity only when needed

**Your Architecture** (Orchestrator-Workers):
- ✅ Correct pattern for your use case
- ✅ Clear module boundaries (HQ → Researcher → Generator)
- ⚠️ Missing: Pydantic schemas for inter-agent contracts

**Critical Gap**: Integration scaffolding
- You built components in the right order
- But skipped contract definitions between modules
- Result: Tests pass in isolation, fail in integration

**Fix**: Add contract tests (see Priority 2 below)

### 2. Testing Strategies for LLM Apps

**Current Approach**:
- 100% mocked tests → $0 cost, deterministic
- Manual end-to-end testing → 5-10 min per cycle, burnout

**Recommended Approach** (Testing Pyramid for LLM Apps):
- 20% Traditional software tests (file I/O, state management)
- 50% Evaluations with fixtures (pytest-vcr - record once, replay forever)
- 30% Agent simulations (real end-to-end, run rarely)

**Key Tool**: `pytest-vcr` (VCR.py pattern)
- First run: Record API response (~$0.05)
- All future runs: Replay from cassette ($0, <100ms)
- Catches regressions automatically

**Cost Reduction**:
- Current: ~$5-10/day (manual testing)
- With fixtures: ~$0.90/week

### 3. Code Audit Results

**Tools to Use**:
1. **Ruff** - Fast linter (10-100x faster than Pylint)
2. **Vulture** - Dead code detection
3. **Radon** - Complexity metrics
4. **Coverage** - Find untested code

**Immediate Cleanup Targets** (from git status):
```
✅ DELETE: nul, errors_delete.md (artifacts)
⚠️ REVIEW: tests/demos/* (likely superseded by test_ui.py)
⚠️ REVIEW: config/ (what's in here?)
⚠️ REVIEW: prompts/hq-*.md (duplicates of hq-orchestrator.md?)
```

**Red Flags to Check**:
- Circular dependencies (use `pydeps core --show-cycles`)
- Functions with complexity > 10 (use `radon cc core/ -a`)
- Modules with < 50% coverage (use `coverage report`)

### 4. Streamlit Best Practices

**Problem Patterns** (Found in your code):
1. ✅ **FIXED**: Manual `st.rerun()` after `st.chat_input` (double-rerun)
2. ✅ **FIXED**: Manual `st.rerun()` after toggle change (unnecessary)
3. ⚠️ **TO FIX**: Blocking `asyncio.run()` prevents progress updates

**Recommended Patterns**:
- Use `st.write_stream()` for streaming (handles placeholders internally)
- Use `@st.fragment(run_every=2)` for progress polling
- Use threading + queues for long-running tasks (non-blocking)

**For Progress Visibility**:
```python
@st.fragment(run_every=1)  # Poll every second
def show_research_progress():
    state = st.session_state.state_manager.get_drop_state(drop_id)
    st.progress(state["progress"])
    if state["status"] == "complete":
        st.rerun()  # Stop polling
```

### 5. Claude Code Workflow Optimization

**The 30-Minute Rule** (Official Anthropic Guidance):
> "Keep scope small - plan what you will do in the next 30 minutes or less."

**Session Structure Template**:
```
1. PLAN (5 min)
   - /onboard to load context
   - Define ONE specific deliverable
   - Ask for plan, review it, approve it

2. BUILD (15 min)
   - Execute plan incrementally
   - Use /clear between independent tasks
   - Interrupt (ESC) if going off-track

3. VALIDATE (5 min)
   - Run tests yourself (don't ask Claude)
   - Manual smoke test
   - Review git diff

4. COMMIT (5 min)
   - git commit with message
   - Update CLAUDE.md
   - /clear to reset context
```

**Red Flags You're Drifting**:
- Session > 45 minutes
- Claude says "done" but you haven't verified
- Tests pass but feature doesn't work
- TODOs appearing instead of working code
- Claude ignoring CLAUDE.md instructions
- Context meter > 80%

---

## 📋 Action Plan by Priority

### Priority 1: Process Fixes (Today - 2 hours)

These fix your workflow, not your code:

**1.1 Clean Up Dead Code (30 min)**
```bash
# Install audit tools
pip install ruff vulture radon coverage

# Delete obvious junk
rm nul
rm errors_delete.md

# Find unused code
vulture . --min-confidence 80 --exclude venv,tests

# Auto-fix style issues
ruff check . --fix --exclude tests/demos
```

**1.2 Add Validation Checklist to CLAUDE.md (30 min)**

Add this section after "Build Status":

```markdown
## ✔️ Validation Checklist

After Claude says "done", YOU must verify:

1. **Tests Run Successfully**
   ```bash
   pytest tests/test_module.py -v
   ```
   ❌ Don't ask Claude "did tests pass?"
   ✅ Run them yourself

2. **Feature Works Manually**
   - Run demo script or manual test
   - Use REAL data, not fixtures
   - Test edge cases

3. **Git Diff Clean**
   ```bash
   git diff
   ```
   Red flags: Unexpected files, TODOs, debug code

4. **Integration Still Works**
   ```bash
   pytest tests/
   ```

5. **Docs Updated**
   - CLAUDE.md build status
   - Function docstrings

ONLY commit after ALL 5 pass.

---

## Session Workflow

### Before Every Session
1. Run `/onboard`
2. Define ONE deliverable (30 min scope)
3. Ask for plan → Review → Approve

### During Session
- Validate each step before proceeding
- Use `/clear` between independent tasks
- Press ESC to interrupt if going off-track

### Session Complete When
- ✅ All 5 validation checks pass
- ✅ Git diff reviewed
- ✅ CLAUDE.md updated
- ✅ Committed and `/clear` executed

### Red Flags (Stop & Reset)
- Session > 45 minutes
- Claude says "done" but unverified
- Tests pass but feature doesn't work
- TODOs appearing
- Context meter > 80%
```

**1.3 Install pytest-vcr (15 min)**
```bash
pip install pytest-recording
```

Update one test as example:
```python
# In tests/test_researcher.py
@pytest.mark.vcr()  # Add this decorator
def test_researcher_executes_task():
    # First run: Records to cassette ($0.05)
    # Future runs: Replays from cassette ($0, <100ms)
    researcher = GeneralResearcher()
    output = researcher.research("What is ICP validation?", max_tokens=3000)
    assert output.token_count < 5000
```

Run once to record:
```bash
pytest tests/test_researcher.py::test_researcher_executes_task --record-mode=once
```

Future runs are free:
```bash
pytest tests/test_researcher.py::test_researcher_executes_task
```

**1.4 Run Code Audit (30 min)**
```bash
# Create audit reports directory
mkdir -p audit_reports

# Run scans
ruff check . --output-format=json > audit_reports/ruff.json
vulture . --min-confidence 70 --exclude venv > audit_reports/vulture.txt
radon cc core/ -j > audit_reports/complexity.json
radon mi core/ -s > audit_reports/maintainability.txt

# Run tests with coverage
coverage run -m pytest tests/
coverage report -m > audit_reports/coverage.txt

# Review results
cat audit_reports/vulture.txt    # Any 80%+ confidence items?
cat audit_reports/maintainability.txt  # Any MI < 50?
cat audit_reports/coverage.txt   # Any < 50% coverage?
```

**Expected Result**:
- Smooth UI ✅ (already fixed)
- Better testing strategy
- Clean workspace
- Visibility into code health

---

### Priority 2: Contract-Based Testing (This Week - 4 hours)

**Goal**: Fix "tests pass but integration fails" problem

**2.1 Define Interface Contracts (1 hour)**

Create `core/interfaces.py`:
```python
from pydantic import BaseModel
from typing import List, Dict

class ResearchPlan(BaseModel):
    """Contract: HQ → Researcher"""
    session_id: str
    drop_id: str
    researchers: List[Dict]
    strategic_context: str  # Extracted WHY only

class ResearchOutput(BaseModel):
    """Contract: Researcher → Generator"""
    researcher_id: str
    findings: str
    sources: List[str]
    metadata: Dict
    token_count: int

class DropSynthesis(BaseModel):
    """Contract: Generator → HQ"""
    drop_id: str
    synthesis: str
    critical_analysis: str
    gaps_identified: List[str]
```

**2.2 Create Contract Tests (1 hour)**

Create `tests/test_contracts.py`:
```python
def test_hq_produces_valid_research_plan():
    """Validate HQ output schema without running HQ."""
    # Mock test - no API call

def test_researcher_accepts_research_plan():
    """Validate Researcher input schema matches HQ output."""
    # Schema validation only

def test_generator_accepts_research_output():
    """Validate Generator input schema matches Researcher output."""
    # Schema validation only
```

**2.3 Add pytest-vcr to All Tests (2 hours)**

Add `@pytest.mark.vcr()` to:
- `tests/test_researcher.py` (all API-heavy tests)
- `tests/test_generators.py` (all synthesis tests)
- `tests/test_hq.py` (streaming tests)

Run once to record cassettes, then all future tests are free.

**Expected Result**:
- Tests run in <30 seconds (vs 5-10 minutes)
- Catch integration bugs early
- API costs drop from ~$5/day to ~$1/week

---

### Priority 3: Systematic Code Cleanup (Next Week - 8 hours)

**3.1 Consolidate Demo Files (2 hours)**

Review `tests/demos/`:
- Which are still used?
- Which can be deleted?
- Create one canonical `tests/demos/smoke_test.py` for manual validation

**3.2 Extract Duplicate Logic (3 hours)**

Check for duplication in:
- `core/ui/adapters/*_adapter.py` (shared boilerplate?)
- `core/generators/*_generator.py` (similar prompt wrapping?)
- `ui/components/*.py` (shared UI patterns?)

Create `core/utils/` for shared logic:
```
core/utils/
├── streaming.py (shared Anthropic streaming logic)
├── validation.py (shared Pydantic validation)
└── file_ops.py (shared file I/O patterns)
```

**3.3 Add Missing Tests (2 hours)**

Target: 70% coverage on `/core/`

```bash
# Check current coverage
coverage run -m pytest tests/
coverage report --skip-covered

# For each < 50% file, add tests
```

**3.4 Fix Architecture Violations (1 hour)**

Check for circular dependencies:
```bash
pip install pydeps
pydeps core --show-cycles
```

Verify Orchestrator-Workers pattern:
```bash
# Workers should NOT import orchestrator
grep -r "from core.hq import" core/researcher/ core/generators/

# UI should use adapters only
grep -r "from core.hq import" ui/
```

**Expected Result**:
- Maintainable codebase
- Clear module boundaries
- Higher test coverage
- No architectural violations

---

### Priority 4: Production Hardening (Future)

**4.1 Add Observability**
- Install Langfuse for agent tracing
- Add visible logs panel in UI
- Track: prompts, responses, tokens, cost, latency

**4.2 Non-Blocking Progress Updates**
- Refactor `progress_display.py` to use threading + fragments
- Show real-time research progress
- Keep UI responsive during long tasks

**4.3 CI/CD Quality Gates**
- Add pre-commit hooks (run tests before commit)
- Add GitHub Actions workflow
- Block merges if coverage < 70%

---

## 🎓 Key Learnings

### 1. The 30-Minute Rule

Break ALL work into 30-minute focused blocks:

**Bad** (your current approach):
```
Session 5: UI ⏳
- Build entire Streamlit application
- 8 components, adapters, state management
- Multi-day session, context drift
```

**Good** (recommended):
```
Session 5.1: UI Basic Layout (30 min)
Session 5.2: Chat Component (30 min)
Session 5.3: Progress Display (30 min)
Session 5.4: Context Meter (30 min)
Session 5.5: File Tree (30 min)
Session 5.6: Integration (30 min)
```

Each session: Plan → Build → Validate → Commit → /clear

### 2. Don't Trust "Done"

When Claude says "done", run the 5-check validation:
1. Run tests yourself (don't ask if they passed)
2. Manually test feature
3. Review git diff
4. Run integration tests
5. Check docs updated

**Only commit when all 5 pass.**

### 3. Testing Pyramid for LLM Apps

Traditional pyramid (70/20/10) doesn't work for agent systems.

LLM pyramid:
- 20% Traditional tests (deterministic logic)
- 50% Fixture-based evals (pytest-vcr)
- 30% Real agent simulations (expensive, run rarely)

### 4. Context Management

**Use `/clear` frequently**:
- Every 20-30 minutes
- Between independent tasks
- When context meter > 70%
- After completing a logical unit

**Don't**:
- Run multi-day sessions
- Let context meter hit 80%+
- Mix unrelated tasks in one session

### 5. Manual Validation is Critical

**You must verify**, not Claude:
- Tests actually pass (run them yourself)
- Feature actually works (manual smoke test)
- Integration still works (full test suite)
- Git diff makes sense (review every line)

**Claude can lie** (unintentionally):
- "Tests pass" → but you haven't run them
- "Feature works" → but only for test cases
- "Integration tested" → but only mocked

---

## 📊 Success Metrics

Track these weekly:

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| **Session Length** | Multi-day | 30 min avg | Time tracking |
| **Test Speed** | 5-10 min | <30 sec | `time pytest tests/` |
| **API Cost** | ~$5-10/day | ~$1/week | Test execution logs |
| **Coverage** | Unknown | >70% on core/ | `coverage report` |
| **Context Resets** | Rarely | 1-2 per session | `/clear` usage count |
| **Failed Sessions** | High | <10% | Require `/reset` count |
| **Integration Bugs** | High | <5% | Tests pass but feature fails |

---

## 🛠️ Tools Reference

### Essential Tools (Install Today)

```bash
pip install ruff vulture radon coverage pytest-recording
```

| Tool | Purpose | Command |
|------|---------|---------|
| **Ruff** | Fast linting | `ruff check . --fix` |
| **Vulture** | Dead code detection | `vulture . --min-confidence 80` |
| **Radon** | Complexity metrics | `radon cc core/ -a` |
| **Coverage** | Test coverage | `coverage run -m pytest` |
| **pytest-vcr** | Record/replay HTTP | `@pytest.mark.vcr()` |

### Recommended Tools (Add to CI/CD)

```bash
pip install pydeps bandit langfuse
```

| Tool | Purpose | Command |
|------|---------|---------|
| **Pydeps** | Dependency graphs | `pydeps core --show-cycles` |
| **Bandit** | Security scanning | `bandit -r core/` |
| **Langfuse** | LLM observability | `@observe()` decorator |

---

## 📚 Research Sources

**Official Anthropic**:
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Common Workflows](https://code.claude.com/docs/en/common-workflows)

**Testing**:
- [Agent Testing Pyramid](https://arize.com/blog/llm-evaluation-the-definitive-guide/)
- [pytest-vcr Documentation](https://pytest-vcr.readthedocs.io/)
- [Langfuse Observability](https://langfuse.com/docs)

**Code Quality**:
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Vulture Documentation](https://github.com/jendrikseipp/vulture)
- [Radon Documentation](https://radon.readthedocs.io/)

---

## Next Steps

### Today (2 hours)
1. ✅ Fix UI jumpiness (DONE)
2. Add Validation Checklist to CLAUDE.md
3. Install pytest-vcr and update one test
4. Run code audit and review results

### This Week (4 hours)
1. Define interface contracts
2. Create contract tests
3. Add pytest-vcr to all tests
4. Set up Langfuse observability

### Next Week (8 hours)
1. Consolidate demo files
2. Extract duplicate logic
3. Add missing tests (70% coverage target)
4. Fix architecture violations

---

**Status**: Ready to implement. Start with Priority 1 tasks today.
