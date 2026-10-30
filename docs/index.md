---
title: TimeRun
---

<h1 align="center">
  <a href="https://github.com/HH-MWB/timerun">
    <img src="https://github.com/user-attachments/assets/00f08873-3ee5-4ee4-a41f-f9eda37fc30d" alt="TimeRun">
  </a>
</h1>

<p align="center">
  <strong>Structured, zero-dependency Python timing for humans and telemetry.</strong><br>
  Instantly isolate wall-clock latency from CPU burn across sync, async, and generators.
</p>

<p align="center">
  <a href="https://pypi.org/project/timerun/"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/timerun.svg"></a>
  <a href="https://codecov.io/gh/HH-MWB/timerun"><img alt="Coverage" src="https://codecov.io/gh/HH-MWB/timerun/branch/main/graph/badge.svg"></a>
  <a href="https://github.com/HH-MWB/timerun/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/timerun.svg"></a>
  <a href="https://pepy.tech/project/timerun"><img alt="Total Downloads" src="https://static.pepy.tech/badge/timerun"></a>
</p>

---

## Why TimeRun?

When your service or script is slow, **is it waiting on network I/O or burning CPU?**

Standard `time.perf_counter()` forces you to write repetitive boilerplate, manual float subtractions, and separate calls to `time.thread_time()`. Heavy profilers (`cProfile`, `py-spy`) and APM agents (Datadog, New Relic) introduce massive overhead, binary dependencies, or vendor lock-in.

**TimeRun bridges the gap:** a single-file, zero-dependency library providing nanosecond-precision wall and CPU timing, bounded execution history, and plug-and-play callbacks for your observability stack.

<div class="grid cards" markdown>

-   **🪶 Zero Dependencies**

    ---

    Standard library only. Safe for libraries, microservices, and air-gapped environments. Single-file architecture with 100% test coverage.

-   **⏱️ Wall + CPU Isolation**

    ---

    Separates elapsed clock time (`perf_counter_ns`) from compute time (`thread_time_ns`). Instantly diagnose whether latency is I/O or CPU bound.

-   **🔌 Observability Ready**

    ---

    Export directly to OpenTelemetry spans, Prometheus histograms, Datadog, or JSON loggers with one lightweight `on_end` callback.

-   **⚡ Async & Thread Safe**

    ---

    Native support for `async with`, async functions, sync/async generators, and multi-threading with task-isolated `ContextVar` stacks.

</div>

---

## Installation

Install TimeRun from [PyPI](https://pypi.org/project/timerun/). Requires **Python 3.10+**.

=== "pip"

    ```bash
    pip install timerun
    ```

=== "uv"

    ```bash
    uv add timerun
    ```

=== "poetry"

    ```bash
    poetry add timerun
    ```

---

## Quickstart

### 1. Measure Code Blocks (Wall vs. CPU)

Wrap any block in `with Timer() as m:` (or `async with Timer() as m:`). On exit, `m.wall_time` and `m.cpu_time` are immediately available:

```python
import time
from timerun import Timer

with Timer() as m:
    time.sleep(0.05)  # Simulates network I/O or database wait
    total = sum(i * i for i in range(100_000))  # Simulates CPU computation

print("Elapsed (Wall):", m.wall_time.timedelta)  # e.g., 0:00:00.055120
print("Compute (CPU):  ", m.cpu_time.timedelta)  # e.g., 0:00:00.005110
```

!!! tip "Why measure both wall-clock and CPU time?"

    If wall time is 2 seconds but CPU time is 5 milliseconds, your code spent 99.7% of its time waiting on I/O. If both are 2 seconds, you have a CPU bottleneck.

### 2. Time Functions and Generators

Use `@Timer()` on sync or async functions. The wrapped function retains a bounded deque of measurements:

```python
from timerun import Timer


@Timer(maxlen=100)
def process_batch(items):
    return [x * 2 for x in items]


process_batch([1, 2, 3])

last = process_batch.measurements[-1]
print("Wall time:", last.wall_time.timedelta)
print("CPU time: ", last.cpu_time.timedelta)
```

### 3. Stream to Logs & Observability

Use `on_end` to ship timings directly to your logs, OpenTelemetry, Prometheus, or Datadog without adding vendor dependencies to your core logic:

```python
import logging
from timerun import Timer

logger = logging.getLogger("app")


def log_timing(m):
    logger.info(
        "task_finished",
        extra={
            "wall_s": m.wall_time.duration / 1e9,
            "cpu_s": m.cpu_time.duration / 1e9,
            **m.metadata,
        },
    )


with Timer(metadata={"endpoint": "/checkout"}, on_end=log_timing):
    pass  # your business logic
```

---

## How It Compares

| Feature | Manual `time.perf_counter()` | Heavy Profilers (`cProfile`, `py-spy`) | APM Agents (`Datadog`, `New Relic`) | **TimeRun** |
| :--- | :---: | :---: | :---: | :---: |
| **Dependencies** | None | Extra tooling | Large binary agents | **Zero (stdlib only)** |
| **Wall vs. CPU Breakdown** | ❌ Manual boilerplate | ⚠️ Sampling overhead | ❌ Usually wall only | **✅ Built-in & precise** |
| **Structured Output** | ❌ Raw floats | ❌ Binary trace files | ⚠️ Proprietary format | **✅ Structured `Measurement`** |
| **Asyncio & Thread Safe** | ❌ Race condition risk | ⚠️ Global runtime cost | ✅ Handled by agent | **✅ Task & Thread isolated** |
| **Telemetry Integration** | ❌ Build it yourself | ❌ Offline analysis only | ⚠️ Vendor locked | **✅ Agnostic (`on_end`)** |
| **Footprint** | 0 LOC | Heavy | Large background daemon | **Single file (~500 LOC)** |

---

## Explore the Docs

<div class="grid cards" markdown>

-   **📖 API Guide**

    ---

    Detailed concepts and lifecycle for `Timer`, `Measurement`, and `TimeSpan`, including concurrency and callbacks.

    [Explore the Guide →](guide/index.md)

-   **🍲 Cookbook & Recipes**

    ---

    Production recipes for FastAPI, OpenTelemetry, Structlog, LLM token streaming, and statistical analysis.

    [View Cookbook Recipes →](cookbook/index.md)

</div>
