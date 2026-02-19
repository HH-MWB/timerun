<p align="center">
  <a href="https://github.com/HH-MWB/timerun">
    <img src="https://user-images.githubusercontent.com/50187675/62002266-8f926b80-b0ce-11e9-9e54-3b7eeb3a2ae1.png" alt="TimeRun">
  </a>
</p>

<p align="center"><strong>TimeRun</strong> — <em>Python package for time measurement.</em></p>

<p align="center">
    <a href="https://pypi.org/project/timerun/"><img alt="Version" src="https://img.shields.io/pypi/v/timerun.svg"></a>
    <a href="https://pypi.org/project/timerun/"><img alt="Status" src="https://img.shields.io/pypi/status/timerun.svg"></a>
    <a href="https://github.com/HH-MWB/timerun/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/timerun.svg"></a>
    <a href="https://codecov.io/gh/HH-MWB/timerun"><img alt="Coverage" src="https://codecov.io/gh/HH-MWB/timerun/branch/main/graph/badge.svg"></a>
    <a href="https://pepy.tech/project/timerun"><img alt="Total Downloads" src="https://static.pepy.tech/badge/timerun"></a>
</p>

TimeRun is a **single-file** Python package with no dependencies beyond the [Python Standard Library](https://docs.python.org/3/library/). The package is designed to stay minimal and dependency-free.

It records **wall-clock time** (real elapsed time) and **CPU time** (process time) for code blocks or function calls, and lets you attach optional **metadata** (e.g. run id, tags) to each measurement.

## Setup

### Prerequisites

**Python 3.10+**

### Installation

From [PyPI](https://pypi.org/project/timerun/):

```bash
pip install timerun
```

From source:

```bash
pip install git+https://github.com/HH-MWB/timerun.git
```

## Quickstart

### Time Code Block

Use `with Timer() as m:` or `async with Timer() as m:`. On block exit, the yielded `Measurement` has `wall_time` and `cpu_time` set.

```python
>>> from timerun import Timer
>>> with Timer() as m:
...     pass  # code block to be measured
...
>>> m.wall_time.timedelta
datetime.timedelta(microseconds=11)
>>> m.cpu_time.timedelta
datetime.timedelta(microseconds=8)
```

*Note: On block exit the timer records CPU time first, then wall time, so wall time is slightly larger than CPU time even when there is no I/O or scheduling.*

### Time Function Calls

Use `@Timer()` to time every call. Works with sync and async functions and with sync and async generators. One `Measurement` per call is appended to the wrapped callable's `measurements` deque.

```python
>>> from timerun import Timer
>>> @Timer()
... def func():  # function to be measured
...     return
...
>>> func()
>>> func.measurements[-1].wall_time.timedelta
datetime.timedelta(microseconds=11)
>>> func.measurements[-1].cpu_time.timedelta
datetime.timedelta(microseconds=8)
```

*Note: Argument `maxlen` caps how many measurements are kept (e.g. `@Timer(maxlen=10)`). By default the deque is unbounded.*

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](https://github.com/HH-MWB/timerun/blob/main/CONTRIBUTING.md) for setup, testing, and pull request guidelines.

## License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/HH-MWB/timerun/blob/main/LICENSE) file for details.
