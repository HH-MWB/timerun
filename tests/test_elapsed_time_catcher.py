"""A collection of tests for class ``ElapsedTimeCatcher``."""

from typing import Callable, List

from pytest import raises

from timerun import ElapsedTime, ElapsedTimeCatcher, NoElapsedTimeCaptured


class TestAsContextManager:
    """Test suite for using ElapsedTimeCatcher as context manager."""

    def test_single_run(
        self,
        patch_elapse: Callable,
        unlimited_catcher: ElapsedTimeCatcher,
        elapsed_1_ms: ElapsedTime,
    ) -> None:
        """Test using it as context manager.

        Test using catcher and ``with`` to capture the duration time for
        code block.

        Parameters
        ----------
        patch_elapse : Callable
            Patcher been used to set the captured duration time.
        unlimited_catcher : ElapsedTimeCatcher
            A elapsed time catcher with unlimited storage size.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        """
        with patch_elapse(elapsed_times=[1000]):
            with unlimited_catcher:
                pass

        assert unlimited_catcher.duration == elapsed_1_ms

    def test_multiple_run(
        self,
        patch_elapse: Callable,
        unlimited_catcher: ElapsedTimeCatcher,
        elapsed_100_ns: ElapsedTime,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test run with multiple times with the same catcher.

        Test run catcher using ``with`` ``3`` times and expected to see
        all three captured duration times.

        Parameters
        ----------
        patch_elapse : Callable
            Patcher been used to set the captured duration time.
        unlimited_catcher : ElapsedTimeCatcher
            A elapsed time catcher with unlimited storage size.
        elapsed_100_ns : ElapsedTime
            Elapsed Time of 100 nanoseconds.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        elapsed_1_pt_5_ms : ElapsedTime
            Elapsed Time of 1.5 microseconds.
        """
        with patch_elapse(elapsed_times=[100, 1000, 1500]):
            for _ in range(3):
                with unlimited_catcher:
                    pass

        assert unlimited_catcher.durations == [
            elapsed_100_ns,
            elapsed_1_ms,
            elapsed_1_pt_5_ms,
        ]


class TestAsDecorator:
    """Test suite for using ElapsedTimeCatcher as function decorator."""

    def test_single_run(
        self,
        patch_elapse: Callable,
        unlimited_catcher: ElapsedTimeCatcher,
        elapsed_1_ms: ElapsedTime,
    ) -> None:
        """Test the function with a single runs.

        Test run decorated function and expected to get the captured
        duration afterwards.

        Parameters
        ----------
        patch_elapse : Callable
            Patcher been used to set the captured duration time.
        unlimited_catcher : ElapsedTimeCatcher
            A elapsed time catcher with unlimited storage size.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        """

        @unlimited_catcher
        def func() -> None:
            pass

        with patch_elapse(elapsed_times=[1000]):
            func()
        assert unlimited_catcher.duration == elapsed_1_ms

    def test_multiple_run(
        self,
        patch_elapse: Callable,
        unlimited_catcher: ElapsedTimeCatcher,
        elapsed_100_ns: ElapsedTime,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test the function with multiple runs.

        Test run decorated function ``3`` times and expected to see all
        three captured duration times.

        Parameters
        ----------
        patch_elapse : Callable
            Patcher been used to set the captured duration time.
        unlimited_catcher : ElapsedTimeCatcher
            A elapsed time catcher with unlimited storage size.
        elapsed_100_ns : ElapsedTime
            Elapsed Time of 100 nanoseconds.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        elapsed_1_pt_5_ms : ElapsedTime
            Elapsed Time of 1.5 microseconds.
        """

        @unlimited_catcher
        def func() -> None:
            pass

        with patch_elapse(elapsed_times=[100, 1000, 1500]):
            for _ in range(3):
                func()

        assert unlimited_catcher.durations == [
            elapsed_100_ns,
            elapsed_1_ms,
            elapsed_1_pt_5_ms,
        ]


class TestNoElapsedTimeCapturedException:
    """Test suite for NoElapsedTimeCaptured exception."""

    def test_access_duration_attr_before_run(
        self, unlimited_catcher: ElapsedTimeCatcher
    ) -> None:
        """Test access duration attribute before capture anything.

        Test try to access duration attribute before capture anything,
        expected to see a NoElapsedTimeCaptured exception.

        Parameters
        ----------
        unlimited_catcher : ElapsedTimeCatcher
            A elapsed time catcher with unlimited storage size.
        """
        with raises(NoElapsedTimeCaptured):
            _ = unlimited_catcher.duration


class TestInit:
    """Test suite for Elapsed Time Catcher initialization."""

    def test_use_customized_duration_list(self) -> None:
        """Test capture durations into an existing list."""
        durations: List[ElapsedTime] = []
        catcher = ElapsedTimeCatcher(durations=durations)
        assert catcher.durations is durations

    def test_max_storage_limitation(
        self,
        patch_elapse: Callable,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test to set max number of durations been saved.

        Test catcher with a max storage limitation at ``2``. Using it to
        catch ``3`` duration times and expected to see two latest only.

        Parameters
        ----------
        patch_elapse : Callable
            Patcher been used to set the captured duration time.
        elapsed_1_ms : ElapsedTime
            Elapsed Time of 1 microsecond.
        elapsed_1_pt_5_ms : ElapsedTime
            Elapsed Time of 1.5 microseconds.
        """
        catcher = ElapsedTimeCatcher(max_storage=2)

        with patch_elapse(elapsed_times=[100, 1000, 1500]):
            for _ in range(3):
                with catcher:
                    pass

        assert catcher.durations == [elapsed_1_ms, elapsed_1_pt_5_ms]
