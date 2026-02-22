---
title: Timer (overview)
---

# Timer (overview)

**Timer** is the main entry point. It measures execution and records wall-clock and CPU time per run. It operates in two modes: as a **context manager** (for a block of code) or as a **decorator** (for function or generator calls). Both modes support synchronous and asynchronous use; the decorator also supports sync and async generators.

## Constructor parameters

All parameters are optional and keyword-only.

| Parameter   | Type | Description |
|------------|------|-------------|
| `metadata` | `dict \| None` | Key-value metadata for the measurement(s). Each measurement gets a deep copy at enter time. Defaults to `{}`. |
| `on_start` | `callable \| None` | Called once per measurement when timing is about to start. Receives the `Measurement` (metadata set; `wall_time` and `cpu_time` are `None`). Defaults to `None`. |
| `on_end`   | `callable \| None` | Called once per measurement when timing has just ended. Receives the `Measurement` with `wall_time` and `cpu_time` set. Defaults to `None`. |
| `maxlen`   | `int \| None` | **Decorator only.** Maximum number of measurements to keep on the wrapped callable. Ignored when used as a context manager. Defaults to `None` (unbounded). |

## Context manager mode

Use `with Timer() as m:` (sync) or `async with Timer() as m:` (async). On block exit, the yielded `Measurement` has its `wall_time` and `cpu_time` set. There is one measurement per block; nested and sequential blocks each receive their own measurement. See [Measure a block](measure-block.md) for nested blocks, multiple threads, and exception behavior.

## Decorator mode

Apply `@Timer()` (or `@Timer(metadata={...}, maxlen=100)` etc.) to a function or generator. Each call produces one `Measurement`, appended to the wrapped callable’s `measurements` deque. Supported callables include sync and async functions and sync and async generators (one measurement per call, or per full consumption for generators). See [Measure functions](measure-functions.md) for `maxlen` and thread safety.

## Callbacks

Callbacks are **synchronous only**. To integrate with asynchronous exporters (e.g. OpenTelemetry), schedule work from the callback (e.g. `asyncio.create_task(export(m))` in an async context, or use a thread or queue). See [Callbacks](callbacks.md) for when `on_start` and `on_end` are invoked and what they receive.

**Next:** [Measure a block](measure-block.md)
