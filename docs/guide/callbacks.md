---
title: Callbacks
---

# Callbacks

The optional **`on_start`** and **`on_end`** callbacks are invoked once per measurement. Both receive the same **Measurement** instance that the Timer yields or appends for that run.

## When they are invoked and what they receive

| Callback | When | State of the Measurement |
|----------|------|---------------------------|
| `on_start(measurement)` | When timing is about to start (on enter of the block or start of the decorated call). | `metadata` is set (a deep copy of the Timer’s initial metadata). `wall_time` and `cpu_time` are **`None`**. |
| `on_end(measurement)`   | When timing has just ended (on block exit or end of the decorated call). | `wall_time` and `cpu_time` are set. `metadata` may have been mutated in the block or in `on_start`. |

Use `on_start` to add to `metadata` (e.g. from context variables). Use `on_end` to read durations and metadata and send them to logging, OpenTelemetry, or a metrics pipeline.

## Synchronous only

Callbacks are **synchronous only**. They are invoked on the same thread and must return before the Timer continues. To integrate with asynchronous exporters (e.g. OpenTelemetry), schedule work from the callback (e.g. `asyncio.create_task(export(m))` in an async context, or use a thread or queue).

## Example

```python
from timerun import Timer

with Timer(on_end=lambda m: print(m.wall_time.timedelta)):
    pass  # code block to be measured
```

For applied patterns (logging, files, OpenTelemetry), see [Share results](../recipes/share-results.md).

**Back to:** [Reference](index.md)
