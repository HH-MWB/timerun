---
title: Reference
---

# Reference

This section describes the TimeRun API: its concepts, parameters, and behavior. Use it after the [Quick start](../index.md#quick-start) for a complete picture of blocks, functions, metadata, callbacks, and sync/async and generator support, or as a lookup while using the library.

For applied patterns (e.g. attaching a request id in `on_start`, exporting to OpenTelemetry), see [Recipes](../recipes/index.md).

---

## Core types

- **[TimeSpan](timespan.md)** — Immutable time interval: attributes, `timedelta`, comparison, and validation.
- **[Measurement](measurement.md)** — A single timing result: `wall_time`, `cpu_time`, and `metadata`; when values are set and how to use them.

## Timer

- **[Timer (overview)](timer.md)** — Constructor parameters and the two modes (context manager and decorator); what each mode yields.
- **[Measure a block](measure-block.md)** — Using `with Timer()` and `async with`; one measurement per block; nested, sequential, and multi-threaded use; exceptions and invalid use.
- **[Measure functions](measure-functions.md)** — Using `@Timer()` with sync/async functions and generators; the `measurements` deque and `maxlen`; thread safety.
- **[Metadata](metadata.md)** — Supplying and copying metadata; per-measurement mutation; isolation between runs.
- **[Callbacks](callbacks.md)** — `on_start` and `on_end`: when they are invoked, what they receive, and the synchronous-only contract.
