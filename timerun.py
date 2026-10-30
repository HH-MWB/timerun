"""Structured wall-clock and CPU timing for Python blocks and callables.

Provides nanosecond-precision timing records combining wall-clock and
CPU durations with optional metadata for profiling and metrics.

Classes
-------
TimeSpan
    Immutable nanosecond time interval with duration and timedelta
    conversion.
Measurement
    Timing record with wall time, CPU time, and metadata for a run.
Timer
    Thread-safe and task-safe context manager and decorator for
    recording measurements.

"""

from asyncio import current_task
from collections import deque
from collections.abc import (
    AsyncGenerator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Mapping,
)
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import timedelta
from functools import wraps
from inspect import (
    isasyncgenfunction,
    iscoroutinefunction,
    isgeneratorfunction,
)
from threading import current_thread
from time import perf_counter_ns, thread_time_ns
from types import TracebackType
from typing import (
    Literal,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
)

__version__: str = "0.7.0"

__all__ = [
    "Measurement",
    "TimeSpan",
    "Timer",
]


# --- Data Models ---


@dataclass(frozen=True, slots=True)
class TimeSpan:
    """A time interval with start and end timestamps.

    Instances are immutable. Equality and hashing are based on interval
    identity (``start`` and ``end``). To compare or sort durations, use
    ``span.duration``.

    Attributes
    ----------
    start : int
        Start timestamp in nanoseconds.
    end : int
        End timestamp in nanoseconds.
    duration : int
        Elapsed interval duration in nanoseconds.
    timedelta : timedelta
        Duration as a ``datetime.timedelta``, converted to whole
        microseconds to match timedelta resolution.

    Raises
    ------
    ValueError
        If ``end < start``.

    """

    start: int
    end: int

    def __post_init__(self) -> None:
        """Validate end >= start."""
        if self.end < self.start:
            msg = "end must be >= start"
            raise ValueError(msg)

    @property
    def duration(self) -> int:
        """Elapsed interval duration in nanoseconds."""
        return self.end - self.start

    @property
    def timedelta(self) -> timedelta:
        """Duration as a datetime.timedelta."""
        return timedelta(microseconds=self.duration // 1000)


@dataclass(slots=True)
class Measurement:
    """Measurement record: wall time, CPU time, and optional metadata.

    When created by :class:`Timer` (context manager or decorator),
    ``wall_time`` and ``cpu_time`` are ``None`` until block exit, then
    they are set to the measured spans.

    Attributes
    ----------
    wall_time : TimeSpan or None
        Wall-clock time for the measurement, or ``None`` if not yet set.
    cpu_time : TimeSpan or None
        CPU time for the measurement, or ``None`` if not yet set.
    metadata : dict
        Optional key-value metadata (e.g., tags, run id). Defaults to
        ``{}``; mutate in place to add or change entries.

    """

    wall_time: TimeSpan | None = None
    cpu_time: TimeSpan | None = None
    metadata: dict[str, object] = field(
        default_factory=cast("Callable[[], dict[str, object]]", dict),
    )


# --- Internal Types & Protocols ---

_StackEntry = tuple[Measurement, int, int]
_StackTuple = tuple[_StackEntry, ...]

_P = ParamSpec("_P")
_R = TypeVar("_R")
_R_co = TypeVar("_R_co", covariant=True)


# pylint: disable=too-few-public-methods
class _TimedCallable(Protocol[_P, _R_co]):
    measurements: deque[Measurement]

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R_co: ...


# --- Timer Engine ---


class Timer:
    """Times execution and records wall-clock and CPU time per run.

    Use as a context manager (``with Timer() as m:`` or ``async with
    Timer() as m:``) to time a block: on exit, the yielded
    :class:`Measurement` has its ``wall_time`` and ``cpu_time`` set.

    Use as a decorator (``@Timer()`` or ``@Timer(metadata={...},
    maxlen=100)``) to time each call: supports sync and async
    functions and generators; one :class:`Measurement` per run is
    appended to the wrapped callable's ``measurements`` deque.

    Parameters
    ----------
    metadata : Mapping or None, optional
        Initial key-value metadata copied to each measurement.
        Defaults to ``{}``.
    on_start : callable or None, optional
        Called once per measurement when timing is about to start.
        Receives the :class:`Measurement` (with ``metadata`` set;
        ``wall_time`` and ``cpu_time`` are ``None``). Use for logging
        or setting up external span context. Defaults to ``None``.
    on_end : callable or None, optional
        Called once per measurement when timing has just ended.
        Receives the :class:`Measurement` with ``wall_time`` and
        ``cpu_time`` set. Use for logging duration, sending to
        OpenTelemetry, or enqueueing to a metrics pipeline. Defaults
        to ``None``.
    maxlen : int or None, optional
        Only used in decorator mode. Maximum number of measurements to
        keep on the wrapped callable. Ignored when used as a context
        manager. Defaults to ``None`` (unbounded).

    Notes
    -----
    Timer instances are safe for concurrent use across threads and
    asyncio tasks. Concurrent or interleaved timings on a shared
    Timer instance do not mix up or corrupt measurements.

    Callbacks are synchronous only. For async exporters (e.g.
    OpenTelemetry), schedule work from the callback (e.g.
    ``asyncio.create_task(export(m))`` when in an async context,
    or a thread/queue).

    Yields (context manager)
    -----------------------
    Measurement
        The measurement record. ``wall_time`` and ``cpu_time`` are
        set on block exit.

    Attributes (decorator mode, on wrapped callable)
    -----------------------------------------------
    measurements : deque of Measurement
        Deque of measurements (oldest to newest).

    Examples
    --------
    Context manager::

        with Timer() as m:
            pass  # code block to be measured
        print(m.wall_time.timedelta)

    Decorator::

        @Timer()
        def func():
            return
        func()
        print(func.measurements[-1].wall_time.timedelta)

    """

    def __init__(
        self,
        *,
        metadata: Mapping[str, object] | None = None,
        on_start: Callable[[Measurement], None] | None = None,
        on_end: Callable[[Measurement], None] | None = None,
        maxlen: int | None = None,
    ) -> None:
        """Initialize Timer with metadata, callbacks, and maxlen."""
        super().__init__()

        # Base metadata copied to each new measurement.
        self._metadata: dict[str, object] = (
            dict(metadata) if isinstance(metadata, Mapping) else {}
        )
        self._on_start = on_start
        self._on_end = on_end
        self._maxlen = maxlen

        # Context-local stack isolating active measurements per thread/task.
        self._stack_var: ContextVar[tuple[int | None, _StackTuple]] = (
            ContextVar(f"timerun_timer_stack_{id(self)}", default=(None, ()))
        )

    # --- Context Manager Protocol ---

    def __enter__(self) -> Measurement:
        """Start timing; return the measurement record."""
        return self._enter(is_async=False)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """Stop timing; update the measurement."""
        self._exit(is_async=False)
        return False

    async def __aenter__(self) -> Measurement:
        """Start timing (async); return the measurement record."""
        return self._enter(is_async=True)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """Stop timing (async); update the measurement."""
        self._exit(is_async=True)
        return False

    # --- Decorator Protocol ---

    def __call__(self, f: Callable[_P, _R]) -> _TimedCallable[_P, _R]:
        """Wrap a callable with timing (decorator usage)."""
        # Shared measurement buffer for the wrapped callable.
        measurements: deque[Measurement] = deque(maxlen=self._maxlen)

        # Build wrapper by callable type: async gen, coroutine, gen, or sync.
        wrapper: Callable[_P, object]
        if isasyncgenfunction(f):
            wrapper = self._wrap_async_gen(
                cast("Callable[_P, AsyncGenerator[_R, None]]", f),
                measurements,
            )
        elif iscoroutinefunction(f):
            wrapper = self._wrap_coroutine(
                cast("Callable[_P, Awaitable[_R]]", f),
                measurements,
            )
        elif isgeneratorfunction(f):
            wrapper = self._wrap_generator(
                cast("Callable[_P, Generator[_R, None, None]]", f),
                measurements,
            )
        else:
            wrapper = self._wrap_sync(f, measurements)

        # Expose measurements deque on wrapper attribute.
        wrapped = cast(
            "_TimedCallable[_P, _R]",
            wrapper,
        )
        wrapped.measurements = measurements
        return wrapped

    # --- Internal Context & Timing Mechanics ---

    def _enter(self, *, is_async: bool) -> Measurement:
        """Start a new timing measurement for the current context.

        Parameters
        ----------
        is_async : bool
            Whether entering from an async context.

        Returns
        -------
        Measurement
            Newly created measurement record for this timing run.

        """
        # Create measurement with isolated metadata copy and notify on_start.
        measurement = Measurement(metadata=self._metadata.copy())
        if self._on_start is not None:
            self._on_start(measurement)

        # Record start timestamps and append to context stack.
        owner_id, stack = self._get_context_stack(is_async=is_async)
        wall_start = perf_counter_ns()
        cpu_start = thread_time_ns()
        _ = self._stack_var.set(
            (owner_id, (*stack, (measurement, wall_start, cpu_start))),
        )
        return measurement

    def _exit(self, *, is_async: bool) -> None:
        """Finalize the active measurement for the current context.

        Parameters
        ----------
        is_async : bool
            Whether exiting from an async context.

        Raises
        ------
        RuntimeError
            If there is no active measurement in the current context.

        """
        # Capture end timestamps immediately to minimize overhead.
        cpu_end = thread_time_ns()
        wall_end = perf_counter_ns()

        # Pop the latest measurement from stack; raise if stack is empty.
        owner_id, stack = self._get_context_stack(is_async=is_async)
        if not stack:
            msg = "__exit__ called without a matching __enter__"
            raise RuntimeError(msg)
        measurement, wall_start, cpu_start = stack[-1]
        _ = self._stack_var.set((owner_id, stack[:-1]))

        # Assign completed time spans and run on_end callback if registered.
        measurement.wall_time = TimeSpan(start=wall_start, end=wall_end)
        measurement.cpu_time = TimeSpan(start=cpu_start, end=cpu_end)
        if self._on_end is not None:
            self._on_end(measurement)

    def _get_context_stack(
        self,
        *,
        is_async: bool,
    ) -> tuple[int, _StackTuple]:
        """Return execution owner id and stack for the current context.

        Parameters
        ----------
        is_async : bool
            True for task-local async stack, False for thread-local
            sync stack.

        Returns
        -------
        tuple
            Tuple of (owner_id, stack) for current execution context.

        Raises
        ------
        RuntimeError
            If is_async is True and there is no current asyncio task.

        """
        # Resolve execution owner: asyncio task ID or thread ID.
        try:
            task = current_task()
        except RuntimeError:
            task = None

        if is_async and task is None:
            msg = "no current asyncio task"
            raise RuntimeError(msg)

        owner_id = id(task) if task is not None else id(current_thread())

        # Use existing stack if owned by this context; reset if inherited.
        owner, stack = self._stack_var.get()
        return (owner_id, stack) if owner == owner_id else (owner_id, ())

    # --- Internal Decorator Wrappers ---

    def _wrap_sync(
        self,
        f: Callable[_P, _R],
        measurements: deque[Measurement],
    ) -> Callable[_P, _R]:
        """Wrap a synchronous function with timing."""

        @wraps(f)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            m: Measurement | None = None
            try:
                with self as m:
                    return f(*args, **kwargs)
            finally:
                if m is not None:
                    measurements.append(m)

        return wrapper

    def _wrap_generator(
        self,
        f: Callable[_P, Generator[_R, None, None]],
        measurements: deque[Measurement],
    ) -> Callable[_P, Generator[_R, None, None]]:
        """Wrap a generator function with timing."""

        @wraps(f)
        def wrapper(
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> Generator[_R, None, None]:
            m: Measurement | None = None
            try:
                with self as m:
                    yield from f(*args, **kwargs)
            finally:
                if m is not None:
                    measurements.append(m)

        return wrapper

    def _wrap_coroutine(
        self,
        f: Callable[_P, Awaitable[_R]],
        measurements: deque[Measurement],
    ) -> Callable[_P, Coroutine[None, None, _R]]:
        """Wrap a coroutine function with timing."""

        @wraps(f)
        async def wrapper(
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> _R:
            m: Measurement | None = None
            try:
                async with self as m:
                    return await f(*args, **kwargs)
            finally:
                if m is not None:
                    measurements.append(m)

        return wrapper

    def _wrap_async_gen(
        self,
        f: Callable[_P, AsyncGenerator[_R, None]],
        measurements: deque[Measurement],
    ) -> Callable[_P, AsyncGenerator[_R, None]]:
        """Wrap an async generator function with timing."""

        @wraps(f)
        async def wrapper(
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> AsyncGenerator[_R, None]:
            m: Measurement | None = None
            try:
                async with self as m:
                    async for x in f(*args, **kwargs):
                        yield x
            finally:
                if m is not None:
                    measurements.append(m)

        return wrapper
