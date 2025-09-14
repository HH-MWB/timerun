"""TimeRun is a Python library for elapsed time measurement."""

from __future__ import annotations

from collections import deque
from contextlib import ContextDecorator
from dataclasses import dataclass
from datetime import timedelta
from time import perf_counter_ns, process_time_ns
from typing import (
    Callable,
    Iterator,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
)

__all__: Tuple[str, ...] = (
    # -- Core --
    "ElapsedTime",
    "Stopwatch",
    "Timer",
    # -- Exceptions --
    "TimeRunException",
    "NoDurationCaptured",
)

__version__: str = "0.2.0"


# =========================================================================== #
#                                Type Protocols                               #
# --------------------------------------------------------------------------- #
#                                                                             #
# The Timer class needs to store captured durations in a flexible way that    #
# allows users to provide their own storage implementations.                  #
#                                                                             #
# Instead of restricting to specific types like List or Deque, timerun uses a #
# protocol to define the required interface for duration storage.             #
#                                                                             #
# This allows users to provide custom storage backends (database, file,       #
# memory-mapped, etc.) as long as they implement the basic sequence methods.  #
#                                                                             #
# =========================================================================== #

T = TypeVar("T")


class AppendableSequence(Protocol[T]):
    """Protocol for sequences that support appending and indexing."""

    def append(self, item: T) -> None:
        """Add an item to the sequence."""

    def __getitem__(self, index: int) -> T:
        """Get item by index (supports negative indexing)."""

    def __len__(self) -> int:
        """Return number of items in the sequence."""

    def __iter__(self) -> Iterator[T]:
        """Iterate over items in the sequence."""


# =========================================================================== #
#                                 Exceptions                                  #
# --------------------------------------------------------------------------- #
#                                                                             #
# Invalid behaviors when using the classes and functions in timerun should be #
# converted to an exception and raised.                                       #
#                                                                             #
# To make exceptions easier to manage, all exceptions created for the timerun #
# library will extend from a base exception ``TimeRunException``.             #
#                                                                             #
# =========================================================================== #


class TimeRunException(Exception):
    """Base exception for TimeRun"""


class NoDurationCaptured(TimeRunException, AttributeError):
    """No Duration Captured Exception"""

    def __init__(self) -> None:
        super().__init__(
            "No duration available. This is likely because the Timer has not "
            "been used to measure any code blocks or functions yet."
        )


# =========================================================================== #
#                                Elapsed Time                                 #
# --------------------------------------------------------------------------- #
#                                                                             #
# In Python, class datetime.timedelta is a duration expressing the difference #
# between two date, time, or datetime instances to microsecond resolution.    #
#                                                                             #
# However, the highest available resolution measurer provided by Python can   #
# measure short durations in nanoseconds.                                     #
#                                                                             #
# Thus, there is a need to have a class that can represent elapsed time at a  #
# higher resolution (nanoseconds) for the best accuracy.                      #
#                                                                             #
# =========================================================================== #


@dataclass(init=True, repr=False, eq=True, order=True, frozen=True)
class ElapsedTime:
    """Elapsed Time

    An immutable object representing elapsed time in nanoseconds.

    Attributes
    ----------
    nanoseconds : int
        The elapsed time expressed in nanoseconds.
    timedelta : timedelta
        The duration as a timedelta type. This attribute may not
        maintain the original accuracy.

    Parameters
    ----------
    nanoseconds : int
        The elapsed time expressed in nanoseconds.

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
        """The duration converted from nanoseconds to a timedelta type."""
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
        An optional boolean variable expressing whether the time elapsed
        during sleep should be counted or not. Defaults to True if None.

    Methods
    -------
    reset
        Restart the stopwatch by setting the starting time to the
        current time.
    split
        Get the elapsed time between now and the starting time.

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
        """Reset the starting time to the current time."""
        self._start = self._clock()

    def split(self) -> ElapsedTime:
        """Get the elapsed time between now and the starting time."""
        return ElapsedTime(self._clock() - self._start)


# =========================================================================== #
#                                    Timer                                    #
# --------------------------------------------------------------------------- #
#                                                                             #
# For most use cases, the user would just want to measure the elapsed time    #
# for a run of a code block or function.                                      #
#                                                                             #
# It would be cleaner and more elegant if the user can measure a function by  #
# using a decorator and measure a code block by using a context manager.      #
#                                                                             #
# =========================================================================== #


class Timer(ContextDecorator):
    """Timer

    A context decorator that can capture and save the measured elapsed
    time.

    Attributes
    ----------
    durations : Tuple[ElapsedTime, ...]
        The captured duration times as a tuple.
    duration : ElapsedTime
        The last captured duration time.

    Parameters
    ----------
    count_sleep : bool, optional
        An optional boolean variable expressing whether the time elapsed
        during sleep should be counted or not. Defaults to True if None.
    storage : AppendableSequence[ElapsedTime], optional
        A sequence-like object used to save captured results.
        If provided, this storage will be used directly and max_len will
        be ignored. If not provided, a new deque will be created.
    max_len : int, optional
        The maximum length for the capturing storage. Defaults to None,
        which will create storage with infinite length.

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
        storage: Optional[AppendableSequence[ElapsedTime]] = None,
        max_len: Optional[int] = None,
    ) -> None:
        self._stopwatch: Stopwatch = Stopwatch(count_sleep)
        self._durations: AppendableSequence[ElapsedTime] = (
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

        A tuple containing all captured duration times, that can be
        unpacked into multiple variables.

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
        NoDurationCaptured
            Error that occurs when accessing an empty durations list,
            which is usually because the measurer has not been triggered
            yet.
        """
        try:
            return self._durations[-1]
        except IndexError as error:
            raise NoDurationCaptured from error
