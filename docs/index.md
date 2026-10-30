---
title: TimeRun
---

<p align="center">
  <a href="https://github.com/HH-MWB/timerun">
    <img src="https://github.com/user-attachments/assets/00f08873-3ee5-4ee4-a41f-f9eda37fc30d" alt="TimeRun">
  </a>
</p>

<p align="center">
  <strong>Structured, zero-dependency Python timing for humans and telemetry.</strong><br>
  A **single-file** Python package with **zero dependencies** beyond the standard library. It records nanosecond-accurate **wall-clock time** (`perf_counter_ns`) and **thread CPU time** (`thread_time_ns`), producing structured `Measurement` objects ready for your logs, metrics, and tracing pipelines.
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

Standard `time.perf_counter()` forces you to write tedious boilerplate, manual float subtractions, and separate calls to `time.thread_time()`. Heavy profilers (`cProfile`, `py-spy`) and APM agents (Datadog, New Relic) introduce massive overhead, binary dependencies, or vendor lock-in.

**TimeRun bridges the gap:** a single-file, zero-dependency library providing nanosecond-precision wall and CPU timing, bounded execution history, and plug-and-play callbacks for your observability stack.

- 🪶 **Zero Dependencies** — Standard library only. Safe for libraries, air-gapped environments, microservices, and CLI tools. Single file, 100% test coverage.
- ⏱️ **Wall + CPU Isolation** — Separates actual elapsed time (`perf_counter_ns`) from compute time (`thread_time_ns`). Instantly diagnose whether latency is I/O or compute bound.
- 🔌 **Observability Ready** — Export directly to OpenTelemetry spans, Prometheus histograms, Datadog, or JSON loggers with one lightweight `on_end` callback.
- ⚡ **Async & Thread Safe** — Native support for `async with`, async functions, sync/async generators, and multi-threading with task-isolated `ContextVar` stacks.

---

## Quickstart

Install from [PyPI](https://pypi.org/project/timerun/). Requires **Python 3.10+**.

```bash
pip install timerun
```

### Measure a code block

Wrap any block in `with Timer() as m:` (or `async with Timer() as m:` for async code). On exit, `m.wall_time` and `m.cpu_time` are set:

```python
import time
from timerun import Timer

with Timer() as m:
    time.sleep(0.05)  # Simulate I/O or network wait
    total = sum(i * i for i in range(100_000))  # Simulate CPU computation

print("Elapsed (Wall):", m.wall_time.timedelta)  # e.g., 0:00:00.055120
print("Compute (CPU):  ", m.cpu_time.timedelta)  # e.g., 0:00:00.005110
```

### Measure function calls

Apply `@Timer()` as a decorator. The wrapped function keeps a bounded deque of measurements:

```python
from timerun import Timer


@Timer(maxlen=10)
def process_data(items):
    return [x * 2 for x in items]


process_data([1, 2, 3])

# Inspect the most recent measurement
last_run = process_data.measurements[-1]
print("Duration:", last_run.wall_time.timedelta)
print("CPU burn:", last_run.cpu_time.timedelta)
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

## Next Steps

- **[📖 Guide](guide/index.md)** — Complete API reference for `Timer`, `Measurement`, `TimeSpan`, metadata, and callbacks.
- **[🍲 Cookbook](cookbook/index.md)** — Production recipes for FastAPI, OpenTelemetry, Structlog, LLM token streaming, and benchmarks.
