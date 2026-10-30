<p align="center">
  <a href="https://github.com/HH-MWB/timerun">
    <img src="https://github.com/user-attachments/assets/00f08873-3ee5-4ee4-a41f-f9eda37fc30d" alt="TimeRun">
  </a>
</p>

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

> **Why both?** If wall time is 2 seconds but CPU time is 5 milliseconds, your code spent 99.7% of its time waiting on I/O. If both are 2 seconds, you have a CPU bottleneck.

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

with Timer(
    metadata={"service": "checkout", "user_id": "u-123"},
    on_end=lambda m: logger.info(
        "checkout_completed",
        extra={
            "wall_ms": m.wall_time.duration / 1e6,
            "cpu_ms": m.cpu_time.duration / 1e6,
            **m.metadata,
        },
    ),
):
    pass  # your operation
```

## Installation

```bash
pip install timerun
```

*Requires Python 3.10+.*

## Why TimeRun?

When code runs slowly, **is it waiting on network/disk I/O, or burning CPU?**

- `time.perf_counter()` only gives a raw float of elapsed wall time. Measuring CPU time requires manual `time.thread_time()` calls and boilerplate.
- Profilers (`cProfile`, `py-spy`) and APM agents (`Datadog`, `New Relic`) introduce binary dependencies, sampling overhead, or vendor lock-in.
- Naive timing patterns risk race conditions and crosstalk in concurrent `asyncio` tasks or multi-threaded workers.

TimeRun provides clean, structured timing with sub-microsecond overhead:

| Feature | Manual `time.perf_counter()` | Profilers (`cProfile`, `py-spy`) | APM Agents (`Datadog`, `New Relic`) | **TimeRun** |
| :--- | :---: | :---: | :---: | :---: |
| **Dependencies** | None | Extra tooling | Large binary agents | **Zero (stdlib only)** |
| **Wall vs. CPU Breakdown** | ❌ Manual boilerplate | ⚠️ Profiling overhead | ❌ Usually wall only | **✅ Built-in & precise** |
| **Structured Output** | ❌ Raw floats | ❌ Binary trace files | ⚠️ Proprietary format | **✅ Structured `Measurement`** |
| **Asyncio & Thread Safe** | ❌ Race condition risk | ⚠️ Global runtime cost | ✅ Handled by agent | **✅ Task & Thread isolated** |
| **Telemetry Hooks** | ❌ Build it yourself | ❌ Offline analysis only | ⚠️ Vendor locked | **✅ Agnostic (`on_end`)** |
| **Footprint** | 0 LOC | Heavy | Large background daemon | **Single file (~500 LOC)** |

## Key Capabilities

- **Zero Supply-Chain Risk:** Pure Python standard library only (`time`, `dataclasses`, `contextvars`); vendorable as a single file (`timerun.py`).
- **Context Isolation:** Native `ContextVar` stacks ensure concurrent `asyncio` tasks and threads never mix up measurements.
- **Sub-Microsecond Overhead:** Slotted dataclasses and integer nanoseconds keep internal overhead under ~0.4 µs.
- **Full Async & Generator Support:** Accurately times coroutines, synchronous generators, and asynchronous streaming generators across full iteration.
- **100% Test Coverage:** Verified with comprehensive Behavior-Driven Development (BDD) test suites.

## Documentation

- **[Documentation Site](https://hh-mwb.github.io/timerun/)** — Tutorials, concepts, and guides.
- **[API Guide](https://hh-mwb.github.io/timerun/guide/)** — In-depth reference for `Timer`, `Measurement`, and `TimeSpan`.
- **[Cookbooks](https://hh-mwb.github.io/timerun/cookbook/)** — Real-world recipes for FastAPI, OpenTelemetry, Structlog, and LLM streaming.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](https://github.com/HH-MWB/timerun/blob/main/CONTRIBUTING.md) for setup, testing, and pull request guidelines.

## License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/HH-MWB/timerun/blob/main/LICENSE) file for details.
