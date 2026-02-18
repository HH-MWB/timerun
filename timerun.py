"""TimeRun is a Python library for time measurements."""

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import AsyncGenerator, Callable, Generator
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import timedelta
from functools import wraps
from inspect import (
    isasyncgenfunction,
    iscoroutinefunction,
    isgeneratorfunction,
)
from threading import Lock, local
from time import perf_counter_ns, process_time_ns
from types import TracebackType
from typing import (
    Generic,
    Literal,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
)

__version__: str = "0.5.0"

__all__ = [
    "BlockTimer",
    "FunctionTimer",
    "Measurement",
    "TimeSpan",
    "__version__",
]

P = ParamSpec("P")  # callable parameters
R = TypeVar("R")  # callable return type
R_co = TypeVar("R_co", covariant=True)  # covariant return (Protocol)
Y = TypeVar("Y")  # generator yield type
T = TypeVar("T")  # context manager resource type


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
    metadata: dict[str, object] = field(default_factory=dict)


class _SyncToAsyncContextManagerMixin(ABC, Generic[T]):
    """Mixin: async context manager that delegates to sync __enter__/__exit__.

    Use with any class that implements __enter__ and __exit__; adds support
    for ``async with`` by calling the sync implementation.
    """

    @abstractmethod
    def __enter__(self) -> T: ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool: ...

    async def __aenter__(self) -> T:
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        return self.__exit__(exc_type, exc_val, exc_tb)


class BlockTimer(_SyncToAsyncContextManagerMixin[Measurement]):
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

    def __init__(self, metadata: dict[str, object] | None = None) -> None:
        """Initialize the context manager."""
        self._metadata = metadata if isinstance(metadata, dict) else {}
        self._local = local()

    def __enter__(self) -> Measurement:  # type: ignore[explicit-override]
        """Start timing; return the measurement record."""
        measurement = Measurement(metadata=deepcopy(self._metadata))
        if not hasattr(self._local, "stack"):
            self._local.stack = deque()
        self._local.stack.append(
            (measurement, perf_counter_ns(), process_time_ns()),
        )
        return measurement

    def __exit__(  # type: ignore[explicit-override]
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


class _BlockRecorder(_SyncToAsyncContextManagerMixin[Measurement]):
    """Records the measurement from a timed block (BlockTimer) into a deque.

    Used by FunctionTimer. Runs BlockTimer, then on exit appends the
    measurement to the deque under the lock and re-raises if the block raised.
    Supports ``with`` and ``async with`` via the mixin.
    """

    def __init__(
        self,
        metadata: dict[str, object] | None,
        measurements: deque[Measurement],
        lock: Lock,
    ) -> None:
        self._timer = BlockTimer(metadata=metadata)
        self._measurements = measurements
        self._lock = lock

    def __enter__(self) -> Measurement:  # type: ignore[explicit-override]
        self._measurement = self._timer.__enter__()  # pylint: disable=attribute-defined-outside-init
        return self._measurement

    def __exit__(  # type: ignore[explicit-override]
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        self._timer.__exit__(exc_type, exc_val, exc_tb)
        with self._lock:
            self._measurements.append(self._measurement)
        if exc_val is not None:
            raise exc_val
        return False


class _TimedCallable(Protocol[P, R_co]):  # pylint: disable=too-few-public-methods
    """Protocol for the wrapped callable with a measurements attribute."""

    measurements: deque[Measurement]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class FunctionTimer:  # pylint: disable=too-few-public-methods
    """Decorator for timing a function (wall time + CPU time).

    Use as ``@FunctionTimer()`` or
    ``@FunctionTimer(metadata={...}, maxlen=100)``.
    Supports sync functions, async functions, sync generators, and async
    generators. Each run uses :class:`BlockTimer`; one :class:`Measurement` per
    invocation (per call or per full generator consumption). Measurements are
    appended to a deque on the wrapped callable (attribute ``measurements``).

    Parameters
    ----------
    metadata : dict or None, optional
        Passed to :class:`BlockTimer` for each run; interpretation and defaults
        follow BlockTimer (e.g. None or non-dict become ``{}``). Read from the
        decorator instance at each invocation, so reassigning it affects future
        runs.
    maxlen : int or None, optional
        Maximum number of measurements to keep on the wrapped callable.
        Passed to the storage deque as ``deque(maxlen=maxlen)``; ``None``
        means unbounded. Oldest entries are dropped when full.

    Attributes (on wrapped callable)
    ---------------------------------
    measurements : deque of Measurement
        Deque of measurements (oldest to newest). Use ``func.measurements[-1]``
        for the last run, or iterate for history. Append is done under a lock
        for thread safety.

    Notes
    -----
    Generators: one measurement per full consumption (from first ``next()`` /
    ``anext()`` until exhausted or closed). Wall time and CPU time cover the
    entire consumption (generator + consumer code between iterations).

    Exceptions: if the callable raises, the measurement is still recorded
    (wall_time and cpu_time set by BlockTimer), then the exception propagates.

    Examples
    --------
    >>> @FunctionTimer(maxlen=10)
    ... def slow():
    ...     pass
    >>> slow()
    >>> slow.measurements[-1].wall_time.duration  # nanoseconds

    """

    def __init__(
        self,
        metadata: dict[str, object] | None = None,
        maxlen: int | None = None,
    ) -> None:
        """Initialize the decorator."""
        self._metadata = metadata
        self._maxlen = maxlen

    def __call__(  # noqa: C901
        self,
        f: Callable[P, R],
    ) -> (
        _TimedCallable[P, R]
        | _TimedCallable[P, AsyncGenerator[Y, None]]
        | _TimedCallable[P, Generator[Y, None, None]]
    ):
        """Wrap the function with timing."""
        measurements: deque[Measurement] = deque(maxlen=self._maxlen)
        lock = Lock()
        if isasyncgenfunction(f):

            @wraps(f)
            async def wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> AsyncGenerator[Y, None]:
                inner = f(*args, **kwargs)
                async with _BlockRecorder(
                    self._metadata,
                    measurements,
                    lock,
                ):
                    async for x in inner:
                        yield x

        elif iscoroutinefunction(f):

            @wraps(f)
            async def wrapper(  # type: ignore[return]
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> R:
                async with _BlockRecorder(
                    self._metadata,
                    measurements,
                    lock,
                ):
                    return cast("R", await f(*args, **kwargs))

        elif isgeneratorfunction(f):

            @wraps(f)
            def wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> Generator[Y, None, None]:
                inner = f(*args, **kwargs)
                with _BlockRecorder(self._metadata, measurements, lock):
                    yield from inner

        else:

            @wraps(f)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with _BlockRecorder(self._metadata, measurements, lock):
                    return f(*args, **kwargs)

        wrapped = cast(
            "_TimedCallable[P, R] | "
            "_TimedCallable[P, AsyncGenerator[Y, None]] | "
            "_TimedCallable[P, Generator[Y, None, None]]",
            wrapper,
        )
        wrapped.measurements = measurements
        return wrapped
