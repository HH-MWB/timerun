"""A collection of tests for class ``ElapsedTimeMeasurer``."""

from time import perf_counter_ns, process_time_ns
from typing import Callable

from pytest import raises

from timerun import ElapsedTime, ElapsedTimeMeasurer, MeasurerNotLaunched


class TestInit:
    """Test suite for Elapsed Time Measurer initialization."""

    def test_include_sleep(self) -> None:
        """Test initialize Elapsed Time Measurer take sleep in count."""
        measurer: ElapsedTimeMeasurer = ElapsedTimeMeasurer(count_sleep=True)
        assert measurer._measure == perf_counter_ns

    def test_exclude_sleep(self) -> None:
        """Test initialize Elapsed Time Measurer do not take sleep in count."""
        measurer: ElapsedTimeMeasurer = ElapsedTimeMeasurer(count_sleep=False)
        assert measurer._measure == process_time_ns

    def test_default_measurer(self) -> None:
        """Test initialize Elapsed Time Measurer without arguments."""
        default: ElapsedTimeMeasurer = ElapsedTimeMeasurer()
        include: ElapsedTimeMeasurer = ElapsedTimeMeasurer(count_sleep=True)
        assert default._measure == include._measure


class TestLaunch:
    """Test suite for launching Elapsed Time Measurer."""

    def test_launch(
        self, patch_measure: Callable, unlaunched_measurer: ElapsedTimeMeasurer
    ) -> None:
        """Test to launch a newly created elapsed time measurer.

        After ``launch`` method been called, expected the `_start`
        attribute been set at ``0``.

        Parameters
        ----------
        patch_measure : Callable
            Patcher been used to set the launching time at ``0``.
        unlaunched_measurer : ElapsedTimeMeasurer
            An unlaunched elapsed time measurer, which will be launched.
        """
        with patch_measure(elapsed_ns=0):
            unlaunched_measurer.launch()
        assert unlaunched_measurer._start == 0

    def test_relaunch(
        self, patch_measure: Callable, launched_measurer: ElapsedTimeMeasurer
    ) -> None:
        """Test to relaunch a launched elapsed time measurer.

        Expected to have a measurer which it's `_start` attribute is not
        ``1``, but been reset to ``1`` after called ``launch`` method.

        Parameters
        ----------
        patch_measure : Callable
            Patcher been used to set the launching time at ``1``.
        launched_measurer : ElapsedTimeMeasurer
            A launched elapsed time measurer, which will be relaunched.
        """
        assert launched_measurer._start != 1
        with patch_measure(elapsed_ns=1):
            launched_measurer.launch()
        assert launched_measurer._start == 1


class TestElapse:
    """Test suite for elapse method in Elapsed Time Measurer."""

    def test_calculation(
        self,
        patch_measure: Callable,
        launched_measurer: ElapsedTimeMeasurer,
        elapsed_1_ns: ElapsedTime,
    ) -> None:
        """Test elapsed time calculation.

        The launched measurer is a measurer been launched at time ``0``.
        With patching measure time at ``1``, the elapsed time should be
        ``1`` nanosecond.

        Parameters
        ----------
        patch_measure : Callable
            Patcher been used to set the launching time at ``1``.
        launched_measurer : ElapsedTimeMeasurer
            A elapsed time measurer which launched at time ``0``.
        elapsed_1_ns : ElapsedTime
            Elapsed Time of 1 nanosecond.
        """
        assert launched_measurer._start == 0
        with patch_measure(elapsed_ns=1):
            elapsed: ElapsedTime = launched_measurer.elapse()
        assert elapsed == elapsed_1_ns

    def test_unlaunched_measurer(
        self, unlaunched_measurer: ElapsedTimeMeasurer
    ) -> None:
        """Test call elapse method on unlaunched measurer.

        Given an unlaunched measurer and call ``elapse`` method,
        expected to see ``MeasurerNotLaunched`` exception.

        Parameters
        ----------
        unlaunched_measurer : ElapsedTimeMeasurer
            A newly created, unlaunched elapsed time measurer.
        """
        with raises(MeasurerNotLaunched):
            unlaunched_measurer.elapse()
