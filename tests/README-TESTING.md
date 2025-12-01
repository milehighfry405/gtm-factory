# Testing Guide - Cost-Aware LLM Testing

## 🚨 CRITICAL: Avoiding Credit Burn

**Your tests call expensive APIs** (Tavily, OpenAI, Anthropic). Without proper setup, running tests repeatedly **burns through credits fast**.

**Solution**: VCR.py pattern (record once, replay forever)

---

## How It Works

### The VCR Pattern

Think of it like recording a TV show:
1. **First run** - Record real API responses to "cassette" files (~$0.70 total for all tests)
2. **Every future run** - Replay from cassettes ($0, instant, deterministic)

**Cassettes** are YAML files stored in `tests/cassettes/` containing:
- HTTP requests
- HTTP responses
- Headers, status codes, body content

---

## Quick Start

### Step 1: Record Cassettes (DO THIS ONCE)

**IMPORTANT**: This will cost ~$0.70 in Tavily credits (one-time cost)

```bash
# Record all researcher tests (makes REAL API calls)
pytest tests/test_researcher.py --record-mode=once

# You'll see:
# - Tests run slower (waiting for real API calls)
# - Cassette files created in tests/cassettes/
# - Cost: ~$0.10 per test = ~$0.70 total
```

### Step 2: Run Tests Normally (FREE FOREVER)

```bash
# Run tests normally (replays from cassettes, $0)
pytest tests/test_researcher.py

# You'll see:
# - Tests run FAST (<30 seconds instead of 2-3 minutes)
# - No API calls made
# - Cost: $0
```

That's it! You can now run tests 1000 times without burning credits.

---

## Test Markers Explained

### @pytest.mark.vcr()

**What it does**: Records HTTP requests/responses to cassettes

**When to use**: Any test that calls external APIs (Tavily, OpenAI, Anthropic)

**Example**:
```python
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_researcher_executes_task():
    # This test will record Tavily API calls to cassette
    researcher = GeneralResearcher()
    output = await researcher.execute_research(...)
```

### @pytest.mark.expensive

**What it does**: Marks tests that cost money (alerts you they're expensive)

**When to use**: Tests with external API calls that have non-trivial cost

**Example**:
```python
@pytest.mark.expensive
@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_parallel_researchers():
    # Two Tavily searches = ~$0.20
    outputs = await researcher.execute_multiple([brief1, brief2])
```

**To run only cheap tests**:
```bash
pytest -m "not expensive"
```

---

## Common Commands

### Run Tests (Normal - Uses Cassettes)

```bash
# All tests (replays from cassettes)
pytest

# Just researcher tests
pytest tests/test_researcher.py

# Run and show which cassettes are used
pytest -v tests/test_researcher.py
```

### Record/Re-record Cassettes

```bash
# Record NEW cassettes only (doesn't overwrite existing)
pytest tests/test_researcher.py --record-mode=once

# Re-record ALL cassettes (overwrites existing - costs money!)
pytest tests/test_researcher.py --record-mode=rewrite

# Record only if cassette is missing (safe)
pytest tests/test_researcher.py --record-mode=new_episodes
```

### Skip Expensive Tests

```bash
# Run only fast, cheap tests
pytest -m "not expensive"

# Run only expensive tests (to verify they still work)
pytest -m expensive --record-mode=once
```

---

## File Structure

```
tests/
├── cassettes/                    # VCR cassettes (recorded API responses)
│   ├── test_researcher/
│   │   ├── test_execute_simple_research.yaml
│   │   ├── test_token_budget_warning.yaml
│   │   ├── test_output_metadata_complete.yaml
│   │   └── ...
│   └── test_generators/
│       └── ...
├── fixtures/                     # Static test data (manually created)
│   ├── sample_research_output.md
│   ├── sample_drop_metadata.json
│   └── ...
├── test_researcher.py           # Tests with @pytest.mark.vcr()
├── test_generators.py
└── README-TESTING.md            # This file
```

---

## Cost Breakdown

### Initial Recording (One-Time)

| Test | API Calls | Tavily Cost | OpenAI Cost | Total |
|------|-----------|-------------|-------------|-------|
| test_execute_simple_research | 1 Tavily search | ~$0.10 | ~$0.02 | ~$0.12 |
| test_token_budget_warning | 1 Tavily search | ~$0.10 | ~$0.02 | ~$0.12 |
| test_output_metadata_complete | 1 Tavily search | ~$0.10 | ~$0.02 | ~$0.12 |
| test_multiple_researchers_parallel | 2 Tavily searches | ~$0.20 | ~$0.04 | ~$0.24 |
| test_markdown_output_valid | 1 Tavily search | ~$0.10 | ~$0.02 | ~$0.12 |
| test_creates_drop_folder_if_missing | 1 Tavily search | ~$0.10 | ~$0.02 | ~$0.12 |

**Total One-Time Cost**: ~$0.84 (Tavily + OpenAI combined)

### Future Test Runs (With Cassettes)

**Cost**: $0
**Speed**: <30 seconds (vs 2-3 minutes with real API calls)

**Savings**: If you run tests 50 times during development:
- Without VCR: 50 × $0.84 = **$42** 😱
- With VCR: $0.84 (first time) + $0 (all future runs) = **$0.84** 🎉

---

## When to Re-record Cassettes

### You MUST re-record when:

1. **Prompt changes** - If you modify mission briefing format
2. **gpt-researcher update** - If you update the gpt-researcher library
3. **API changes** - If Tavily/OpenAI changes their API

### How to know cassettes are outdated:

- Tests start failing with schema errors
- Responses don't match new expected format
- You added new fields to ResearchOutput

### How to re-record:

```bash
# Re-record specific test
pytest tests/test_researcher.py::TestResearcherIsolation::test_execute_simple_research --record-mode=rewrite

# Re-record all researcher tests (costs ~$0.84)
pytest tests/test_researcher.py --record-mode=rewrite
```

---

## Safety Features

### 1. Default Record Mode = `none`

In `pytest.ini`, we set:
```ini
vcr_record_mode = none  # Never record, always replay
```

**This means**:
- By default, tests NEVER make real API calls
- If cassette is missing, test fails (you must explicitly record)
- Prevents accidental credit burn

### 2. Expensive Test Marker

All tests with API calls are marked `@pytest.mark.expensive`:

```bash
# Skip expensive tests by default in CI
pytest -m "not expensive"
```

### 3. Git Ignore (Optional)

If cassettes contain sensitive data (API keys in headers), add to `.gitignore`:
```
tests/cassettes/
```

But usually it's GOOD to commit cassettes so teammates don't need to record them.

---

## Troubleshooting

### "Cassette not found" Error

**Problem**: Test fails with "Can not find cassette"

**Solution**: Record cassettes first
```bash
pytest tests/test_researcher.py --record-mode=once
```

### Tests Pass But Feature Broken

**Problem**: Cassettes are outdated, tests replay old successful responses

**Solution**: Re-record cassettes
```bash
pytest tests/test_researcher.py --record-mode=rewrite
```

### Test Hangs Forever

**Problem**: Test is making real API call (not using VCR)

**Solution**: Check test has `@pytest.mark.vcr()` decorator

### Cassettes Too Large

**Problem**: Cassette files are huge (>1MB)

**Solution**: Filter response bodies in pytest.ini:
```ini
[pytest]
vcr_filter_post_data_parameters = api_key
```

---

## Best Practices

### ✅ DO

- Record cassettes once, commit to git
- Mark all API tests with `@pytest.mark.expensive`
- Use `--record-mode=once` for initial recording
- Re-record when prompts/APIs change
- Run tests frequently (they're free with cassettes!)

### ❌ DON'T

- Use `--record-mode=all` (re-records EVERY time = $$$ burn)
- Delete cassettes directory accidentally
- Forget to add `@pytest.mark.vcr()` to new API tests
- Run expensive tests in CI without cassettes

---

## Adding VCR to New Tests

When writing a new test that calls external APIs:

```python
@pytest.mark.vcr()          # Record HTTP to cassette
@pytest.mark.expensive      # Mark as costly
@pytest.mark.asyncio        # If async
async def test_new_feature():
    # Test that calls Tavily/OpenAI/Anthropic
    result = await some_api_call()
    assert result
```

Then record once:
```bash
pytest tests/test_file.py::test_new_feature --record-mode=once
```

Done! Future runs are free.

---

## Summary

**The Golden Rule**:
> Record cassettes ONCE, replay FOREVER

**Commands to remember**:
```bash
# First time (costs ~$0.84)
pytest tests/test_researcher.py --record-mode=once

# Every other time (FREE)
pytest tests/test_researcher.py
```

**You're protected from credit burn** because:
1. Default record mode = `none` (never records unless you ask)
2. Tests are marked `@pytest.mark.expensive` (easy to skip)
3. Cassettes are reusable (record once, team uses forever)

---

## Next Steps

1. ✅ **Record cassettes** (one-time ~$0.84 cost)
   ```bash
   pytest tests/test_researcher.py --record-mode=once
   ```

2. ✅ **Verify they work** (should be fast and free)
   ```bash
   pytest tests/test_researcher.py
   ```

3. ✅ **Commit cassettes** to git
   ```bash
   git add tests/cassettes/
   git commit -m "chore: Add VCR cassettes for researcher tests"
   ```

4. ✅ **Run tests as often as you want** (now FREE)
   ```bash
   pytest
   ```

**You can now iterate rapidly without burning credits!** 🎉
