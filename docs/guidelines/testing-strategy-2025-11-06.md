# Testing Strategy for GTM Factory

**Date**: 2025-11-06
**Status**: Active guideline - follow this for all test creation

---

## Context: Why This Strategy Exists

**User Pain Point (Helldiver experience):**
> "I had to have these very rich convos only to find out that all the chat history wasn't being saved or something then restart, another bug, restart over and over and it was exhausting"

**User Requirement:**
> "I don't want to pass all the tests and then like a ton of shit breaks when I run for first time. These tests need to be representative of how it's going to work."

**User Context:** GTM professional, not SWE - needs confidence system will work in real use, not just isolated unit tests.

---

## Testing Philosophy

### ❌ What We DON'T Do

**No Pure Unit Tests:**
- Testing individual methods in isolation doesn't prove the system works
- Example: `test_save_file()` passing doesn't mean conversation persists correctly
- Unit tests give false confidence for conversational systems

### ✅ What We DO Instead

**Integration Tests for Critical Paths:**
- Test complete workflows that would force user to restart if broken
- Simulate real user interactions end-to-end
- Focus on "bugs that matter" vs "code coverage"

---

## The Strategy: Iterative Integration Testing

### Build-Test-Integrate Pattern

**Session 2 (HQ):**
- Test HQ in isolation
- Critical paths:
  - Conversation save/load round trip
  - User context extraction and persistence
  - Drop folder creation and naming
  - System survives missing files

**Session 3 (Researcher):**
- Test Researcher in isolation:
  - Can execute research task
  - Respects token budget (3-5K limit)
  - Handles network failures gracefully
- Test HQ → Researcher integration:
  - HQ drop plan converts to researcher tasks
  - Research outputs save to correct drop folder
  - User context available to researcher

**Session 4 (Generator):**
- Test Generator in isolation:
  - Synthesizes multiple research outputs
  - Handles invalidation logic
  - Produces valid markdown
- Test full workflow (HQ → Research → Synthesis):
  - Complete drop creation end-to-end
  - `latest.md` updates correctly
  - Progressive disclosure works (metadata → content)

**Session 5 (UI):**
- Test UI with complete backend
- Real user workflow simulation:
  - Start conversation → clarify intent → execute research → view synthesis
  - Session persistence across restarts
  - Multiple drops compound correctly

### Why This Works

1. **Each piece works in isolation** - confidence individual modules function
2. **Pieces work together** - confidence integration points don't break
3. **Matches real workflow** - user can verify behavior makes sense
4. **Catches Helldiver-class bugs** - conversation lost, file corruption, folder naming failures

---

## Test Writing Guidelines

### What to Test (Critical Paths)

**Always test these scenarios:**
- Save/load round trips (data persists correctly)
- File corruption scenarios (system survives gracefully)
- Missing file scenarios (doesn't crash, provides useful error)
- Folder/file naming consistency (predictable structure)
- End-to-end workflows (user can complete task without manual intervention)

### What NOT to Test

**Don't test these:**
- Individual getter/setter methods
- Private utility functions in isolation
- Mock-heavy tests that don't represent real usage
- Code coverage for coverage's sake

### CRITICAL: Avoid API Credit Burn

**Lesson from Session 3 (Researcher):**
- Running 7 full research tests burned through Tavily API credits unnecessarily
- Each test made real API calls: OpenAI GPT-4o + Tavily web search
- Cost adds up fast: ~$0.02-0.08 per research execution

**Strategy to Avoid This:**
1. **ONE real end-to-end test** per module - proves integration works
2. **MOCK everything else** - use pre-captured outputs in `/tests/fixtures/`
3. **Run full suite sparingly** - only when validating major changes
4. **Use demo scripts for manual validation** - stored in `/tests/demos/`

**Mock Pattern:**
```python
# tests/fixtures/sample_research_output.json
{
  "findings": "...",
  "sources": [...],
  "token_count": 2500
}

# In test file
def test_token_budget_warning(mock_research_output):
    """Test using pre-captured fixture, no API calls"""
    output = ResearchOutput(**mock_research_output)
    assert output.token_count < 5000
```

**When to Use Real API Calls:**
- Initial validation that integration works (Session 3: 1 passing test proved researcher works)
- Before marking session complete (final smoke test)
- When debugging API-specific issues

**When to Use Mocks:**
- All other test scenarios (error handling, metadata validation, parallel execution)
- CI/CD pipeline runs
- Rapid development iteration

### Test Structure Pattern

```python
def test_{critical_workflow_name}(self, temp_project):
    """
    CRITICAL END-TO-END TEST: {What user workflow this represents}

    This is the flow that MUST work or you have to restart:
    1. {Step 1}
    2. {Step 2}
    3. {Step 3}
    """
    # Setup
    {create necessary objects}

    # Execute workflow
    {simulate user actions}

    # Verify critical outcomes
    assert {thing exists}, "❌ CRITICAL: {why this matters}"
    assert {data loadable}, "❌ CRITICAL: {why this matters}"
```

### Test Naming Convention

**Good test names:**
- `test_complete_drop_workflow` - describes user-facing workflow
- `test_conversation_survives_restart` - describes what user needs
- `test_researcher_respects_token_budget` - describes critical constraint

**Bad test names:**
- `test_save_file` - too granular, doesn't show user impact
- `test_orchestrator_init` - testing implementation detail
- `test_valid_input` - unclear what "valid" means in user terms

---

## Integration Points to Test

### Session Handoffs (File-Based Persistence)

**HQ → Researcher:**
- User context saved by HQ
- Researcher loads context correctly
- Drop plan converts to executable tasks

**Researcher → Generator:**
- Research outputs saved to drop folder
- Generator loads all outputs
- Token budget respected (inputs < context window)

**Generator → UI:**
- `latest.md` is valid markdown
- UI can parse and display
- Invalidation markup renders correctly

### Cross-Session Continuity

**Test that subsequent sessions can:**
- Load previous session metadata
- Access historical drops via progressive disclosure
- Update `latest.md` without corrupting existing content

---

## Where Tests Live

```
tests/
├── test_hq.py              # Session 2: HQ isolation + internal workflows
├── test_researcher.py       # Session 3: Researcher isolation
├── test_hq_researcher.py    # Session 3: HQ → Researcher integration
├── test_generator.py        # Session 4: Generator isolation
├── test_full_workflow.py    # Session 4: HQ → Research → Synthesis
└── test_ui.py              # Session 5: UI + complete backend
```

**Naming Pattern:**
- `test_{module}.py` - Tests module in isolation
- `test_{module1}_{module2}.py` - Tests integration between modules
- `test_full_workflow.py` - Tests complete user journey

---

## Success Criteria

**Tests are successful when:**
- ✅ User can run demo and verify behavior matches expectations
- ✅ Tests catch the bugs that would force conversation restart
- ✅ Integration tests pass = high confidence system works
- ✅ Test failures clearly indicate what user workflow broke

**Tests are failing their purpose when:**
- ❌ All tests pass but system breaks on first real use
- ❌ User can't understand what test failure means for their workflow
- ❌ Tests only validate code structure, not user outcomes

---

## Update Protocol

**When to update this document:**
- New critical path discovered during development
- User experiences bug that tests didn't catch
- Testing strategy proves ineffective (tests pass but system breaks)

**How to update:**
- Add new critical path to "What to Test" section
- Document the user pain point that motivated the change
- Update integration points if new modules added

**Who updates:**
- Any Claude session building new modules
- User can request updates based on real-world usage

---

## Quick Reference

**"Should I write a test for X?"**

Ask yourself:
1. If this breaks, does the user have to restart their conversation?
2. Does this represent a complete user workflow?
3. Would this catch a "Helldiver-class bug" (conversation lost, files corrupted)?

If yes to any → **Write the test**
If no to all → **Don't write the test**

**"What type of test should I write?"**

- Module works in isolation → `test_{module}.py`
- Module integrates with another → `test_{module1}_{module2}.py`
- Complete user journey → `test_full_workflow.py`

---

**Last Updated**: 2025-11-06
**Next Review**: After Session 5 (UI complete) - validate strategy with real usage
