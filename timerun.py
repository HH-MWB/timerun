"""TimeRun is a Python library for time measurements."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import timedelta
from threading import local
from time import perf_counter_ns, process_time_ns
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from types import TracebackType

__version__: str = "0.5.0"

__all__ = [
    "BlockTimer",
    "Measurement",
    "TimeSpan",
    "__version__",
]


@dataclass(order=True, frozen=True)
class TimeSpan:
    """A time interval with start and end timestamps.

    Instances are immutable. Equality and ordering are based only on
    ``duration``; ``start`` and ``end`` are excluded from comparison.

    Attributes
    ----------
    duration : int
        Elapsed time in nanoseconds (end - start). Set in ``__post_init__``,
        not a constructor argument. Used for equality, ordering, and hashing.
    start : int
        Start timestamp in nanoseconds.
    end : int
        End timestamp in nanoseconds.
    timedelta : timedelta
        Read-only. Duration as a ``datetime.timedelta``; nanoseconds are
        converted to whole microseconds (``duration // 1000``) to match
        timedelta's resolution.

    Notes
    -----
    ``start`` and ``end`` use ``field(compare=False)``, so two spans with
    the same duration compare equal even if their intervals differ.

    """

    duration: int = field(init=False)
    start: int = field(compare=False)
    end: int = field(compare=False)

    def __post_init__(self) -> None:
        """Set duration to end minus start (nanoseconds)."""
        if self.end < self.start:
            msg = "end must be >= start"
            raise ValueError(msg)
        object.__setattr__(self, "duration", self.end - self.start)

    @property
    def timedelta(self) -> timedelta:
        """Duration as a datetime.timedelta."""
        return timedelta(microseconds=self.duration // 1000)


@dataclass
class Measurement:
    """A measurement collection: wall time, CPU time, and optional metadata.

    Stores one measurement only. Use this to collect the result of a single
    timing run: wall-clock time, CPU time, and any user-defined metadata.

    When created by :class:`BlockTimer`, ``wall_time`` and ``cpu_time`` are
    ``None`` until the block exits, then they are set to the measured spans.

    Attributes
    ----------
    wall_time : TimeSpan or None
        Wall-clock time for the measurement, or ``None`` if not yet set.
    cpu_time : TimeSpan or None
        CPU time for the measurement, or ``None`` if not yet set.
    metadata : dict
        Optional key-value metadata (e.g., tags, run id). Defaults to ``{}``;
        mutate in place to add or change entries.

    """

    wall_time: TimeSpan | None = None
    cpu_time: TimeSpan | None = None
    metadata: dict[object, object] = field(default_factory=dict)


class BlockTimer:
    """Context manager for timing a block (wall time + CPU time).

    Use with ``with`` or ``async with``. Yields a :class:`Measurement` whose
    ``wall_time`` and ``cpu_time`` are set when the block exits. End times are
    taken at the start of ``__exit__``, with wall time last.

    Optional ``metadata`` is stored by reference at construction; each
    measurement gets a deep copy at enter time. Exceptions propagate.

    Parameters
    ----------
    metadata : dict or None, optional
        Key-value metadata to attach to the yielded :class:`Measurement`.
        Stored by reference; each measurement gets a deep copy at enter time.
        Defaults to ``{}``.

    Yields
    ------
    Measurement
        The measurement record. Its ``wall_time`` and ``cpu_time`` are
        ``None`` on entry and set to :class:`TimeSpan` instances when the
        block exits.

    Notes
    -----
    Thread-safe: state is thread-local; one measurement per thread.

    Nested blocks: the same instance may be reused in sequential or nested
    blocks; each block gets its own measurement.

    Exceptions: if the block raises, ``wall_time`` and ``cpu_time`` are still
    set before the exception propagates.

    Async: ``async with`` uses the same synchronous timing.

    Examples
    --------
    >>> with BlockTimer() as m:
    ...     pass
    >>> m.wall_time.duration  # nanoseconds

    """

    def __init__(self, metadata: dict[object, object] | None = None) -> None:
        """Initialize the context manager."""
        self._metadata = metadata if isinstance(metadata, dict) else {}
        self._local = local()

    def __enter__(self) -> Measurement:
        """Start timing; return the measurement record."""
        measurement = Measurement(metadata=deepcopy(self._metadata))
        if not hasattr(self._local, "stack"):
            self._local.stack = deque()
        self._local.stack.append(
            (measurement, perf_counter_ns(), process_time_ns()),
        )
        return measurement

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        """Stop timing; set wall_time and cpu_time on the measurement."""
        cpu_end = process_time_ns()
        wall_end = perf_counter_ns()
        try:
            measurement, wall_start, cpu_start = self._local.stack.pop()
        except (AttributeError, IndexError) as e:
            msg = "__exit__ called without a matching __enter__"
            raise RuntimeError(msg) from e
        measurement.wall_time = TimeSpan(start=wall_start, end=wall_end)
        measurement.cpu_time = TimeSpan(start=cpu_start, end=cpu_end)
        return False

    async def __aenter__(self) -> Measurement:
        """Async entry: delegates to __enter__."""
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        """Async exit: delegates to __exit__."""
        return self.__exit__(exc_type, exc_value, traceback)
