<p align="center">
  <a href="https://github.com/HH-MWB/timerun">
    <img src="https://user-images.githubusercontent.com/50187675/62002266-8f926b80-b0ce-11e9-9e54-3b7eeb3a2ae1.png" alt="TimeRun">
  </a>
</p>

<p align="center"><strong>TimeRun</strong> - <em>Python library for elapsed time measurement.</em></p>

<p align="center">
    <a href="https://github.com/HH-MWB/timerun/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/timerun.svg"></a>
    <a href="https://pypi.org/project/timerun/"><img alt="PyPI Latest Release" src="https://img.shields.io/pypi/v/timerun.svg"></a>
    <a href="https://pypi.org/project/timerun/"><img alt="Package Status" src="https://img.shields.io/pypi/status/timerun.svg"></a>
    <a href="https://github.com/psf/black/"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="https://pycqa.github.io/isort/"><img alt="Imports: isort" src="https://img.shields.io/badge/%20imports-isort-%231674b1"></a>
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
>>> from timerun import Timer
>>> with Timer() as timer:
...     pass  # put your code here
>>> print(timer.duration)
0:00:00.000000100
```

### Measure Function

```python
>>> from timerun import Timer
>>> timer = Timer()
>>> @timer
... def func():
...     pass  # put your code here
>>> func()
>>> print(timer.duration)
0:00:00.000000100
```

### Measure Async Function

```python
>>> import asyncio
>>> from timerun import Timer
>>> timer = Timer()
>>> @timer
... async def async_func():
...     await asyncio.sleep(0.1)
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
...         await asyncio.sleep(0.1)
...     print(timer.duration)
>>> asyncio.run(async_code())
0:00:00.100000000
```

### Multiple Measurements

```python
>>> from timerun import Timer
>>> timer = Timer()
>>> with timer:
...     pass
>>> with timer:
...     pass
>>> print(timer.duration)  # Last duration
0:00:00.000000100
>>> print(timer.durations)  # All durations
(ElapsedTime(nanoseconds=100), ElapsedTime(nanoseconds=100))
```

### Advanced Options

```python
>>> from timerun import Timer
>>> # Exclude sleep time from measurements
>>> timer = Timer(count_sleep=False)
>>> # Limit storage to last 10 measurements
>>> timer = Timer(max_len=10)
```

## Usage

### Stopwatch

The `Stopwatch` class provides manual control over timing measurements:

```python
>>> from timerun import Stopwatch
>>> stopwatch = Stopwatch()
>>> stopwatch.reset()
>>> # ... your code here ...
>>> elapsed = stopwatch.split()
>>> print(elapsed)
0:00:00.000000100
```

You can configure whether to count sleep time:

```python
>>> # Exclude sleep time from measurements
>>> stopwatch = Stopwatch(count_sleep=False)
```

### ElapsedTime

The `ElapsedTime` class represents elapsed time in nanoseconds with high precision:

```python
>>> from timerun import ElapsedTime
>>> t = ElapsedTime(1000000000)  # 1 second in nanoseconds
>>> print(t)
0:00:01
>>> print(t.nanoseconds)
1000000000
>>> print(t.timedelta)  # Convert to timedelta
0:00:01
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/HH-MWB/timerun/blob/master/LICENSE) file for details.
