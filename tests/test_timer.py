"""A collection of tests for class ``Timer``."""

# pylint: disable=no-self-use

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

import pytest

from timerun import ElapsedTime, NoDurationCapturedError, Timer

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable, Iterable
    from contextlib import AbstractContextManager

# =========================================================================== #
# Test suite for using Timer as a context manager.                            #
# =========================================================================== #


def test_use_timer_as_context_manager_single_run(
    patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
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
    with patch_split([1000]), timer:
        pass

    assert timer.duration == elapsed_1_ms


def test_use_timer_as_context_manager_multiple_run(
    patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
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
    with patch_split([100, 1000, 1500]):
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
        patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
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

        with patch_split([1000]):
            func()
        assert timer.duration == elapsed_1_ms

    def test_multiple_run(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
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

        with patch_split([100, 1000, 1500]):
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
        anything, expected to see ``NoDurationCapturedError`` exception.

        Parameters
        ----------
        timer : Timer
            A newly created Timer with unlimited storage size.

        """
        with pytest.raises(NoDurationCapturedError):
            _ = timer.duration


class TestInit:
    """Test suite for Timerinitialization."""

    def test_use_customized_duration_list(self) -> None:
        """Test capture durations into an existing list."""
        durations: list[ElapsedTime] = []
        timer = Timer(storage=durations)
        assert (
            timer._durations is durations  # pylint: disable=protected-access  # noqa: SLF001
        )

    def test_max_storage_limitation(
        self,
        patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
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

        with patch_split([100, 1000, 1500]):
            for _ in range(3):
                with timer:
                    pass

        assert timer.durations == (elapsed_1_ms, elapsed_1_pt_5_ms)


# =========================================================================== #
# Test suite for using Timer as an async context manager.                     #
# =========================================================================== #


@pytest.mark.asyncio
async def test_use_timer_as_async_context_manager_single_run(
    patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
    timer: Timer,
    elapsed_1_ms: ElapsedTime,
) -> None:
    """Test using it as an async context manager.

    Test using the timer and ``async with`` to capture the duration time
    for async code block.

    Parameters
    ----------
    patch_split : Callable
        Patcher has been used to set the captured duration time.
    timer : Timer
        A newly created Timer with unlimited storage size.
    elapsed_1_ms : ElapsedTime
        Elapsed Time of 1 microsecond.

    """
    with patch_split([1000]):
        async with timer:
            await asyncio.sleep(0)

    assert timer.duration == elapsed_1_ms


@pytest.mark.asyncio
async def test_use_timer_as_async_context_manager_multiple_run(
    patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
    timer: Timer,
    elapsed_100_ns: ElapsedTime,
    elapsed_1_ms: ElapsedTime,
    elapsed_1_pt_5_ms: ElapsedTime,
) -> None:
    """Test run multiple times with the same timer (async).

    Test run timer using ``async with`` ``3`` times and expected to see
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
    with patch_split([100, 1000, 1500]):
        for _ in range(3):
            async with timer:
                await asyncio.sleep(0)

    assert timer.durations == (
        elapsed_100_ns,
        elapsed_1_ms,
        elapsed_1_pt_5_ms,
    )


class TestAsAsyncDecorator:
    """Test suite for using Timer as an async function decorator."""

    @pytest.mark.asyncio
    async def test_single_run(
        self,
        patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
        timer: Timer,
        elapsed_1_ms: ElapsedTime,
    ) -> None:
        """Test the async function with a single run.

        Test run decorated async function and expected to get the captured
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
        async def async_func() -> None:
            await asyncio.sleep(0)

        with patch_split([1000]):
            await cast("Awaitable[None]", async_func())
        assert timer.duration == elapsed_1_ms

    @pytest.mark.asyncio
    async def test_multiple_run(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
        timer: Timer,
        elapsed_100_ns: ElapsedTime,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test the async function with multiple runs.

        Test run decorated async function ``3`` times and expected to see all
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
        async def async_func() -> None:
            await asyncio.sleep(0)

        with patch_split([100, 1000, 1500]):
            for _ in range(3):
                await cast("Awaitable[None]", async_func())

        assert timer.durations == (
            elapsed_100_ns,
            elapsed_1_ms,
            elapsed_1_pt_5_ms,
        )


class TestAsAsyncGeneratorDecorator:
    """Test suite for using Timer as an async generator function decorator."""

    @pytest.mark.asyncio
    async def test_single_run(
        self,
        patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
        timer: Timer,
        elapsed_1_ms: ElapsedTime,
    ) -> None:
        """Test the async generator function with a single run.

        Test run decorated async generator function and expected to get the
        captured duration afterward.

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
        async def async_gen_func() -> AsyncGenerator[int]:
            """Async generator function for testing.

            Yields
            ------
            int
                Sequential integers for testing.

            """
            await asyncio.sleep(0)
            yield 1
            await asyncio.sleep(0)
            yield 2

        with patch_split([1000]):
            items: list[int] = [
                item
                async for item in cast(
                    "AsyncGenerator[int]",
                    async_gen_func(),
                )
            ]

        assert items == [1, 2]
        assert timer.duration == elapsed_1_ms

    @pytest.mark.asyncio
    async def test_multiple_run(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        patch_split: Callable[[Iterable[int]], AbstractContextManager[None]],
        timer: Timer,
        elapsed_100_ns: ElapsedTime,
        elapsed_1_ms: ElapsedTime,
        elapsed_1_pt_5_ms: ElapsedTime,
    ) -> None:
        """Test the async generator function with multiple runs.

        Test run decorated async generator function ``3`` times and expected
        to see all three captured duration times.

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
        async def async_gen_func() -> AsyncGenerator[int]:
            """Async generator function for testing.

            Yields
            ------
            int
                Sequential integers for testing.

            """
            await asyncio.sleep(0)
            yield 1

        with patch_split([100, 1000, 1500]):
            for _ in range(3):
                async_gen: AsyncGenerator[int] = cast(
                    "AsyncGenerator[int]",
                    async_gen_func(),
                )
                async for _ in async_gen:
                    pass

        assert timer.durations == (
            elapsed_100_ns,
            elapsed_1_ms,
            elapsed_1_pt_5_ms,
        )
