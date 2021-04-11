"""TimeRun is a Python library for elapsed time measurement."""

from __future__ import annotations

from collections import deque
from contextlib import ContextDecorator
from dataclasses import dataclass
from datetime import timedelta
from time import perf_counter_ns, process_time_ns
from typing import Callable, Deque, List, Optional, Tuple, Union

__all__: Tuple[str, ...] = (
    # -- Core --
    "ElapsedTime",
    "Stopwatch",
    "Timer",
    # -- Exceptions --
    "TimeRunException",
    "ElapsedTimeNotCaptured",
)

__version__: str = "0.2.0"


# =========================================================================== #
#                                 Exceptions                                  #
# --------------------------------------------------------------------------- #
#                                                                             #
# The invalid behaviors of using the classes, functions in timerun should be  #
# converted to an exception and raised.                                       #
#                                                                             #
# To make exceptions be easier managed, all exceptions created for timerun    #
# library will extend from a base exception ``TimeRunException``.             #
#                                                                             #
# =========================================================================== #


class TimeRunException(Exception):
    """Based exception for TimeRun"""


class ElapsedTimeNotCaptured(TimeRunException, AttributeError):
    """Elapsed Time Not Captured Exception"""

    def __init__(self) -> None:
        super().__init__("Elapsed Time Not Captured.")


# =========================================================================== #
#                                Elapsed Time                                 #
# --------------------------------------------------------------------------- #
#                                                                             #
# In Python, class datetime.timedelta is a duration expressing the difference #
# between two date, time, or datetime instances to microsecond resolution.    #
#                                                                             #
# However, the highest available resolution measurer provided by Python can   #
# measure a short duration in nanoseconds.                                    #
#                                                                             #
# Thus, there is a needs to have a class that can represent elapsed time in   #
# nanoseconds or a higher resolution.                                         #
#                                                                             #
# =========================================================================== #


@dataclass(init=True, repr=False, eq=True, order=True, frozen=True)
class ElapsedTime:
    """Elapsed Time

    An immutable object represent elapsed time in nanoseconds.

    Attributes
    ----------
    nanoseconds : int
        Expressing the elapsed time in nanoseconds.
    timedelta : timedelta
        The duration in timedelta type. This attribute may not maintain
        the original accuracy.

    Parameters
    ----------
    nanoseconds : int
        Expressing the elapsed time in nanoseconds.

    Examples
    --------
    >>> t = ElapsedTime(10)
    >>> t
    ElapsedTime(nanoseconds=10)
    >>> print(t)
    0:00:00.000000010
    """

    __slots__ = ["nanoseconds"]

    nanoseconds: int

    def __str__(self) -> str:
        integer_part = timedelta(seconds=self.nanoseconds // int(1e9))
        decimal_part = self.nanoseconds % int(1e9)

        if decimal_part == 0:
            return str(integer_part)
        return f"{integer_part}.{decimal_part:09}"

    def __repr__(self) -> str:
        return f"ElapsedTime(nanoseconds={self.nanoseconds})"

    @property
    def timedelta(self) -> timedelta:
        """The duration converted from nanoseconds to timedelta type."""
        return timedelta(microseconds=self.nanoseconds // int(1e3))


# =========================================================================== #
#                                  Stopwatch                                  #
# --------------------------------------------------------------------------- #
#                                                                             #
# Based on PEP 418, Python provides performance counter and process time      #
# functions to measure a short duration of time elapsed.                      #
#                                                                             #
# Based on PEP 564, Python got new time functions with nanosecond resolution. #
#                                                                             #
# Ref:                                                                        #
#   *  https://www.python.org/dev/peps/pep-0418/                              #
#   *  https://www.python.org/dev/peps/pep-0564/                              #
#                                                                             #
# =========================================================================== #


class Stopwatch:
    """Stopwatch

    A stopwatch with the highest available resolution (in nanoseconds)
    to measure elapsed time. It can be set to include or exclude the
    sleeping time.

    Parameters
    ----------
    count_sleep : bool, optional
        An optional boolean variable express if the time elapsed during
        sleep should be counted or not.

    Methods
    -------
    reset
        Restart the stopwatch by set starting time to the current time.
    split
        Get elapsed time between now and the starting time.

    Examples
    --------
    >>> stopwatch = Stopwatch()
    >>> stopwatch.reset()
    >>> stopwatch.split()
    ElapsedTime(nanoseconds=100)
    """

    __slots__ = ["_clock", "_start"]

    def __init__(self, count_sleep: Optional[bool] = None) -> None:
        if count_sleep is None:
            count_sleep = True

        self._clock: Callable[[], int] = (
            perf_counter_ns if count_sleep else process_time_ns
        )

        self._start: int = self._clock()

    def reset(self) -> None:
        """Reset the starting time to current time."""
        self._start = self._clock()

    def split(self) -> ElapsedTime:
        """Get elapsed time between now and the starting time."""
        return ElapsedTime(self._clock() - self._start)


# =========================================================================== #
#                                    Timer                                    #
# --------------------------------------------------------------------------- #
#                                                                             #
# For the most use case, the user would just want to measure the elapsed time #
# for a run of code block or function.                                        #
#                                                                             #
# It would be more clean and elegant if the user can measure a function by    #
# using a decorator and measure a code block by using a context manager.      #
#                                                                             #
# =========================================================================== #


class Timer(ContextDecorator):
    """Timer

    A context decorator can capture and save the measured elapsed time.

    Attributes
    ----------
    durations : Tuple[ElapsedTime, ...]
        The captured duration times as a tuple.
    duration : ElapsedTime
        The last captured duration time.

    Parameters
    ----------
    count_sleep : bool, optional
        An optional boolean variable express if the time elapsed during
        sleep should be counted or not.
    storage : List[ElapsedTime] or Deque[ElapsedTime], optional
        A list is used to save captured results. By default initiate a
        new one using deque.
    max_len : int, optional
        The max length for capturing storage, by default infinity.
        Notice that this parameter will only be used when this object
        needs to initiate a new storage queue.

    Examples
    --------
    >>> with Timer() as timer:
    ...     pass
    >>> print(timer.duration)
    0:00:00.000000100

    >>> timer = Timer()
    >>> @timer
    ... def func():
    ...     pass
    >>> func()
    >>> print(timer.duration)
    0:00:00.000000100
    """

    __slots__ = ["_stopwatch", "_durations"]

    def __init__(
        self,
        count_sleep: Optional[bool] = None,
        storage: Optional[Union[List[ElapsedTime], Deque[ElapsedTime]]] = None,
        max_len: Optional[int] = None,
    ) -> None:
        self._stopwatch: Stopwatch = Stopwatch(count_sleep)
        self._durations: Union[List[ElapsedTime], Deque[ElapsedTime]] = (
            storage if storage is not None else deque(maxlen=max_len)
        )

    def __enter__(self) -> Timer:
        self._stopwatch.reset()
        return self

    def __exit__(self, *exc) -> None:
        duration: ElapsedTime = self._stopwatch.split()
        self._durations.append(duration)

    @property
    def durations(self) -> Tuple[ElapsedTime, ...]:
        """The captured duration times as a tuple.

        A tuple contains all captured duration times. Python can unpack
        tuple into multiple variables.

        Examples
        --------
        >>> first_duration, second_duration = timer.durations
        """
        return tuple(self._durations)

    @property
    def duration(self) -> ElapsedTime:
        """The last captured duration time.

        Raises
        ------
        NoElapsedTimeCaptured
            Error occurred by accessing the empty durations list, which
            normally because the measurer has not been triggered yet.
        """
        try:
            return self._durations[-1]
        except IndexError as error:
            raise ElapsedTimeNotCaptured from error
