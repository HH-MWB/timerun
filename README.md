<p align="center">
  <a href="https://github.com/HH-MWB/timerun">
    <img src="https://user-images.githubusercontent.com/50187675/62002266-8f926b80-b0ce-11e9-9e54-3b7eeb3a2ae1.png" alt="TimeRun">
  </a>
</p>

<p align="center"><strong>TimeRun</strong> — <em>Structured timing for Python.</em></p>

<p align="center">
    <a href="https://pypi.org/project/timerun/"><img alt="Version" src="https://img.shields.io/pypi/v/timerun.svg"></a>
    <a href="https://pypi.org/project/timerun/"><img alt="Status" src="https://img.shields.io/pypi/status/timerun.svg"></a>
    <a href="https://github.com/HH-MWB/timerun/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/timerun.svg"></a>
    <a href="https://codecov.io/gh/HH-MWB/timerun"><img alt="Coverage" src="https://codecov.io/gh/HH-MWB/timerun/branch/main/graph/badge.svg"></a>
    <a href="https://pepy.tech/project/timerun"><img alt="Total Downloads" src="https://static.pepy.tech/badge/timerun"></a>
</p>

TimeRun is a **single-file** Python package with **no dependencies** beyond the standard library. It records **wall-clock time** and **CPU time** when you measure **a block** or **function calls** (one `Measurement` per block or per call) and supports optional **metadata** (e.g. run id, tags) and **callbacks** (`on_start` / `on_end`) per measurement.

For positioning and the full value proposition, see [Overview](https://hh-mwb.github.io/timerun/overview/) on the docs site.

## Installation

From [PyPI](https://pypi.org/project/timerun/):

```bash
pip install timerun
```

From [source](https://github.com/HH-MWB/timerun):

```bash
pip install git+https://github.com/HH-MWB/timerun.git
```

*Note: Requires Python 3.10+.*

## Usage

### Time Code Block

Use `with Timer() as m:` (or `async with`). The yielded `Measurement` has `wall_time` and `cpu_time`:

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

Use `@Timer()`. One `Measurement` per call is appended to the callable’s `measurements` deque:

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

### Callbacks

Optional `on_start` and `on_end` callbacks run once per measurement. Both receive the `Measurement` instance — `on_start` before timings are set, `on_end` after. For example:

Print elapsed time when a block finishes:

```python
>>> from timerun import Timer
>>> with Timer(on_end=lambda m: print(m.wall_time.timedelta)):
...     pass  # code block to be measured
...  
0:00:00.000008
```

Attach a trace id before each call starts:

```python
>>> from uuid import uuid4
>>> from timerun import Timer
>>> @Timer(on_start=lambda m: m.metadata.update(trace_id=uuid4().hex))
... def func():
...     return
...  
>>> func()
>>> func.measurements[-1].metadata
{'trace_id': '8aa2c000c98843738a2f0d5d3600d052'}
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](https://github.com/HH-MWB/timerun/blob/main/CONTRIBUTING.md) for setup, testing, and pull request guidelines.

## License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/HH-MWB/timerun/blob/main/LICENSE) file for details.
