"""A collection of tests for class ``Timer``."""

from typing import Callable, List

from pytest import raises

from timerun import ElapsedTime, ElapsedTimeNotCaptured, Timer


class TestAsContextManager:
    """Test suite for using Timer as a context manager."""

    def test_single_run(
        self,
        patch_split: Callable,
        timer: Timer,
        elapsed_1_ms: ElapsedTime,
    ) -> None:
        """Test using it as a context manager.

        Test using the timer and ``with`` to capture the duration time
        for code block.

        Parameters
        ----------
        patch_split : Callable
            Patcher has been used to set the captured duration time.
        timer : Timer
            A newly created Timer with unlimited storage size.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        """
        with patch_split(elapsed_times=[1000]):
            with timer:
                pass

        assert timer.duration == elapsed_1_ms

    def test_multiple_run(
        self,
        patch_split: Callable,
        timer: Timer,
        elapsed_100_ns: ElapsedTime,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test run multiple times with the same timer.

        Test run timer using ``with`` ``3`` times and expected to see
        all three captured duration times.

        Parameters
        ----------
        patch_split : Callable
            Patcher has been used to set the captured duration time.
        timer : Timer
            A newly created Timer with unlimited storage size.
        elapsed_100_ns : ElapsedTime
            Elapsed Time of 100 nanoseconds.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        elapsed_1_pt_5_ms : ElapsedTime
            Elapsed Time of 1.5 microseconds.
        """
        with patch_split(elapsed_times=[100, 1000, 1500]):
            for _ in range(3):
                with timer:
                    pass

        assert timer.durations == (
            elapsed_100_ns,
            elapsed_1_ms,
            elapsed_1_pt_5_ms,
        )


class TestAsDecorator:
    """Test suite for using Timer as a function decorator."""

    def test_single_run(
        self,
        patch_split: Callable,
        timer: Timer,
        elapsed_1_ms: ElapsedTime,
    ) -> None:
        """Test the function with a single run.

        Test run decorated function and expected to get the captured
        duration afterward.

        Parameters
        ----------
        patch_split : Callable
            Patcher has been used to set the captured duration time.
        timer : Timer
            A newly created Timer with unlimited storage size.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        """

        @timer
        def func() -> None:
            pass

        with patch_split(elapsed_times=[1000]):
            func()
        assert timer.duration == elapsed_1_ms

    def test_multiple_run(
        self,
        patch_split: Callable,
        timer: Timer,
        elapsed_100_ns: ElapsedTime,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test the function with multiple runs.

        Test run decorated function ``3`` times and expected to see all
        three captured duration times.

        Parameters
        ----------
        patch_split : Callable
            Patcher has been used to set the captured duration time.
        timer : Timer
            A newly created Timer with unlimited storage size.
        elapsed_100_ns : ElapsedTime
            Elapsed Time of 100 nanoseconds.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        elapsed_1_pt_5_ms : ElapsedTime
            Elapsed Time of 1.5 microseconds.
        """

        @timer
        def func() -> None:
            pass

        with patch_split(elapsed_times=[100, 1000, 1500]):
            for _ in range(3):
                func()

        assert timer.durations == (
            elapsed_100_ns,
            elapsed_1_ms,
            elapsed_1_pt_5_ms,
        )


class TestNoElapsedTimeCapturedException:
    """Test suite for NoElapsedTimeCaptured exception."""

    def test_access_duration_attr_before_run(self, timer: Timer) -> None:
        """Test access duration attribute before capturing anything.

        Test tries to access duration attribute before capturing
        anything, expected to see ``ElapsedTimeNotCaptured`` exception.

        Parameters
        ----------
        timer : Timer
            A newly created Timer with unlimited storage size.
        """
        with raises(ElapsedTimeNotCaptured):
            _ = timer.duration


class TestInit:
    """Test suite for Timerinitialization."""

    def test_use_customized_duration_list(self) -> None:
        """Test capture durations into an existing list."""
        durations: List[ElapsedTime] = []
        timer = Timer(storage=durations)
        assert timer._durations is durations

    def test_max_storage_limitation(
        self,
        patch_split: Callable,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test to set the max number of durations been saved.

        Test timer with a max storage limitation at ``2``. Using it to
        catch ``3`` duration times and expected to see two latest only.

        Parameters
        ----------
        patch_split : Callable
            Patcher been used to set the captured duration time.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        elapsed_1_pt_5_ms : ElapsedTime
            Elapsed Time of 1.5 microseconds.
        """
        timer = Timer(max_len=2)

        with patch_split(elapsed_times=[100, 1000, 1500]):
            for _ in range(3):
                with timer:
                    pass

        assert timer.durations == (elapsed_1_ms, elapsed_1_pt_5_ms)
