---
title: Overview
---

# Overview

TimeRun gives you **structured, dependency-free timing** (wall + CPU) with optional **metadata and callbacks**, so you can measure any Python code and plug results into your existing **observability stack**. Single file, zero dependencies, standard library only.

---

## The problem we solve

Developers and teams need to **measure execution time** of Python code (blocks, functions, async) in a way that is:

- **Trustworthy** — wall-clock and CPU time, not ad-hoc `time.time()` or `time.perf_counter()`.
- **Observable** — easy to send measurements into logging, metrics, or tracing (e.g. OpenTelemetry) without locking them into one vendor.
- **Low-friction** — minimal setup, no extra runtime dependencies, and usable in both scripts and production services.

Alternatives (manual `time.perf_counter()`, heavy APM agents, or “batteries-included” profilers) either lack structure (no CPU vs wall, no metadata), add complexity, or don’t fit the “measure and export” workflow. TimeRun fills that gap.

---

## Who it’s for

- **Python developers** doing performance tuning, benchmarking, or debugging latency.
- **Platform / SRE / backend engineers** who need lightweight, library-level timing that can feed into existing observability (logs, metrics, tracing).
- **Libraries and frameworks** that want optional timing without imposing dependencies on their users.

If that sounds like you, TimeRun is a good fit.

---

## What you get

| Benefit | What it means |
|--------|----------------|
| **Zero dependencies** | Standard library only → no supply-chain or version conflicts; safe to add to libraries and constrained environments. |
| **Single-file** | One module to reason about, audit, or vendor; easy to copy or fork if needed. |
| **Wall + CPU time** | Distinguish “real” elapsed time from CPU burn; better for I/O vs CPU-bound analysis. |
| **Structured measurements** | `Measurement` with `TimeSpan` (nanosecond precision, `timedelta` view) and metadata → ready for logging, metrics, or tracing. |
| **Context manager + decorator** | Same API for ad-hoc blocks and for repeated function/generator/async calls; one mental model. |
| **Observability hooks** | `on_start` / `on_end` with full `Measurement` → integrate with OpenTelemetry, metrics pipelines, or custom logging without baking them into the library. |
| **Bounded history (decorator)** | `maxlen` on the measurements deque → avoid unbounded memory when timing hot paths. |
| **Async-aware** | `async with` and decorators for async functions and async generators → fits modern async Python. |

**Outcomes:**

- **Faster performance work** — add timing with a context manager or decorator; get wall + CPU and optional metadata without wiring up timers by hand.
- **Clean observability integration** — one callback (`on_end`) to push measurements to logs, metrics, or tracing, without coupling the app to a specific vendor.
- **Fewer dependency and maintenance worries** — no extra packages, single-file design, MIT license.

---

## How it compares

| Aspect | TimeRun | Manual `perf_counter` / `process_time()` | Heavy profilers (cProfile, py-spy) | Vendor APM agents |
|--------|--------|----------------------------------------|------------------------------------|-------------------|
| **Dependencies** | None | None | Often extra tooling | Agent + vendor stack |
| **Wall + CPU** | Yes | You wire both | Varies | Usually wall only |
| **Observability** | Your choice (callbacks) | You build it | Export varies | Locked to vendor |
| **Use case** | Targeted timing, feed your stack | Ad-hoc scripts | Whole-process profiling | Full APM |

- **vs manual timing** — TimeRun gives a consistent `Measurement` (wall + CPU + metadata), callbacks, and decorator/context-manager API so you don’t reimplement the same pattern.
- **vs heavy profilers** — TimeRun is for **targeted** timing of chosen blocks or functions and for **feeding observability**, not for whole-process profiling.
- **vs vendor APM** — TimeRun is library-level, dependency-free, and export-agnostic; you decide where measurements go (OpenTelemetry, Prometheus, logs, etc.).

---

## When not to use TimeRun

- **Whole-process profiling** — use cProfile, py-spy, or similar.
- **Full APM (errors, infra, traces)** — use a vendor APM; TimeRun can still feed it via callbacks.
- **Need only ad-hoc one-off timings in a script** — `time.perf_counter()` is fine; TimeRun pays off when you want structure, CPU time, or observability hooks.

---

## Next steps

[Quickstart](../quickstart/index.md#quick-start) to install and run. [Guide](../guide/index.md) for the API. [Cookbook](../cookbook/index.md) for real-world patterns.
