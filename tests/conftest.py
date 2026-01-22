"""A collection of shared PyTest fixtures for timerun."""

from collections.abc import Callable, Iterable, Iterator
from contextlib import AbstractContextManager, contextmanager
from unittest.mock import Mock

import pytest

from timerun import ElapsedTime, Stopwatch, Timer

# =========================================================================== #
#                                  Patcheres                                  #
# =========================================================================== #


@pytest.fixture
def patch_clock(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[int], AbstractContextManager[None]]:
    """Patch the clock method in Stopwatch.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        The fixture has been used to patch the clock method.

    Returns
    -------
    Callable[[int], AbstractContextManager[None]]
        A context manager takes integer argument and patch that value as
        the return value of the clock method.

    Examples
    --------
    >>> with patch_clock(1):
    ...     pass

    """

    @contextmanager
    def patch(elapsed_ns: int) -> Iterator[None]:
        """Patch clock method through monkeypatch context.

        Parameters
        ----------
        elapsed_ns : int
            The value should be returned by the clock method.

        Yields
        ------
        None
            Control is yielded back to the caller.

        """
        monkeypatch.setattr(Stopwatch, "_clock", lambda _: elapsed_ns)
        yield

    return patch


@pytest.fixture
def patch_split(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[Iterable[int]], AbstractContextManager[None]]:
    """Patch the split method in Timer.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        The fixture has been used to patch the split method.

    Returns
    -------
    Callable[[Iterable[int]], AbstractContextManager[None]]
        A context manager takes a list of integers as nanoseconds and
        patch those as the return values of the elapse method.

    Examples
    --------
    >>> with patch_split([100, 200, 300]):
    ...     pass

    """

    @contextmanager
    def patch(elapsed_times: Iterable[int]) -> Iterator[None]:
        """Patch split method through monkeypatch context.

        Parameters
        ----------
        elapsed_times : Iterable[int]
            The nanoseconds should be returned by the split method.

        Yields
        ------
        None
            Control is yielded back to the caller.

        """
        mock_stopwatch = Mock(spec=["reset", "split"])
        mock_stopwatch.split.configure_mock(
            side_effect=[ElapsedTime(nanoseconds=t) for t in elapsed_times],
        )

        monkeypatch.setattr(Timer, "_stopwatch", mock_stopwatch)
        yield

    return patch


# =========================================================================== #
#                             Initiated Instances                             #
# =========================================================================== #


@pytest.fixture
def stopwatch() -> Stopwatch:
    """Create a Stopwatch started at time ``0``.

    Returns
    -------
    Stopwatch
        A stopwatch started at time ``0``.

    """
    watch: Stopwatch = Stopwatch()
    watch._start = 0  # pylint: disable=protected-access  # noqa: SLF001
    return watch


@pytest.fixture
def timer() -> Timer:
    """Create a Timer with unlimited storage size.

    Returns
    -------
    Timer
        A newly created Timer.

    """
    return Timer()


# =========================================================================== #
#                                Elapsed Time                                 #
# =========================================================================== #


@pytest.fixture
def elapsed_1_ns() -> ElapsedTime:
    """Elapsed Time of 1 nanosecond.

    Returns
    -------
    ElapsedTime
        Elapsed time of 1 nanosecond.

    """
    return ElapsedTime(nanoseconds=1)


@pytest.fixture
def elapsed_100_ns() -> ElapsedTime:
    """Elapsed Time of 100 nanoseconds.

    Returns
    -------
    ElapsedTime
        Elapsed time of 100 nanoseconds.

    """
    return ElapsedTime(nanoseconds=100)


@pytest.fixture
def elapsed_1_ms() -> ElapsedTime:
    """Elapsed Time of 1 microsecond.

    Returns
    -------
    ElapsedTime
        Elapsed time of 1 microsecond.

    """
    return ElapsedTime(nanoseconds=1000)


@pytest.fixture
def elapsed_1_pt_5_ms() -> ElapsedTime:
    """Elapsed Time of 1.5 microseconds.

    Returns
    -------
    ElapsedTime
        Elapsed time of 1.5 microseconds.

    """
    return ElapsedTime(nanoseconds=1500)


@pytest.fixture
def elapsed_1_sec() -> ElapsedTime:
    """Elapsed Time of 1 second.

    Returns
    -------
    ElapsedTime
        Elapsed time of 1 second.

    """
    return ElapsedTime(nanoseconds=int(1e9))
