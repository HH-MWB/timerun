![TimeRun](https://user-images.githubusercontent.com/50187675/62002266-8f926b80-b0ce-11e9-9e54-3b7eeb3a2ae1.png)

TimeRun is a simple, yet elegant elapsed time measurement library for [Python](https://www.python.org). It is distributed as a single file module and has no dependencies other than the [Python Standard Library](https://docs.python.org/3/library/).

- **Elapsed Time**: Customized time delta which represent elapsed time in nanoseconds.
- **Elapsed Time Measurer**: Measure a time elapsed with the highest available resolution.
- **Elapsed Time Catcher**: Convenient syntax to capture measured result and save it.

## Requirements

- Python 3.6+

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

### Measure A Code Block

```python
>>> from timerun import ElapsedTimeCatcher
>>> with ElapsedTimeCatcher() as catcher:
...     pass  # put your code here
>>> print(catcher.duration)
0:00:00.000000100
```

### Measure A Function

```python
>>> from timerun import ElapsedTimeCatcher
>>> catcher = ElapsedTimeCatcher()
>>> @catcher
... def func():
...     pass  # put your code here
>>> func()
>>> print(catcher.duration)
0:00:00.000000100
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/HH-MWB/timerun/blob/master/LICENSE) file for details.
