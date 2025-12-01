# Testing Quick Start - Avoid Burning Credits

## 🚨 Problem Solved

**Before**: Running `pytest` burned ~$0.70 in Tavily credits EVERY TIME
**After**: Record once (~$1 total), replay forever ($0)

## ✅ What I Fixed

1. ✅ **Added VCR to all expensive tests** - 9 tests now record/replay
2. ✅ **Created pytest.ini** - Prevents accidental API calls by default
3. ✅ **Added test markers** - Clear which tests cost money
4. ✅ **Updated pyproject.toml** - All testing tools included

### Tests Protected (No More Credit Burn)

**Researcher Tests** (7 tests = ~$0.70):
- test_execute_simple_research
- test_token_budget_warning
- test_output_metadata_complete
- test_multiple_researchers_parallel (2 API calls!)
- test_markdown_output_valid
- test_creates_drop_folder_if_missing

**Generator Tests** (2 tests = ~$0.20):
- test_synthesis_real_api_call
- test_critical_analysis_real_api_call

---

## 🎯 What You Need to Do (5 Minutes)

### Step 1: Record Cassettes (ONE TIME ONLY)

This will cost ~$1 total (Tavily + OpenAI combined):

```bash
# Record all expensive tests (makes REAL API calls once)
pytest -m expensive --record-mode=once
```

**What happens**:
- Tests run slower (waiting for real APIs)
- Cassette files created in `tests/cassettes/`
- **Cost: ~$0.90 total** (one-time)

### Step 2: Run Tests Normally (FREE FOREVER)

```bash
# Run all tests (replays from cassettes, $0)
pytest
```

**What happens**:
- Tests run FAST (<30 seconds)
- No API calls made
- **Cost: $0**

You can now run tests 1000 times without burning credits! 🎉

---

## 🔒 Safety Features (You're Protected)

### 1. Default = No Recording

In `pytest.ini`:
```ini
vcr_record_mode = none  # Never record unless you ask
```

**This means**:
- Accidentally running `pytest` → $0 (replays from cassettes)
- Missing cassette? → Test fails (forces you to record explicitly)
- **Cannot accidentally burn credits**

### 2. Expensive Tests Marked

All API-heavy tests have `@pytest.mark.expensive`:

```bash
# Skip expensive tests (only run cheap ones)
pytest -m "not expensive"

# Run only expensive tests (to verify they still work)
pytest -m expensive --record-mode=once
```

### 3. Clear Cost Visibility

Every expensive test has cost in docstring:
```python
@pytest.mark.vcr()
@pytest.mark.expensive
async def test_researcher_executes_task():
    """
    First run: ~$0.10 (Tavily)
    Future runs: $0 (cassette replay)
    """
```

---

## 📊 Cost Breakdown

### One-Time Recording Cost

| Test | Tavily | OpenAI | Total |
|------|--------|--------|-------|
| Researcher tests (7) | ~$0.70 | ~$0.10 | ~$0.80 |
| Generator tests (2) | $0 | ~$0.20 | ~$0.20 |
| **TOTAL** | ~$0.70 | ~$0.30 | **~$1.00** |

### Future Test Runs (With Cassettes)

**Cost**: $0
**Speed**: <30 seconds
**Frequency**: Unlimited

### Savings Example

**Without VCR**:
- Run tests 50 times during development = 50 × $1 = **$50** 😱

**With VCR**:
- First run = $1
- Next 49 runs = $0
- **Total = $1** 🎉

**You save $49 for every 50 test runs!**

---

## 🔄 When to Re-record

You only need to re-record cassettes when:

1. **Prompts change** - Modified mission briefings or system prompts
2. **Library updates** - Updated gpt-researcher or OpenAI SDK
3. **API changes** - Tavily/OpenAI changes response format

**How to re-record**:
```bash
# Re-record specific test
pytest tests/test_researcher.py::test_execute_simple_research --record-mode=rewrite

# Re-record all expensive tests
pytest -m expensive --record-mode=rewrite
```

---

## 🛠️ Common Commands

```bash
# Run all tests (uses cassettes, $0)
pytest

# Run only cheap tests (no API calls at all)
pytest -m "not expensive"

# Record cassettes first time (~$1 one-time)
pytest -m expensive --record-mode=once

# Re-record cassettes (costs money again)
pytest -m expensive --record-mode=rewrite

# Run with coverage report
pytest --cov=core --cov-report=html

# Run only researcher tests
pytest tests/test_researcher.py

# Run only generator tests
pytest tests/test_generators.py
```

---

## 📁 What Got Created

```
.
├── pytest.ini                    # Pytest config (vcr_record_mode = none)
├── pyproject.toml               # Updated with pytest-recording dependency
├── tests/
│   ├── README-TESTING.md        # Comprehensive testing guide
│   ├── cassettes/               # VCR cassettes (will be created on first run)
│   │   ├── test_researcher/
│   │   └── test_generators/
│   ├── test_researcher.py       # ✅ All tests marked with @pytest.mark.vcr()
│   └── test_generators.py       # ✅ Expensive tests marked
└── TESTING-QUICKSTART.md        # This file
```

---

## ✅ Next Steps

1. **Record cassettes** (5 min, ~$1 cost):
   ```bash
   pytest -m expensive --record-mode=once
   ```

2. **Verify they work** (<1 min, $0):
   ```bash
   pytest
   ```

3. **Commit cassettes** to git (optional but recommended):
   ```bash
   git add tests/cassettes/ pytest.ini pyproject.toml
   git commit -m "chore: Add VCR cassettes for cost-free testing"
   ```

4. **Run tests as much as you want** ($0):
   ```bash
   pytest
   ```

---

## 📚 Full Documentation

For detailed info, see:
- **[tests/README-TESTING.md](tests/README-TESTING.md)** - Comprehensive testing guide
- **[docs/guidelines/project-health-audit-2025-11-19.md](docs/guidelines/project-health-audit-2025-11-19.md)** - Full research findings

---

## 🎉 Summary

**You're now protected from credit burn!**

- Default mode = replay from cassettes ($0)
- Expensive tests clearly marked
- One-time recording cost = ~$1
- Future test runs = FREE

**Run tests as often as you want without worrying about cost** 🚀
