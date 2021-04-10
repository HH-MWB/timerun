"""A collection of shared PyTest fixtures for timerun."""

from contextlib import contextmanager
from typing import Callable, ContextManager, Iterable, Iterator, Tuple
from unittest.mock import Mock

from pytest import MonkeyPatch, fixture

from timerun import ElapsedTime, ElapsedTimeCatcher, ElapsedTimeMeasurer

__all__: Tuple[str, ...] = (
    # -- Elapsed Time --
    "elapsed_1_ns",
    "elapsed_100_ns",
    "elapsed_1_ms",
    "elapsed_1_pt_5_ms",
    "elapsed_1_sec",
    # -- Elapsed Time Measurer --
    "patch_measure",
    "unlaunched_measurer",
    "launched_measurer",
    # -- Elapsed Time Catcher --
    "patch_elapse",
    "unlimited_catcher",
)


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


# =========================================================================== #
#                            Elapsed Time Measurer                            #
# =========================================================================== #


@fixture
def patch_measure(monkeypatch: MonkeyPatch) -> Callable[[int], ContextManager]:
    """Patch the measure method in ElapsedTimeMeasurer.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        Fixture been used to patch measure method.

    Returns
    -------
    Callable[[int], ContextManager]
        A context manager takes intger argument and patch that value as
        the return value of the measure method.

    Examples
    --------
    >>> with patch_measure(elapsed_ns=1):
    ...     pass
    """

    @contextmanager
    def patch(elapsed_ns: int) -> Iterator[None]:
        """Patch measure method through monkeypatch context.

        Parameters
        ----------
        elapsed_ns : int
            Value should be returned by the measure method.
        """
        monkeypatch.setattr(
            ElapsedTimeMeasurer, "_measure", lambda self: elapsed_ns
        )
        yield

    return patch


@fixture
def unlaunched_measurer() -> ElapsedTimeMeasurer:
    """Unlaunced Elapsed Time Measurer

    A newly created, unlaunched elapsed time measurer.

    Returns
    -------
    ElapsedTimeMeasurer
        A newly created, unlaunched elapsed time measurer.
    """
    return ElapsedTimeMeasurer()


@fixture
def launched_measurer(
    patch_measure: Callable, unlaunched_measurer: ElapsedTimeMeasurer
) -> ElapsedTimeMeasurer:
    """Launched Elapsed Time Measurer

    A elapsed time measurer which launched at time ``0``.

    Parameters
    ----------
    patch_measure : Callable
        Patcher been used to set the launching time at ``0``.
    unlaunched_measurer : ElapsedTimeMeasurer
        A newly created, unlaunched elapsed time measurer.

    Returns
    -------
    ElapsedTimeMeasurer
        A newly created elapsed time measurer launched at time ``0``.
    """
    with patch_measure(elapsed_ns=0):
        unlaunched_measurer.launch()
    return unlaunched_measurer


# =========================================================================== #
#                            Elapsed Time Catcher                             #
# =========================================================================== #


@fixture
def patch_elapse(
    monkeypatch: MonkeyPatch,
) -> Callable[[Iterable[int]], ContextManager]:
    """Patch the elapse method in ElapsedTimeCatcher.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        Fixture been used to patch measure method.

    Returns
    -------
    Callable[[Iterable[int]], ContextManager]
        A context manager takes a list of intgers as nanoseconds and
        patch those as the return values of the elapse method.

    Examples
    --------
    >>> with patch_elapse(elapsed_times=[100, 200, 300]):
    ...     pass
    """

    @contextmanager
    def patch(elapsed_times: Iterable[int]) -> Iterator[None]:
        """Patch elapse method through monkeypatch context.

        Parameters
        ----------
        elapsed_times : Iterable[int]
            List of nanoseconds should be returned by the elapse method.
        """
        mock_measurer = Mock(spec=["launch", "elapse"])
        mock_measurer.elapse.side_effect = [
            ElapsedTime(nanoseconds=t) for t in elapsed_times
        ]

        monkeypatch.setattr(ElapsedTimeCatcher, "_measurer", mock_measurer)
        yield

    return patch


@fixture
def unlimited_catcher() -> ElapsedTimeCatcher:
    """Elapsed Time Catcher with unlimited storage size.

    Returns
    -------
    ElapsedTimeCatcher
        A newly created elapsed time catcher.
    """
    return ElapsedTimeCatcher()
