<p align="center">
  <a href="https://github.com/HH-MWB/timerun">
    <img src="https://user-images.githubusercontent.com/50187675/62002266-8f926b80-b0ce-11e9-9e54-3b7eeb3a2ae1.png" alt="TimeRun">
  </a>
</p>

<p align="center"><strong>TimeRun</strong> - <em>Python library for elapsed time measurement.</em></p>

<p align="center">
    <a href="https://pypi.org/project/timerun/"><img alt="Version" src="https://img.shields.io/pypi/v/timerun.svg"></a>
    <a href="https://pypi.org/project/timerun/"><img alt="Status" src="https://img.shields.io/pypi/status/timerun.svg"></a>
    <a href="https://github.com/HH-MWB/timerun/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/timerun.svg"></a>
    <a href="https://codecov.io/gh/HH-MWB/timerun"><img alt="Coverage" src="https://codecov.io/gh/HH-MWB/timerun/branch/main/graph/badge.svg"></a>
    <a href="https://pepy.tech/project/timerun"><img alt="Total Downloads" src="https://static.pepy.tech/badge/timerun"></a>
</p>

TimeRun is a simple, yet elegant elapsed time measurement library for [Python](https://www.python.org). It is distributed as a single file module and has no dependencies other than the [Python Standard Library](https://docs.python.org/3/library/).

- **Elapsed Time**: Customized time delta which represents elapsed time in nanoseconds
- **Stopwatch**: An elapsed time measurer with the highest available resolution
- **Timer**: Convenient syntax to capture and save measured elapsed time results

## Setup

### Prerequisites

The only prerequisite to use TimeRun is running **Python 3.9+**.

### Installation

Install TimeRun from [Python Package Index](https://pypi.org/project/timerun/):

```bash
pip install timerun
```

Install TimeRun from [Source Code](https://github.com/HH-MWB/timerun):

```bash
pip install git+https://github.com/HH-MWB/timerun.git
```

## Quickstart

### Measure Code Block

```python
>>> import time
>>> from timerun import Timer
>>> with Timer() as timer:
...     time.sleep(0.1)  # your code here
>>> print(timer.duration)
0:00:00.100000000
```

### Measure Function

```python
>>> import time
>>> from timerun import Timer
>>> timer = Timer()
>>> @timer
... def func():
...     time.sleep(0.1)  # your code here
>>> func()
>>> print(timer.duration)
0:00:00.100000000
```

### Measure Async Function

```python
>>> import asyncio
>>> from timerun import Timer
>>> timer = Timer()
>>> @timer
... async def async_func():
...     await asyncio.sleep(0.1)  # your code here
>>> asyncio.run(async_func())
>>> print(timer.duration)
0:00:00.100000000
```

### Measure Async Code Block

```python
>>> import asyncio
>>> from timerun import Timer
>>> async def async_code():
...     async with Timer() as timer:
...         await asyncio.sleep(0.1)  # your code here
...     print(timer.duration)
>>> asyncio.run(async_code())
0:00:00.100000000
```

### Multiple Measurements

```python
>>> import time
>>> from timerun import Timer
>>> timer = Timer()
>>> with timer:
...     time.sleep(0.1)  # your code here
>>> with timer:
...     time.sleep(0.1)  # your code here
>>> print(timer.duration)  # Last duration
0:00:00.100000000
>>> print(timer.durations)  # All durations
(ElapsedTime(nanoseconds=100000000), ElapsedTime(nanoseconds=100000000))
```

### Advanced Options

```python
>>> from timerun import Timer
>>> # Exclude sleep time from measurements
>>> timer = Timer(count_sleep=False)
>>> # Limit storage to last 10 measurements
>>> timer = Timer(max_len=10)
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/HH-MWB/timerun/blob/main/LICENSE) file for details.
