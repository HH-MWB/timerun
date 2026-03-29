---
title: Guide
---

# Guide

This section describes the TimeRun API: its concepts, parameters, and behavior. Use it after the [Quickstart](../quickstart/index.md#quick-start) for a complete picture of blocks, functions, metadata, callbacks, and sync/async and generator support.

You can also use it as a lookup while working with the library.

For applied patterns (e.g. attaching a request id in `on_start`, exporting to OpenTelemetry), see the [Cookbook](../cookbook/index.md).

---

## Using the Timer

- **[Timer overview](timer.md)** — How wall and CPU time are recorded, constructor parameters, context manager and decorator usage, and callbacks.
- **[Measure a block](measure-block.md)** — Using `with Timer()` and `async with`; one measurement per block; nested, sequential, and multi-threaded use; exceptions and invalid use.
- **[Measure function calls](measure-functions.md)** — Using `@Timer()` with sync/async functions and generators; the `measurements` deque and `maxlen`; thread safety.
- **[Metadata](metadata.md)** — Supplying and copying metadata; per-measurement mutation; isolation between runs.
- **[Callbacks](callbacks.md)** — `on_start` and `on_end`: when they are invoked, what they receive, and the synchronous-only contract.

## Core types

- **[TimeSpan](timespan.md)** — Immutable time interval: attributes, `timedelta`, comparison, and validation.
- **[Measurement](measurement.md)** — A single run’s result: `wall_time`, `cpu_time`, and `metadata`.
