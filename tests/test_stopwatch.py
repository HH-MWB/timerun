"""A collection of tests for class ``Stopwatch``."""

from time import perf_counter_ns, process_time_ns
from typing import Callable

from timerun import ElapsedTime, Stopwatch


class TestInit:
    """Test suite for stopwatch initialization."""

    def test_include_sleep(self) -> None:
        """Test initialize stopwatch take sleep in count."""
        stopwatch: Stopwatch = Stopwatch(count_sleep=True)
        assert stopwatch._clock == perf_counter_ns

    def test_exclude_sleep(self) -> None:
        """Test initialize stopwatch do not take sleep in count."""
        stopwatch: Stopwatch = Stopwatch(count_sleep=False)
        assert stopwatch._clock == process_time_ns

    def test_default_measurer(self) -> None:
        """Test initialize stopwatch without arguments."""
        default: Stopwatch = Stopwatch()
        include: Stopwatch = Stopwatch(count_sleep=True)
        assert default._clock == include._clock


class TestReset:
    """Test suite for starting stopwatch."""

    def test_reset(self, patch_clock: Callable, stopwatch: Stopwatch) -> None:
        """Test to reset a stopwatch.

        Expected to have a stopwatch which it's `_start` attribute is
        not ``1``, but been reset to ``1`` after call ``reset`` method.

        Parameters
        ----------
        patch_clock : Callable
            Patcher been used to set the starting time at ``1``.
        stopwatch : Stopwatch
            A started Stopwatch, which will be reset.
        """
        assert stopwatch._start != 1
        with patch_clock(elapsed_ns=1):
            stopwatch.reset()
        assert stopwatch._start == 1


class TestSplit:
    """Test suite for split method in stopwatch."""

    def test_calculation(
        self,
        patch_clock: Callable,
        stopwatch: Stopwatch,
        elapsed_100_ns: ElapsedTime,
    ) -> None:
        """Test elapsed time calculation.

        The stopwatch has been started at time ``0``. With patching
        clock time to ``100``, the captured elapsed time should be
        ``100`` nanoseconds.

        Parameters
        ----------
        patch_clock : Callable
            Patcher been used to set the clock time.
        stopwatch : Stopwatch
            A stopwatch which started at time ``0``.
        elapsed_100_ns : ElapsedTime
            Elapsed Time of 100 nanoseconds.
        """
        assert stopwatch._start == 0

        with patch_clock(elapsed_ns=100):
            elapsed: ElapsedTime = stopwatch.split()
        assert elapsed == elapsed_100_ns

    def test_split_multiple_times(
        self,
        patch_clock: Callable,
        stopwatch: Stopwatch,
        elapsed_100_ns: ElapsedTime,
        elapsed_1_ms: ElapsedTime,
    ) -> None:
        """Test call split method multiple times.

        The stopwatch has been started at time ``0``. With patching
        clock time to ``100``, the first captured elapsed time should be
        ``100`` nanoseconds. Then, patching clock time to ``1000``, the
        second captured elapsed time should be ``1000`` nanoseconds.

        Parameters
        ----------
        patch_clock : Callable
            Patcher been used to set the clock time.
        stopwatch : Stopwatch
            A stopwatch which started at time ``0``.
        elapsed_100_ns : ElapsedTime
            Elapsed Time of 100 nanoseconds.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        """
        assert stopwatch._start == 0

        with patch_clock(elapsed_ns=100):
            first_elapsed: ElapsedTime = stopwatch.split()
        assert first_elapsed == elapsed_100_ns

        with patch_clock(elapsed_ns=1000):
            second_elapsed: ElapsedTime = stopwatch.split()
        assert second_elapsed == elapsed_1_ms
