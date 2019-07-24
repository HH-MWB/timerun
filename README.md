# TimeRun

TimeRun is a [Python](https://www.python.org) library for elapsed time measurement.

* Measure elapsed time and format output in **one line** yet providing the highest resolution for time measurement
* All in a single file with no dependencies other than [Python Standard Library](https://docs.python.org/3/library/)

## Features

* Elapsed Time Estimator
    * Measure elapsed time with sleep
    * Measure elapsed time without sleep
* Elapsed Time Formatter
    * Format time into hours, minutes, seconds and nanoseconds
    * Hide days part if time is less than 1 day 
* Shortcut to Time Measurement
    * Measure elapsed time for a code block
    * Measure elapsed time for a function

## Installation

Install TimeRun from [Python Package Index](https://pypi.org/project/timerun/)

```
pip install timerun
```

Install TimeRun from [Source Code](https://github.com/HH-MWB/timerun)

```
python setup.py install
```

## Examples

### Measure code block execution time

```python
from timerun import time_code

with time_code('countdown'):
    n = 1e6
    while n > 0:
        n -= 1
```

```
countdown - 00:00:00.110983022
```

### Measure function execution time

```python
from timerun import time_func

@time_func
def countdown():
    n = 1e6
    while n > 0:
        n -= 1

countdown()
```

```
__main__.countdown - 00:00:00.069651527
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/HH-MWB/timerun/blob/master/LICENSE) file for details
