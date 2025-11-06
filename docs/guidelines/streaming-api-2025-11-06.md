# Streaming API - Anthropic Best Practices

**Researched**: 2025-11-06
**For**: HQ Orchestrator conversational interface
**Status**: Active ✅

---

## Overview

Claude API supports server-sent events (SSE) for incremental streaming, providing real-time feedback during long responses. Critical for Socratic conversation UX.

---

## Key Principles

### Principle 1: Use SDK Context Manager

**Source**: [Streaming Messages](https://docs.claude.com/en/docs/build-with-claude/streaming)

**What**: Python SDK provides `messages.stream()` context manager that handles SSE complexity automatically.

**Why**: Raw HTTP SSE parsing is error-prone. SDK handles event flow, delta accumulation, and recovery.

**How**: Use `with client.messages.stream(...) as stream` pattern.

**Code Example**:
```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-sonnet-4-5",
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

✅ DO:
- Use SDK's automatic handling
- Flush output immediately for real-time display
- Use `text_stream` iterator for simple text responses

❌ DON'T:
- Parse SSE events manually
- Buffer text before displaying (kills real-time feel)
- Use raw HTTP unless absolutely necessary

### Principle 2: Handle Error Events Gracefully

**Source**: [Streaming Messages - Error Handling](https://docs.claude.com/en/docs/build-with-claude/streaming)

**What**: Streams may encounter `overloaded_error` or interruptions.

**Why**: High API usage can cause temporary failures.

**How**: Capture partial responses, resume from last successful point.

**Code Example**:
```python
try:
    with client.messages.stream(...) as stream:
        partial_response = []
        for text in stream.text_stream:
            partial_response.append(text)
            print(text, end="", flush=True)
except anthropic.APIError as e:
    # Resume from partial_response
    messages.append({"role": "assistant", "content": "".join(partial_response)})
    # Retry with accumulated context
```

✅ DO:
- Capture partial responses during streaming
- Resume from last text block on error
- Handle ping events gracefully (they're normal)

❌ DON'T:
- Assume streams always complete
- Try to recover partial tool use blocks (not supported)
- Ignore error events

### Principle 3: Event Flow Understanding

**Source**: [Streaming Messages - Event Types](https://docs.claude.com/en/docs/build-with-claude/streaming)

**What**: Streams follow predictable sequence: `message_start` → content deltas → `message_stop`

**Why**: Understanding flow enables custom handling if SDK insufficient.

**How**: Expect text_delta, input_json_delta (tools), thinking_delta (extended thinking).

**Event Sequence**:
```
1. message_start (empty content)
2. content_block_start
3. content_block_delta (type: text_delta, input_json_delta, thinking_delta)
4. content_block_delta (more chunks...)
5. content_block_stop
6. message_delta (cumulative token counts)
7. message_stop
```

✅ DO:
- Accumulate JSON deltas for tool use
- Wait for `content_block_stop` before parsing tools
- Note cumulative token counts in `message_delta`

❌ DON'T:
- Parse incomplete JSON from `input_json_delta`
- Assume single content block per message

---

## Token Budgets

- No specific limits mentioned for streaming
- Same token budgets as non-streaming API
- Cumulative counts in `message_delta` events

---

## Common Mistakes

1. **Manual SSE Parsing**: Trying to parse events yourself → Use SDK instead
2. **Buffering Text**: Collecting all text before display → Stream immediately with `flush=True`
3. **Ignoring Errors**: Not capturing partial responses → Always save progress for recovery

---

## Latest Updates (2025)

- `thinking_delta` events for extended thinking (new in Claude 4)
- Better error recovery with partial assistant messages
- SDK handles all delta types automatically

---

## Resources

1. [Streaming Messages](https://docs.claude.com/en/docs/build-with-claude/streaming) - Official streaming docs
2. [Messages API](https://docs.anthropic.com/en/api/messages) - Core API reference

---

**Last Updated**: 2025-11-06
**Used In**: Session 2 (HQ Orchestrator)
