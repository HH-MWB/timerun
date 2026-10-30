---
title: Time LLM token streaming
---

# Time LLM token streaming

**Problem:** You are building an AI/LLM pipeline and need to measure **latency**, **Time to First Token (TTFT)**, and **total generation time**—while capturing model names and token counts in structured metadata.

**Idea:** Use **`Timer`** around the generation stream or decorate streaming generator functions. TimeRun natively measures generator consumption end-to-end and lets you attach metadata (like model name, prompt tokens, or completion tokens) directly to the measurement.

---

## 1. Measuring full stream completion

Use `@Timer()` on your generator function. The measurement is recorded automatically when the generator finishes yielding:

```python
import time
from timerun import Timer


@Timer(metadata={"model": "gpt-4o", "temperature": 0.7})
def stream_llm_response(prompt: str):
    # Simulated token stream from an LLM API
    tokens = ["The", " quick", " brown", " fox", " jumps."]
    for token in tokens:
        time.sleep(0.05)  # Simulate network chunk arrival
        yield token


# Consume the full stream
chunks = list(stream_llm_response("Hello!"))

# Inspect timing after consumption
m = stream_llm_response.measurements[-1]
print(f"Total Stream Wall Time: {m.wall_time.timedelta}")
print(f"Total Stream CPU Time:  {m.cpu_time.timedelta}")
print(f"Metadata: {m.metadata}")
```

---

## 2. Measuring Time to First Token (TTFT) and Total Time

For interactive applications (chatbots, real-time agents), **Time to First Token (TTFT)** is critical for user experience. You can measure TTFT and total generation time by wrapping the token stream consumer in a `with Timer()` block and recording TTFT into `m.metadata`:

```python
import time
from timerun import Timer


def stream_llm_tokens():
    """Simulate an upstream LLM client yielding token chunks."""
    tokens = ["Hello", " world", "!"]
    for token in tokens:
        time.sleep(0.04)  # Simulate network arrival delay
        yield token


# Measure consumer iteration: capture TTFT and total duration
with Timer(metadata={"stage": "chat_completion"}) as m:
    start_ns = time.perf_counter_ns()
    token_count = 0

    for i, token in enumerate(stream_llm_tokens()):
        if i == 0:
            # Capture Time to First Token (TTFT) on the first yielded chunk
            ttft_ms = (time.perf_counter_ns() - start_ns) / 1e6
            m.metadata["ttft_ms"] = round(ttft_ms, 2)
        token_count += 1

    m.metadata["token_count"] = token_count

# On block exit, full wall & CPU times and custom metadata are available
print(f"Wall time: {m.wall_time.timedelta}")
print(f"TTFT:      {m.metadata['ttft_ms']} ms")
print(f"Tokens:    {m.metadata['token_count']}")
```

---

## 3. Async LLM Streaming

In modern asynchronous web apps (e.g., FastAPI with streaming responses), use `async for` with `@Timer()`:

```python
import asyncio
from timerun import Timer


@Timer(metadata={"pipeline": "rag_streaming"})
async def async_stream_tokens():
    tokens = ["Searching", " knowledge", " base", " ..."]
    for token in tokens:
        await asyncio.sleep(0.02)
        yield token


async def main():
    async for chunk in async_stream_tokens():
        print(chunk, end="", flush=True)
    print()

    m = async_stream_tokens.measurements[-1]
    print(f"Streaming Latency: {m.wall_time.duration / 1e6:.2f} ms")


asyncio.run(main())
```

**See also:** [Time web requests](web-framework.md) for streaming responses in FastAPI endpoints, and [Share results](share-results.md) for shipping LLM metrics to OpenTelemetry or Prometheus.
