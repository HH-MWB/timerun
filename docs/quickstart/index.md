---
title: Quickstart
---

<h1 align="center">TimeRun</h1>

**Structured timing for Python.** One small library, no dependencies — wall and CPU time, ready for your logs, metrics, or tracing.

---

## At a glance

You need to **measure execution time** of Python code in a way that’s trustworthy (wall + CPU, not ad-hoc timers), observable (send to logging, OpenTelemetry, or any pipeline), and low-friction (no new dependencies, works in scripts and production). TimeRun does exactly that.

- **Zero dependencies** — Standard library only; safe for libraries and constrained environments.
- **Wall + CPU time** — Distinguish real elapsed time from CPU burn (I/O vs CPU-bound).
- **Observability-ready** — `on_start` / `on_end` callbacks and metadata to plug into logging, OpenTelemetry, or any metrics pipeline.

[Read the full story for positioning →](../overview/index.md)

---

## Quick start

#### Install from [PyPI](https://pypi.org/project/timerun/)

Requires **Python 3.10+**.

```bash
pip install timerun
```

#### Measure a code block

```python
from timerun import Timer

with Timer() as m:
    pass  # your code
```

For async code, use `async with Timer() as m:` the same way.

#### Measure function calls

```python
@Timer()
def my_func():
    pass

my_func()
m = my_func.measurements[-1]  # measurement for last call
```

#### Use the measurement

```python
>>> m.wall_time.timedelta
datetime.timedelta(microseconds=11)
>>> m.cpu_time.timedelta
datetime.timedelta(microseconds=8)
```

How wall and CPU time relate (and why they can differ) is explained in [Timer overview](../guide/timer.md#how-timing-works).

#### Callbacks

Optional `on_start` and `on_end` run once per measurement and receive the same `Measurement` — `on_start` before timings are set, `on_end` after.

```python
from timerun import Timer

with Timer(on_end=lambda m: print(m.wall_time.timedelta)):
    pass  # your code
```

More examples: [Callbacks](../guide/callbacks.md), [Cookbook](../cookbook/index.md) (metadata, logging, OpenTelemetry).

[Read the guide for API details →](../guide/index.md)

---

PyPI, license, coverage, and download stats:

[![PyPI version](https://img.shields.io/pypi/v/timerun.svg)](https://pypi.org/project/timerun/) [![License](https://img.shields.io/pypi/l/timerun.svg)](https://github.com/HH-MWB/timerun/blob/main/LICENSE) [![Coverage](https://codecov.io/gh/HH-MWB/timerun/branch/main/graph/badge.svg)](https://codecov.io/gh/HH-MWB/timerun) [![Total downloads](https://static.pepy.tech/badge/timerun)](https://pepy.tech/project/timerun)
