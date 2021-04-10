"""TimeRun is an elapsed time measurement library."""

from __future__ import annotations

from contextlib import ContextDecorator
from dataclasses import dataclass
from datetime import timedelta
from time import perf_counter_ns, process_time_ns
from typing import Callable, List, Optional, Tuple

__all__: Tuple[str, ...] = (
    # -- Core --
    "ElapsedTime",
    "ElapsedTimeMeasurer",
    "ElapsedTimeCatcher",
    # -- Exceptions --
    "TimeRunException",
    "MeasurerNotLaunched",
    "NoElapsedTimeCaptured",
)

__version__: str = "0.2.0"


# =========================================================================== #
#                                 Exceptions                                  #
# --------------------------------------------------------------------------- #
#                                                                             #
# All invalid behavior of using timerun classes, functions should be convert  #
# to an exception and raised.                                                 #
#                                                                             #
# In order to make the exceptions be easier managed, all exceptions created   #
# for timerun library will extend from a base exception ``TimeRunException``. #
#                                                                             #
# =========================================================================== #


class TimeRunException(Exception):
    """Based exception for all error raised from ``timerun``."""


class MeasurerNotLaunched(TimeRunException):
    """Measurer Not Launched Exception"""

    def __init__(self) -> None:
        super().__init__("Measurer has not been launched yet.")


class NoElapsedTimeCaptured(TimeRunException):
    """No Elapsed Time Captured Exception"""

    def __init__(self) -> None:
        super().__init__("No duration has been captured yet.")


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
# Thus, there is a need to have a class which can represent elapsed time in   #
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
        The duration in timedelta type. May lose accuracy.

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

    @property
    def timedelta(self) -> timedelta:
        """The duration converted from nanoseconds to timedelta type."""
        return timedelta(microseconds=self.nanoseconds // int(1e3))

    def __str__(self) -> str:
        integer_part = timedelta(seconds=self.nanoseconds // int(1e9))
        decimal_part = self.nanoseconds % int(1e9)

        if decimal_part == 0:
            return str(integer_part)
        return f"{integer_part}.{decimal_part:09}"

    def __repr__(self) -> str:
        return f"ElapsedTime(nanoseconds={self.nanoseconds})"


# =========================================================================== #
#                            Elapsed Time Measurer                            #
# --------------------------------------------------------------------------- #
#                                                                             #
# Based on PEP 418, Python provides performance counter and process time      #
# functions to measure a short duration of time elapsed.                      #
#                                                                             #
# Based on PEP 564, Python provides new function with nanosecond resolution.  #
#                                                                             #
# Ref:                                                                        #
#   *  https://www.python.org/dev/peps/pep-0418/                              #
#   *  https://www.python.org/dev/peps/pep-0564/                              #
#                                                                             #
# =========================================================================== #


class ElapsedTimeMeasurer:
    """Elapsed Time Measurer

    A measurer with the highest available resolution (in nanoseconds) to
    measure elapsed time. It can include or exclude the sleeping time.

    Parameters
    ----------
    count_sleep : bool, optional
        An optional boolean variable express if the time elapsed during
        sleep should be counted or not.

    Methods
    -------
    launch
        Launch or relaunch Elapsed Time Measurer.
    elapse
        Get elapsed time from latest launch point.

    Examples
    --------
    >>> m = ElapsedTimeMeasurer()
    >>> m.launch()
    >>> m.elapse()
    ElapsedTime(nanoseconds=100)
    """

    __slots__ = ["_measure", "_start"]

    def __init__(self, count_sleep: Optional[bool] = None) -> None:
        if count_sleep is None:
            count_sleep = True

        self._measure: Callable[[], int] = (
            perf_counter_ns if count_sleep else process_time_ns
        )

    def launch(self) -> None:
        """Launch or relaunch Elapsed Time Measurer.

        The calling of this method will either set the current state to
        the private attribute ``_start`` or overwrite it.

        The measurer will only record the value from the latest calling
        and drop all previous values.
        """
        self._start: int = self._measure()

    def elapse(self) -> ElapsedTime:
        """Get elapsed time from latest launch point.

        Returns
        -------
        ElapsedTime
            The elapsed time between the launch point and now.

        Raises
        ------
        MeasurerNotLaunched
            Error occurred by accessing the launch point, which normally
            because of the measurer has not been launched before.
        """
        try:
            return ElapsedTime(self._measure() - self._start)
        except AttributeError as e:
            raise MeasurerNotLaunched from e


# =========================================================================== #
#                            Elapsed Time Catcher                             #
# --------------------------------------------------------------------------- #
#                                                                             #
# For the most use case, user would just want to measure the elapsed time for #
# a run of code block or function.                                            #
#                                                                             #
# It would be more Pythonic if user can measure a code block by using context #
# manager and measure a function by using decorator.                          #
#                                                                             #
# =========================================================================== #


class ElapsedTimeCatcher(ContextDecorator):
    """Elapsed Time Catcher

    A context decorator can capture measured elapsed time into list and
    reuse the result afterwards.

    Attributes
    ----------
    durations : List[ElapsedTime]
        The captured duration times.
    duration : ElapsedTime
        The last captured duration time.

    Parameters
    ----------
    count_sleep : bool, optional
        An optional boolean variable express if the time elapsed during
        sleep should be counted or not.
    max_storage : int, optional
        The max length for capturing storage, by default infinity.
    durations : List[ElapsedTime], optional
        A list be used to save captured results. By default init one.

    Examples
    --------
    >>> with ElapsedTimeCatcher() as catcher:
    ...     pass
    >>> print(catcher.duration)
    0:00:00.000000100

    >>> catcher = ElapsedTimeCatcher()
    >>> @catcher
    ... def func():
    ...     pass
    >>> func()
    >>> print(catcher.duration)
    0:00:00.000000100
    """

    __slots__ = ["_measurer", "_max_storage", "durations"]

    def __init__(
        self,
        count_sleep: Optional[bool] = None,
        max_storage: Optional[int] = None,
        durations: Optional[List[ElapsedTime]] = None,
    ) -> None:
        self._measurer: ElapsedTimeMeasurer = ElapsedTimeMeasurer(count_sleep)
        self._max_storage = max_storage
        self.durations: List[ElapsedTime] = (
            durations if durations is not None else []
        )

    @property
    def duration(self) -> ElapsedTime:
        """The last captured duration time.

        Raises
        ------
        NoElapsedTimeCaptured
            Error occurred by accessing the empty durations list, which
            normally because of the measurer has not been triggered yet.
        """
        try:
            return self.durations[-1]
        except IndexError as e:
            raise NoElapsedTimeCaptured from e

    def __enter__(self) -> ElapsedTimeCatcher:
        self._measurer.launch()
        return self

    def __exit__(self, *exc) -> None:
        self.durations.append(self._measurer.elapse())
        if (
            self._max_storage is not None
            and len(self.durations) > self._max_storage
        ):
            self.durations = self.durations[1:]
