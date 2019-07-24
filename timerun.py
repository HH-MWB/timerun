# -*- coding: utf-8 -*-
"""
TimeRun is a Python library for elapsed time measurement.
"""

from time import perf_counter
from time import process_time
from enum import unique
from enum import IntEnum
from contextlib import contextmanager
from functools import partial
from functools import wraps

__version__ = '0.1'
__license__ = 'MIT'


###############################################################################
# Elapsed Time Estimator ######################################################
###############################################################################


class ETE(object):
    """Elapsed Time Estimator

    Elapsed Time Estimator uses the encapsulation of perf_counter function and
    process_time function to measure elapsed time.

    Attributes:
        _timer: a function with the highest available resolution to measure a
                short duration.
        _start: a value in fractional seconds recorded from the last calling of
                the launch function.

    """

    def __init__(self, count_sleep=True):
        """Initialize Elapsed Time Estimator.

        This method will select a time measurement function based on whether
        the user would like to count time elapsed during sleep or not.

        Parameters:
            count_sleep: An optional boolean variable express if the time
                         elapsed during sleep should be counted or not.

        """
        self._timer = perf_counter if count_sleep else process_time

    def launch(self):
        """Launch or relaunch Elapsed Time Estimator.

        The calling of this method will either set the current state to the
        '_start' attribute or rewrite the '_start' attribute. The Estimator
        will only record the value from the latest calling and drop all
        previous values.

        """
        self._start = self._timer()

    def elapse(self):
        """Get elapsed time from latest launch point.

        Returns:
            A float number for time elapsed in fractional seconds.

        Raises:
            AttributeError: An error occurred by accessing the launch point,
                            which is caused by the current Elapsed Time
                            Estimator not been launched after initialization.

        """
        try:
            return self._timer() - self._start
        except AttributeError:
            raise AttributeError('timer has not been launched')


###############################################################################
# Elapsed Time Formatter ######################################################
###############################################################################


@unique
class TimeUnit(IntEnum):
    """Units of Time Delta

    The units of time delta are defined in the following way:
        the name of the unit - number of seconds that this unit has.

    Attributes:
        SEC: second
        MIN: minute - has 60 seconds
        HRS: hour   - has 3,600 (60 * 60) seconds
        DAY: day    - has 86,400 (24 * 60 * 60) seconds

    """

    SEC = 1
    MIN = 60 * SEC
    HRS = 60 * MIN
    DAY = 24 * HRS


class ETF(object):
    """Elapsed Time Formatter

    Elapsed Time Formatter is used to format time from seconds into a nicely
    printable string that involves other units of time, i.e., days, hours,
    minutes, seconds, and nanoseconds.

    Attributes:
        _d: an integer represents days passed for a given time
        _h: an integer represents hours passed for a given time
        _m: an integer represents minutes passed for a given time
        _s: an integer represents seconds passed for a given time
        _n: an integer represents nano seconds passed for a given time

    """

    def __init__(self, time):
        """Initialize Elapsed Time Formatter.

        This method takes time in seconds and converts it into the combination
        of five units: days, hours, minutes, seconds, and nanoseconds. Parts
        smaller than nanoseconds will be rounded off.

        Parameters:
            time: a floating number, which represents time in seconds

        """
        self._d, rem = divmod(int(time), TimeUnit.DAY)
        self._h, rem = divmod(rem, TimeUnit.HRS)
        self._m, self._s = divmod(rem, TimeUnit.MIN)
        self._n = round((time - int(time)) * 1e9)

    def __str__(self):
        """Format String

        This method takes the result from the attributes and converts it into a
        nicely printable string. It also detects if the given time is less than
        one day, and remove the day part from the string if it is.

        """
        time = '{hrs:02}:{min:02}:{sec:02}.{ns:09}'.format(
                hrs=self._h, min=self._m, sec=self._s, ns=self._n)
        return '{} days {}'.format(self._d, time) if self._d > 0 else time


###############################################################################
# Shortcut to Time Measurement ################################################
###############################################################################


@contextmanager
def time_code(label, count_sleep=True):
    """Time a Code Block

    This function is used to measure the time used for a block of code to run
    and print out the time in a nicely printable string with the given name of
    the code block.

    Parameters:
        count_sleep: An optional boolean variable express if the time elapsed
                     during sleep should be counted or not.

    """
    timer = ETE(count_sleep=count_sleep)
    timer.launch()
    try:
        yield
    finally:
        time = ETF(time=timer.elapse())
        print('{} - {}'.format(label, time))


def time_func(func=None, count_sleep=True):
    """Time a Function

    This function is used to measure the time used for a function to run and
    print out the time in a nicely printable string with the name of the
    measured function.

    Parameters:
        count_sleep: An optional boolean variable express if the time elapsed
                     during sleep should be counted or not.

    """
    if func is None:
        return partial(time_func, count_sleep=count_sleep)

    label = '{}.{}'.format(func.__module__, func.__name__)
    timer = ETE(count_sleep=count_sleep)

    @wraps(func)
    def wrapper(*args, **kwargs):
        timer.launch()
        try:
            r = func(*args, **kwargs)
        finally:
            time = ETF(time=timer.elapse())
            print('{} - {}'.format(label, time))
        return r

    return wrapper
