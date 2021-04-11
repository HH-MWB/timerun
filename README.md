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

- **Elapsed Time**: Customized time delta which represents elapsed time in nanoseconds.
- **Stopwatch**: An elapsed time measurer with the highest available resolution.
- **Timer**: Convenient syntax to capture measured elapsed time result and save it.

## Setup

### Prerequisites

The only prerequisite to use TimeRun is running **Python 3.7+**.

### Installation

Install TimeRun from [Python Package Index](https://pypi.org/project/timerun/):

```
pip install timerun
```

Install TimeRun from [Source Code](https://github.com/HH-MWB/timerun):

```
python setup.py install
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

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/HH-MWB/timerun/blob/master/LICENSE) file for details.
