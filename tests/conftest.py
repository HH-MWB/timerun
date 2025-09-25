"""A collection of shared PyTest fixtures for timerun."""

from contextlib import contextmanager
from typing import Callable, ContextManager, Iterable, Iterator, Tuple
from unittest.mock import Mock

from pytest import MonkeyPatch, fixture

from timerun import ElapsedTime, Stopwatch, Timer

__all__: Tuple[str, ...] = (
    # -- Patcheres --
    "patch_clock",
    "patch_split",
    # -- Initiated Instances --
    "stopwatch",
    "timer",
    # -- Elapsed Time --
    "elapsed_1_ns",
    "elapsed_100_ns",
    "elapsed_1_ms",
    "elapsed_1_pt_5_ms",
    "elapsed_1_sec",
)


# =========================================================================== #
#                                  Patcheres                                  #
# =========================================================================== #


@fixture
def patch_clock(monkeypatch: MonkeyPatch) -> Callable[[int], ContextManager]:
    """Patch the clock method in Stopwatch.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        The fixture has been used to patch the clock method.

    Returns
    -------
    Callable[[int], ContextManager]
        A context manager takes integer argument and patch that value as
        the return value of the clock method.

    Examples
    --------
    >>> with patch_clock(elapsed_ns=1):
    ...     pass
    """

    @contextmanager
    def patch(elapsed_ns: int) -> Iterator[None]:
        """Patch clock method through monkeypatch context.

        Parameters
        ----------
        elapsed_ns : int
            The value should be returned by the clock method.
        """
        monkeypatch.setattr(Stopwatch, "_clock", lambda self: elapsed_ns)
        yield

    return patch


@fixture
def patch_split(
    monkeypatch: MonkeyPatch,
) -> Callable[[Iterable[int]], ContextManager]:
    """Patch the split method in Timer.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
         The fixture has been used to patch the split method.

    Returns
    -------
    Callable[[Iterable[int]], ContextManager]
        A context manager takes a list of integers as nanoseconds and
        patch those as the return values of the elapse method.

    Examples
    --------
    >>> with patch_split(elapsed_times=[100, 200, 300]):
    ...     pass
    """

    @contextmanager
    def patch(elapsed_times: Iterable[int]) -> Iterator[None]:
        """Patch split method through monkeypatch context.

        Parameters
        ----------
        elapsed_times : Iterable[int]
            The nanoseconds should be returned by the split method.
        """
        mock_stopwatch = Mock(spec=["reset", "split"])
        mock_stopwatch.split.side_effect = [
            ElapsedTime(nanoseconds=t) for t in elapsed_times
        ]

        monkeypatch.setattr(Timer, "_stopwatch", mock_stopwatch)
        yield

    return patch


# =========================================================================== #
#                             Initiated Instances                             #
# =========================================================================== #


@fixture
def stopwatch() -> Stopwatch:
    """A newly created Stopwatch started at time ``0``."""
    watch: Stopwatch = Stopwatch()
    watch._start = 0  # pylint: disable=protected-access
    return watch


@fixture
def timer() -> Timer:
    """A newly created Timer with unlimited storage size."""
    return Timer()


# =========================================================================== #
#                                Elapsed Time                                 #
# =========================================================================== #


@fixture
def elapsed_1_ns() -> ElapsedTime:
    """Elapsed Time of 1 nanosecond."""
    return ElapsedTime(nanoseconds=1)


@fixture
def elapsed_100_ns() -> ElapsedTime:
    """Elapsed Time of 100 nanoseconds."""
    return ElapsedTime(nanoseconds=100)


@fixture
def elapsed_1_ms() -> ElapsedTime:
    """Elapsed Time of 1 microsecond."""
    return ElapsedTime(nanoseconds=1000)


@fixture
def elapsed_1_pt_5_ms() -> ElapsedTime:
    """Elapsed Time of 1.5 microseconds."""
    return ElapsedTime(nanoseconds=1500)


@fixture
def elapsed_1_sec() -> ElapsedTime:
    """Elapsed Time of 1 second."""
    return ElapsedTime(nanoseconds=int(1e9))
